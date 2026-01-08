from fastapi import APIRouter

from .data import router as data_router
from .quotes import router as quotes_router
from .tushare import router as tushare_router
from .market import router as market_router
from .etf import router as etf_router
from .stock import router as stock_router
from .fundamentals import router as fundamentals_router

api_router = APIRouter()
api_router.include_router(router=data_router, prefix="/data", tags=["data"])
api_router.include_router(router=quotes_router, prefix="/quotes", tags=["quotes"])
api_router.include_router(router=tushare_router, prefix="/tushare", tags=["tushare"])
api_router.include_router(router=market_router, prefix="/market", tags=["market"])
api_router.include_router(router=etf_router, prefix="/etf", tags=["etf"])
api_router.include_router(router=stock_router, prefix="/stock", tags=["stock"])
api_router.include_router(router=fundamentals_router, prefix="/fundamentals", tags=["fundamentals"])

__all__ = ["api_router", "data_router", "quotes_router", "tushare_router", "market_router", "etf_router", "stock_router", "fundamentals_router"]

