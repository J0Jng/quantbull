"""盈利预测数据路由"""
from fastapi import APIRouter, Query
from typing import Optional

from core.response import success, error
from services.eastmoney_profit_forecast_service import EastmoneyProfitForecastService

router = APIRouter()


@router.get("/profit-forecast")
async def get_profit_forecast(
    scope_type: str = Query("all", description="范围类型 industry/concept/region/market/all"),
    scope_value: Optional[str] = Query(None, description="范围值（板块代码/名称或市场代码）"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    keyword: Optional[str] = Query(None, description="关键字（代码/名称）"),
    refresh: bool = Query(False),
):
    try:
        service = EastmoneyProfitForecastService()
        data = await service.fetch_profit_forecast(
            scope_type=scope_type,
            scope_value=scope_value,
            page=page,
            page_size=page_size,
            keyword=keyword,
            refresh=refresh,
        )
        return success(data)
    except Exception as exc:
        return error(f"获取盈利预测失败: {exc}")


@router.get("/profit-forecast/scopes")
async def get_profit_forecast_scopes(
    refresh: bool = Query(False),
):
    try:
        service = EastmoneyProfitForecastService()
        data = await service.get_scopes(refresh=refresh)
        return success(data)
    except Exception as exc:
        return error(f"获取盈利预测范围失败: {exc}")
