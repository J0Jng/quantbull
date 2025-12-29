import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class BacktestStatus(str):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class BacktestRecord(SQLModel, table=True):
    __tablename__ = "backtest_results"

    id: str = Field(default_factory=lambda: f"backtest_{uuid.uuid4().hex[:8]}", primary_key=True, index=True)
    task_id: Optional[str] = Field(default=None, index=True)
    strategy_code: Optional[str] = Field(default=None, index=True)
    stock_code: str = Field(index=True)
    start_date: str
    end_date: str
    data_source: Optional[str] = None
    params: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    metrics: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    equity_curve: Optional[List[Dict[str, Any]]] = Field(default=None, sa_column=Column(JSON))
    status: str = Field(default=BacktestStatus.pending)
    message: Optional[str] = None
    error_code: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
