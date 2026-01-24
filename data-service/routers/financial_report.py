"""财报（年报季报）数据路由"""
from fastapi import APIRouter, Query
from typing import Optional

from core.database import get_async_session
from services.eastmoney_bbsj_service import EastmoneyBbsjService

router = APIRouter()


@router.get("/financial-report/yjbb")
async def get_yjbb(
    period: Optional[str] = Query(None, description="报告期 YYYYMM"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    market: str = Query("all"),
    industry: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    refresh: bool = Query(False),
    codes: Optional[str] = Query(None),
):
    async for db_session in get_async_session():
        service = EastmoneyBbsjService(db_session=db_session)
        data = await service.fetch_yjbb(
            period=period,
            page=page,
            page_size=page_size,
            market=market,
            industry=industry,
            sort=sort,
            refresh=refresh,
            codes=codes,
        )
        return data


@router.get("/financial-report/yjkb")
async def get_yjkb(
    period: Optional[str] = Query(None, description="报告期 YYYYMM"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    market: str = Query("all"),
    industry: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    refresh: bool = Query(False),
    codes: Optional[str] = Query(None),
):
    async for db_session in get_async_session():
        service = EastmoneyBbsjService(db_session=db_session)
        data = await service.fetch_yjkb(
            period=period,
            page=page,
            page_size=page_size,
            market=market,
            industry=industry,
            sort=sort,
            refresh=refresh,
            codes=codes,
        )
        return data


@router.get("/financial-report/yjyg")
async def get_yjyg(
    period: Optional[str] = Query(None, description="报告期 YYYYMM"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    market: str = Query("all"),
    indicator: Optional[str] = Query(None, description="预告指标"),
    forecast_type: Optional[str] = Query(None, alias="type", description="预告类型"),
    refresh: bool = Query(False),
    codes: Optional[str] = Query(None),
):
    async for db_session in get_async_session():
        service = EastmoneyBbsjService(db_session=db_session)
        data = await service.fetch_yjyg(
            period=period,
            page=page,
            page_size=page_size,
            market=market,
            indicator=indicator,
            forecast_type=forecast_type,
            refresh=refresh,
            codes=codes,
        )
        return data


@router.get("/financial-report/yysj")
async def get_yysj(
    period: Optional[str] = Query(None, description="报告期 YYYYMM"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    market: str = Query("all"),
    refresh: bool = Query(False),
    codes: Optional[str] = Query(None),
):
    async for db_session in get_async_session():
        service = EastmoneyBbsjService(db_session=db_session)
        data = await service.fetch_yysj(
            period=period,
            page=page,
            page_size=page_size,
            market=market,
            refresh=refresh,
            codes=codes,
        )
        return data
