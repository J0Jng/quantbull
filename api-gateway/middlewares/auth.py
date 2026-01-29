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
        "/api/ai/health",
        "/api/ai/health/",
        "/api/strategy/builtin",
        "/api/strategy/builtin/",
        "/api/strategy/validate",
        "/api/auth/login",
        "/api/auth/login/json",
        "/api/auth/register"
    ]
    
    # 白名单路径正则 这里用的是 ^，表示“从字符串开头匹配”，所以它等价于“放行某个前缀
    WHITELIST_PATTERNS = [
        r"^/docs",
        r"^/openapi",
        r"^/redoc",
        r"^/api/company-research",  # 公司研报接口不需要认证
        r"^/api/market/overview",  # 市场概览不需要认证
        r"^/api/finance-channel",  # 财经频道前台页面公开访问
        r"^/api/news/eastmoney",  # 东方财富新闻公开访问
        r"^/api/funds",  # 基金排行榜公开访问
        r"^/api/fundflow",  # 资金流向公开访问
        r"^/api/financial-report",  # 财报数据公开访问
        r"^/api/lhb",  # 龙虎榜公开访问
        r"^/api/profit-forecast",  # 盈利预测公开访问
    ]
    
    def __init__(self, app):
        super().__init__(app)
        self.whitelist_patterns = [re.compile(pattern) for pattern in self.WHITELIST_PATTERNS]
        self.protected_prefixes = tuple(
            f"/api{prefix if prefix.startswith('/') else '/' + prefix}".rstrip("/")
            for prefix in settings.route_mapping.keys()
        )
    
    def is_whitelisted(self, path: str, method: str) -> bool:
        """检查路径是否在白名单中"""
        if path in self.WHITELIST_PATHS:
            return True
        
        for pattern in self.whitelist_patterns:
            if pattern.match(path):
                return True
        
        # 特殊处理：/api/news/headlines 仅 GET 放行
        if path.startswith("/api/news/headlines") and method.upper() == "GET":
            return True

        # 视频中心列表允许匿名访问（仅 GET 放行）
        if path.startswith("/api/videos") and method.upper() == "GET":
            return True

        # 静态资源允许匿名访问（仅 GET 放行）
        if path.startswith("/api/static") and method.upper() == "GET":
            return True

        # 商城商品列表/详情允许匿名访问（仅 GET 放行）
        if path.startswith("/api/products") and method.upper() == "GET":
            return True
        
        return False

    def requires_auth(self, path: str) -> bool:
        """检查路径是否需要鉴权（基于服务前缀）"""
        if path.startswith("/api/gateway"):
            return True
        return any(path.startswith(prefix) for prefix in self.protected_prefixes)
    
    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 预检请求直接放行，避免因无 Authorization 导致 401
        if request.method.upper() == "OPTIONS":
            return await call_next(request)

        # 检查是否在白名单中
        if self.is_whitelisted(request.url.path, request.method):
            return await call_next(request)

        # 仅保护指定的业务前缀
        if not self.requires_auth(request.url.path):
            return await call_next(request)

        token = None
        authorization = request.headers.get("authorization")
        if authorization:
            scheme, _, raw = authorization.partition(" ")
            if scheme.lower() == "bearer" and raw.strip():
                token = raw.strip()

        if token is None:
            cookie_token = request.cookies.get(settings.auth_cookie_name)
            if cookie_token:
                token = cookie_token

        if not token:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"code": status.HTTP_401_UNAUTHORIZED, "message": "缺少认证信息", "data": None},
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
        try:
            response = await call_next(request)
        except RuntimeError as exc:
            if "No response returned" in str(exc):
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "下游服务未返回响应", "data": None},
                )
            raise

        if response is None:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "下游服务未返回响应", "data": None},
            )

        return response
