from typing import Optional

from fastapi import APIRouter, HTTPException

from core.logger import get_logger
from schemas.report import (
    ReportCreateRequest,
    ReportUpdateRequest,
    ReportResponse,
    ReportListResponse,
    ReportSummaryResponse,
)
from services.report_service import ReportService

logger = get_logger(__name__)
router = APIRouter()

# 初始化服务
report_service = ReportService()


@router.post("", response_model=ReportResponse, summary="创建日报")
async def create_report(request: ReportCreateRequest) -> ReportResponse:
    """
    创建新的日报
    
    支持创建日报、周报、月报
    """
    try:
        return await report_service.create_report(request)
    except Exception as e:
        logger.error(f"创建日报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建日报失败: {str(e)}")


@router.get("/{report_id}", response_model=ReportResponse, summary="获取日报")
async def get_report(report_id: str) -> ReportResponse:
    """
    获取指定日报的详细信息
    """
    try:
        report = await report_service.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="日报不存在")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取日报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取日报失败: {str(e)}")


@router.put("/{report_id}", response_model=ReportResponse, summary="更新日报")
async def update_report(
    report_id: str,
    request: ReportUpdateRequest
) -> ReportResponse:
    """
    更新日报信息
    """
    try:
        report = await report_service.update_report(report_id, request)
        if not report:
            raise HTTPException(status_code=404, detail="日报不存在")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新日报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新日报失败: {str(e)}")


@router.delete("/{report_id}", summary="删除日报")
async def delete_report(report_id: str) -> dict:
    """
    删除日报
    """
    try:
        success = await report_service.delete_report(report_id)
        if not success:
            raise HTTPException(status_code=404, detail="日报不存在")
        return {"message": "日报已删除", "report_id": report_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除日报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除日报失败: {str(e)}")


@router.get("", response_model=ReportListResponse, summary="列出日报")
async def list_reports(
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    report_date: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> ReportListResponse:
    """
    列出所有日报
    
    支持按类型、状态、日期过滤和分页
    """
    try:
        return await report_service.list_reports(
            report_type=report_type,
            status=status,
            report_date=report_date,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"列出日报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出日报失败: {str(e)}")


@router.get("/summaries/list", response_model=list[ReportSummaryResponse], summary="获取日报摘要列表")
async def get_report_summaries(
    report_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> list[ReportSummaryResponse]:
    """
    获取日报摘要列表（不包含完整内容）
    
    适用于列表展示场景，性能更优
    """
    try:
        return await report_service.get_report_summaries(
            report_type=report_type,
            status=status,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"获取日报摘要失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取日报摘要失败: {str(e)}")


@router.post("/{report_id}/publish", response_model=ReportResponse, summary="发布日报")
async def publish_report(report_id: str) -> ReportResponse:
    """
    发布日报
    
    将状态从 draft 改为 published
    """
    try:
        report = await report_service.publish_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="日报不存在")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发布日报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"发布日报失败: {str(e)}")


@router.post("/{report_id}/archive", response_model=ReportResponse, summary="归档日报")
async def archive_report(report_id: str) -> ReportResponse:
    """
    归档日报
    
    将状态改为 archived
    """
    try:
        report = await report_service.archive_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="日报不存在")
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"归档日报失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"归档日报失败: {str(e)}")
