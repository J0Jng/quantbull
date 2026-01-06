import re

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    """网关鉴权中间件：对受保护路由强制校验 Bearer Token（委托 user-service）。"""
    
    # 白名单路径（不需要鉴权）精确匹配的白名单
    WHITELIST_PATHS = [
        "/health",
        ##"/docs",
        ##"/openapi.json",
        ##"/redoc",
        "/",
        "/api/auth/login",
        "/api/auth/login/json",
        "/api/auth/register",
    ]
    
    # 白名单路径正则 这里用的是 ^，表示“从字符串开头匹配”，所以它等价于“放行某个前缀
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

        authorization = request.headers.get("authorization")
        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"code": status.HTTP_401_UNAUTHORIZED, "message": "缺少 Authorization 请求头", "data": None},
            )

        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token.strip():
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "code": status.HTTP_401_UNAUTHORIZED,
                    "message": "无效的 Authorization 格式，需使用 'Bearer <token>'",
                    "data": None,
                },
            )

        # 网关层统一校验 token（委托 user-service），并注入 request.state.user
        from services.auth_service import AuthService

        token_data = await AuthService.verify_token(token.strip())
        if token_data is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"code": status.HTTP_401_UNAUTHORIZED, "message": "无效或已过期的令牌", "data": None},
            )

        request.state.user = token_data
        return await call_next(request)
