from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from auth.dependencies import get_current_user
from core.config import settings
from models import User, get_session

router = APIRouter(prefix="/api/tokens", tags=["ai-tokens"])


class Envelope(BaseModel):
    code: int
    message: str
    data: dict | list | None


class BalanceResponse(BaseModel):
    user_id: int = 0
    username: str = "guest"
    role: str = "guest"
    ai_tokens: int


class ConsumeRequest(BaseModel):
    tokens: int = Field(..., gt=0, description="要扣减的 token 数量")
    reason: Optional[str] = Field(default=None, description="扣减原因")
    request_id: Optional[str] = Field(default=None, description="请求 ID（用于幂等）")


class ConsumeResponse(BaseModel):
    success: bool
    remaining: int
    consumed: int


@router.get("/balance")
async def get_balance(current_user: User = Depends(get_current_user)) -> Envelope:
    """
    获取 AI Token 余额（免登录）
    """
    return Envelope(
        code=0,
        message="ok",
        data=BalanceResponse(
            user_id=current_user.id or 0,
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
    AI Token 扣减接口（已禁用真实扣减，始终返回成功）
    """
    if payload.tokens > current_user.ai_tokens:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"required": payload.tokens, "remaining": current_user.ai_tokens},
        )

    current_user.ai_tokens -= payload.tokens
    session.add(current_user)
    session.commit()
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
