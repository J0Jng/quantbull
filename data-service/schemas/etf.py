from typing import List

from pydantic import BaseModel, Field


class ETFItem(BaseModel):
    """ETF 数据项"""
    symbol: str = Field(..., description="ETF 代码")
    name: str = Field(..., description="ETF 名称")
    category: str = Field(..., description="ETF 类别，如宽基、行业")
    latest_price: float = Field(..., description="最新价")
    pct_change: float = Field(..., description="涨跌幅（百分比）")
    volume: int = Field(..., description="成交量")


class ETFListResponse(BaseModel):
    """ETF 列表响应"""
    code: int = Field(default=0, description="响应码")
    message: str = Field(default="ok", description="响应消息")
    data: List[ETFItem] = Field(..., description="ETF 列表")