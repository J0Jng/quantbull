"""
财经新闻接口

支持两种数据源：
1. 东方财富网新闻（推荐，/eastmoney/*）
2. 微博财经新闻（已弃用，/weibo/*，内部转发到东方财富实现）
3. 财经头条（/headlines/*，面向页面展示）
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from core.database import get_async_session
from services.eastmoney_news_service import get_eastmoney_news_aggregator, EastmoneyNewsAggregator
from services.headlines_ai_service import generate_headlines_from_news
from models.headline_news import HeadlineNews
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/news", tags=["news"])


class NewsItem(BaseModel):
    """新闻条目"""
    id: str = Field(..., description="新闻唯一标识")
    title: str = Field(..., description="新闻标题")
    summary: str = Field(..., description="新闻摘要")
    source: str = Field(..., description="新闻来源")
    time: str = Field(..., description="发布时间")
    url: str = Field(..., description="原文链接")
    img: Optional[str] = Field(None, description="配图链接")
    author: Optional[str] = Field(None, description="作者/账号名")


class NewsListResponse(BaseModel):
    """新闻列表响应"""
    items: List[NewsItem] = Field(..., description="新闻列表")
    cached: bool = Field(..., description="是否来自缓存")
    stale: bool = Field(..., description="缓存是否过期（降级场景）")
    timestamp: int = Field(..., description="数据时间戳")


# ==================== 东方财富网新闻接口（推荐） ====================

@router.get(
    "/eastmoney/latest",
    response_model=NewsListResponse,
    summary="获取东方财富网最新财经新闻",
    description="""
    从东方财富网抓取最新财经新闻，支持快讯和文章两种数据源。
    
    **数据来源**：
    - 东方财富网 7×24 小时快讯（优先）
    - 东方财富网财经频道文章列表（兜底）
    
    **合规说明**：
    - 仅采集公开可访问内容的"摘要级信息"
    - 不模拟登录、不使用 Cookie
    - 使用内存缓存，TTL 默认 5 分钟
    - 抓取失败时返回缓存旧数据或空列表
    
    **参数说明**：
    - `limit`: 返回的最大条数，默认 20
    - `keyword`: 关键词过滤，在标题/摘要中搜索（大小写不敏感）
    """
)
async def get_eastmoney_latest_news(
    limit: int = Query(20, ge=1, le=100, description="返回的最大条数"),
    keyword: Optional[str] = Query(None, description="关键词过滤")
):
    """
    获取东方财富网最新财经新闻
    
    Args:
        limit: 返回的最大条数
        keyword: 关键词过滤
        
    Returns:
        NewsListResponse
    """
    try:
        aggregator = get_eastmoney_news_aggregator()
        result = await aggregator.aggregate_news(limit=limit, keyword=keyword)
        return result
    except Exception as e:
        logger.error(f"获取东方财富网新闻失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取东方财富网新闻失败：{str(e)}")


@router.get(
    "/eastmoney/history",
    response_model=NewsListResponse,
    summary="查询历史东方财富网新闻（从数据库）",
    description="""
    从数据库查询历史东方财富网新闻数据，支持时间范围和关键词过滤。
    
    **数据来源**：
    - PostgreSQL 数据库中存储的历史东方财富网新闻
    
    **使用场景**：
    - 查看历史新闻
    - 分析新闻趋势
    - 数据统计分析
    
    **参数说明**：
    - `limit`: 返回的最大条数，默认 20
    - `keyword`: 关键词过滤，在标题/摘要中搜索（大小写不敏感）
    - `hours`: 查询最近多少小时的数据，默认 24 小时
    """
)
async def get_eastmoney_history_news(
    limit: int = Query(20, ge=1, le=100, description="返回的最大条数"),
    keyword: Optional[str] = Query(None, description="关键词过滤"),
    hours: int = Query(24, ge=1, le=168, description="查询最近多少小时的数据（1-168小时）"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    查询历史东方财富网新闻（从数据库）
    
    Args:
        limit: 返回的最大条数
        keyword: 关键词过滤
        hours: 查询最近多少小时的数据
        db: 数据库会话
        
    Returns:
        NewsListResponse
    """
    try:
        aggregator = EastmoneyNewsAggregator(db_session=db)
        items = await aggregator.get_news_from_database(
            limit=limit,
            keyword=keyword,
            hours=hours
        )
        
        return {
            "items": items,
            "cached": False,
            "stale": False,
            "timestamp": int(__import__("time").time())
        }
    except Exception as e:
        logger.error(f"查询历史东方财富网新闻失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询历史新闻失败：{str(e)}")


