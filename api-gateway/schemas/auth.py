from typing import Optional

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class Token(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token 数据"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
