import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from schemas.auth import LoginRequest, RegisterRequest
from core.config import settings
from services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def _set_auth_cookies(response: Response, token: str) -> None:
    csrf_token = secrets.token_urlsafe(32)
    max_age = settings.token_expire_minutes * 60
    secure_flag = False if settings.env == "local" else settings.cookie_secure
    response.set_cookie(
        settings.auth_cookie_name,
        token,
        httponly=True,
        secure=secure_flag,
        samesite=settings.cookie_samesite,
        max_age=max_age,
        domain=settings.cookie_domain,
        path="/",
    )
    response.set_cookie(
        settings.csrf_cookie_name,
        csrf_token,
        httponly=False,
        secure=secure_flag,
        samesite=settings.cookie_samesite,
        max_age=max_age,
        domain=settings.cookie_domain,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(settings.auth_cookie_name, domain=settings.cookie_domain, path="/")
    response.delete_cookie(settings.csrf_cookie_name, domain=settings.cookie_domain, path="/")


def _extract_token(request: Request, fallback: str | None = None) -> str | None:
    authorization = request.headers.get("authorization")
    if authorization:
        scheme, _, raw = authorization.partition(" ")
        if scheme.lower() == "bearer" and raw.strip():
            return raw.strip()
    cookie_token = request.cookies.get(settings.auth_cookie_name)
    return cookie_token or fallback


@router.post("/login", openapi_extra={"security": []})
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """用户登录（OAuth2 标准格式）- 委托 user-service
    
    返回格式符合 OAuth2 标准，供 Swagger UI 使用
    """
    result = await AuthService.login_with_form(form_data.username, form_data.password)
    # 将 Envelope 格式转换为 OAuth2 标准格式
    if result.get("code") == 0 and result.get("data"):
        token = result["data"].get("access_token")
        if token:
            _set_auth_cookies(response, token)
        return {"code": 0, "message": "ok", "data": result["data"]}
    return result


@router.post("/login/json", openapi_extra={"security": []})
async def login_json(response: Response, login_data: LoginRequest) -> dict:
    """用户登录（JSON 格式）- 委托 user-service"""
    result = await AuthService.login_with_json(login_data.username, login_data.password)
    if result.get("code") == 0 and result.get("data"):
        token = result["data"].get("access_token")
        if token:
            _set_auth_cookies(response, token)
        return {"code": 0, "message": "ok", "data": result["data"]}
    return result


@router.post("/register", openapi_extra={"security": []})
async def register(response: Response, register_data: RegisterRequest) -> dict:
    """用户注册 - 透传 user-service"""
    result = await AuthService.register(
        register_data.username,
        register_data.password,
        register_data.phone,
        register_data.email,
    )
    if result.get("code") == 0 and result.get("data"):
        token = result["data"].get("access_token")
        if token:
            _set_auth_cookies(response, token)
        return {"code": 0, "message": "ok", "data": result["data"]}
    return result


@router.get("/me")
async def get_current_user(request: Request, token: str | None = Depends(oauth2_scheme)) -> dict:
    """获取当前用户信息，依赖 user-service 校验"""
    real_token = _extract_token(request, token)
    if not real_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌")
    token_data = await AuthService.verify_token(real_token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
        )
    return {
        "username": token_data.username,
        "user_id": token_data.user_id,
        "role": token_data.role or "user",
        "qualified_investor": token_data.qualified_investor,
        "investor_tags": token_data.investor_tags,
        "investor_certified_at": token_data.investor_certified_at,
        "email": token_data.email,
        "phone": token_data.phone,
        "created_at": token_data.created_at,
    }


@router.get("/verify")
async def verify_token(request: Request, token: str | None = Depends(oauth2_scheme)) -> dict:
    """校验令牌有效性 - 透传 user-service"""
    real_token = _extract_token(request, token)
    if not real_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的令牌")
    return await AuthService.verify_raw(real_token)


@router.post("/logout")
async def logout(response: Response) -> dict:
    _clear_auth_cookies(response)
    return {"code": 0, "message": "ok", "data": None}
