from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Strategy(BaseModel):
    """策略模型"""
    id: Optional[str] = Field(default=None, description="策略ID")
    name: str = Field(..., description="策略名称", min_length=1)
    description: str = Field(default="", description="策略描述")
    code: str = Field(..., description="策略代码")
    parameters: dict = Field(default_factory=dict, description="策略参数")
    status: str = Field(default="active", description="状态：active/inactive")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "双均线策略",
                "description": "基于5日和20日均线的简单策略",
                "code": "class MyStrategy(bt.Strategy): ...",
                "parameters": {"fast_period": 5, "slow_period": 20}
            }
        }


class BacktestResult(BaseModel):
    """回测结果模型"""
    strategy_id: str = Field(..., description="策略ID")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    initial_cash: float = Field(..., description="初始资金")
    final_value: float = Field(..., description="最终资产")
    total_return: float = Field(..., description="总收益率")
    annual_return: float = Field(..., description="年化收益率")
    sharpe_ratio: Optional[float] = Field(default=None, description="夏普比率")
    max_drawdown: float = Field(..., description="最大回撤")
    win_rate: Optional[float] = Field(default=None, description="胜率")
    total_trades: int = Field(..., description="总交易次数")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
