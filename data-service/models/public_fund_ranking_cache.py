"""公募基金排行榜缓存表模型"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index
from sqlmodel import SQLModel, Field, Column, DateTime, JSON


class PublicFundRankingCache(SQLModel, table=True):
    """公募基金排行榜缓存表 - 按查询参数缓存排行结果"""

    __tablename__ = "public_fund_ranking_cache"  # type: ignore

    __table_args__ = (
        Index("idx_public_fund_cache_key", "cache_key"),
        Index("idx_public_fund_cache_expires_at", "expires_at"),
        Index("idx_public_fund_cache_fetched_at", "fetched_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, description="自增主键")

    cache_key: str = Field(max_length=300, unique=True, index=True, description="缓存唯一键")
    payload_json: dict = Field(sa_column=Column(JSON), description="缓存的 JSON 数据")
    source: str = Field(default="unknown", max_length=100, description="数据源标识")

    fetched_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, nullable=False),
        description="数据抓取时间",
    )
    expires_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        description="缓存过期时间",
    )

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, nullable=False),
        description="记录创建时间",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
        description="记录更新时间",
    )
