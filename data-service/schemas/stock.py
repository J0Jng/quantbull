from typing import List

from pydantic import BaseModel, Field


class StockItem(BaseModel):
    """股票数据项"""
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    industry: str = Field(..., description="行业")
    latest_price: float = Field(..., description="最新价")
    pct_change: float = Field(..., description="涨跌幅（百分比）")
    turnover_rate: float = Field(..., description="换手率（百分比）")


class StockListResponse(BaseModel):
    """股票列表响应"""
    code: int = Field(default=0, description="响应码")
    message: str = Field(default="ok", description="响应消息")
    data: List[StockItem] = Field(..., description="股票列表")