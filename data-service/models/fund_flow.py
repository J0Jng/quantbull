"""资金流向数据模型"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class MarketFundFlow(SQLModel, table=True):
    """大盘资金流向表"""

    __tablename__ = "market_fund_flow"  # type: ignore

    __table_args__ = (
        UniqueConstraint("market", "as_of", "bucket", name="uq_market_fund_flow_market_asof_bucket"),
        Index("idx_market_fund_flow_market_as_of", "market", "as_of"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    market: str = Field(max_length=10, description="市场标识 hs/sh/sz")
    as_of: datetime = Field(sa_column=Column(DateTime), description="数据时间")
    bucket: str = Field(max_length=20, description="资金档位 super/large/medium/small")

    inflow: float = Field(default=0.0, description="流入金额（元）")
    outflow: float = Field(default=0.0, description="流出金额（元）")
    net: float = Field(default=0.0, description="净流入金额（元）")

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now),
        description="创建时间",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now),
        description="更新时间",
    )


class SectorFundFlow(SQLModel, table=True):
    """板块资金流向表"""

    __tablename__ = "sector_fund_flow"  # type: ignore

    __table_args__ = (
        UniqueConstraint("sector_type", "as_of", "rank", name="uq_sector_fund_flow_type_asof_rank"),
        Index("idx_sector_fund_flow_type_as_of_rank", "sector_type", "as_of", "rank"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    sector_type: str = Field(max_length=20, description="板块类型 industry/concept/region")
    as_of: datetime = Field(sa_column=Column(DateTime), description="数据时间")
    rank: int = Field(description="排名")
    name: str = Field(max_length=100, description="板块名称")

    pct_change: Optional[float] = Field(default=None, description="涨跌幅（百分比）")
    main_net_inflow: Optional[float] = Field(default=None, description="主力净流入（元）")
    main_net_ratio: Optional[float] = Field(default=None, description="主力净占比（百分比）")

    super_net_inflow: Optional[float] = Field(default=None, description="超大单净流入（元）")
    super_net_ratio: Optional[float] = Field(default=None, description="超大单净占比（百分比）")
    large_net_inflow: Optional[float] = Field(default=None, description="大单净流入（元）")
    large_net_ratio: Optional[float] = Field(default=None, description="大单净占比（百分比）")
    medium_net_inflow: Optional[float] = Field(default=None, description="中单净流入（元）")
    medium_net_ratio: Optional[float] = Field(default=None, description="中单净占比（百分比）")
    small_net_inflow: Optional[float] = Field(default=None, description="小单净流入（元）")
    small_net_ratio: Optional[float] = Field(default=None, description="小单净占比（百分比）")

    leader: Optional[str] = Field(default=None, max_length=100, description="领涨股")

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now),
        description="创建时间",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now),
        description="更新时间",
    )


class StockFundFlow(SQLModel, table=True):
    """个股资金流向表"""

    __tablename__ = "stock_fund_flow"  # type: ignore

    __table_args__ = (
        UniqueConstraint("market", "stat", "as_of", "rank", name="uq_stock_fund_flow_market_stat_asof_rank"),
        Index("idx_stock_fund_flow_market_stat_as_of_rank", "market", "stat", "as_of", "rank"),
        Index("idx_stock_fund_flow_market_stat_as_of_code", "market", "stat", "as_of", "code"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    market: str = Field(max_length=20, description="市场 all/hsa/sha/sza/kcb/cyb")
    stat: int = Field(description="统计周期 1/5/10")
    as_of: datetime = Field(sa_column=Column(DateTime), description="数据时间")
    rank: int = Field(description="排名")

    code: str = Field(max_length=10, description="股票代码")
    name: str = Field(max_length=100, description="股票名称")
    price: Optional[float] = Field(default=None, description="最新价")
    pct_change: Optional[float] = Field(default=None, description="涨跌幅（百分比）")

    main_net_inflow: Optional[float] = Field(default=None, description="主力净流入（元）")
    main_net_ratio: Optional[float] = Field(default=None, description="主力净占比（百分比）")

    super_net_inflow: Optional[float] = Field(default=None, description="超大单净流入（元）")
    super_net_ratio: Optional[float] = Field(default=None, description="超大单净占比（百分比）")
    large_net_inflow: Optional[float] = Field(default=None, description="大单净流入（元）")
    large_net_ratio: Optional[float] = Field(default=None, description="大单净占比（百分比）")
    medium_net_inflow: Optional[float] = Field(default=None, description="中单净流入（元）")
    medium_net_ratio: Optional[float] = Field(default=None, description="中单净占比（百分比）")
    small_net_inflow: Optional[float] = Field(default=None, description="小单净流入（元）")
    small_net_ratio: Optional[float] = Field(default=None, description="小单净占比（百分比）")

    industry: Optional[str] = Field(default=None, max_length=100, description="所属行业")

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now),
        description="创建时间",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now),
        description="更新时间",
    )
