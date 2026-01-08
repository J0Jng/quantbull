"""行业景气度排名模型"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class IndustryRank(SQLModel, table=True):
    """行业景气度排名表 - 存储每月行业景气度评分和排名"""
    __tablename__ = "industry_rank"  # type: ignore
    
    __table_args__ = (
        UniqueConstraint("month", "industry", name="uq_industry_rank_month_industry"),
        Index("idx_industry_rank_month", "month"),
        Index("idx_industry_rank_industry", "industry"),
        Index("idx_industry_rank_rank", "rank"),
    )
    
    id: Optional[int] = Field(default=None, primary_key=True)
    month: str = Field(max_length=7, description="月份 YYYY-MM")
    industry: str = Field(max_length=50, description="行业名称")
    rank: int = Field(description="排名（1为最好）")
    score: float = Field(description="景气度分数（-1到1）")
    avg_netprofit_yoy: Optional[float] = Field(default=None, description="平均净利润同比增长率（%）")
    avg_revenue_yoy: Optional[float] = Field(default=None, description="平均营收同比增长率（%）")
    avg_roe_yoy: Optional[float] = Field(default=None, description="平均ROE同比增长率（%）")
    stock_count: int = Field(default=0, description="该行业股票数量")
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now),
        description="更新时间"
    )
