"""龙虎榜上榜个股明细数据模型"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class LhbStockItem(SQLModel, table=True):
    __tablename__ = "lhb_stock_item"  # type: ignore

    __table_args__ = (
        UniqueConstraint("trade_date", "code", "reason", name="uq_lhb_stock_item_trade_code_reason"),
        Index("idx_lhb_stock_item_trade_code", "trade_date", "code"),
        Index("idx_lhb_stock_item_trade_rank", "trade_date", "rank"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    trade_date: str = Field(max_length=20, description="交易日期 YYYY-MM-DD")

    code: str = Field(max_length=10, description="股票代码")
    name: str = Field(max_length=100, description="股票名称")

    close: Optional[float] = Field(default=None, description="收盘价")
    pct_change: Optional[float] = Field(default=None, description="涨跌幅（百分比）")

    buy_amount: Optional[float] = Field(default=None, description="买入金额（元）")
    sell_amount: Optional[float] = Field(default=None, description="卖出金额（元）")
    net_buy_amount: Optional[float] = Field(default=None, description="净买入金额（元）")
    turnover: Optional[float] = Field(default=None, description="成交额/换手金额（元）")

    net_buy_ratio: Optional[float] = Field(default=None, description="净买额占总成交比")
    turnover_rate: Optional[float] = Field(default=None, description="换手率（百分比）")
    circulation_market_value: Optional[float] = Field(default=None, description="流通市值（元）")

    reason: Optional[str] = Field(default=None, max_length=300, description="上榜原因")
    rank: Optional[int] = Field(default=None, description="榜内排名")

    source_url: Optional[str] = Field(default=None, max_length=300, description="来源 URL")
    as_of: Optional[datetime] = Field(default=None, sa_column=Column(DateTime), description="抓取时间")

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
