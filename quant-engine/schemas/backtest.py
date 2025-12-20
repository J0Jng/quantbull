from datetime import date
from typing import Optional, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class BacktestRequest(BaseModel):
    """回测请求"""
    stock_code: str = Field(..., description="股票代码（如：000001）", min_length=1)
    start_date: str = Field(..., description="开始日期（YYYY-MM-DD）")
    end_date: str = Field(..., description="结束日期（YYYY-MM-DD）")
    
    strategy_mode: Literal["custom", "builtin"] = Field(
        default="custom",
        description="策略模式：custom（AI生成）或 builtin（系统内置）"
    )
    strategy_code: Optional[str] = Field(
        default=None,
        description="策略代码（strategy_mode=custom 时必填）",
        min_length=1
    )
    strategy_name: Optional[str] = Field(
        default=None,
        description="策略名称（strategy_mode=builtin 时必填，如：ma_cross, rsi）"
    )
    
    data_source: Literal["tdengine", "tushare"] = Field(
        default="tushare",
        description="数据源：tdengine 或 tushare"
    )
    
    enable_ai_review: bool = Field(
        default=False,
        description="是否启用 AI 评价（返回结构化评价输入数据）"
    )
    
    # 回测参数（可选，使用默认值）
    initial_cash: float = Field(default=1000000.0, ge=1000.0, description="初始资金")
    commission: float = Field(default=0.001, ge=0.0, le=0.01, description="手续费率")
    slippage: float = Field(default=0.0, ge=0.0, le=0.01, description="滑点")
    parameters: dict = Field(default_factory=dict, description="策略参数")
    
    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """验证日期格式"""
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError("日期格式必须为 YYYY-MM-DD")
        return v
    
    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: str, info) -> str:
        """验证结束日期必须晚于开始日期"""
        if "start_date" in info.data:
            start = date.fromisoformat(info.data["start_date"])
            end = date.fromisoformat(v)
            if end <= start:
                raise ValueError("结束日期必须晚于开始日期")
        return v
    
    @model_validator(mode="after")
    def validate_strategy(self):
        """验证策略参数"""
        if self.strategy_mode == "custom" and not self.strategy_code:
            raise ValueError("strategy_mode=custom 时，strategy_code 必填")
        if self.strategy_mode == "builtin" and not self.strategy_name:
            raise ValueError("strategy_mode=builtin 时，strategy_name 必填")
        return self


class AIReviewData(BaseModel):
    """AI 策略评价输入数据结构"""
    strategy_type: str = Field(..., description="策略类型（如：trend_following, mean_reversion）")
    holding_period_days_avg: float = Field(..., description="平均持仓天数")
    trade_count: int = Field(..., description="交易次数")
    win_rate: float = Field(..., description="胜率（0-1）")
    profit_loss_ratio: float = Field(..., description="盈亏比")
    volatility: float = Field(..., description="波动率")
    max_consecutive_loss: int = Field(..., description="最大连续亏损次数")
    drawdown_duration_days: int = Field(..., description="最大回撤持续时间（天）")
    return_over_drawdown: float = Field(..., description="收益回撤比")


class BacktestResponse(BaseModel):
    """回测响应"""
    success: bool = Field(..., description="是否成功")
    backtest_id: str = Field(..., description="回测ID")
    
    # 基础回测输出（始终返回）
    metrics: dict = Field(..., description="基础指标")
    daily_nav: list[dict] = Field(..., description="每日净值曲线，格式：[{date: 'YYYY-MM-DD', nav: float}]")
    
    # AI 策略评价输入（enable_ai_review=true 时返回）
    ai_review: Optional[AIReviewData] = Field(default=None, description="AI 评价所需的结构化数据")
    
    message: Optional[str] = Field(default=None, description="消息或错误信息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "backtest_id": "backtest_001",
                "metrics": {
                    "annual_return": 0.18,
                    "sharpe_ratio": 1.42,
                    "max_drawdown": -0.21
                },
                "daily_nav": [
                    {"date": "2022-01-01", "nav": 1.0},
                    {"date": "2022-01-02", "nav": 1.02}
                ],
                "ai_review": {
                    "strategy_type": "trend_following",
                    "holding_period_days_avg": 12.4,
                    "trade_count": 86,
                    "win_rate": 0.54,
                    "profit_loss_ratio": 1.37,
                    "volatility": 0.22,
                    "max_consecutive_loss": 5,
                    "drawdown_duration_days": 78,
                    "return_over_drawdown": 0.86
                }
            }
        }


class BacktestSubmitResponse(BaseModel):
    """回测任务提交响应，返回 task_id，前端使用统一查询接口轮询状态"""
    task_id: str

