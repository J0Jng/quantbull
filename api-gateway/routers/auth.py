from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from schemas.auth import LoginRequest
from services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/login", openapi_extra={"security": []})
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """用户登录（OAuth2 标准格式）- 委托 user-service"""
    return await AuthService.login_with_form(form_data.username, form_data.password)


@router.post("/login/json", openapi_extra={"security": []})
async def login_json(login_data: LoginRequest) -> dict:
    """用户登录（JSON 格式）- 委托 user-service"""
    return await AuthService.login_with_json(login_data.username, login_data.password)


@router.post("/register", openapi_extra={"security": []})
async def register(login_data: LoginRequest) -> dict:
    """用户注册 - 透传 user-service"""
    return await AuthService.register(login_data.username, login_data.password)


@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """获取当前用户信息，依赖 user-service 校验"""
    token_data = await AuthService.verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
        )
    return {
        "username": token_data.username,
        "user_id": token_data.user_id
    }


@router.get("/verify")
async def verify_token(token: str = Depends(oauth2_scheme)) -> dict:
    """校验令牌有效性 - 透传 user-service"""
    return await AuthService.verify_raw(token)
