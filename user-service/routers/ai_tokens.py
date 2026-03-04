from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field
from core.config import settings

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
async def get_balance() -> Envelope:
    """
    获取 AI Token 余额（免登录）
    """
    return Envelope(
        code=0,
        message="ok",
        data=BalanceResponse(
            ai_tokens=settings.default_ai_tokens,
        ).model_dump()
    )


@router.post("/consume")
async def consume_tokens(
    payload: ConsumeRequest,
) -> Envelope:
    """
    AI Token 扣减接口（已禁用真实扣减，始终返回成功）
    """
    return Envelope(
        code=0,
        message="ok",
        data=ConsumeResponse(
            success=True,
            remaining=settings.default_ai_tokens,
            consumed=0,
        ).model_dump()
    )
