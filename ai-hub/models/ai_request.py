from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    """AI 请求记录模型"""
    id: Optional[str] = None
    task_type: str = Field(..., description="任务类型")
    model: str = Field(..., description="使用的模型")
    request_content: str = Field(..., description="请求内容")
    response_content: Optional[str] = Field(default=None, description="响应内容")
    tokens_used: Optional[int] = Field(default=None, description="使用的token数")
    status: str = Field(default="pending", description="状态：pending/success/failed")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")
    duration_ms: Optional[int] = Field(default=None, description="耗时（毫秒）")
