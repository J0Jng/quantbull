from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RealtimeQuoteRequest(BaseModel):
    """实时行情请求"""
    codes: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=100)


class QuoteItem(BaseModel):
    """行情数据项"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    price: float = Field(..., description="最新价")
    pct_change: float = Field(..., description="涨跌幅（百分比）")
    turnover: float = Field(..., description="成交额（元）")
    update_time: datetime = Field(..., description="更新时间")


class RealtimeQuoteResponse(BaseModel):
    """实时行情响应"""
    data: List[QuoteItem] = Field(..., description="行情数据列表")
    success_codes: List[str] = Field(default_factory=list, description="成功获取的股票代码")
    failed_codes: List[str] = Field(default_factory=list, description="获取失败的股票代码")

