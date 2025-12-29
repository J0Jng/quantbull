from fastapi import APIRouter

from services.market_service import MarketService

router = APIRouter()


@router.get("/overview")
async def get_market_overview():
    """获取市场概览"""
    service = MarketService()
    return service.get_market_overview()