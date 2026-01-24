from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from services.eastmoney_fund_flow_service import EastmoneyFundFlowService

router = APIRouter()


@router.get("/market", summary="大盘资金流向")
async def get_market_fund_flow(
    market: str = Query("hs", description="市场标识 hs/sh/sz"),
    refresh: bool = Query(False, description="是否强制刷新"),
    db: AsyncSession = Depends(get_async_session),
):
    service = EastmoneyFundFlowService(db_session=db)
    return await service.get_market_flow(market=market, refresh=refresh)


@router.get("/sectors", summary="板块资金流向")
async def get_sector_fund_flow(
    type: str = Query("industry", description="板块类型 industry/concept/region"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    order: str = Query("desc", description="排序方向 desc/asc"),
    refresh: bool = Query(False, description="是否强制刷新"),
    db: AsyncSession = Depends(get_async_session),
):
    service = EastmoneyFundFlowService(db_session=db)
    return await service.get_sector_flow(
        sector_type=type,
        page=page,
        page_size=page_size,
        order=order,
        refresh=refresh,
    )


@router.get("/stocks", summary="个股资金流向")
async def get_stock_fund_flow(
    market: str = Query("all", description="市场 all/hsa/sha/sza/kcb/cyb"),
    stat: int = Query(1, description="统计周期 1/5/10"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    refresh: bool = Query(False, description="是否强制刷新"),
    db: AsyncSession = Depends(get_async_session),
):
    service = EastmoneyFundFlowService(db_session=db)
    return await service.get_stock_flow(
        market=market,
        stat=stat,
        page=page,
        page_size=page_size,
        refresh=refresh,
    )