# ==================== 微博新闻接口（已弃用，兼容保留） ====================


@router.get(
    "/weibo/media",
    response_model=NewsListResponse,
    summary="【已弃用】获取微博财经媒体聚合新闻",
    deprecated=True,
    description="""
    ⚠️ **此接口已弃用，请使用 `/api/news/eastmoney/latest` 替代**
    
    为兼容旧版前端，此接口内部已转发到东方财富网数据源。
    返回数据格式保持不变，但数据来源已改为东方财富网。
    
    **参数说明**：
    - `limit`: 返回的最大条数，默认 20
    - `keyword`: 关键词过滤，在标题/摘要中搜索（可选）
    """
)
async def get_weibo_media_news(
    limit: int = Query(20, ge=1, le=100, description="返回的最大条数"),
    keyword: Optional[str] = Query(None, description="关键词过滤")
):
    """
    【已弃用】获取微博财经媒体聚合新闻
    
    内部转发到东方财富网实现，保持接口兼容。
    
    Args:
        limit: 返回的最大条数
        keyword: 关键词过滤
        
    Returns:
        NewsListResponse
    """
    try:
        # 转发到东方财富网实现
        aggregator = get_eastmoney_news_aggregator()
        result = await aggregator.aggregate_news(limit=limit, keyword=keyword)
        return result
    except Exception as e:
        logger.error(f"获取新闻失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取新闻失败：{str(e)}")


