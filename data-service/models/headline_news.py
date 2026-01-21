"""
财经头条新闻数据模型
专门服务于前端 NewsListPage.vue 页面的数据接口
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Index, Text, JSON
from sqlmodel import SQLModel, Field, Column, DateTime


class HeadlineNews(SQLModel, table=True):
    """财经头条新闻表 - 存储面向页面展示的财经头条数据"""
    __tablename__ = "headline_news"  # type: ignore
    
    __table_args__ = (
        Index("idx_headline_news_publish_time", "publish_time"),
        Index("idx_headline_news_is_hot", "is_hot"),
        Index("idx_headline_news_hot_rank", "hot_rank"),
        Index("idx_headline_news_created_at", "created_at"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True, description="自增主键")
    title: str = Field(max_length=300, description="新闻标题")
    summary: str = Field(sa_column=Column(Text), description="新闻摘要")
    content: Optional[str] = Field(default=None, sa_column=Column(Text), description="新闻正文（详情页使用）")
    
    # 时间字段：存储原始 datetime 用于排序，存储格式化字符串用于前端显示
    publish_time: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        description="发布时间（用于排序）"
    )
    date_text: str = Field(max_length=50, description="发布时间文本（格式：YYYY-MM-DD HH:mm）")
    
    # 标签：JSON 数组存储
    tags: List[str] = Field(default=[], sa_column=Column(JSON), description="新闻标签列表")
    
    # 热点标记
    is_hot: bool = Field(default=False, index=True, description="是否为热点聚焦")
    hot_rank: Optional[int] = Field(default=None, description="热点排序（1-8，数字越小越靠前）")
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, nullable=False),
        description="数据入库时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
        description="数据更新时间"
    )
