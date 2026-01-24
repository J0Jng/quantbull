"""龙虎榜多日统计/汇总数据模型"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class LhbStockSummary(SQLModel, table=True):
    __tablename__ = "lhb_stock_summary"  # type: ignore

    __table_args__ = (
        UniqueConstraint("window_days", "end_trade_date", "code", name="uq_lhb_stock_summary_days_end_code"),
        Index("idx_lhb_stock_summary_days_end", "window_days", "end_trade_date"),
        Index("idx_lhb_stock_summary_days_rank", "window_days", "end_trade_date", "rank"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    window_days: int = Field(description="统计窗口天数")
    end_trade_date: str = Field(max_length=20, description="统计截止交易日 YYYY-MM-DD")

    code: str = Field(max_length=10, description="股票代码")
    name: str = Field(max_length=100, description="股票名称")

    appear_count: Optional[int] = Field(default=None, description="上榜次数")

    net_buy_amount: Optional[float] = Field(default=None, description="净买入金额（元）")
    buy_amount: Optional[float] = Field(default=None, description="买入金额（元）")
    sell_amount: Optional[float] = Field(default=None, description="卖出金额（元）")
    total_amount: Optional[float] = Field(default=None, description="买卖总额（元）")

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
