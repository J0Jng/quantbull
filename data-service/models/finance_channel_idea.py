"""
财经频道投资观点明细表模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, Text, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class FinanceChannelIdea(SQLModel, table=True):
    """投资观点明细表"""
    __tablename__ = "finance_channel_idea"  # type: ignore

    __table_args__ = (
        UniqueConstraint("idea_id", name="uq_finance_channel_idea_id"),
        Index("idx_finance_idea_publish_time", "publish_time"),
        Index("idx_finance_idea_source", "source"),
        Index("idx_finance_idea_created_at", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, description="自增主键")
    idea_id: str = Field(max_length=64, unique=True, index=True, description="观点唯一标识")
    title: str = Field(max_length=300, description="标题")
    content: str = Field(sa_column=Column(Text), description="摘要内容")
    source: str = Field(default="10jqka", max_length=100, description="来源")
    author: Optional[str] = Field(default=None, max_length=100, description="作者")
    publish_time: str = Field(max_length=20, index=True, description="发布时间（YYYY-MM-DD 或 YYYY-MM-DD HH:MM）")
    url: Optional[str] = Field(default=None, max_length=500, description="原文链接")

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, nullable=False),
        description="入库时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
        description="更新时间"
    )

    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "idea_id": "d2a7f6c4b1",
                "title": "公告解读：某公司发布年度业绩预告",
                "content": "公司公告显示业绩增长...",
                "source": "10jqka-独家公告解读",
                "author": "",
                "publish_time": "2026-01-24 06:28",
                "url": "https://yuanchuang.10jqka.com.cn/djggjd/123456.shtml"
            }
        }
