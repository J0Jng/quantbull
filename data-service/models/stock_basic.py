"""股票基础信息模型"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, Date, DateTime


class StockBasic(SQLModel, table=True):
    """股票基础信息表 - 用于缓存 tushare 股票列表数据"""
    __tablename__ = "stock_basic"  # type: ignore
    
    __table_args__ = (
        UniqueConstraint("symbol", "trade_date", name="uq_stock_symbol_trade_date"),
        Index("idx_stock_trade_date", "trade_date"),
        Index("idx_stock_symbol", "symbol"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True, max_length=10, description="股票代码(6位)")
    name: str = Field(max_length=50, description="股票名称")
    industry: str = Field(default="未知", max_length=50, description="所属行业")
    trade_date: date = Field(
        sa_column=Column(Date, nullable=False),
        description="交易日期"
    )
    latest_price: float = Field(default=0.0, description="最新价格")
    pct_change: float = Field(default=0.0, description="涨跌幅")
    turnover_rate: float = Field(default=0.0, description="换手率")
    amount: float = Field(default=0.0, description="成交额（千元）")
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now),
        description="创建时间"
    )
