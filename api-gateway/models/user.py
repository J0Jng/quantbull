from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """用户模型"""
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True
