from datetime import datetime
from typing import Optional

from sqlmodel import Field
from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_mixin, declared_attr


@declarative_mixin
class TimestampMixin:
    """Mixin that provides per-class SQLAlchemy Column objects for timestamps.

    Use as a base for SQLModel table classes to avoid reusing the same Column
    object across multiple tables (which triggers "already assigned" errors).
    """

    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

