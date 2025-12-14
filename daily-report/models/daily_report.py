"""每日投资方案数据库模型"""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import Column, String, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from db.session import Base
from core.config import settings


# 根据数据库类型选择 ID 类型
if settings.db_type == "postgresql":
    IDType = PostgresUUID(as_uuid=False)
else:
    # SQLite 不支持 UUID 类型，使用 String
    IDType = String(36)


class DailyInvestmentReport(Base):
    """每日投资方案表"""
    __tablename__ = "daily_investment_reports"

    # 主键（兼容 PostgreSQL 和 SQLite）
    id = Column(IDType, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 报告基本信息
    report_date = Column(String(10), nullable=False, unique=True, index=True, comment="报告日期 YYYY-MM-DD")
    title = Column(String(200), nullable=False, comment="报告标题")
    status = Column(String(20), default="draft", comment="状态: draft/published/archived")
    
    # 市场情绪总结
    market_sentiment = Column(Text, comment="市场情绪总结")
    
    # ETF 推荐（JSON 格式存储）
    etf_recommendations = Column(JSON, comment="ETF 推荐列表，包含3个ETF")
    
    # 股票推荐（JSON 格式存储）
    stock_recommendations = Column(JSON, comment="股票推荐列表，包含10只股票")
    
    # 风险提示
    risk_warning = Column(Text, comment="风险提示与合规免责声明")
    
    # 公众号文章结构
    article_title = Column(String(200), comment="公众号文章标题")
    article_outline = Column(JSON, comment="公众号文章小标题大纲")
    
    # 元数据
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 生成信息
    generation_status = Column(String(20), default="pending", comment="生成状态: pending/processing/completed/failed")
    generation_error = Column(Text, nullable=True, comment="生成错误信息")
    
    def __repr__(self):
        return f"<DailyInvestmentReport(id={self.id}, report_date={self.report_date}, status={self.status})>"
