from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from services.fund_ranking_service import FundRankingService

router = APIRouter()


@router.get(
    "/public/ranking",
    summary="获取公募基金排行榜",
)
async def get_public_fund_ranking(
    fund_type: str = Query("", description="基金类型: stock/hybrid/bond/monetary/空为全部"),
    return_sign: str = Query("", description="收益率区间: positive/negative/空为全部"),
    sort_by: str = Query("default", description="排序字段: default/return1w/return1m/return3m/return6m/return1y/return3y"),
    order: str = Query("desc", description="排序方向: desc/asc"),
    keyword: str = Query("", description="基金代码/名称关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    refresh: bool = Query(False, description="是否跳过缓存并刷新"),
    db: AsyncSession = Depends(get_async_session),
):
    """公募基金排行榜

    数据源策略：优先尝试 Tushare；当 token 未配置或数据不足/报错时回退到东方财富。
    """
    service = FundRankingService(db_session=db)
    return await service.get_public_ranking(
        fund_type=fund_type,
        return_sign=return_sign,
        sort_by=sort_by,  # service 内部会兜底
        order=order,
        keyword=keyword,
        page=page,
        page_size=page_size,
        refresh=refresh,
    )


@router.get(
    "/private/ranking",
    summary="获取私募基金排行榜",
)
async def get_private_fund_ranking(
    strategy: str = Query("", description="策略类型: equity/futures/hedge/composite/空为全部"),
    risk_level: str = Query("", description="风险等级: low/medium/high/空为全部"),
    sort_by: str = Query("default", description="排序字段: default/return1y/sharpe/maxdrawdown"),
    order: str = Query("desc", description="排序方向: desc/asc"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    refresh: bool = Query(False, description="保留参数，当前不影响内置数据"),
    db: AsyncSession = Depends(get_async_session),
):
    """私募基金排行榜

    当前版本使用后端内置数据（可后续替换为 DB/外部数据源）。
    """
    service = FundRankingService(db_session=db)
    return await service.get_private_ranking(
        strategy=strategy,
        risk_level=risk_level,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
        refresh=refresh,
    )
