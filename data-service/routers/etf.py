from fastapi import APIRouter, Query
from typing import Optional

from services.etf_service import ETFService

router = APIRouter()


@router.get("/list")
async def get_etf_list(
    date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD，不传则使用最近交易日"),
    limit: int = Query(50, ge=1, le=500, description="返回数量限制")
):
    """获取 ETF 候选池"""
    service = ETFService()
    return service.get_etf_list(date=date, limit=limit)