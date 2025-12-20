from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, JSON

from .base import TimestampMixin


class News(TimestampMixin, SQLModel, table=True):
    __tablename__ = "news"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, max_length=300)
    summary: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = Field(default=None, index=True)
    symbol: Optional[str] = Field(default=None, index=True)
    publish_time: Optional[datetime] = Field(default=None, index=True)
    importance: Optional[int] = Field(default=0)
    sentiment: Optional[float] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
