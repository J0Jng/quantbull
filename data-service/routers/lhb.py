"""龙虎榜数据路由"""
from fastapi import APIRouter, Query
from typing import Optional

from core.database import get_async_session
from core.response import success, error
from services.eastmoney_lhb_service import EastmoneyLhbService

router = APIRouter()


@router.get("/lhb/stocks")
async def get_lhb_stocks(
    trade_date: Optional[str] = Query(None, description="交易日期 YYYYMMDD 或 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    refresh: bool = Query(False),
):
    try:
        async for db_session in get_async_session():
            service = EastmoneyLhbService(db_session=db_session)
            data = await service.fetch_stocks(
                trade_date=trade_date,
                page=page,
                page_size=page_size,
                refresh=refresh,
            )
            return success(data)
    except Exception as exc:
        return error(f"获取龙虎榜数据失败: {exc}")


@router.get("/lhb/stocks/summary")
async def get_lhb_summary(
    days: int = Query(5, ge=1, le=30),
    end_trade_date: Optional[str] = Query(None, description="截止交易日 YYYYMMDD 或 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    refresh: bool = Query(False),
):
    if days not in {1, 3, 5, 10, 20, 30}:
        return error("days 必须为 1/3/5/10/20/30")
    try:
        async for db_session in get_async_session():
            service = EastmoneyLhbService(db_session=db_session)
            data = await service.fetch_summary(
                window_days=days,
                end_trade_date=end_trade_date,
                page=page,
                page_size=page_size,
                refresh=refresh,
            )
            return success(data)
    except Exception as exc:
        return error(f"获取龙虎榜汇总失败: {exc}")


@router.get("/lhb/institutions/trades")
async def get_lhb_institution_trades(
    trade_date: Optional[str] = Query(None, description="交易日期 YYYYMMDD 或 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    refresh: bool = Query(False),
):
    try:
        async for db_session in get_async_session():
            service = EastmoneyLhbService(db_session=db_session)
            data = await service.fetch_institution_trades(
                trade_date=trade_date,
                page=page,
                page_size=page_size,
                refresh=refresh,
            )
            return success(data)
    except Exception as exc:
        return error(f"获取机构买卖情况失败: {exc}")


@router.get("/lhb/institutions/seats/track")
async def get_lhb_institution_seat_track(
    days: int = Query(5, ge=1, le=30),
    end_trade_date: Optional[str] = Query(None, description="截止交易日 YYYYMMDD 或 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    refresh: bool = Query(False),
):
    if days not in {1, 3, 5, 10, 20, 30}:
        return error("days 必须为 1/3/5/10/20/30")
    try:
        async for db_session in get_async_session():
            service = EastmoneyLhbService(db_session=db_session)
            data = await service.fetch_institution_seat_track(
                window_days=days,
                end_trade_date=end_trade_date,
                page=page,
                page_size=page_size,
                refresh=refresh,
            )
            return success(data)
    except Exception as exc:
        return error(f"获取机构席位追踪失败: {exc}")


@router.get("/lhb/brokers/active")
async def get_lhb_active_brokers(
    trade_date: Optional[str] = Query(None, description="交易日期 YYYYMMDD 或 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    refresh: bool = Query(False),
):
    try:
        async for db_session in get_async_session():
            service = EastmoneyLhbService(db_session=db_session)
            data = await service.fetch_active_brokers(
                trade_date=trade_date,
                page=page,
                page_size=page_size,
                refresh=refresh,
            )
            return success(data)
    except Exception as exc:
        return error(f"获取每日活跃营业部失败: {exc}")


@router.get("/lhb/brokers/rank")
async def get_lhb_broker_rank(
    days: int = Query(5, ge=1, le=30),
    end_trade_date: Optional[str] = Query(None, description="截止交易日 YYYYMMDD 或 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    refresh: bool = Query(False),
):
    if days not in {1, 3, 5, 10, 20, 30}:
        return error("days 必须为 1/3/5/10/20/30")
    try:
        async for db_session in get_async_session():
            service = EastmoneyLhbService(db_session=db_session)
            data = await service.fetch_broker_rank(
                window_days=days,
                end_trade_date=end_trade_date,
                page=page,
                page_size=page_size,
                refresh=refresh,
            )
            return success(data)
    except Exception as exc:
        return error(f"获取营业部排行失败: {exc}")


@router.get("/lhb/brokers/onlist/stats")
async def get_lhb_broker_onlist_stats(
    days: int = Query(90, ge=1, le=365),
    end_trade_date: Optional[str] = Query(None, description="截止交易日 YYYYMMDD 或 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    refresh: bool = Query(False),
):
    if days not in {30, 90, 180, 365}:
        return error("days 必须为 30/90/180/365")
    try:
        async for db_session in get_async_session():
            service = EastmoneyLhbService(db_session=db_session)
            data = await service.fetch_broker_onlist_stats(
                window_days=days,
                end_trade_date=end_trade_date,
                page=page,
                page_size=page_size,
                refresh=refresh,
            )
            return success(data)
    except Exception as exc:
        return error(f"获取营业部上榜统计失败: {exc}")
