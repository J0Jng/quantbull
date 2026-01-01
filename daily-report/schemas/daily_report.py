"""每日投资方案 Schema（Pydantic v2）"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


# ==================== 数据输入 Schema ====================

class MarketOverview(BaseModel):
    """市场概览数据（来自 data-service）"""
    indices: dict = Field(..., description="指数数据（上证、深证、创业板等）")
    total_turnover: float = Field(..., description="总成交额")
    rising_count: int = Field(..., description="上涨股票数")
    falling_count: int = Field(..., description="下跌股票数")
    flat_count: int = Field(..., description="平盘股票数")


class ETFData(BaseModel):
    """ETF 行情数据（来自 data-service）"""
    code: str = Field(..., description="ETF 代码")
    name: str = Field(..., description="ETF 名称")
    change_pct: float = Field(..., description="涨跌幅 %")
    turnover: float = Field(..., description="成交额")
    volume: float = Field(..., description="成交量")
    category: Optional[str] = Field(default=None, description="所属主题/行业")


class StockData(BaseModel):
    """股票行情数据（来自 data-service）"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    change_pct: float = Field(..., description="涨跌幅 %")
    turnover: float = Field(..., description="成交额")
    turnover_rate: float = Field(..., description="换手率 %")
    industry: Optional[str] = Field(default=None, description="所属行业")


class MarketDataInput(BaseModel):
    """市场数据输入（聚合 data-service 数据）"""
    market_overview: MarketOverview = Field(..., description="市场概览")
    etf_list: List[ETFData] = Field(..., description="ETF 列表")
    stock_list: List[StockData] = Field(..., description="股票列表")
    report_date: str = Field(..., description="报告日期 YYYY-MM-DD")
    
    @field_validator("report_date")
    @classmethod
    def validate_report_date(cls, v: str) -> str:
        """验证报告日期格式"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("报告日期格式必须为 YYYY-MM-DD")
        return v


# ==================== AI 生成内容 Schema ====================

class ETFRecommendation(BaseModel):
    """ETF 推荐"""
    code: str = Field(..., description="ETF 代码")
    name: str = Field(..., description="ETF 名称")
    category: str = Field(..., description="所属主题/行业")
    reasoning: str = Field(..., description="推荐逻辑（结合市场风格、行业轮动、情绪）", max_length=500)


class StockRecommendation(BaseModel):
    """股票推荐"""
    code: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    factor_scores: dict = Field(..., description="多因子评分，如: {momentum: 8.5, liquidity: 7.2, sentiment: 6.8}")
    ai_analysis: str = Field(..., description="AI 解读（不超过80字）", max_length=80)


class ArticleOutline(BaseModel):
    """公众号文章大纲"""
    title: str = Field(..., description="文章标题")
    sections: List[str] = Field(..., description="小标题列表")


class AIGeneratedContent(BaseModel):
    """AI 生成的结构化内容"""
    etf_recommendations: List[ETFRecommendation] = Field(default_factory=list, description="ETF 推荐（建议3个）")
    stock_recommendations: List[StockRecommendation] = Field(default_factory=list, description="股票推荐（建议10只）")
    market_sentiment: str = Field(default="", description="市场情绪总结（1-2段话）")
    risk_warning: str = Field(default="", description="风险提示与合规免责声明")
    article_outline: ArticleOutline = Field(default_factory=lambda: ArticleOutline(title="投资方案", sections=[]), description="公众号文章结构")


# ==================== API 响应 Schema ====================

class DailyReportResponse(BaseModel):
    """每日投资方案响应"""
    id: str = Field(..., description="报告ID")
    report_date: str = Field(..., description="报告日期")
    title: str = Field(..., description="报告标题")
    status: str = Field(..., description="状态")
    market_sentiment: str = Field(..., description="市场情绪总结")
    etf_recommendations: List[ETFRecommendation] = Field(..., description="ETF 推荐")
    stock_recommendations: List[StockRecommendation] = Field(..., description="股票推荐")
    risk_warning: str = Field(..., description="风险提示")
    article_title: Optional[str] = Field(default=None, description="公众号文章标题")
    article_outline: Optional[dict] = Field(default=None, description="公众号文章大纲")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    generation_status: str = Field(..., description="生成状态")


class DailyReportListResponse(BaseModel):
    """每日投资方案列表响应"""
    total: int = Field(..., description="总数")
    reports: List[DailyReportResponse] = Field(..., description="报告列表")


class DailyReportSummaryResponse(BaseModel):
    """每日投资方案摘要响应"""
    id: str = Field(..., description="报告ID")
    report_date: str = Field(..., description="报告日期")
    title: str = Field(..., description="报告标题")
    status: str = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")
    generation_status: str = Field(..., description="生成状态")


class GenerateReportRequest(BaseModel):
    """手动触发生成报告请求"""
    report_date: Optional[str] = Field(default=None, description="报告日期，不提供则使用今日")
    force: bool = Field(default=False, description="是否强制重新生成（如果已存在）")
    
    @field_validator("report_date")
    @classmethod
    def validate_report_date(cls, v: Optional[str]) -> Optional[str]:
        """验证报告日期格式"""
        if v is None:
            return v
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("报告日期格式必须为 YYYY-MM-DD")
        return v
