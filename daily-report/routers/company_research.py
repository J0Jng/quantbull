"""公司研报路由"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.company_research import (
    CompanyResearchGenerateRequest,
    CompanyResearchQueryRequest,
    CompanyResearchReportResponse,
    CompanyResearchListResponse,
)
from services.company_research_service import CompanyResearchService
from core.response import success, error
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/company-research", tags=["公司研报"])


@router.post("/reports/generate", summary="生成公司研报并入库")
async def generate_report(
    request: CompanyResearchGenerateRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    生成公司研报并入库
    
    - company_name: 公司名称（必填）
    - stock_code: 股票代码（可选）
    - rating: 评级（buy/add/hold/reduce/sell，默认 hold）
    - company_info: 公司基本信息（可空，为空时自动构造）
    - report_type: 报告类型（summary/analysis，默认 summary）
    - include_risks: 是否包含风险提示（默认 true）
    - tags: 标签列表（可选）
    - force: 是否强制重新生成（默认 false，为 false 时启用去重）
    """
    try:
        service = CompanyResearchService(db)
        result = await service.generate_report(request)
        return success(data=result.dict(), message="ok")
    
    except Exception as e:
        logger.error(f"生成公司研报失败: {e}", exc_info=True)
        return error(message=f"生成失败: {str(e)}", code=50001)


@router.get("/reports", summary="查询公司研报列表")
async def get_reports(
    limit: int = 20,
    offset: int = 0,
    rating: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    查询公司研报列表
    
    - limit: 每页数量（默认 20）
    - offset: 偏移量（默认 0）
    - rating: 评级筛选（可选）
    - keyword: 关键词搜索（可选：在 company_name、stock_code、tags 中模糊匹配）
    """
    try:
        service = CompanyResearchService(db)
        request = CompanyResearchQueryRequest(
            limit=limit,
            offset=offset,
            rating=rating,
            keyword=keyword,
        )
        result = service.get_reports(request)
        return success(data=result.dict(), message="ok")
    
    except Exception as e:
        logger.error(f"查询公司研报列表失败: {e}", exc_info=True)
        return error(message=f"查询失败: {str(e)}", code=50002)


@router.get("/reports/{report_id}", summary="获取公司研报详情")
async def get_report_by_id(
    report_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """
    根据 ID 获取公司研报详情
    
    - report_id: 研报 ID
    """
    try:
        service = CompanyResearchService(db)
        result = service.get_report_by_id(report_id)
        
        if not result:
            return error(message="研报不存在", code=40401)
        
        return success(data=result.dict(), message="ok")
    
    except Exception as e:
        logger.error(f"获取公司研报详情失败: {e}", exc_info=True)
        return error(message=f"查询失败: {str(e)}", code=50002)
