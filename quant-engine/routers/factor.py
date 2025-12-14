from typing import Optional

from fastapi import APIRouter, HTTPException

from core.logger import get_logger
from schemas.factor import (
    FactorCreateRequest,
    FactorUpdateRequest,
    FactorResponse,
    FactorListResponse,
    FactorCalculateRequest,
    FactorCalculateResponse,
)
from services.factor_service import FactorService

logger = get_logger(__name__)
router = APIRouter()

# 初始化服务
factor_service = FactorService()


@router.post("", response_model=FactorResponse, summary="创建因子")
async def create_factor(request: FactorCreateRequest) -> FactorResponse:
    """
    创建新的量化因子
    
    因子类别：
    - technical: 技术指标
    - fundamental: 基本面因子
    - macro: 宏观因子
    """
    try:
        return await factor_service.create_factor(request)
    except Exception as e:
        logger.error(f"创建因子失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建因子失败: {str(e)}")


@router.get("/{factor_id}", response_model=FactorResponse, summary="获取因子")
async def get_factor(factor_id: str) -> FactorResponse:
    """
    获取指定因子的详细信息
    """
    try:
        factor = await factor_service.get_factor(factor_id)
        if not factor:
            raise HTTPException(status_code=404, detail="因子不存在")
        return factor
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取因子失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取因子失败: {str(e)}")


@router.put("/{factor_id}", response_model=FactorResponse, summary="更新因子")
async def update_factor(
    factor_id: str,
    request: FactorUpdateRequest
) -> FactorResponse:
    """
    更新因子信息
    """
    try:
        factor = await factor_service.update_factor(factor_id, request)
        if not factor:
            raise HTTPException(status_code=404, detail="因子不存在")
        return factor
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新因子失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新因子失败: {str(e)}")


@router.delete("/{factor_id}", summary="删除因子")
async def delete_factor(factor_id: str) -> dict:
    """
    删除因子
    """
    try:
        success = await factor_service.delete_factor(factor_id)
        if not success:
            raise HTTPException(status_code=404, detail="因子不存在")
        return {"message": "因子已删除", "factor_id": factor_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除因子失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除因子失败: {str(e)}")


@router.get("", response_model=FactorListResponse, summary="列出因子")
async def list_factors(
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> FactorListResponse:
    """
    列出所有因子
    
    支持按类别过滤和分页
    """
    try:
        factors = await factor_service.list_factors(
            category=category,
            limit=limit,
            offset=offset
        )
        return FactorListResponse(
            total=len(factors),
            factors=factors
        )
    except Exception as e:
        logger.error(f"列出因子失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出因子失败: {str(e)}")


@router.post("/calculate", response_model=FactorCalculateResponse, summary="计算因子值")
async def calculate_factor(request: FactorCalculateRequest) -> FactorCalculateResponse:
    """
    计算指定因子在给定时间范围内的值
    
    返回时间序列数据，可用于策略分析和可视化
    """
    try:
        return await factor_service.calculate_factor(request)
    except ValueError as e:
        logger.error(f"计算因子参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"计算因子失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"计算因子失败: {str(e)}")
