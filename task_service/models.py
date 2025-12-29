import enum
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class TaskStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    task_type: str = Field(index=True)
    status: TaskStatus = Field(default=TaskStatus.pending)
    progress: float = Field(default=0.0)
    result_url: Optional[str] = None
    result: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    payload: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
