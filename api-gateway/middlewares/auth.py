import re
from typing import Optional

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from core.config import settings
from services.auth_service import AuthService


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT 鉴权中间件"""
    
    # 白名单路径（不需要鉴权）
    WHITELIST_PATHS = [
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/",
        "/api/auth/login",
        "/api/auth/login/json",
        "/api/auth/me",
    ]
    
    # 白名单路径正则
    WHITELIST_PATTERNS = [
        r"^/docs",
        r"^/openapi",
        r"^/redoc",
        r"^/api/auth",
    ]
    
    def __init__(self, app):
        super().__init__(app)
        self.whitelist_patterns = [re.compile(pattern) for pattern in self.WHITELIST_PATTERNS]
    
    def is_whitelisted(self, path: str) -> bool:
        """检查路径是否在白名单中"""
        if path in self.WHITELIST_PATHS:
            return True
        
        for pattern in self.whitelist_patterns:
            if pattern.match(path):
                return True
        
        return False
    
    def extract_token(self, authorization: Optional[str]) -> Optional[str]:
        """从 Authorization 头中提取 token"""
        if not authorization:
            return None
        
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        return parts[1]
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 预检请求直接放行，避免因无 Authorization 导致 401
        if request.method.upper() == "OPTIONS":
            return await call_next(request)

        # 检查是否在白名单中
        if self.is_whitelisted(request.url.path):
            return await call_next(request)
        
        # 提取 token
        authorization = request.headers.get("Authorization")
        token = self.extract_token(authorization)
        
        if not token:
            return Response(
                content='{"detail": "缺少认证令牌"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 验证 token
        token_data = AuthService.verify_token(token)
        if token_data is None:
            return Response(
                content='{"detail": "无效或过期的令牌"}',
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="application/json",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # 将用户信息添加到请求状态中
        request.state.user = token_data
        
        return await call_next(request)
