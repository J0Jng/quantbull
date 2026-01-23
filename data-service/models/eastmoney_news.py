"""
东方财富网财经新闻数据模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, Text, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class EastmoneyNews(SQLModel, table=True):
    """东方财富网财经新闻表 - 存储从东方财富网抓取的财经新闻数据"""
    __tablename__ = "eastmoney_news"  # type: ignore
    
    __table_args__ = (
        UniqueConstraint("news_id", name="uq_eastmoney_news_id"),
        Index("idx_eastmoney_news_created_at", "created_at"),
        Index("idx_eastmoney_news_author", "author"),
        Index("idx_eastmoney_news_publish_time", "publish_timestamp"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True, description="自增主键")
    news_id: str = Field(max_length=64, unique=True, index=True, description="新闻唯一标识（eastmoney_前缀 + URL哈希或文章ID）")
    title: str = Field(max_length=200, description="新闻标题")
    summary: str = Field(sa_column=Column(Text), description="新闻摘要")
    source: str = Field(default="东方财富网", max_length=50, description="新闻来源")
    author: Optional[str] = Field(default=None, max_length=100, description="作者/栏目名")
    url: Optional[str] = Field(default=None, max_length=500, description="原文链接")
    img_url: Optional[str] = Field(default=None, max_length=500, description="配图链接（缩略图）")
    
    publish_time: str = Field(max_length=50, description="发布时间（人类可读格式，如 2026-01-21 10:35 或 2小时前）")
    publish_timestamp: int = Field(index=True, description="发布时间戳（Unix秒，用于排序和时间范围查询）")
    
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
                "news_id": "eastmoney_202601213625140518",
                "title": "央行宣布下调金融机构存款准备金率",
                "summary": "中国人民银行决定于2026年1月25日下调金融机构存款准备金率0.5个百分点，预计释放长期资金约1万亿元...",
                "source": "东方财富网",
                "author": "要闻",
                "url": "https://finance.eastmoney.com/a/202601213625140518.html",
                "img_url": "https://np-newspic.dfcfw.com/download/202601213625140518_w210h154.jpg",
                "publish_time": "2026-01-21 10:35",
                "publish_timestamp": 1737459600
            }
        }
