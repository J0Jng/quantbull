from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings


class CsrfMiddleware(BaseHTTPMiddleware):
    """对 Cookie 认证请求启用 CSRF 校验"""

    # 不需要 CSRF 校验的路径（认证相关接口必须放行）
    WHITELIST_PATHS = {
        "/api/auth/login",
        "/api/auth/login/json",
        "/api/auth/register",
        "/api/auth/logout",
    }

    async def dispatch(self, request: Request, call_next):
        method = request.method.upper()
        if method in {"GET", "HEAD", "OPTIONS"}:
            return await call_next(request)

        # 登录/注册/退出等认证接口不需要 CSRF 校验
        if request.url.path in self.WHITELIST_PATHS:
            return await call_next(request)

        # 若使用 Authorization 头，则认为是非 Cookie 认证，跳过 CSRF
        authorization = request.headers.get("authorization")
        if authorization and authorization.lower().startswith("bearer "):
            return await call_next(request)

        # Cookie 认证场景：要求 X-CSRF-Token 与 Cookie 一致
        auth_cookie = request.cookies.get(settings.auth_cookie_name)
        if auth_cookie:
            csrf_cookie = request.cookies.get(settings.csrf_cookie_name)
            csrf_header = request.headers.get("X-CSRF-Token")
            if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"code": status.HTTP_403_FORBIDDEN, "message": "CSRF 校验失败", "data": None},
                )

        return await call_next(request)