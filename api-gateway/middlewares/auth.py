import re

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    """网关仅透传 Authorization，不在此处做 JWT 校验。"""
    
    # 白名单路径（不需要鉴权）
    WHITELIST_PATHS = [
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/",
        "/api/auth/login",
        "/api/auth/login/json",
        "/api/auth/register",
    ]
    
    # 白名单路径正则
    WHITELIST_PATTERNS = [
        r"^/docs",
        r"^/openapi",
        r"^/redoc",
    ]
    
    def __init__(self, app):
        super().__init__(app)
        self.whitelist_patterns = [re.compile(pattern) for pattern in self.WHITELIST_PATTERNS]
        self.protected_prefixes = tuple(
            f"/api{prefix if prefix.startswith('/') else '/' + prefix}".rstrip("/")
            for prefix in settings.route_mapping.keys()
        )
    
    def is_whitelisted(self, path: str) -> bool:
        """检查路径是否在白名单中"""
        if path in self.WHITELIST_PATHS:
            return True
        
        for pattern in self.whitelist_patterns:
            if pattern.match(path):
                return True
        
        return False

    def requires_auth(self, path: str) -> bool:
        """检查路径是否需要鉴权（基于服务前缀）"""
        return any(path.startswith(prefix) for prefix in self.protected_prefixes)
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 预检请求直接放行，避免因无 Authorization 导致 401
        if request.method.upper() == "OPTIONS":
            return await call_next(request)

        # 检查是否在白名单中
        if self.is_whitelisted(request.url.path):
            return await call_next(request)

        # 仅保护指定的业务前缀
        if not self.requires_auth(request.url.path):
            return await call_next(request)

        # 网关层只透传 Authorization 头，鉴权由下游服务负责
        return await call_next(request)
