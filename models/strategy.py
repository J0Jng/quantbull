from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON

from .base import TimestampMixin


class Strategy(TimestampMixin, SQLModel, table=True):
    __tablename__ = "strategy"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, nullable=False, max_length=200)
    user_id: int = Field(foreign_key="user.id", index=True)
    description: Optional[str] = None
    symbol: Optional[str] = Field(default=None, index=True)
    parameters: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    code_repo: Optional[str] = None
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    status: str = Field(default="draft")
    score: Optional[float] = None

    user: Optional["User"] = Relationship(back_populates="strategies")
    reports: List["DailyReport"] = Relationship(back_populates="strategy")


class StrategyCreate(SQLModel):
    name: str
    user_id: int
    symbol: Optional[str]
    description: Optional[str]
    parameters: Optional[dict]


class StrategyRead(SQLModel):
    id: int
    name: str
    user_id: int
    symbol: Optional[str]
    score: Optional[float]
