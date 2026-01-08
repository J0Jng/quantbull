"""基本面数据 Schema"""
from typing import List, Optional

from pydantic import BaseModel, Field


class FundamentalsRequest(BaseModel):
    """基本面批量请求"""
    codes: List[str] = Field(..., description="股票代码列表（6位）", min_length=1, max_length=100)
    trade_date: Optional[str] = Field(None, description="交易日期 YYYYMMDD，不传则使用最近日期")


class FundamentalsItem(BaseModel):
    """单只股票基本面数据"""
    code: str = Field(..., description="股票代码（6位）")
    industry: Optional[str] = Field(None, description="所属行业")
    list_date: Optional[str] = Field(None, description="上市日期 YYYYMMDD")
    is_st: bool = Field(False, description="是否ST股票")
    circ_mv: Optional[float] = Field(None, description="流通市值（万元）")
    total_mv: Optional[float] = Field(None, description="总市值（万元）")
    pe_ttm: Optional[float] = Field(None, description="市盈率TTM")
    pb: Optional[float] = Field(None, description="市净率")
    gross_margin: Optional[float] = Field(None, description="毛利率（%）")
    debt_to_assets: Optional[float] = Field(None, description="资产负债率（%）")
    roe_yoy: Optional[float] = Field(None, description="ROE同比增长率（%）")
    netprofit_yoy: Optional[float] = Field(None, description="净利润同比增长率（%）")
    revenue_yoy: Optional[float] = Field(None, description="营收同比增长率（%）")
    name: Optional[str] = Field(None, description="股票名称")


class FundamentalsResponse(BaseModel):
    """基本面批量响应"""
    data: List[FundamentalsItem] = Field(default_factory=list, description="基本面数据列表")
    success_codes: List[str] = Field(default_factory=list, description="成功获取的股票代码")
    failed_codes: List[str] = Field(default_factory=list, description="获取失败的股票代码")


class IndustryRankRequest(BaseModel):
    """行业排名请求"""
    month: Optional[str] = Field(None, description="月份 YYYY-MM，不传则使用最近月")


class IndustryRankItem(BaseModel):
    """行业排名项"""
    industry: str = Field(..., description="行业名称")
    rank: int = Field(..., description="排名（1为最好）")
    score: float = Field(..., description="景气度分数（-1到1）")
    avg_netprofit_yoy: Optional[float] = Field(None, description="平均净利润同比")
    avg_revenue_yoy: Optional[float] = Field(None, description="平均营收同比")
    avg_roe_yoy: Optional[float] = Field(None, description="平均ROE同比")
    stock_count: int = Field(0, description="该行业股票数量")


class IndustryRankResponse(BaseModel):
    """行业排名响应"""
    month: str = Field(..., description="数据月份")
    data: List[IndustryRankItem] = Field(default_factory=list, description="行业排名列表")


class SentimentRequest(BaseModel):
    """舆情评分请求"""
    codes: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=100)
    start_date: Optional[str] = Field(None, description="开始日期 YYYYMMDD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYYMMDD")


class SentimentItem(BaseModel):
    """舆情评分项"""
    code: str = Field(..., description="股票代码")
    sentiment_score: float = Field(0.0, description="舆情分数（-1到1）")
    discussion_volume: int = Field(0, description="讨论量")


class SentimentResponse(BaseModel):
    """舆情评分响应"""
    data: List[SentimentItem] = Field(default_factory=list, description="舆情数据列表")


class HotScoreRequest(BaseModel):
    """热点分数请求"""
    codes: List[str] = Field(..., description="股票代码列表", min_length=1, max_length=100)


class HotScoreItem(BaseModel):
    """热点分数项"""
    code: str = Field(..., description="股票代码")
    hot_score: float = Field(0.0, description="热点分数（0到1）")


class HotScoreResponse(BaseModel):
    """热点分数响应"""
    data: List[HotScoreItem] = Field(default_factory=list, description="热点数据列表")
