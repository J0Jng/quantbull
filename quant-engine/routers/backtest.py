from fastapi import APIRouter, HTTPException

from core.logger import get_logger
from schemas.backtest import BacktestRequest, BacktestResponse
from schemas.response import BaseResponse, PaginatedResponse, BacktestDetail
from services.backtest_service import BacktestService
import os
import httpx
from schemas.backtest import BacktestSubmitResponse
import os
import httpx

logger = get_logger(__name__)
router = APIRouter()

# 初始化服务
backtest_service = BacktestService()


@router.post("/run", response_model=BacktestSubmitResponse, summary="提交回测任务（异步，返回 task_id）")
async def run_backtest(request: BacktestRequest) -> BacktestSubmitResponse:
    """将回测任务提交到平台级 `task-service`，立即返回 `task_id` 给前端。

    注意：此接口不在请求中执行回测计算，回测由 task-service 后台异步执行。
    """
    TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL", "http://localhost:9000")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(f"{TASK_SERVICE_URL}/api/tasks", json={
                "task_type": "backtest",
                "payload": {
                    "name": request.stock_code + "_" + request.start_date,
                    "steps": 5,
                    "step_delay": 1,
                    "params": request.model_dump()
                }
            })
            resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.error(f"提交任务到 task-service 失败: {e}")
            raise HTTPException(status_code=502, detail=f"task-service unavailable: {e}")
    data = resp.json()
    return BacktestSubmitResponse(task_id=data.get("task_id"))


@router.get("/{backtest_id}", response_model=BaseResponse[BacktestDetail], summary="获取回测结果")
async def get_backtest(backtest_id: str) -> BaseResponse[BacktestDetail]:
    """
    获取指定回测的详细结果
    """
    try:
        result = await backtest_service.get_backtest(backtest_id)
        if not result:
            raise HTTPException(status_code=404, detail="回测记录不存在")
        # 使用统一响应信封包装数据
        return BaseResponse[BacktestDetail](success=True, data=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取回测结果失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取回测结果失败: {str(e)}")


@router.get("", response_model=PaginatedResponse[BacktestDetail], summary="列出回测记录")
async def list_backtests(limit: int = 10, offset: int = 0) -> PaginatedResponse[BacktestDetail]:
    """
    列出所有回测记录
    """
    try:
        backtests = await backtest_service.list_backtests(limit=limit, offset=offset)
        # 统一返回字段为 total 和 items，保持业务数据不变
        return PaginatedResponse[BacktestDetail](total=len(backtests), items=backtests)
    except Exception as e:
        logger.error(f"列出回测记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出回测记录失败: {str(e)}")


@router.post("/run_async", summary="异步提交回测任务（示例：调用 task-service）")
async def run_backtest_async(request: BacktestRequest):
    """示例业务：将回测任务提交到平台级 task-service，立即返回 task_id 给前端。"""
    TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL", "http://localhost:9000")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(f"{TASK_SERVICE_URL}/api/tasks", json={
                "task_type": "backtest",
                "payload": {
                    "name": request.stock_code + "_" + request.start_date,
                    # demo: pass limited steps to control duration in MVP
                    "steps": 5,
                    "step_delay": 1,
                    "params": request.model_dump()
                }
            })
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"task-service unavailable: {e}")
    data = resp.json()
    return {"task_id": data.get("task_id")}
