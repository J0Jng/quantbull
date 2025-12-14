from fastapi import APIRouter

from routers.ai import router as ai_router

api_router = APIRouter()

# 注册所有路由
api_router.include_router(ai_router, prefix="/ai", tags=["AI"])

__all__ = ["api_router"]
