from __future__ import annotations

from datetime import date, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


PublicFundType = Literal["", "stock", "hybrid", "bond", "monetary"]
ReturnSign = Literal["", "positive", "negative"]
PublicSortBy = Literal["default", "return1w", "return1m", "return3m", "return6m", "return1y", "return3y"]
Order = Literal["desc", "asc"]


class PublicFundRankingItem(BaseModel):
    code: str = Field(..., description="基金代码")
    name: str = Field(..., description="基金名称")
    type: str = Field(..., description="基金类型")

    nav: float = Field(..., description="单位净值")
    change: float = Field(..., description="日涨跌幅（百分比数值）")

    return1w: float = Field(..., description="近 1 周收益率（百分比数值）")
    return1m: float = Field(..., description="近 1 月收益率（百分比数值）")
    return3m: float = Field(..., description="近 3 月收益率（百分比数值）")
    return6m: float = Field(..., description="近 6 月收益率（百分比数值）")
    return1y: float = Field(..., description="近 1 年收益率（百分比数值）")
    return3y: float = Field(..., description="近 3 年收益率（百分比数值）")

    as_of: date = Field(..., description="数据日期")
    source: Literal["tushare", "eastmoney"] = Field(..., description="数据来源")
    cached: bool = Field(default=False, description="是否来自缓存")


class PublicFundRankingResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PublicFundRankingItem]
    source_used: Literal["tushare", "eastmoney"]
    updated_at: datetime


PrivateStrategy = Literal["", "equity", "futures", "hedge", "composite"]
PrivateRiskLevel = Literal["", "low", "medium", "high"]
PrivateSortBy = Literal["default", "return1y", "sharpe", "maxdrawdown"]


class PrivateFundRankingItem(BaseModel):
    id: str
    name: str
    strategy: str
    risk_level: str
    established: str

    return1m: float
    return3m: float
    return1y: float
    annualizedReturn: float
    maxDrawdown: float
    sharpeRatio: float

    as_of: date
    source: Literal["internal"] = "internal"
    cached: bool = Field(default=True, description="是否来自缓存/内置")


class PrivateFundRankingResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[PrivateFundRankingItem]
    source_used: Literal["internal"]
    updated_at: datetime
