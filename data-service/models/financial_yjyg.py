"""业绩预告数据模型"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class FinancialReportYjyg(SQLModel, table=True):
    __tablename__ = "financial_report_yjyg"  # type: ignore

    __table_args__ = (
        UniqueConstraint(
            "period",
            "code",
            "forecast_indicator",
            "forecast_type",
            "notice_date",
            name="uq_fin_yjyg_period_code_indicator_type_notice",
        ),
        Index("idx_fin_yjyg_period_code", "period", "code"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    period: str = Field(max_length=10, description="报告期 YYYYMM")

    code: str = Field(max_length=10, description="股票代码")
    name: str = Field(max_length=100, description="股票名称")

    forecast_indicator: Optional[str] = Field(default=None, max_length=100, description="预告指标")
    forecast_value_range: Optional[str] = Field(default=None, max_length=100, description="预告数值区间")
    yoy_range: Optional[str] = Field(default=None, max_length=100, description="同比区间")
    forecast_type: Optional[str] = Field(default=None, max_length=50, description="预告类型")
    last_year_value: Optional[str] = Field(default=None, max_length=100, description="上年同期值")
    brief_reason: Optional[str] = Field(default=None, max_length=500, description="预告原因摘要")

    notice_date: Optional[str] = Field(default=None, max_length=20, description="公告/披露日期")

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
