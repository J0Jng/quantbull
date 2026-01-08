"""基本面数据路由"""
from fastapi import APIRouter, Query
from typing import Optional

from schemas.fundamentals import (
    FundamentalsRequest,
    FundamentalsResponse,
    IndustryRankResponse,
    SentimentRequest,
    SentimentResponse,
    HotScoreRequest,
    HotScoreResponse,
)
from services.fundamentals_service import FundamentalsService

router = APIRouter()


@router.post("/batch")
async def get_fundamentals_batch(request: FundamentalsRequest):
    """
    批量获取股票基本面数据
    
    返回：行业、上市日期、是否ST、市值、估值（PE/PB）、财务指标等
    """
    service = FundamentalsService()
    items, success_codes, failed_codes = service.fetch_batch(
        codes=request.codes,
        trade_date=request.trade_date
    )
    
    return FundamentalsResponse(
        data=items,
        success_codes=success_codes,
        failed_codes=failed_codes,
    )


@router.get("/industry/rank")
async def get_industry_rank(
    month: Optional[str] = Query(None, description="月份 YYYY-MM，不传则使用最近月"),
    auto_calculate: bool = Query(False, description="如果数据库没有数据，是否自动计算（默认否，避免超时）")
):
    """
    获取行业景气度排名
    
    基于行业内股票的平均财务增长率（净利润yoy、营收yoy、ROE yoy）计算
    
    注意：如果数据库没有数据且 auto_calculate=False，会返回空列表。
    建议通过定时任务预热数据，而非通过接口触发实时计算（需 10-15 分钟）
    """
    from datetime import datetime
    
    service = FundamentalsService()
    actual_month = month or datetime.now().strftime("%Y-%m")
    
    # 优先从数据库读取
    items = service.load_industry_rank_from_db(actual_month)
    
    # 如果数据库没有且允许自动计算
    if not items and auto_calculate:
        items = service.calculate_industry_rank(month=month, force_recalculate=True)
    
    return IndustryRankResponse(
        month=actual_month,
        data=items,
    )


@router.post("/sentiment/score")
async def get_sentiment_scores(request: SentimentRequest):
    """
    获取舆情评分
    
    基于同花顺热度、龙虎榜、资金流向综合计算
    """
    service = FundamentalsService()
    items = service.get_sentiment_scores(
        codes=request.codes,
        start_date=request.start_date,
        end_date=request.end_date
    )
    
    return SentimentResponse(data=items)


@router.post("/hot/score")
async def get_hot_scores(request: HotScoreRequest):
    """
    获取热点/主线分数
    
    基于涨跌停统计、概念板块、龙虎榜综合计算
    """
    service = FundamentalsService()
    items = service.get_hot_scores(codes=request.codes)
    
    return HotScoreResponse(data=items)
