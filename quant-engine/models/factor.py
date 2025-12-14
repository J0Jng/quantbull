from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Factor(BaseModel):
    """因子模型"""
    id: Optional[str] = Field(default=None, description="因子ID")
    name: str = Field(..., description="因子名称", min_length=1)
    description: str = Field(default="", description="因子描述")
    category: str = Field(default="technical", description="因子类别：technical/fundamental/macro")
    formula: Optional[str] = Field(default=None, description="因子公式")
    parameters: dict = Field(default_factory=dict, description="因子参数")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "RSI",
                "description": "相对强弱指标",
                "category": "technical",
                "formula": "RSI = 100 - (100 / (1 + RS))",
                "parameters": {"period": 14}
            }
        }


class FactorValue(BaseModel):
    """因子值模型"""
    factor_id: str = Field(..., description="因子ID")
    symbol: str = Field(..., description="股票代码")
    date: str = Field(..., description="日期")
    value: float = Field(..., description="因子值")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
