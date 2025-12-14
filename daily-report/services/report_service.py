"""每日投资方案业务编排核心服务"""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from core.logger import get_logger
from db.session import SessionLocal
from models.daily_report import DailyInvestmentReport
from schemas.daily_report import (
    DailyReportResponse,
    DailyReportListResponse,
    DailyReportSummaryResponse,
    MarketDataInput,
    AIGeneratedContent,
)
from services.data_client import DataServiceClient
from services.ai_client import AIHubClient

logger = get_logger(__name__)


class ReportService:
    """每日投资方案服务（编排型）"""
    
    def __init__(self):
        """初始化服务"""
        self.data_client = DataServiceClient()
        self.ai_client = AIHubClient()
    
    async def generate_daily_report(
        self, 
        report_date: Optional[str] = None,
        force: bool = False
    ) -> DailyReportResponse:
        """
        生成每日投资方案（核心编排逻辑）
        
        Args:
            report_date: 报告日期 YYYY-MM-DD，不提供则使用今日
            force: 是否强制重新生成
            
        Returns:
            DailyReportResponse: 生成的报告
        """
        # 确定报告日期
        if report_date is None:
            report_date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"开始生成 {report_date} 的投资方案")
        
        # 检查是否已存在
        db = SessionLocal()
        try:
            existing_report = (
                db.query(DailyInvestmentReport)
                .filter(DailyInvestmentReport.report_date == report_date)
                .first()
            )
            
            if existing_report and not force:
                logger.warning(f"{report_date} 的报告已存在，跳过生成")
                return self._model_to_response(existing_report)
            
            # 更新或创建记录状态为 processing
            if existing_report:
                existing_report.generation_status = "processing"
                existing_report.generation_error = None
                db.commit()
                report_id = existing_report.id
            else:
                new_report = DailyInvestmentReport(
                    report_date=report_date,
                    title=f"{report_date} 投资方案",
                    status="draft",
                    generation_status="processing",
                )
                db.add(new_report)
                db.commit()
                db.refresh(new_report)
                report_id = new_report.id
            
            try:
                # 步骤1: 获取市场数据（来自 data-service）
                logger.info("步骤1: 获取市场数据")
                market_data = await self.data_client.fetch_market_data(report_date)
                
                # 步骤2: 调用 AI 生成内容（调用 ai-hub）
                logger.info("步骤2: 调用 AI 生成内容")
                ai_content = await self.ai_client.generate_investment_report(market_data)
                
                # 步骤3: 保存到数据库
                logger.info("步骤3: 保存到数据库")
                report = db.query(DailyInvestmentReport).filter(
                    DailyInvestmentReport.id == report_id
                ).first()
                
                if report:
                    report.title = ai_content.article_outline.title
                    report.market_sentiment = ai_content.market_sentiment
                    report.etf_recommendations = [
                        item.model_dump() for item in ai_content.etf_recommendations
                    ]
                    report.stock_recommendations = [
                        item.model_dump() for item in ai_content.stock_recommendations
                    ]
                    report.risk_warning = ai_content.risk_warning
                    report.article_title = ai_content.article_outline.title
                    report.article_outline = {
                        "sections": ai_content.article_outline.sections
                    }
                    report.status = "published"
                    report.generation_status = "completed"
                    report.updated_at = datetime.now()
                    
                    db.commit()
                    db.refresh(report)
                    
                    logger.info(f"成功生成 {report_date} 的投资方案: {report_id}")
                    return self._model_to_response(report)
                else:
                    raise Exception("报告记录不存在")
                    
            except Exception as e:
                # 更新错误状态
                report = db.query(DailyInvestmentReport).filter(
                    DailyInvestmentReport.id == report_id
                ).first()
                if report:
                    report.generation_status = "failed"
                    report.generation_error = str(e)
                    db.commit()
                
                logger.error(f"生成报告失败: {e}", exc_info=True)
                raise
                
        finally:
            db.close()
    
    async def get_report(
        self, 
        report_id: str
    ) -> Optional[DailyReportResponse]:
        """
        获取报告详情
        
        Args:
            report_id: 报告ID
            
        Returns:
            Optional[DailyReportResponse]: 报告详情
        """
        db = SessionLocal()
        try:
            report = (
                db.query(DailyInvestmentReport)
                .filter(DailyInvestmentReport.id == report_id)
                .first()
            )
            
            if not report:
                return None
            
            return self._model_to_response(report)
        finally:
            db.close()
    
    async def get_report_by_date(
        self, 
        report_date: str
    ) -> Optional[DailyReportResponse]:
        """
        根据日期获取报告
        
        Args:
            report_date: 报告日期 YYYY-MM-DD
            
        Returns:
            Optional[DailyReportResponse]: 报告详情
        """
        db = SessionLocal()
        try:
            report = (
                db.query(DailyInvestmentReport)
                .filter(DailyInvestmentReport.report_date == report_date)
                .first()
            )
            
            if not report:
                return None
            
            return self._model_to_response(report)
        finally:
            db.close()
    
    async def list_reports(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> DailyReportListResponse:
        """
        列出报告
        
        Args:
            limit: 每页数量
            offset: 偏移量
            status: 状态过滤
            
        Returns:
            DailyReportListResponse: 报告列表
        """
        db = SessionLocal()
        try:
            query = db.query(DailyInvestmentReport)
            
            if status:
                query = query.filter(DailyInvestmentReport.status == status)
            
            # 按日期倒序
            query = query.order_by(desc(DailyInvestmentReport.report_date))
            
            total = query.count()
            reports = query.offset(offset).limit(limit).all()
            
            return DailyReportListResponse(
                total=total,
                reports=[self._model_to_response(r) for r in reports]
            )
        finally:
            db.close()
    
    async def get_latest_report(self) -> Optional[DailyReportResponse]:
        """
        获取最新的报告
        
        Returns:
            Optional[DailyReportResponse]: 最新报告
        """
        db = SessionLocal()
        try:
            report = (
                db.query(DailyInvestmentReport)
                .order_by(desc(DailyInvestmentReport.report_date))
                .first()
            )
            
            if not report:
                return None
            
            return self._model_to_response(report)
        finally:
            db.close()
    
    def _model_to_response(
        self, 
        model: DailyInvestmentReport
    ) -> DailyReportResponse:
        """将数据库模型转换为响应模型"""
        return DailyReportResponse(
            id=str(model.id),
            report_date=model.report_date,
            title=model.title,
            status=model.status,
            market_sentiment=model.market_sentiment or "",
            etf_recommendations=model.etf_recommendations or [],
            stock_recommendations=model.stock_recommendations or [],
            risk_warning=model.risk_warning or "",
            article_title=model.article_title,
            article_outline=model.article_outline,
            created_at=model.created_at,
            updated_at=model.updated_at,
            generation_status=model.generation_status,
        )
