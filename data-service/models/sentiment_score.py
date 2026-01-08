"""情绪分数数据模型"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class SentimentScore(SQLModel, table=True):
    """情绪分数表"""
    __tablename__ = "sentiment_score"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, description="股票代码")
    trade_date: str = Field(index=True, description="交易日期 YYYYMMDD")
    sentiment_score: float = Field(default=0.0, description="情绪分数 [-1, 1]")
    discussion_volume: int = Field(default=0, description="讨论量")
    hot_rank: int = Field(default=0, description="热度排名")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "000001",
                "trade_date": "20260107",
                "sentiment_score": 0.65,
                "discussion_volume": 12345,
                "hot_rank": 25
            }
        }
