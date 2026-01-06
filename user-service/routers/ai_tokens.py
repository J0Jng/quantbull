from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlmodel import Session
from sqlalchemy import text

from auth.jwt import verify_token
from models import User, get_session, get_user_by_username, auth_engine

router = APIRouter(prefix="/api/tokens", tags=["ai-tokens"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Envelope(BaseModel):
    code: int
    message: str
    data: dict | list | None


class BalanceResponse(BaseModel):
    user_id: int
    username: str
    role: str
    ai_tokens: int


class ConsumeRequest(BaseModel):
    tokens: int = Field(..., gt=0, description="要扣减的 token 数量")
    reason: Optional[str] = Field(default=None, description="扣减原因")
    request_id: Optional[str] = Field(default=None, description="请求 ID（用于幂等）")


class ConsumeResponse(BaseModel):
    success: bool
    remaining: int
    consumed: int


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    """依赖函数：获取当前用户"""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
    
    user = get_user_by_username(session, payload["username"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")
    
    return user


@router.get("/balance")
async def get_balance(
    current_user: User = Depends(get_current_user),
) -> Envelope:
    """
    获取当前用户的 AI Token 余额
    
    - admin 用户虽然返回 ai_tokens 值，但实际上没有限制
    """
    if current_user.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="user id is missing")
    
    return Envelope(
        code=0,
        message="ok",
        data=BalanceResponse(
            user_id=current_user.id,
            username=current_user.username,
            role=current_user.role,
            ai_tokens=current_user.ai_tokens,
        ).model_dump()
    )


@router.post("/consume")
async def consume_tokens(
    payload: ConsumeRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Envelope:
    """
    扣减用户 AI Token
    
    - admin 用户不检查、不扣减，直接返回成功
    - 普通用户检查余额，余额不足返回 402 错误
    - 使用数据库原子更新保证并发安全
    """
    if current_user.id is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="user id is missing")
    
    # admin 用户不扣减
    if current_user.role == "admin":
        return Envelope(
            code=0,
            message="ok",
            data=ConsumeResponse(
                success=True,
                remaining=current_user.ai_tokens,
                consumed=0,
            ).model_dump()
        )
    
    # 普通用户：原子扣减
    # 使用原子更新确保并发安全：UPDATE user SET ai_tokens = ai_tokens - :tokens WHERE id=:id AND ai_tokens >= :tokens
    with auth_engine.connect() as conn:
        # 根据数据库类型执行不同的 SQL
        from core.config import settings
        
        if settings.database_url.startswith("sqlite"):
            result = conn.execute(
                text("UPDATE user SET ai_tokens = ai_tokens - :tokens WHERE id = :id AND ai_tokens >= :tokens"),
                {"tokens": payload.tokens, "id": current_user.id}
            )
        else:
            # PostgreSQL 和其他数据库
            result = conn.execute(
                text("UPDATE \"user\" SET ai_tokens = ai_tokens - :tokens WHERE id = :id AND ai_tokens >= :tokens"),
                {"tokens": payload.tokens, "id": current_user.id}
            )
        
        conn.commit()
        
        # 检查是否更新成功（受影响行数）
        if result.rowcount == 0:
            # 余额不足
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "code": 402,
                    "message": "Insufficient AI tokens",
                    "required": payload.tokens,
                    "remaining": current_user.ai_tokens,
                }
            )
    
    # 刷新用户信息获取最新余额
    session.refresh(current_user)
    
    return Envelope(
        code=0,
        message="ok",
        data=ConsumeResponse(
            success=True,
            remaining=current_user.ai_tokens,
            consumed=payload.tokens,
        ).model_dump()
    )
