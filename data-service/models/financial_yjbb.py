"""业绩报表（年报季报）数据模型"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class FinancialReportYjbb(SQLModel, table=True):
    __tablename__ = "financial_report_yjbb"  # type: ignore

    __table_args__ = (
        UniqueConstraint("period", "code", "notice_date", name="uq_fin_yjbb_period_code_notice"),
        Index("idx_fin_yjbb_period_code", "period", "code"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    period: str = Field(max_length=10, description="报告期 YYYYMM")

    code: str = Field(max_length=10, description="股票代码")
    name: str = Field(max_length=100, description="股票名称")

    eps: Optional[float] = Field(default=None, description="每股收益")
    revenue: Optional[float] = Field(default=None, description="营业总收入")
    revenue_yoy: Optional[float] = Field(default=None, description="营业总收入同比")
    net_profit: Optional[float] = Field(default=None, description="净利润")
    net_profit_yoy: Optional[float] = Field(default=None, description="净利润同比")
    roe: Optional[float] = Field(default=None, description="净资产收益率 ROE")
    bps: Optional[float] = Field(default=None, description="每股净资产")
    cashflow_ps: Optional[float] = Field(default=None, description="每股经营现金流")

    industry: Optional[str] = Field(default=None, max_length=100, description="行业")

    notice_date: Optional[str] = Field(default=None, max_length=20, description="公告/披露日期")
    update_date: Optional[str] = Field(default=None, max_length=20, description="更新时间")

    source_url: Optional[str] = Field(default=None, max_length=300, description="来源 URL")
    as_of: Optional[datetime] = Field(default=None, sa_column=Column(DateTime), description="抓取时间")

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now),
        description="创建时间",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now),
        description="更新时间",
    )
