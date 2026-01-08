"""ETF 基础信息模型"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, Date, DateTime


class ETFBasic(SQLModel, table=True):
    """ETF 基础信息表 - 用于缓存 tushare ETF 列表数据"""
    __tablename__ = "etf_basic"  # type: ignore
    
    __table_args__ = (
        UniqueConstraint("symbol", "trade_date", name="uq_etf_symbol_trade_date"),
        Index("idx_etf_trade_date", "trade_date"),
        Index("idx_etf_symbol", "symbol"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True, max_length=10, description="ETF代码(6位)")
    name: str = Field(max_length=100, description="ETF名称")
    category: str = Field(default="其他", max_length=20, description="类别(宽基/行业/其他)")
    trade_date: date = Field(
        sa_column=Column(Date, nullable=False),
        description="交易日期"
    )
    latest_price: float = Field(default=0.0, description="最新价格")
    pct_change: float = Field(default=0.0, description="涨跌幅")
    volume: int = Field(default=0, description="成交量")
    amount: float = Field(default=0.0, description="成交额（千元）")
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now),
        description="创建时间"
    )
