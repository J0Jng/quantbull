from fastapi import APIRouter

from . import report, daily_report, company_research

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(report.router, prefix="/report", tags=["日报"])
api_router.include_router(daily_report.router, prefix="/daily-report", tags=["每日投资方案"])
api_router.include_router(company_research.router, tags=["公司研报"])
