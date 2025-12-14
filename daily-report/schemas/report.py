from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ReportCreateRequest(BaseModel):
    """创建日报请求"""
    title: str = Field(..., description="日报标题", min_length=1, max_length=200)
    content: str = Field(..., description="日报内容", min_length=1)
    report_date: str = Field(..., description="报告日期 (YYYY-MM-DD)")
    report_type: str = Field(default="daily", description="报告类型：daily/weekly/monthly")
    author: Optional[str] = Field(default=None, description="作者", max_length=100)
    tags: list[str] = Field(default_factory=list, description="标签列表")
    
    @field_validator("report_date")
    @classmethod
    def validate_report_date(cls, v: str) -> str:
        """验证报告日期格式"""
        try:
            from datetime import datetime
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("报告日期格式必须为 YYYY-MM-DD")
        return v
    
    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: str) -> str:
        """验证报告类型"""
        if v not in ["daily", "weekly", "monthly"]:
            raise ValueError("报告类型必须是 daily、weekly 或 monthly")
        return v


class ReportUpdateRequest(BaseModel):
    """更新日报请求"""
    title: Optional[str] = Field(default=None, description="日报标题", min_length=1, max_length=200)
    content: Optional[str] = Field(default=None, description="日报内容", min_length=1)
    report_date: Optional[str] = Field(default=None, description="报告日期 (YYYY-MM-DD)")
    report_type: Optional[str] = Field(default=None, description="报告类型：daily/weekly/monthly")
    status: Optional[str] = Field(default=None, description="状态：draft/published/archived")
    author: Optional[str] = Field(default=None, description="作者", max_length=100)
    tags: Optional[list[str]] = Field(default=None, description="标签列表")
    
    @field_validator("report_date")
    @classmethod
    def validate_report_date(cls, v: Optional[str]) -> Optional[str]:
        """验证报告日期格式"""
        if v is None:
            return v
        try:
            from datetime import datetime
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("报告日期格式必须为 YYYY-MM-DD")
        return v
    
    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, v: Optional[str]) -> Optional[str]:
        """验证报告类型"""
        if v is not None and v not in ["daily", "weekly", "monthly"]:
            raise ValueError("报告类型必须是 daily、weekly 或 monthly")
        return v
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """验证状态"""
        if v is not None and v not in ["draft", "published", "archived"]:
            raise ValueError("状态必须是 draft、published 或 archived")
        return v


class ReportResponse(BaseModel):
    """日报响应"""
    id: str = Field(..., description="日报ID")
    title: str = Field(..., description="日报标题")
    content: str = Field(..., description="日报内容")
    report_date: str = Field(..., description="报告日期")
    report_type: str = Field(..., description="报告类型")
    status: str = Field(..., description="状态")
    author: Optional[str] = Field(default=None, description="作者")
    tags: list[str] = Field(..., description="标签列表")
    created_at: str = Field(..., description="创建时间")
    updated_at: Optional[str] = Field(default=None, description="更新时间")


class ReportListResponse(BaseModel):
    """日报列表响应"""
    total: int = Field(..., description="总数")
    reports: list[ReportResponse] = Field(..., description="日报列表")


class ReportSummaryResponse(BaseModel):
    """日报摘要响应"""
    id: str = Field(..., description="日报ID")
    title: str = Field(..., description="日报标题")
    report_date: str = Field(..., description="报告日期")
    report_type: str = Field(..., description="报告类型")
    status: str = Field(..., description="状态")
    author: Optional[str] = Field(default=None, description="作者")
    tags: list[str] = Field(..., description="标签列表")
    created_at: str = Field(..., description="创建时间")
