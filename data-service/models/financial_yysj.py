"""预约披露时间表数据模型"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import SQLModel, Field, Column, DateTime


class FinancialReportYysj(SQLModel, table=True):
    __tablename__ = "financial_report_yysj"  # type: ignore

    __table_args__ = (
        UniqueConstraint("period", "code", name="uq_fin_yysj_period_code"),
        Index("idx_fin_yysj_period_code", "period", "code"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    period: str = Field(max_length=10, description="报告期 YYYYMM")

    code: str = Field(max_length=10, description="股票代码")
    name: str = Field(max_length=100, description="股票名称")

    first_appoint_date: Optional[str] = Field(default=None, max_length=20, description="首次预约披露日期")
    change_1_date: Optional[str] = Field(default=None, max_length=20, description="一次变更日期")
    change_2_date: Optional[str] = Field(default=None, max_length=20, description="二次变更日期")
    change_3_date: Optional[str] = Field(default=None, max_length=20, description="三次变更日期")
    actual_date: Optional[str] = Field(default=None, max_length=20, description="实际披露日期")

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
