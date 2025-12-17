from datetime import datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class RealtimeQuote(SQLModel, table=True):
    """实时行情数据表"""
    __tablename__ = "realtime_quotes" # type: ignore
    
    # 复合唯一约束：code + update_time
    __table_args__ = (
        UniqueConstraint("code", "update_time", name="uq_code_update_time"),
        Index("idx_code", "code"),
        Index("idx_update_time", "update_time"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, description="股票代码")
    name: str = Field(description="股票名称")
    price: float = Field(description="最新价")
    pct_change: float = Field(description="涨跌幅（百分比）")
    turnover: float = Field(description="成交额（元）")
    update_time: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        description="更新时间"
    )

