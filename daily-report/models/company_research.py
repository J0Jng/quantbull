"""公司研报数据库模型"""
from datetime import datetime
from typing import Optional
import uuid
import hashlib

from sqlalchemy import Column, String, Text, JSON, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID

from db.session import Base
from core.config import settings


# 根据数据库类型选择 ID 类型
if settings.db_type == "postgresql":
    IDType = PostgresUUID(as_uuid=False)
else:
    # SQLite 不支持 UUID 类型，使用 String
    IDType = String(36)


class CompanyResearchReport(Base):
    """公司研报表"""
    __tablename__ = "company_research_reports"

    # 主键（兼容 PostgreSQL 和 SQLite）
    id = Column(IDType, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 公司基本信息
    company_name = Column(String(200), nullable=False, index=True, comment="公司名称")
    stock_code = Column(String(20), nullable=True, index=True, comment="股票代码")
    
    # 研报评级和类型
    rating = Column(String(20), nullable=False, default="hold", comment="评级: buy/add/hold/reduce/sell")
    report_type = Column(String(20), nullable=False, default="summary", comment="报告类型: summary/analysis")
    
    # 研报内容
    company_info = Column(Text, nullable=True, comment="公司基本信息（用户输入或自动构造）")
    report_content = Column(Text, nullable=False, comment="AI 生成的研报正文（markdown）")
    
    # 元数据
    tags = Column(JSON, nullable=True, comment="标签数组")
    include_risks = Column(Boolean, default=True, comment="是否包含风险提示")
    
    # AI 生成信息
    model = Column(String(50), nullable=True, comment="使用的模型名称")
    tokens_used = Column(JSON, nullable=True, comment="token 使用情况")
    sections = Column(JSON, nullable=True, comment="研报章节结构")
    
    # 去重字段
    content_hash = Column(String(64), nullable=False, index=True, comment="内容哈希（用于去重）")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    @staticmethod
    def compute_content_hash(
        company_name: str,
        stock_code: Optional[str],
        rating: str,
        report_type: str,
        company_info: Optional[str],
        include_risks: bool,
        tags: Optional[list]
    ) -> str:
        """
        计算内容哈希（用于去重）
        
        Args:
            company_name: 公司名称
            stock_code: 股票代码
            rating: 评级
            report_type: 报告类型
            company_info: 公司信息
            include_risks: 是否包含风险
            tags: 标签
            
        Returns:
            str: SHA256 哈希值
        """
        # 构造哈希输入（包含所有影响生成结果的字段）
        hash_input = f"{company_name}|{stock_code or ''}|{rating}|{report_type}|{company_info or ''}|{include_risks}|{','.join(sorted(tags or []))}"
        return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
