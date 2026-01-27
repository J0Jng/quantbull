from fastapi import APIRouter, Query
from typing import Optional

from services.market_service import MarketService

router = APIRouter()


@router.get("/overview")
async def get_market_overview(
    date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD，不传则使用最近交易日")
):
    """获取市场概览"""
    service = MarketService()
    return service.get_market_overview(date=date)


@router.get("/is-trading-day")
async def is_trading_day(
    date: str = Query(..., description="日期 YYYY-MM-DD")
):
    """判断是否交易日"""
    service = MarketService()
    return service.is_trading_day(date=date)