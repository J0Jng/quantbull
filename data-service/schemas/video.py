"""
视频中心 API 数据模式
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class VideoItem(BaseModel):
    """视频条目"""
    id: int = Field(..., description="视频 ID")
    title: str = Field(..., description="标题")
    description: Optional[str] = Field(None, description="简介")
    url: str = Field(..., description="视频访问 URL")
    cover_url: Optional[str] = Field(None, description="封面图 URL")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class VideoListResponse(BaseModel):
    """视频列表响应"""
    items: List[VideoItem] = Field(..., description="视频列表")
