"""每日投资方案业务编排核心服务"""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid

from core.logger import get_logger
from core.access_control import get_china_today
from db.session import SessionLocal
from models.daily_report import DailyInvestmentReport
from schemas.daily_report import (
    DailyReportResponse,
    DailyReportListResponse,
    DailyReportSummaryResponse,
    MarketDataInput,
    AIGeneratedContent,
)
from schemas.report import (
    ReportCreateRequest,
    ReportUpdateRequest,
    ReportResponse,
    ReportListResponse,
    ReportSummaryResponse,
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
    ) -> Optional[ReportResponse]:
        """
        获取报告详情（通用格式）
        
        Args:
            report_id: 报告ID
            
        Returns:
            Optional[ReportResponse]: 报告详情
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
            
            return self._model_to_report_response(report)
        finally:
            db.close()
    
    async def get_daily_report(
        self, 
        report_id: str
    ) -> Optional[DailyReportResponse]:
        """
        获取报告详情（投资方案格式）
        
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
    
    async def list_daily_reports(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
        exclude_today: bool = False,
    ) -> DailyReportListResponse:
        """
        列出投资方案报告
        
        Args:
            limit: 每页数量
            offset: 偏移量
            status: 状态过滤
            exclude_today: 是否排除今天的报告
            
        Returns:
            DailyReportListResponse: 投资方案报告列表
        """
        db = SessionLocal()
        try:
            query = db.query(DailyInvestmentReport)
            
            if status:
                query = query.filter(DailyInvestmentReport.status == status)
            
            # 如果需要排除今天，添加过滤条件
            if exclude_today:
                today = get_china_today()
                query = query.filter(DailyInvestmentReport.report_date < today)
            
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
    
    async def get_latest_report(self, exclude_today: bool = False) -> Optional[DailyReportResponse]:
        """
        获取最新的报告
        
        Args:
            exclude_today: 是否排除今天的报告
            
        Returns:
            Optional[DailyReportResponse]: 最新报告
        """
        db = SessionLocal()
        try:
            query = db.query(DailyInvestmentReport)
            
            # 如果需要排除今天，添加过滤条件
            if exclude_today:
                today = get_china_today()
                query = query.filter(DailyInvestmentReport.report_date < today)
            
            report = (
                query
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
    
    def _model_to_report_response(
        self, 
        model: DailyInvestmentReport
    ) -> ReportResponse:
        """将数据库模型转换为通用报告响应模型"""
        # 将投资方案的字段映射到通用报告格式
        content = f"""市场情绪：{model.market_sentiment or ''}

ETF推荐：
{self._format_recommendations(model.etf_recommendations or [])}

股票推荐：
{self._format_recommendations(model.stock_recommendations or [])}

风险提示：
{model.risk_warning or ''}
"""
        return ReportResponse(
            id=str(model.id),
            title=model.title,
            content=content,
            report_date=model.report_date,
            report_type="daily",
            status=model.status,
            author="系统",
            tags=[],
            created_at=model.created_at.isoformat() if model.created_at else "",
            updated_at=model.updated_at.isoformat() if model.updated_at else None,
        )
    
    def _format_recommendations(self, recommendations: list) -> str:
        """格式化推荐列表"""
        if not recommendations:
            return "暂无推荐"
        result = []
        for i, rec in enumerate(recommendations, 1):
            if isinstance(rec, dict):
                symbol = rec.get("symbol", rec.get("code", ""))
                name = rec.get("name", "")
                reason = rec.get("reason", rec.get("recommendation_reason", ""))
                result.append(f"{i}. {symbol} {name}: {reason}")
        return "\n".join(result) if result else "暂无推荐"
    
    async def create_report(
        self, 
        request: ReportCreateRequest
    ) -> ReportResponse:
        """
        创建新的报告（手动创建）
        
        Args:
            request: 报告创建请求
            
        Returns:
            ReportResponse: 创建的报告
        """
        db = SessionLocal()
        try:
            # 检查是否已存在相同日期的报告
            existing = db.query(DailyInvestmentReport).filter(
                DailyInvestmentReport.report_date == request.report_date
            ).first()
            
            if existing:
                logger.warning(f"报告日期 {request.report_date} 已存在")
                raise ValueError(f"报告日期 {request.report_date} 已存在")
            
            # 创建新报告
            new_report = DailyInvestmentReport(
                id=str(uuid.uuid4()),
                report_date=request.report_date,
                title=request.title,
                status="draft",
                market_sentiment=request.content,  # 将content存储为market_sentiment
                etf_recommendations=[],
                stock_recommendations=[],
                risk_warning="",
                article_title=request.title,
                article_outline={},
                generation_status="manual",  # 标记为手动创建
            )
            
            db.add(new_report)
            db.commit()
            db.refresh(new_report)
            
            logger.info(f"成功创建报告: {new_report.id}")
            return self._model_to_report_response(new_report)
            
        except Exception as e:
            db.rollback()
            logger.error(f"创建报告失败: {e}", exc_info=True)
            raise
        finally:
            db.close()
    
    async def update_report(
        self, 
        report_id: str,
        request: ReportUpdateRequest
    ) -> Optional[ReportResponse]:
        """
        更新报告
        
        Args:
            report_id: 报告ID
            request: 更新请求
            
        Returns:
            Optional[ReportResponse]: 更新后的报告
        """
        db = SessionLocal()
        try:
            report = db.query(DailyInvestmentReport).filter(
                DailyInvestmentReport.id == report_id
            ).first()
            
            if not report:
                return None
            
            # 更新字段
            if request.title is not None:
                report.title = request.title
                report.article_title = request.title
            if request.content is not None:
                report.market_sentiment = request.content
            if request.report_date is not None:
                report.report_date = request.report_date
            if request.status is not None:
                report.status = request.status
            
            report.updated_at = datetime.now()
            
            db.commit()
            db.refresh(report)
            
            logger.info(f"成功更新报告: {report_id}")
            return self._model_to_report_response(report)
            
        except Exception as e:
            db.rollback()
            logger.error(f"更新报告失败: {e}", exc_info=True)
            raise
        finally:
            db.close()
    
    async def delete_report(
        self, 
        report_id: str
    ) -> bool:
        """
        删除报告
        
        Args:
            report_id: 报告ID
            
        Returns:
            bool: 是否删除成功
        """
        db = SessionLocal()
        try:
            report = db.query(DailyInvestmentReport).filter(
                DailyInvestmentReport.id == report_id
            ).first()
            
            if not report:
                return False
            
            db.delete(report)
            db.commit()
            
            logger.info(f"成功删除报告: {report_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"删除报告失败: {e}", exc_info=True)
            raise
        finally:
            db.close()
    
    async def list_reports(
        self,
        report_type: Optional[str] = None,
        status: Optional[str] = None,
        report_date: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ReportListResponse:
        """
        列出报告
        
        Args:
            report_type: 报告类型过滤（暂不使用）
            status: 状态过滤
            report_date: 日期过滤
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            ReportListResponse: 报告列表响应
        """
        db = SessionLocal()
        try:
            query = db.query(DailyInvestmentReport)
            
            if status:
                query = query.filter(DailyInvestmentReport.status == status)
            if report_date:
                query = query.filter(DailyInvestmentReport.report_date == report_date)
            
            # 获取总数
            total = query.count()
            
            # 按日期倒序
            query = query.order_by(desc(DailyInvestmentReport.report_date))
            
            reports = query.offset(offset).limit(limit).all()
            
            return ReportListResponse(
                total=total,
                reports=[self._model_to_report_response(r) for r in reports]
            )
        finally:
            db.close()
    
    async def get_report_summaries(
        self,
        report_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[ReportSummaryResponse]:
        """
        获取报告摘要列表
        
        Args:
            report_type: 报告类型过滤（暂不使用）
            status: 状态过滤
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            List[ReportSummaryResponse]: 报告摘要列表
        """
        db = SessionLocal()
        try:
            query = db.query(DailyInvestmentReport)
            
            if status:
                query = query.filter(DailyInvestmentReport.status == status)
            
            query = query.order_by(desc(DailyInvestmentReport.report_date))
            reports = query.offset(offset).limit(limit).all()
            
            return [
                ReportSummaryResponse(
                    id=str(r.id),
                    title=r.title,
                    report_date=r.report_date,
                    report_type="daily",
                    status=r.status,
                    author="系统",
                    tags=[],
                    created_at=r.created_at.isoformat() if r.created_at else "",
                )
                for r in reports
            ]
        finally:
            db.close()
    
    async def publish_report(
        self, 
        report_id: str
    ) -> Optional[ReportResponse]:
        """
        发布报告
        
        Args:
            report_id: 报告ID
            
        Returns:
            Optional[ReportResponse]: 发布后的报告
        """
        db = SessionLocal()
        try:
            report = db.query(DailyInvestmentReport).filter(
                DailyInvestmentReport.id == report_id
            ).first()
            
            if not report:
                return None
            
            report.status = "published"
            report.updated_at = datetime.now()
            
            db.commit()
            db.refresh(report)
            
            logger.info(f"成功发布报告: {report_id}")
            return self._model_to_report_response(report)
            
        except Exception as e:
            db.rollback()
            logger.error(f"发布报告失败: {e}", exc_info=True)
            raise
        finally:
            db.close()
    
    async def archive_report(
        self, 
        report_id: str
    ) -> Optional[ReportResponse]:
        """
        归档报告
        
        Args:
            report_id: 报告ID
            
        Returns:
            Optional[ReportResponse]: 归档后的报告
        """
        db = SessionLocal()
        try:
            report = db.query(DailyInvestmentReport).filter(
                DailyInvestmentReport.id == report_id
            ).first()
            
            if not report:
                return None
            
            report.status = "archived"
            report.updated_at = datetime.now()
            
            db.commit()
            db.refresh(report)
            
            logger.info(f"成功归档报告: {report_id}")
            return self._model_to_report_response(report)
            
        except Exception as e:
            db.rollback()
            logger.error(f"归档报告失败: {e}", exc_info=True)
            raise
        finally:
            db.close()

