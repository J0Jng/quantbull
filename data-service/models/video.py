"""
视频中心数据模型
"""
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column, DateTime


class Video(SQLModel, table=True):
    """视频表 - 存储视频元数据与文件路径"""
    __tablename__ = "videos"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True, description="自增主键")
    title: str = Field(max_length=200, description="视频标题")
    description: Optional[str] = Field(default=None, description="视频简介")

    url: str = Field(max_length=500, description="视频访问 URL")
    cover_url: Optional[str] = Field(default=None, max_length=500, description="封面图 URL")

    file_path: str = Field(max_length=500, description="视频文件路径")
    cover_path: Optional[str] = Field(default=None, max_length=500, description="封面图文件路径")

    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, nullable=False),
        description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False),
        description="更新时间"
    )
