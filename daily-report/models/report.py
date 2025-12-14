from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DailyReport(BaseModel):
    """日报模型"""
    id: Optional[str] = Field(default=None, description="日报ID")
    title: str = Field(..., description="日报标题", min_length=1)
    content: str = Field(..., description="日报内容")
    report_date: str = Field(..., description="报告日期 (YYYY-MM-DD)")
    report_type: str = Field(default="daily", description="报告类型：daily/weekly/monthly")
    status: str = Field(default="draft", description="状态：draft/published/archived")
    author: Optional[str] = Field(default=None, description="作者")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    created_at: Optional[datetime] = Field(default=None, description="创建时间")
    updated_at: Optional[datetime] = Field(default=None, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "2024年1月1日市场日报",
                "content": "今日市场表现...",
                "report_date": "2024-01-01",
                "report_type": "daily",
                "author": "系统",
                "tags": ["市场分析", "技术指标"]
            }
        }
