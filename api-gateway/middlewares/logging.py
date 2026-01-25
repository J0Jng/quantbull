import json
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from core.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """结构化日志中间件"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """记录请求和响应"""
        start_time = time.time()
        
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"
        
        # 读取请求体（如果需要记录）
        request_body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = (request.headers.get("content-type") or "").lower()
            content_length_raw = request.headers.get("content-length")
            try:
                content_length = int(content_length_raw) if content_length_raw else 0
            except Exception:
                content_length = 0

            # multipart/大请求不读取 body，避免占用内存并影响后续处理（例如文件上传）。
            if "multipart/form-data" not in content_type and (not content_length or content_length <= 1024 * 1024):
            try:
                body = await request.body()
                if body:
                    request_body = body.decode("utf-8")[:500]  # 限制长度
            except Exception:
                pass
        
        # 处理请求
        try:
            response = await call_next(request)
            
            # 计算耗时
            process_time = time.time() - start_time
            
            # 获取响应体（如果是流式响应，跳过）
            response_body = None
            if isinstance(response, StreamingResponse):
                response_body = "[Streaming Response]"
            else:
                try:
                    if hasattr(response, "body"):
                        body_str = response.body.decode("utf-8")[:500] if response.body else None
                        response_body = body_str
                except Exception:
                    pass
            
            # 构建日志数据
            log_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "method": request.method,
                "path": str(request.url.path),
                "query_params": str(request.query_params) if request.query_params else None,
                "client_ip": client_ip,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 2),
                "request_body": request_body,
                "response_body": response_body,
            }
            
            # 记录日志
            if response.status_code >= 500:
                logger.error(json.dumps(log_data, ensure_ascii=False))
            elif response.status_code >= 400:
                logger.warning(json.dumps(log_data, ensure_ascii=False))
            else:
                logger.info(json.dumps(log_data, ensure_ascii=False))
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            log_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "method": request.method,
                "path": str(request.url.path),
                "client_ip": client_ip,
                "status_code": 500,
                "process_time_ms": round(process_time * 1000, 2),
                "error": str(e),
            }
            logger.error(json.dumps(log_data, ensure_ascii=False))
            raise
