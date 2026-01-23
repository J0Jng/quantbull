"""
政策法规明细表模型
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, Text, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class PolicyRegulation(SQLModel, table=True):
    """政策法规明细表"""
    __tablename__ = "policy_regulation"  # type: ignore

    __table_args__ = (
        UniqueConstraint("policy_id", name="uq_policy_regulation_id"),
        Index("idx_policy_regulation_date", "publish_date"),
        Index("idx_policy_regulation_source", "source"),
        Index("idx_policy_regulation_created_at", "created_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, description="自增主键")
    policy_id: str = Field(max_length=64, unique=True, index=True, description="政策唯一标识")
    title: str = Field(max_length=300, description="标题")
    summary: str = Field(sa_column=Column(Text), description="摘要")
    source: str = Field(default="official", max_length=100, description="来源")
    publish_date: str = Field(max_length=20, index=True, description="发布日期（YYYY-MM-DD）")
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
                "policy_id": "b8f9c1a3d7e5f0",
                "title": "关于推动解决政府采购异常低价问题的通知",
                "summary": "为规范政府采购秩序，推动解决异常低价问题...",
                "source": "财政部",
                "publish_date": "2026-01-23",
                "url": "https://www.mof.gov.cn/..."
            }
        }