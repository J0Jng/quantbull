from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON

from .base import TimestampMixin


class User(TimestampMixin, SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False, max_length=50)
    email: Optional[str] = Field(index=True, default=None, max_length=120)
    full_name: Optional[str] = None
    hashed_password: Optional[str] = None
    is_active: bool = Field(default=True)
    role: str = Field(default="user")
    profile: Optional[dict] = Field(default=None, sa_column=Column(JSON, nullable=True))

    strategies: List["Strategy"] = Relationship(back_populates="user")


class UserCreate(SQLModel):
    username: str
    email: Optional[str]
    full_name: Optional[str]
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    email: Optional[str]
    full_name: Optional[str]
    is_active: bool
    role: str
