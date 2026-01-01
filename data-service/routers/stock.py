from fastapi import APIRouter, Query
from typing import Optional

from services.stock_service import StockService

router = APIRouter()


@router.get("/list")
async def get_stock_list(
    date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD，不传则使用最近交易日"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    min_turnover: float = Query(0, ge=0, description="最小成交额过滤（元）")
):
    """获取股票候选池"""
    service = StockService()
    return service.get_stock_list(date=date, limit=limit, min_turnover=min_turnover)