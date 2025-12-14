from fastapi import APIRouter

from .data import router as data_router
from .quotes import router as quotes_router
from .tushare import router as tushare_router

api_router = APIRouter()
api_router.include_router(router=data_router, prefix="/data", tags=["data"])
api_router.include_router(router=quotes_router, prefix="/quotes", tags=["quotes"])
api_router.include_router(router=tushare_router, prefix="/tushare", tags=["tushare"])

__all__ = ["api_router", "data_router", "quotes_router", "tushare_router"]

