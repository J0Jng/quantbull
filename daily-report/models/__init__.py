"""模型导入

确保所有模型都被导入，这样 SQLAlchemy 才能在 Base.metadata.create_all() 时创建表
"""
from .company_research import CompanyResearchReport
from .daily_report import DailyInvestmentReport

__all__ = ["CompanyResearchReport", "DailyInvestmentReport"]
