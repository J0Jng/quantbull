"""
财经频道数据缓存表模型
用于统一存储财经频道各模块（市场数据、日历、观点、政策）的缓存数据
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, Text
from sqlmodel import SQLModel, Field, Column, DateTime, JSON


class FinanceChannelCache(SQLModel, table=True):
    """财经频道数据缓存表 - 通用缓存表，支持所有模块数据"""
    __tablename__ = "finance_channel_cache"  # type: ignore
    
    __table_args__ = (
        Index("idx_finance_cache_key", "cache_key"),
        Index("idx_finance_cache_module", "module"),
        Index("idx_finance_cache_fetched_at", "fetched_at"),
        Index("idx_finance_cache_expires_at", "expires_at"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True, description="自增主键")
    
    # 缓存标识
    cache_key: str = Field(max_length=200, unique=True, index=True, description="缓存唯一键（如 market, calendar, ideas:page=1）")
    module: str = Field(max_length=50, index=True, description="模块类型（market/calendar/ideas/policies）")
    
    # 缓存内容
    payload_json: dict = Field(sa_column=Column(JSON), description="缓存的 JSON 数据（标准化后的 items 列表）")
    source: str = Field(default="unknown", max_length=100, description="数据源标识")
    
    # 时间戳
    fetched_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, nullable=False),
        description="数据抓取时间"
    )
    expires_at: datetime = Field(
        sa_column=Column(DateTime, nullable=False),
        description="缓存过期时间"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, nullable=False),
        description="记录创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
        description="记录更新时间"
    )
    
    class Config:
        """Pydantic 配置"""
        json_schema_extra = {
            "example": {
                "cache_key": "market",
                "module": "market",
                "payload_json": {
                    "items": [
                        {"code": "000001.SH", "title": "上证指数", "value": "3245.67", "change_pct": 1.25}
                    ]
                },
                "source": "eastmoney",
                "fetched_at": "2025-01-22T10:00:00",
                "expires_at": "2025-01-22T10:05:00"
            }
        }