@router.get(
    "/weibo/history",
    response_model=NewsListResponse,
    summary="【已弃用】查询历史微博新闻（从数据库）",
    deprecated=True,
    description="""
    ⚠️ **此接口已弃用，请使用 `/api/news/eastmoney/history` 替代**
    
    为兼容旧版前端，此接口内部已转发到东方财富网数据库查询。
    返回数据格式保持不变，但数据来源已改为东方财富网。
    
    **参数说明**：
    - `limit`: 返回的最大条数，默认 20
    - `keyword`: 关键词过滤，在标题/摘要中搜索（可选）
    - `hours`: 查询最近多少小时的数据，默认 24 小时
    """
)
async def get_weibo_history_news(
    limit: int = Query(20, ge=1, le=100, description="返回的最大条数"),
    keyword: Optional[str] = Query(None, description="关键词过滤"),
    hours: int = Query(24, ge=1, le=168, description="查询最近多少小时的数据（1-168小时）"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    【已弃用】查询历史微博新闻（从数据库）
    
    内部转发到东方财富网数据库查询，保持接口兼容。
    
    Args:
        limit: 返回的最大条数
        keyword: 关键词过滤
        hours: 查询最近多少小时的数据
        db: 数据库会话
        
    Returns:
        NewsListResponse
    """
    try:
        # 转发到东方财富网数据库查询
        aggregator = EastmoneyNewsAggregator(db_session=db)
        items = await aggregator.get_news_from_database(
            limit=limit,
            keyword=keyword,
            hours=hours
        )
        
        return {
            "items": items,
            "cached": False,
            "stale": False,
            "timestamp": int(__import__("time").time())
        }
    except Exception as e:
        logger.error(f"查询历史新闻失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询历史新闻失败：{str(e)}")


# ==================== 财经头条接口（面向页面展示） ====================


class HeadlineItem(BaseModel):
    """财经头条条目"""
    id: int = Field(..., description="新闻唯一标识")
    title: str = Field(..., description="新闻标题")
    date: str = Field(..., description="发布时间（格式：YYYY-MM-DD HH:mm）")
    summary: str = Field(..., description="新闻摘要")
    tags: List[str] = Field(..., description="新闻标签")


class HeadlineListResponse(BaseModel):
    """财经头条列表响应"""
    items: List[HeadlineItem] = Field(..., description="新闻列表")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    total: int = Field(..., description="总数")


class HotHeadlineItem(BaseModel):
    """热点聚焦条目"""
    id: int = Field(..., description="新闻唯一标识")
    title: str = Field(..., description="新闻标题")


class HotHeadlineListResponse(BaseModel):
    """热点聚焦列表响应"""
    items: List[HotHeadlineItem] = Field(..., description="热点列表")


class HeadlineDetailResponse(BaseModel):
    """财经头条详情响应"""
    id: int = Field(..., description="新闻唯一标识")
    title: str = Field(..., description="新闻标题")
    date: str = Field(..., description="发布时间（格式：YYYY-MM-DD HH:mm）")
    summary: str = Field(..., description="新闻摘要")
    tags: List[str] = Field(..., description="新闻标签")
    content: Optional[str] = Field(None, description="新闻正文")


class CreateHeadlineRequest(BaseModel):
    """创建财经头条请求"""
    title: str = Field(..., min_length=1, max_length=200, description="新闻标题")
    summary: str = Field(..., min_length=1, max_length=500, description="新闻摘要")
    tags: List[str] = Field(default_factory=list, description="新闻标签")
    content: Optional[str] = Field(None, description="新闻正文")
    source: str = Field(default="手动添加", description="新闻来源")
    url: str = Field(default="", description="原文链接")
    is_hot: bool = Field(default=False, description="是否为热点新闻")


class UpdateHeadlineRequest(BaseModel):
    """更新财经头条请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="新闻标题")
    summary: Optional[str] = Field(None, min_length=1, max_length=500, description="新闻摘要")
    tags: Optional[List[str]] = Field(None, description="新闻标签")
    content: Optional[str] = Field(None, description="新闻正文")
    is_hot: Optional[bool] = Field(None, description="是否为热点新闻")


@router.get(
    "/headlines",
    response_model=HeadlineListResponse,
    summary="获取财经头条列表（分页）",
    description="""
    获取面向页面展示的财经头条列表，支持分页和关键词过滤。
    
    **数据来源**：
    - PostgreSQL 数据库中存储的财经头条数据
    
    **参数说明**：
    - `page`: 页码，从 1 开始，默认 1
    - `page_size`: 每页条数，1-50，默认 10
    - `keyword`: 关键词过滤，在标题/摘要中搜索（大小写不敏感）
    """
)
async def get_headlines(
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(10, ge=1, le=50, description="每页条数"),
    keyword: Optional[str] = Query(None, description="关键词过滤"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取财经头条列表（分页）
    
    Args:
        page: 页码，从 1 开始
        page_size: 每页条数
        keyword: 关键词过滤
        db: 数据库会话
        
    Returns:
        HeadlineListResponse
    """
    try:
        # 构建基础查询（非热点新闻）
        query = select(HeadlineNews).where(HeadlineNews.is_hot == False)  # type: ignore
        count_query = select(func.count()).select_from(HeadlineNews).where(HeadlineNews.is_hot == False)  # type: ignore
        
        # 关键词过滤
        if keyword:
            keyword_filter = f"%{keyword}%"
            filter_condition = or_(
                HeadlineNews.title.like(keyword_filter),  # type: ignore
                HeadlineNews.summary.like(keyword_filter)  # type: ignore
            )
            query = query.where(filter_condition)
            count_query = count_query.where(filter_condition)
        
        # 排序和分页
        query = query.order_by(HeadlineNews.publish_time.desc())  # type: ignore
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        # 执行查询
        result = await db.execute(query)
        headlines = result.scalars().all()
        
        # 统计总数
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        
        # 转换为响应格式
        items = [
            HeadlineItem(
                id=h.id or 0,
                title=h.title,
                date=h.date_text,
                summary=h.summary,
                tags=h.tags
            )
            for h in headlines
        ]
        
        return HeadlineListResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total
        )
    except Exception as e:
        logger.error(f"获取财经头条列表失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取财经头条列表失败：{str(e)}")


@router.get(
    "/headlines/hot",
    response_model=HotHeadlineListResponse,
    summary="获取热点聚焦列表",
    description="""
    获取热点聚焦新闻列表，按 hot_rank 排序。
    
    **数据来源**：
    - PostgreSQL 数据库中标记为热点的财经头条数据
    
    **参数说明**：
    - `limit`: 返回的最大条数，1-20，默认 8
    """
)
async def get_hot_headlines(
    limit: int = Query(8, ge=1, le=20, description="返回的最大条数"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取热点聚焦列表
    
    Args:
        limit: 返回的最大条数
        db: 数据库会话
        
    Returns:
        HotHeadlineListResponse
    """
    try:
        # 查询热点新闻，按 hot_rank 排序
        query = select(HeadlineNews).where(HeadlineNews.is_hot == True)  # type: ignore
        query = query.order_by(HeadlineNews.hot_rank.asc())  # type: ignore
        query = query.limit(limit)
        
        result = await db.execute(query)
        hot_headlines = result.scalars().all()
        
        # 转换为响应格式
        items = [
            HotHeadlineItem(
                id=h.id or 0,
                title=h.title
            )
            for h in hot_headlines
        ]
        
        return HotHeadlineListResponse(items=items)
    except Exception as e:
        logger.error(f"获取热点聚焦列表失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取热点聚焦列表失败：{str(e)}")


@router.get(
    "/headlines/{id}",
    response_model=HeadlineDetailResponse,
    summary="获取财经头条详情",
    description="""
    根据 ID 获取财经头条详情。
    
    **数据来源**：
    - PostgreSQL 数据库中存储的财经头条数据
    
    **参数说明**：
    - `id`: 新闻 ID
    """
)
async def get_headline_detail(
    id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取财经头条详情
    
    Args:
        id: 新闻 ID
        db: 数据库会话
        
    Returns:
        HeadlineDetailResponse
    """
    try:
        # 查询详情
        query = select(HeadlineNews).where(HeadlineNews.id == id)  # type: ignore
        result = await db.execute(query)
        headline = result.scalar_one_or_none()
        
        if not headline:
            raise HTTPException(status_code=404, detail=f"未找到 ID 为 {id} 的财经头条")
        
        # 转换为响应格式
        return HeadlineDetailResponse(
            id=headline.id or 0,
            title=headline.title,
            date=headline.date_text,
            summary=headline.summary,
            tags=headline.tags,
            content=headline.content
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取财经头条详情失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取财经头条详情失败：{str(e)}")


# ==================== 财经头条管理接口（创建、更新、删除） ====================


@router.post(
    "/headlines",
    response_model=HeadlineDetailResponse,
    summary="创建财经头条",
    description="""
    创建新的财经头条新闻。
    
    **权限要求**：需要管理员权限
    
    **参数说明**：
    - `title`: 新闻标题，必填，1-200字符
    - `summary`: 新闻摘要，必填，1-500字符
    - `tags`: 新闻标签列表，可选
    - `content`: 新闻正文，可选
    - `source`: 新闻来源，默认"手动添加"
    - `url`: 原文链接，可选
    - `is_hot`: 是否为热点新闻，默认 False
    """
)
async def create_headline(
    request: CreateHeadlineRequest,
    db: AsyncSession = Depends(get_async_session),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
):
    """
    创建财经头条
    
    Args:
        request: 创建请求
        db: 数据库会话
        x_user_role: 用户角色（从网关传递）
        
    Returns:
        HeadlineDetailResponse
    """
    # 权限检查
    _check_admin_role(x_user_role)
    
    try:
        # 创建新头条
        from datetime import datetime
        now = datetime.now()
        
        headline = HeadlineNews(
            title=request.title,
            date=now.strftime("%Y-%m-%d %H:%M"),
            summary=request.summary,
            tags=request.tags,
            content=request.content,
            source=request.source,
            url=request.url,
            is_hot=request.is_hot,
            publish_time=now
        )
        
        db.add(headline)
        await db.commit()
        await db.refresh(headline)
        
        logger.info(f"创建财经头条成功：ID={headline.id}, 标题={headline.title}")
        
        return HeadlineDetailResponse(
            id=headline.id or 0,
            title=headline.title,
            date=headline.date_text,
            summary=headline.summary,
            tags=headline.tags,
            content=headline.content
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"创建财经头条失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建财经头条失败：{str(e)}")


@router.put(
    "/headlines/{headline_id}",
    response_model=HeadlineDetailResponse,
    summary="更新财经头条",
    description="""
    更新指定的财经头条新闻。
    
    **权限要求**：需要管理员权限
    
    **参数说明**：
    - `headline_id`: 新闻ID
    - 请求体中的所有字段都是可选的，只更新提供的字段
    """
)
async def update_headline(
    headline_id: int,
    request: UpdateHeadlineRequest,
    db: AsyncSession = Depends(get_async_session),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
):
    """
    更新财经头条
    
    Args:
        headline_id: 新闻ID
        request: 更新请求
        db: 数据库会话
        x_user_role: 用户角色（从网关传递）
        
    Returns:
        HeadlineDetailResponse
    """
    # 权限检查
    _check_admin_role(x_user_role)
    
    try:
        # 查询头条
        result = await db.execute(
            select(HeadlineNews).where(HeadlineNews.id == headline_id)
        )
        headline = result.scalar_one_or_none()
        
        if not headline:
            raise HTTPException(status_code=404, detail=f"新闻不存在：ID={headline_id}")
        
        # 更新字段
        if request.title is not None:
            headline.title = request.title
        if request.summary is not None:
            headline.summary = request.summary
        if request.tags is not None:
            headline.tags = request.tags
        if request.content is not None:
            headline.content = request.content
        if request.is_hot is not None:
            headline.is_hot = request.is_hot
        
        await db.commit()
        await db.refresh(headline)
        
        logger.info(f"更新财经头条成功：ID={headline.id}, 标题={headline.title}")
        
        return HeadlineDetailResponse(
            id=headline.id or 0,
            title=headline.title,
            date=headline.date_text,
            summary=headline.summary,
            tags=headline.tags,
            content=headline.content
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"更新财经头条失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新财经头条失败：{str(e)}")


@router.delete(
    "/headlines/{headline_id}",
    summary="删除财经头条",
    description="""
    删除指定的财经头条新闻。
    
    **权限要求**：需要管理员权限
    
    **参数说明**：
    - `headline_id`: 新闻ID
    """
)
async def delete_headline(
    headline_id: int,
    db: AsyncSession = Depends(get_async_session),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
):
    """
    删除财经头条
    
    Args:
        headline_id: 新闻ID
        db: 数据库会话
        x_user_role: 用户角色（从网关传递）
        
    Returns:
        删除成功的消息
    """
    # 权限检查
    _check_admin_role(x_user_role)
    
    try:
        # 查询头条
        result = await db.execute(
            select(HeadlineNews).where(HeadlineNews.id == headline_id)
        )
        headline = result.scalar_one_or_none()
        
        if not headline:
            raise HTTPException(status_code=404, detail=f"新闻不存在：ID={headline_id}")
        
        # 删除
        await db.delete(headline)
        await db.commit()
        
        logger.info(f"删除财经头条成功：ID={headline_id}")
        
        return {"message": f"删除成功：ID={headline_id}"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"删除财经头条失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除财经头条失败：{str(e)}")


# ==================== AI 生成财经头条 ====================


class GenerateHeadlinesRequest(BaseModel):
    """AI 生成头条请求"""
    limit: int = Field(10, ge=1, le=20, description="生成数量，1-20")
    hours: int = Field(24, ge=1, le=168, description="源新闻时间范围（小时），1-168")
    force: bool = Field(False, description="是否强制重新生成（暂未使用）")


class GenerateHeadlinesResponse(BaseModel):
    """AI 生成头条响应"""
    created_count: int = Field(..., description="成功创建的数量")
    items: List[HeadlineDetailResponse] = Field(..., description="创建的头条列表")
    source_news_count: int = Field(..., description="源新闻数量")


def _check_admin_role(x_user_role: Optional[str]):
    """检查管理员权限"""
    if not x_user_role or x_user_role != "admin":
        raise HTTPException(
            status_code=403,
            detail="权限不足：该操作仅限管理员"
        )


@router.post(
    "/headlines/generate_daily",
    response_model=GenerateHeadlinesResponse,
    summary="AI 生成今日财经头条（管理员）",
    description="""
    基于数据库中最新财经新闻，使用 AI 生成精炼的财经头条。
    
    **权限要求**：仅管理员可用
    
    **工作流程**：
    1. 从数据库读取最近 N 小时内最新 M 条新闻
    2. 调用 AI 服务生成结构化头条
    3. 验证和清洗生成内容
    4. 批量写入头条表
    
    **参数说明**：
    - `limit`: 生成数量，默认 10，范围 1-20
    - `hours`: 源新闻时间范围（小时），默认 24，范围 1-168
    - `force`: 是否强制重新生成（预留，当前未使用）
    
    **注意事项**：
    - 若源新闻数量不足，将返回 400 错误
    - AI 生成可能耗时 30-60 秒，请耐心等待
    - 生成失败会自动回滚，不会写入半成品数据
    """
)
async def generate_daily_headlines(
    request: GenerateHeadlinesRequest,
    db: AsyncSession = Depends(get_async_session),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role")
):
    """
    AI 生成今日财经头条
    
    Args:
        request: 生成请求
        db: 数据库会话
        x_user_role: 用户角色（从网关传递）
        
    Returns:
        GenerateHeadlinesResponse
    """
    # 权限检查
    _check_admin_role(x_user_role)
    
    try:
        # 1. 从数据库获取源新闻
        logger.info(f"开始生成头条：limit={request.limit}, hours={request.hours}")
        
        aggregator = EastmoneyNewsAggregator(db_session=db)
        source_news = await aggregator.get_news_from_database(
            limit=request.limit,
            hours=request.hours
        )
        
        if len(source_news) < request.limit:
            raise HTTPException(
                status_code=400,
                detail=f"源新闻数量不足：需要 {request.limit} 条，实际仅 {len(source_news)} 条"
            )
        
        logger.info(f"获取到 {len(source_news)} 条源新闻")
        
        # 2. 调用 AI 生成头条
        logger.info("调用 AI 生成头条...")
        generated = await generate_headlines_from_news(source_news, limit=request.limit)
        logger.info(f"AI 生成完成，共 {len(generated)} 条")
        
        # 3. 批量写入数据库
        from datetime import datetime
        now = datetime.now()
        created_items = []
        
        for item in generated:
            headline = HeadlineNews(
                title=item["title"],
                date=now.strftime("%Y-%m-%d %H:%M"),
                summary=item["summary"],
                tags=item["tags"],
                content=item.get("content"),
                source="AI生成",
                url="",
                is_hot=False,
                publish_time=now
            )
            db.add(headline)
            created_items.append(headline)
        
        await db.commit()
        
        # 刷新获取生成的 ID
        for headline in created_items:
            await db.refresh(headline)
        
        logger.info(f"成功创建 {len(created_items)} 条头条")
        
        # 4. 构建响应
        items = [
            HeadlineDetailResponse(
                id=h.id or 0,
                title=h.title,
                date=h.date_text,
                summary=h.summary,
                tags=h.tags,
                content=h.content
            )
            for h in created_items
        ]
        
        return GenerateHeadlinesResponse(
            created_count=len(items),
            items=items,
            source_news_count=len(source_news)
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        # AI 生成或验证失败
        await db.rollback()
        logger.error(f"生成头条失败：{e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error(f"生成头条失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成头条失败：{str(e)}")
