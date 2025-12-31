import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class Strategy(SQLModel, table=True):
    """策略表"""

    __tablename__ = "strategies"

    id: str = Field(default_factory=lambda: f"strategy_{uuid.uuid4().hex[:8]}", primary_key=True, index=True)
    name: str = Field(index=True, description="策略名称", max_length=100)
    description: str = Field(default="", description="策略描述", max_length=1000)
    code: str = Field(description="策略代码（Python）")
    factor_ids: List[str] = Field(default_factory=list, sa_column=Column(JSON), description="关联因子ID列表")
    parameters: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="策略参数")
    status: str = Field(default="draft", description="策略状态：draft/active/archived", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


class BacktestResult(SQLModel, table=False):
    """回测结果模型（非持久化）"""

    strategy_id: str
    start_date: str
    end_date: str
    initial_cash: float
    final_value: float
    total_return: float
    annual_return: float
    sharpe_ratio: Optional[float] = None
    max_drawdown: float
    win_rate: Optional[float] = None
    total_trades: int
    created_at: Optional[datetime] = None
