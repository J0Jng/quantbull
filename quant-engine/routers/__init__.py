from fastapi import APIRouter

from routers import backtest, strategy, factor

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(backtest.router, prefix="/backtest", tags=["回测"])
api_router.include_router(strategy.router, prefix="/strategy", tags=["策略"])
api_router.include_router(factor.router, prefix="/factor", tags=["因子"])
