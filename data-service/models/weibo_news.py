"""
微博财经新闻数据模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, Text, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class WeiboNews(SQLModel, table=True):
    """微博财经新闻表 - 存储从微博抓取的财经新闻数据"""
    __tablename__ = "weibo_news"  # type: ignore
    
    __table_args__ = (
        UniqueConstraint("weibo_id", name="uq_weibo_news_id"),
        Index("idx_weibo_news_created_at", "created_at"),
        Index("idx_weibo_news_author", "author"),
        Index("idx_weibo_news_publish_time", "publish_timestamp"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True, description="自增主键")
    weibo_id: str = Field(max_length=50, unique=True, index=True, description="微博唯一标识")
    title: str = Field(max_length=200, description="新闻标题")
    summary: str = Field(sa_column=Column(Text), description="新闻摘要")
    content: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True), description="完整内容（可选）")
    source: str = Field(default="新浪微博", max_length=50, description="新闻来源")
    author: Optional[str] = Field(default=None, max_length=100, description="作者/账号名")
    url: Optional[str] = Field(default=None, max_length=500, description="原文链接")
    img_url: Optional[str] = Field(default=None, max_length=500, description="配图链接")
    
    publish_time: str = Field(max_length=50, description="发布时间（人类可读格式）")
    publish_timestamp: int = Field(index=True, description="发布时间戳（用于排序）")
    
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
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "weibo_id": "weibo_a1b2c3d4e5f6g7h8",
                "title": "央行降准释放流动性，金融市场迎来利好",
                "summary": "央行宣布下调金融机构存款准备金率0.5个百分点...",
                "source": "新浪微博",
                "author": "新浪财经",
                "url": "https://m.weibo.cn/status/5089123456789",
                "img_url": "https://wx1.sinaimg.cn/thumbnail/abc123.jpg",
                "publish_time": "2小时前",
                "publish_timestamp": 1737459600
            }
        }
