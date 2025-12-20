from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

from .base import TimestampMixin


class Quote(TimestampMixin, SQLModel, table=True):
    __tablename__ = "quotes"

    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True, nullable=False, max_length=64)
    timestamp: datetime = Field(index=True)
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    last: Optional[float] = None
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume: Optional[float] = None
    extra: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # Composite index commonly useful: (symbol, timestamp)
