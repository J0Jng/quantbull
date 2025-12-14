from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from core.config import settings
from schemas.auth import Token, LoginRequest
from services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """用户登录（OAuth2 标准格式）"""
    if not AuthService.authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"sub": form_data.username, "user_id": 1},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login/json", response_model=Token)
async def login_json(login_data: LoginRequest) -> Token:
    """用户登录（JSON 格式）"""
    if not AuthService.authenticate_user(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    
    access_token_expires = timedelta(minutes=settings.token_expire_minutes)
    access_token = AuthService.create_access_token(
        data={"sub": login_data.username, "user_id": 1},
        expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """获取当前用户信息"""
    token_data = AuthService.verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌",
        )
    return {
        "username": token_data.username,
        "user_id": token_data.user_id
    }
