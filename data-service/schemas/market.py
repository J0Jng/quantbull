from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class IndexItem(BaseModel):
    """指数数据项"""
    symbol: str = Field(..., description="指数代码")
    name: str = Field(..., description="指数名称")
    close: float = Field(..., description="收盘价")
    pct_change: float = Field(..., description="涨跌幅（百分比）")


class MarketOverviewData(BaseModel):
    """市场概览数据"""
    trade_date: str = Field(..., description="交易日期 YYYY-MM-DD")
    market_status: str = Field(..., description="市场状态: bull | bear |震荡")
    indices: List[IndexItem] = Field(..., description="主要指数列表")
    total_turnover: float = Field(..., description="总成交额（元）")


class MarketOverviewResponse(BaseModel):
    """市场概览响应"""
    code: int = Field(default=0, description="响应码")
    message: str = Field(default="ok", description="响应消息")
    data: MarketOverviewData = Field(..., description="市场概览数据")


class TradingDayStatusData(BaseModel):
    """交易日状态数据"""
    date: str = Field(..., description="日期 YYYY-MM-DD")
    is_trading_day: bool = Field(..., description="是否交易日")
    source: str = Field(default="trade_cal", description="数据来源")


class TradingDayStatusResponse(BaseModel):
    """交易日状态响应"""
    code: int = Field(default=0, description="响应码")
    message: str = Field(default="ok", description="响应消息")
    data: TradingDayStatusData = Field(..., description="交易日状态数据")