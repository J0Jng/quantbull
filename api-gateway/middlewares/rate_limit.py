import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IP 级别限流中间件（内存实现）"""
    
    def __init__(self, app):
        super().__init__(app)
        # IP -> [(timestamp, count), ...]
        self.rate_limit_store: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 60  # 清理间隔（秒）
        self.last_cleanup = time.time()
    
    def get_client_ip(self, request: Request) -> str:
        """获取客户端 IP"""
        client_host = request.client.host if request.client else "unknown"

        # 仅在可信代理或本地环境下读取转发头
        trust_forwarded = settings.env == "local" or client_host in set(settings.trusted_proxies)
        if trust_forwarded:
            forwarded = request.headers.get("X-Forwarded-For")
            if forwarded:
                return forwarded.split(",")[0].strip()
            
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                return real_ip
        
        return client_host
    
    def cleanup_old_records(self):
        """清理过期记录"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        self.last_cleanup = current_time
        cutoff_time = current_time - 3600  # 保留1小时内的记录
        
        for ip in list(self.rate_limit_store.keys()):
            self.rate_limit_store[ip] = [
                (ts, count) for ts, count in self.rate_limit_store[ip]
                if ts > cutoff_time
            ]
            if not self.rate_limit_store[ip]:
                del self.rate_limit_store[ip]
    
    def check_rate_limit(self, ip: str) -> Tuple[bool, str]:
        """检查是否超过限流"""
        current_time = time.time()
        
        # 清理过期记录
        self.cleanup_old_records()
        
        # 获取该 IP 的记录
        records = self.rate_limit_store[ip]
        
        # 检查每分钟限制
        minute_records = [
            (ts, count) for ts, count in records
            if current_time - ts < 60
        ]
        minute_count = sum(count for _, count in minute_records)
        
        if minute_count >= settings.rate_limit_per_minute:
            return False, f"每分钟请求数超过限制 ({settings.rate_limit_per_minute})"
        
        # 检查每小时限制
        hour_records = [
            (ts, count) for ts, count in records
            if current_time - ts < 3600
        ]
        hour_count = sum(count for _, count in hour_records)
        
        if hour_count >= settings.rate_limit_per_hour:
            return False, f"每小时请求数超过限制 ({settings.rate_limit_per_hour})"
        
        # 记录本次请求
        records.append((current_time, 1))
        self.rate_limit_store[ip] = records
        
        return True, ""
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 白名单路径跳过限流
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc", "/"]:
            return await call_next(request)
        
        # 获取客户端 IP
        client_ip = self.get_client_ip(request)
        
        # 检查限流
        allowed, message = self.check_rate_limit(client_ip)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for IP {client_ip}: {message}")
            return Response(
                content=f'{{"detail": "{message}"}}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(settings.rate_limit_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60"
                }
            )
        
        return await call_next(request)
