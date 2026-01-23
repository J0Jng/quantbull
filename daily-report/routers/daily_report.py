"""每日投资方案路由"""
from typing import Optional
from fastapi import APIRouter, HTTPException

from core.logger import get_logger
from core.access_control import (
    can_access_today_report,
    get_china_today,
    get_access_denied_message,
)
from schemas.daily_report import (
    DailyReportResponse,
    DailyReportListResponse,
    GenerateReportRequest,
)
from services.report_service import ReportService

logger = get_logger(__name__)
router = APIRouter()

# 初始化服务
report_service = ReportService()


@router.post(
    "/generate",
    response_model=DailyReportResponse,
    summary="手动触发生成每日投资方案"
)
async def generate_report(request: GenerateReportRequest) -> DailyReportResponse:
    """
    手动触发生成每日投资方案
    
    - 如果不提供 report_date，则使用今日日期
    - 如果 force=True，即使已存在也会重新生成
    - 当天报告需在 16:00 后才能生成
    """
    try:
        # 门禁检查：如果要生成今天的报告，需要在16:00之后
        target_date = request.report_date or get_china_today()
        if target_date == get_china_today() and not can_access_today_report():
            raise HTTPException(
                status_code=403,
                detail=get_access_denied_message()
            )
        
        report = await report_service.generate_daily_report(
            report_date=request.report_date,
            force=request.force
        )
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成报告失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")


@router.get(
    "/latest",
    response_model=DailyReportResponse,
    summary="获取最新的投资方案"
)
async def get_latest_report() -> DailyReportResponse:
    """
    获取最新的投资方案
    
    - 16:00 前不返回当天报告，返回最近的历史报告
    """
    try:
        # 门禁检查：16:00前不允许返回今天的报告
        exclude_today = not can_access_today_report()
        report = await report_service.get_latest_report(exclude_today=exclude_today)
        if not report:
            if exclude_today:
                raise HTTPException(
                    status_code=404,
                    detail="暂无历史投资方案，今日方案需在 16:00 后查看"
                )
            else:
                raise HTTPException(status_code=404, detail="暂无投资方案")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取最新报告失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取最新报告失败: {str(e)}")


@router.get(
    "/date/{report_date}",
    response_model=DailyReportResponse,
    summary="根据日期获取投资方案"
)
async def get_report_by_date(report_date: str) -> DailyReportResponse:
    """
    根据日期获取投资方案
    
    - report_date: 日期格式 YYYY-MM-DD
    - 当天报告需在 16:00 后才能查看
    """
    try:
        # 门禁检查：如果请求今天的报告，需要在16:00之后
        if report_date == get_china_today() and not can_access_today_report():
            raise HTTPException(
                status_code=403,
                detail=get_access_denied_message()
            )
        
        report = await report_service.get_report_by_date(report_date)
        if not report:
            raise HTTPException(status_code=404, detail=f"{report_date} 的投资方案不存在")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取报告失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取报告失败: {str(e)}")


@router.get(
    "/{report_id}",
    response_model=DailyReportResponse,
    summary="根据ID获取投资方案"
)
async def get_report(report_id: str) -> DailyReportResponse:
    """根据ID获取投资方案详情"""
    try:
        report = await report_service.get_daily_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="投资方案不存在")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取报告失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取报告失败: {str(e)}")


@router.get(
    "",
    response_model=DailyReportListResponse,
    summary="列出所有投资方案"
)
async def list_reports(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
) -> DailyReportListResponse:
    """
    列出所有投资方案
    
    - 支持分页（limit, offset）
    - 支持按状态过滤（status: draft/published/archived）
    - 16:00 前不返回当天报告
    """
    try:
        # 门禁检查：16:00前过滤掉今天的报告
        exclude_today = not can_access_today_report()
        return await report_service.list_daily_reports(
            limit=limit,
            offset=offset,
            status=status,
            exclude_today=exclude_today
        )
    except Exception as e:
        logger.error(f"列出报告失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出报告失败: {str(e)}")
