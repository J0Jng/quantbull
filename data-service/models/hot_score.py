"""热点分数数据模型"""
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class HotScore(SQLModel, table=True):
    """热点分数表"""
    __tablename__ = "hot_score"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, description="股票代码")
    trade_date: str = Field(index=True, description="交易日期 YYYYMMDD")
    hot_score: float = Field(default=0.0, description="热点分数 [0, 1]")
    concept_score: float = Field(default=0.0, description="概念强度分数")
    limit_score: float = Field(default=0.0, description="涨停/连板分数")
    up_stat: int = Field(default=0, description="连板天数")
    concept_tags: str = Field(default="", description="概念标签(逗号分隔)")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "000001",
                "trade_date": "20260107",
                "hot_score": 0.75,
                "concept_score": 0.5,
                "limit_score": 0.8,
                "up_stat": 3,
                "concept_tags": "芯片,人工智能,5G"
            }
        }
