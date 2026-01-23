"""公募基金排行榜数据表模型"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime, Date


class PublicFundRankingItemModel(SQLModel, table=True):
    """公募基金排行榜数据表 - 存储明细数据用于数据库分页筛选"""

    __tablename__ = "public_fund_ranking_item"  # type: ignore

    __table_args__ = (
        UniqueConstraint("code", "as_of", "source", "fund_type_key", name="uq_public_fund_rank_item"),
        Index("idx_public_fund_rank_code", "code"),
        Index("idx_public_fund_rank_name", "name"),
        Index("idx_public_fund_rank_type_key", "fund_type_key"),
        Index("idx_public_fund_rank_as_of", "as_of"),
        Index("idx_public_fund_rank_fetched_at", "fetched_at"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    code: str = Field(max_length=20, description="基金代码")
    name: str = Field(max_length=200, description="基金名称")
    fund_type_key: str = Field(max_length=20, description="基金类型 key（stock/hybrid/bond/monetary/空）")
    type_label: str = Field(max_length=50, description="基金类型展示文本")

    nav: float = Field(description="单位净值")
    change: float = Field(description="日涨跌幅（百分比数值）")
    return1w: float = Field(description="近 1 周收益率（百分比数值）")
    return1m: float = Field(description="近 1 月收益率（百分比数值）")
    return3m: float = Field(description="近 3 月收益率（百分比数值）")
    return6m: float = Field(description="近 6 月收益率（百分比数值）")
    return1y: float = Field(description="近 1 年收益率（百分比数值）")
    return3y: float = Field(description="近 3 年收益率（百分比数值）")

    as_of: date = Field(sa_column=Column(Date), description="数据日期")
    source: str = Field(default="eastmoney", max_length=50, description="数据来源")

    fetched_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, nullable=False),
        description="抓取时间",
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
