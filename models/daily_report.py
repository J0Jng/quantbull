from typing import Optional, List
from datetime import date, datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON

from .base import TimestampMixin


class DailyReport(TimestampMixin, SQLModel, table=True):
    __tablename__ = "daily_report" 

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)
    strategy_id: Optional[int] = Field(default=None, foreign_key="strategy.id", index=True)
    report_date: date = Field(index=True)
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    signals: Optional[List[dict]] = Field(default=None, sa_column=Column(JSON))
    score: Optional[float] = None
    ai_version: Optional[str] = None
    published: bool = Field(default=False, index=True)

    user: Optional["User"] = Relationship()
    strategy: Optional["Strategy"] = Relationship(back_populates="reports")
