from fastapi import APIRouter, HTTPException

from core.logger import get_logger
from schemas.backtest import BacktestRequest, BacktestResponse
from services.backtest_service import BacktestService

logger = get_logger(__name__)
router = APIRouter()

# 初始化服务
backtest_service = BacktestService()


@router.post("/run", response_model=BacktestResponse, summary="执行回测")
async def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """
    执行量化策略回测
    
    支持：
    - Custom 策略（AI 生成）：提供 strategy_code
    - Builtin 策略（系统内置）：提供 strategy_name（如：ma_cross, rsi）
    - 多种数据源：tushare、tdengine
    - AI 评价数据：设置 enable_ai_review=true 获取结构化评价输入
    
    示例请求：
    ```json
    {
      "stock_code": "000001",
      "start_date": "2022-01-01",
      "end_date": "2023-01-01",
      "strategy_mode": "builtin",
      "strategy_name": "ma_cross",
      "data_source": "tushare",
      "enable_ai_review": true
    }
    ```
    """
    try:
        return await backtest_service.run_backtest(request)
    except ValueError as e:
        logger.error(f"回测请求参数错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"回测执行失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"回测执行失败: {str(e)}")


@router.get("/{backtest_id}", summary="获取回测结果")
async def get_backtest(backtest_id: str) -> dict:
    """
    获取指定回测的详细结果
    """
    try:
        result = await backtest_service.get_backtest(backtest_id)
        if not result:
            raise HTTPException(status_code=404, detail="回测记录不存在")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取回测结果失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取回测结果失败: {str(e)}")


@router.get("", summary="列出回测记录")
async def list_backtests(limit: int = 10, offset: int = 0) -> dict:
    """
    列出所有回测记录
    """
    try:
        backtests = await backtest_service.list_backtests(limit=limit, offset=offset)
        return {
            "total": len(backtests),
            "backtests": backtests
        }
    except Exception as e:
        logger.error(f"列出回测记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出回测记录失败: {str(e)}")
