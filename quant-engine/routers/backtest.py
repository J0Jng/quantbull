from fastapi import APIRouter, HTTPException, BackgroundTasks
import uuid

from core.logger import get_logger
from schemas.backtest import BacktestRequest, BacktestExecuteRequest
from schemas.response import BaseResponse, PaginatedResponse, BacktestDetail
from services.backtest_service import BacktestService
from services.backtest_repository import BacktestRepository
from core.response import success

logger = get_logger(__name__)
router = APIRouter()

# 初始化服务（直接执行回测并落库）
backtest_service = BacktestService()


@router.post("/run", summary="异步执行回测（后台任务）")
async def run_backtest(request: BacktestRequest, background_tasks: BackgroundTasks):
    """提交回测任务到后台执行，立即返回 backtest_id，客户端轮询状态。"""
    try:
        # 创建 backtest 记录，状态 pending
        backtest_id = f"backtest_{uuid.uuid4().hex[:8]}"
        BacktestRepository.create_stub(request, backtest_id=backtest_id)
        
        # 添加后台任务
        background_tasks.add_task(execute_backtest_async, request, backtest_id)
        
        return success({"backtest_id": backtest_id, "status": "pending"})
    except Exception as e:
        logger.error(f"提交回测任务失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"提交回测任务失败: {str(e)}")


async def execute_backtest_async(request: BacktestRequest, backtest_id: str):
    """后台异步执行回测"""
    try:
        await backtest_service.run_backtest(request, backtest_id=backtest_id)
        logger.info(f"后台回测完成: {backtest_id}")
    except Exception as e:
        logger.error(f"后台回测执行失败: {backtest_id}, {e}", exc_info=True)
        BacktestRepository.mark_failed(backtest_id, str(e))


@router.get("/{backtest_id}", summary="获取回测结果")
async def get_backtest(backtest_id: str):
    """
    获取指定回测的详细结果
    """
    try:
        result = await backtest_service.get_backtest(backtest_id)
        if not result:
            raise HTTPException(status_code=404, detail="回测记录不存在")
        return success(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取回测结果失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取回测结果失败: {str(e)}")


@router.get("", summary="列出回测记录")
async def list_backtests(limit: int = 10, offset: int = 0):
    """
    列出所有回测记录
    """
    try:
        backtests = await backtest_service.list_backtests(limit=limit, offset=offset)
        # 统一返回 envelope，data 中包含分页结构
        return success({"total": len(backtests), "items": backtests})
    except Exception as e:
        logger.error(f"列出回测记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出回测记录失败: {str(e)}")


# 兼容旧接口，仍提供异步入口（复用 /run）
@router.post("/run_async", summary="兼容：异步提交回测（后台执行）")
async def run_backtest_async(request: BacktestRequest, background_tasks: BackgroundTasks):
    return await run_backtest(request, background_tasks)


# 兼容 task-service worker 的同步执行入口，仍由 quant-engine 真正执行
@router.post("/run_sync", summary="同步执行回测（task-service worker 调用）")
async def run_backtest_sync(request: BacktestExecuteRequest):
    try:
        result = await backtest_service.run_backtest(
            request,
            backtest_id=request.backtest_id,
            task_id=request.task_id,
        )
        return success({
            "backtest_id": result.backtest_id,
            "metrics": result.metrics,
            "daily_nav": result.daily_nav,
            "result_url": f"/api/backtest/{result.backtest_id}",
        })
    except Exception as e:
        logger.error(f"同步回测执行失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
