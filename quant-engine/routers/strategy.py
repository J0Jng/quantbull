from typing import Optional

from fastapi import APIRouter, HTTPException

from core.logger import get_logger
from schemas.strategy import (
    StrategyCreateRequest,
    StrategyUpdateRequest,
    StrategyResponse,
    StrategyListResponse,
    StrategyValidateRequest,
    StrategyValidateResponse,
)
from services.strategy_service import StrategyService

logger = get_logger(__name__)
router = APIRouter()

# 初始化服务
strategy_service = StrategyService()


@router.post("", response_model=StrategyResponse, summary="创建策略")
async def create_strategy(request: StrategyCreateRequest) -> StrategyResponse:
    """
    创建新的量化策略
    
    策略代码应为 Python 代码，通常继承 backtrader.Strategy
    """
    try:
        return await strategy_service.create_strategy(request)
    except ValueError as e:
        logger.error(f"创建策略参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建策略失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建策略失败: {str(e)}")


@router.get("/{strategy_id}", response_model=StrategyResponse, summary="获取策略")
async def get_strategy(strategy_id: str) -> StrategyResponse:
    """
    获取指定策略的详细信息
    """
    try:
        strategy = await strategy_service.get_strategy(strategy_id)
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        return strategy
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取策略失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取策略失败: {str(e)}")


@router.put("/{strategy_id}", response_model=StrategyResponse, summary="更新策略")
async def update_strategy(
    strategy_id: str,
    request: StrategyUpdateRequest
) -> StrategyResponse:
    """
    更新策略信息
    """
    try:
        strategy = await strategy_service.update_strategy(strategy_id, request)
        if not strategy:
            raise HTTPException(status_code=404, detail="策略不存在")
        return strategy
    except ValueError as e:
        logger.error(f"更新策略参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新策略失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新策略失败: {str(e)}")


@router.delete("/{strategy_id}", summary="删除策略")
async def delete_strategy(strategy_id: str) -> dict:
    """
    删除策略
    """
    try:
        success = await strategy_service.delete_strategy(strategy_id)
        if not success:
            raise HTTPException(status_code=404, detail="策略不存在")
        return {"message": "策略已删除", "strategy_id": strategy_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除策略失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除策略失败: {str(e)}")


@router.get("", response_model=StrategyListResponse, summary="列出策略")
async def list_strategies(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> StrategyListResponse:
    """
    列出所有策略
    
    支持按状态过滤和分页
    """
    try:
        strategies, total = await strategy_service.list_strategies(
            status=status,
            limit=limit,
            offset=offset
        )
        return StrategyListResponse(
            total=total,
            strategies=strategies
        )
    except Exception as e:
        logger.error(f"列出策略失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出策略失败: {str(e)}")


@router.post("/validate", response_model=StrategyValidateResponse, summary="验证策略代码")
async def validate_strategy(request: StrategyValidateRequest) -> StrategyValidateResponse:
    """
    验证策略代码
    
    检查：
    - Python 语法
    - 必要的类和方法
    - 潜在的安全问题
    """
    try:
        return await strategy_service.validate_strategy(request)
    except Exception as e:
        logger.error(f"验证策略失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"验证策略失败: {str(e)}")
