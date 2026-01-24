from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


MarketBucket = Literal["super", "large", "medium", "small"]
SectorType = Literal["industry", "concept", "region"]
StockMarket = Literal["all", "hsa", "sha", "sza", "kcb", "cyb"]
StatType = Literal[1, 5, 10]
Order = Literal["desc", "asc"]


class MarketFlowItem(BaseModel):
    bucket: MarketBucket
    inflow: float
    outflow: float
    net: Optional[float] = None


class MarketFlowResponse(BaseModel):
    as_of: datetime
    market: str
    items: List[MarketFlowItem]


class SectorFlowItem(BaseModel):
    rank: int
    name: str
    pct_change: Optional[float] = None
    main_net_inflow: Optional[float] = None
    main_net_ratio: Optional[float] = None
    super_net_inflow: Optional[float] = None
    super_net_ratio: Optional[float] = None
    large_net_inflow: Optional[float] = None
    large_net_ratio: Optional[float] = None
    medium_net_inflow: Optional[float] = None
    medium_net_ratio: Optional[float] = None
    small_net_inflow: Optional[float] = None
    small_net_ratio: Optional[float] = None
    leader: Optional[str] = None


class SectorFlowResponse(BaseModel):
    as_of: datetime
    type: SectorType
    page: int
    page_size: int
    total: int
    items: List[SectorFlowItem]


class StockFlowItem(BaseModel):
    rank: int
    code: str
    name: str
    price: Optional[float] = None
    pct_change: Optional[float] = None
    main_net_inflow: Optional[float] = None
    main_net_ratio: Optional[float] = None
    super_net_inflow: Optional[float] = None
    super_net_ratio: Optional[float] = None
    large_net_inflow: Optional[float] = None
    large_net_ratio: Optional[float] = None
    medium_net_inflow: Optional[float] = None
    medium_net_ratio: Optional[float] = None
    small_net_inflow: Optional[float] = None
    small_net_ratio: Optional[float] = None
    industry: Optional[str] = None


class StockFlowResponse(BaseModel):
    as_of: datetime
    market: StockMarket
    stat: StatType
    page: int
    page_size: int
    total: int
    items: List[StockFlowItem]
