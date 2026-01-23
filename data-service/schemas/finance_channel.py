"""
财经频道 API 数据模式定义
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ==================== 市场数据 ====================

class MarketDataItem(BaseModel):
    """市场数据条目"""
    code: str = Field(..., description="代码（如 000001.SH）")
    title: str = Field(..., description="名称（如 上证指数）")
    value: str = Field(..., description="当前值")
    change_pct: float = Field(..., description="涨跌幅（百分比）")
    updated_at: str = Field(..., description="更新时间")


class MarketDataResponse(BaseModel):
    """市场数据响应"""
    items: List[MarketDataItem] = Field(..., description="市场数据列表")
    cached: bool = Field(..., description="是否来自缓存")
    stale: bool = Field(..., description="缓存是否过期")
    source: str = Field(..., description="数据源")
    updated_at: str = Field(..., description="数据更新时间")


# ==================== 投资观点 ====================

class IdeasItem(BaseModel):
    """投资观点条目"""
    id: str = Field(..., description="观点唯一标识")
    title: str = Field(..., description="标题")
    author: Optional[str] = Field(None, description="作者")
    source: str = Field(..., description="来源")
    content: str = Field(..., description="内容摘要")
    date: str = Field(..., description="发布日期")
    url: Optional[str] = Field(None, description="原文链接")


class IdeasResponse(BaseModel):
    """投资观点响应"""
    items: List[IdeasItem] = Field(..., description="观点列表")
    cached: bool = Field(..., description="是否来自缓存")
    stale: bool = Field(..., description="缓存是否过期")
    source: str = Field(..., description="数据源")
    updated_at: str = Field(..., description="数据更新时间")


# ==================== 政策法规 ====================

class PolicyItem(BaseModel):
    """政策法规条目"""
    id: str = Field(..., description="政策唯一标识")
    title: str = Field(..., description="标题")
    summary: str = Field(..., description="摘要")
    source: str = Field(..., description="来源")
    date: str = Field(..., description="发布日期")
    url: Optional[str] = Field(None, description="原文链接")


class PolicyResponse(BaseModel):
    """政策法规响应"""
    items: List[PolicyItem] = Field(..., description="政策列表")
    cached: bool = Field(..., description="是否来自缓存")
    stale: bool = Field(..., description="缓存是否过期")
    source: str = Field(..., description="数据源")
    updated_at: str = Field(..., description="数据更新时间")


# ==================== 综合响应 ====================

class FinanceChannelOverview(BaseModel):
    """财经频道综合数据"""
    news: dict = Field(..., description="财经资讯（使用现有 NewsListResponse）")
    market: MarketDataResponse = Field(..., description="市场数据")
    ideas: IdeasResponse = Field(..., description="投资观点")
    policies: PolicyResponse = Field(..., description="政策法规")
