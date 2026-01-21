"""
财经频道聚合API

提供财经频道所需的所有数据接口：
- 财经资讯（复用现有微博/东方财富新闻）
- 市场数据（指数、汇率、黄金等）
- 财经日历（未来14天宏观事件）
- 投资观点（研报、分析师评论）
- 政策法规（监管政策、法规通知）
"""
from typing import Optional
from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from schemas.finance_channel import (
    MarketDataResponse,
    CalendarResponse,
    IdeasResponse,
    PolicyResponse,
    FinanceChannelOverview
)
from services.market_data_service import get_market_data_aggregator
from services.calendar_service import get_calendar_aggregator
from services.ideas_service import get_ideas_aggregator
from services.policy_service import get_policy_aggregator
from services.eastmoney_news_service import get_eastmoney_news_aggregator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/finance-channel", tags=["finance-channel"])


# ==================== 市场数据 ====================

@router.get(
    "/market",
    response_model=MarketDataResponse,
    summary="获取市场数据",
    description="""
    获取市场主要指数的实时行情数据。
    
    **数据来源**：东方财富网实时行情接口
    **更新频率**：5分钟缓存
    **包含指数**：上证指数、深证成指、创业板指、沪深300、上证50、中小板指
    
    **降级策略**：
    - 优先返回实时数据
    - 实时数据获取失败时返回缓存数据（标记 cached=true, stale=true）
    - 无缓存时返回空列表
    """
)
async def get_market_data(
    db_session: AsyncSession = Depends(get_async_session)
):
    """获取市场数据"""
    aggregator = get_market_data_aggregator(db_session)
    return await aggregator.aggregate_market_data()


# ==================== 财经日历 ====================

@router.get(
    "/calendar",
    response_model=CalendarResponse,
    summary="获取财经日历",
    description="""
    获取未来宏观经济事件日历。
    
    **数据来源**：模拟数据（生产环境需对接金十数据或其他API）
    **更新频率**：6小时缓存
    **时间范围**：未来14天
    **重要性等级**：1-5（1=低, 3=中, 4=高, 5=极高）
    
    **降级策略**：
    - 优先返回最新数据
    - 数据获取失败时返回缓存数据
    - 无缓存时返回空列表
    """
)
async def get_calendar(
    start_date: Optional[str] = Query(None, description="开始日期（YYYY-MM-DD）"),
    end_date: Optional[str] = Query(None, description="结束日期（YYYY-MM-DD）"),
    db_session: AsyncSession = Depends(get_async_session)
):
    """获取财经日历"""
    aggregator = get_calendar_aggregator(db_session)
    return await aggregator.aggregate_calendar(start_date=start_date, end_date=end_date)


# ==================== 投资观点 ====================

@router.get(
    "/ideas",
    response_model=IdeasResponse,
    summary="获取投资观点",
    description="""
    获取投资观点、研报摘要、分析师评论。
    
    **数据来源**：模拟数据（生产环境需爬取真实网站）
    **更新频率**：30分钟缓存
    **支持功能**：关键词搜索、分页
    
    **降级策略**：
    - 优先返回最新数据
    - 数据获取失败时返回缓存数据
    - 无缓存时返回空列表
    """
)
async def get_ideas(
    limit: int = Query(10, ge=1, le=50, description="返回条数"),
    keyword: Optional[str] = Query(None, description="关键词过滤"),
    page: int = Query(1, ge=1, description="页码（暂未实现分页）"),
    db_session: AsyncSession = Depends(get_async_session)
):
    """获取投资观点"""
    aggregator = get_ideas_aggregator(db_session)
    return await aggregator.aggregate_ideas(limit=limit, keyword=keyword)


# ==================== 政策法规 ====================

@router.get(
    "/policies",
    response_model=PolicyResponse,
    summary="获取政策法规",
    description="""
    获取金融监管政策、法规通知。
    
    **数据来源**：模拟数据（生产环境需爬取官方网站）
    **更新频率**：1小时缓存
    **支持功能**：关键词搜索、分页
    
    **降级策略**：
    - 优先返回最新数据
    - 数据获取失败时返回缓存数据
    - 无缓存时返回空列表
    """
)
async def get_policies(
    limit: int = Query(10, ge=1, le=50, description="返回条数"),
    keyword: Optional[str] = Query(None, description="关键词过滤"),
    page: int = Query(1, ge=1, description="页码（暂未实现分页）"),
    db_session: AsyncSession = Depends(get_async_session)
):
    """获取政策法规"""
    aggregator = get_policy_aggregator(db_session)
    return await aggregator.aggregate_policies(limit=limit, keyword=keyword)


# ==================== 综合接口（一次性获取所有数据） ====================

@router.get(
    "/overview",
    response_model=FinanceChannelOverview,
    summary="获取财经频道综合数据",
    description="""
    一次性获取财经频道所有模块的数据。
    
    **包含模块**：
    - news: 财经资讯（东方财富网新闻）
    - market: 市场数据（主要指数）
    - calendar: 财经日历（未来14天）
    - ideas: 投资观点（研报评论）
    - policies: 政策法规（监管政策）
    
    **注意**：
    - 此接口会并发请求所有模块，可能耗时较长
    - 建议前端优先使用分模块接口，按需加载
    """
)
async def get_overview(
    keyword: Optional[str] = Query(None, description="新闻/观点/政策的关键词过滤"),
    limit: int = Query(10, ge=1, le=50, description="各模块返回条数"),
    db_session: AsyncSession = Depends(get_async_session)
):
    """获取财经频道综合数据"""
    # 并发获取所有数据
    import asyncio
    
    # 创建各模块的聚合器
    news_aggregator = get_eastmoney_news_aggregator()
    market_aggregator = get_market_data_aggregator(db_session)
    calendar_aggregator = get_calendar_aggregator(db_session)
    ideas_aggregator = get_ideas_aggregator(db_session)
    policy_aggregator = get_policy_aggregator(db_session)
    
    # 并发请求
    results = await asyncio.gather(
        news_aggregator.aggregate_news(limit=limit, keyword=keyword),
        market_aggregator.aggregate_market_data(),
        calendar_aggregator.aggregate_calendar(),
        ideas_aggregator.aggregate_ideas(limit=limit, keyword=keyword),
        policy_aggregator.aggregate_policies(limit=limit, keyword=keyword),
        return_exceptions=True
    )
    
    # 处理结果
    news_data = results[0] if not isinstance(results[0], Exception) else {"items": [], "cached": False, "stale": True, "timestamp": 0}
    market_data = results[1] if not isinstance(results[1], Exception) else {"items": [], "cached": False, "stale": True, "source": "none", "updated_at": ""}
    calendar_data = results[2] if not isinstance(results[2], Exception) else {"items": [], "cached": False, "stale": True, "source": "none", "updated_at": ""}
    ideas_data = results[3] if not isinstance(results[3], Exception) else {"items": [], "cached": False, "stale": True, "source": "none", "updated_at": ""}
    policies_data = results[4] if not isinstance(results[4], Exception) else {"items": [], "cached": False, "stale": True, "source": "none", "updated_at": ""}
    
    return {
        "news": news_data,
        "market": market_data,
        "calendar": calendar_data,
        "ideas": ideas_data,
        "policies": policies_data
    }
