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


@router.get("/snapshot")
async def get_stock_snapshot(
    date: Optional[str] = Query(None, description="交易日期 YYYY-MM-DD，不传则使用最近交易日"),
    limit: int = Query(200, ge=1, le=1000, description="返回数量限制"),
    min_turnover: float = Query(0, ge=0, description="最小成交额过滤（元）"),
    sort: str = Query("amount", description="排序方式：rise/fall/amount/volume"),
    refresh: bool = Query(False, description="是否触发后台数据刷新")
):
    """
    获取聚合股票快照列表
    
    整合 stock_basic（基础信息、换手率）和 realtime_quotes（实时价格、成交额）
    优先使用实时数据，若无实时数据则降级到基础数据
    
    - 消除"未知/--"字段
    - DB 侧完成数据整合
    - 一次查询返回完整字段
    """
    service = StockService()
    return service.get_stock_snapshot_list(
        date=date,
        limit=limit,
        min_turnover=min_turnover,
        sort=sort,
        refresh=refresh
    )