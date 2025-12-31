import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel


class Factor(SQLModel, table=True):
    """因子表，用于持久化因子定义"""

    __tablename__ = "factors"

    id: str = Field(default_factory=lambda: f"factor_{uuid.uuid4().hex[:8]}", primary_key=True, index=True)
    name: str = Field(index=True, description="因子名称", max_length=100)
    description: str = Field(default="", description="因子描述", max_length=1000)
    expression: str = Field(description="因子表达式/公式", max_length=2000)
    data_source: str = Field(default="price", description="数据来源：price/fundamental/tdengine", index=True)
    category: Optional[str] = Field(default=None, description="因子类别，兼容旧字段")
    formula: Optional[str] = Field(default=None, description="兼容旧字段：因子公式")
    parameters: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="参数，兼容旧字段")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")


class FactorValue(SQLModel, table=False):
    """因子值模型（非持久化，仅用于序列化）"""

    factor_id: str
    symbol: str
    date: str
    value: float
    created_at: Optional[datetime] = None
