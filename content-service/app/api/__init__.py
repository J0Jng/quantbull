"""
API Router aggregation
"""
from fastapi import APIRouter
from . import content, h5, wechat

router = APIRouter()

router.include_router(content.router, prefix="/content", tags=["content"])
router.include_router(h5.router, prefix="/h5", tags=["h5"])
router.include_router(wechat.router, prefix="/wechat", tags=["wechat"])