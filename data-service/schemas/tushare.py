from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class DailyQuoteRequest(BaseModel):
    """日线行情请求"""
    codes: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=100)
    start_date: str = Field(..., description="开始日期 YYYYMMDD")
    end_date: str = Field(..., description="结束日期 YYYYMMDD")
    
    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """验证日期格式"""
        if len(v) != 8 or not v.isdigit():
            raise ValueError("日期格式必须为 YYYYMMDD")
        return v


class DailyQuoteItem(BaseModel):
    """日线行情数据项"""
    code: str = Field(..., description="股票代码（6位）")
    trade_date: str = Field(..., description="交易日期 YYYYMMDD")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    vol: int = Field(..., description="成交量（手）")
    amount: float = Field(..., description="成交额（元）")


class DailyQuoteResponse(BaseModel):
    """日线行情响应"""
    data: List[DailyQuoteItem] = Field(default_factory=list, description="行情数据列表")
    success_codes: List[str] = Field(default_factory=list, description="成功获取的股票代码")
    failed_codes: List[str] = Field(default_factory=list, description="获取失败的股票代码")


class StockBasicRequest(BaseModel):
    """股票基础信息请求"""
    exchange: Optional[str] = Field(None, description="交易所 SSE/SZSE，空表示全部")


class StockBasicResponse(BaseModel):
    """股票基础信息响应"""
    data: List[dict] = Field(default_factory=list, description="股票基础信息列表")

