from datetime import date
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, Date


class DailyQuote(SQLModel, table=True):
    """日线行情数据表"""
    __tablename__ = "daily_quotes"  # type: ignore
    
    #复合唯一约束：code + trade_date
    __table_args__ = (
        UniqueConstraint("code", "trade_date", name="uq_code_trade_date"),
        Index("idx_trade_date", "trade_date")  #为trade_date字段创建名为idx_trade_date的索引，加速按交易日期查询的速度。
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, description="股票代码(6位)")
    trade_date: date = Field(
        sa_column=Column(Date, nullable=False),
        description="交易日期"
    )
    open: float = Field(description="开盘价")
    high: float = Field(description="最高价")
    low: float = Field(description="最低价")
    close: float = Field(description="收盘价")
    vol: int = Field(description="成交量（手）")
    amount: float = Field(description="成交额（元）")

