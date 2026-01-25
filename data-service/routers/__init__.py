from fastapi import APIRouter

from .data import router as data_router
from .quotes import router as quotes_router
from .tushare import router as tushare_router
from .market import router as market_router
from .etf import router as etf_router
from .stock import router as stock_router
from .fundamentals import router as fundamentals_router
from .news import router as news_router
from .finance_channel import router as finance_channel_router
from .funds import router as funds_router
from .fund_flow import router as fund_flow_router
from .financial_report import router as financial_report_router
from .lhb import router as lhb_router
from .profit_forecast import router as profit_forecast_router
from .videos import router as videos_router

api_router = APIRouter()
api_router.include_router(router=data_router, prefix="/data", tags=["data"])
api_router.include_router(router=quotes_router, prefix="/quotes", tags=["quotes"])
api_router.include_router(router=tushare_router, prefix="/tushare", tags=["tushare"])
api_router.include_router(router=market_router, prefix="/market", tags=["market"])
api_router.include_router(router=etf_router, prefix="/etf", tags=["etf"])
api_router.include_router(router=stock_router, prefix="/stock", tags=["stock"])
api_router.include_router(router=fundamentals_router, prefix="/fundamentals", tags=["fundamentals"])
api_router.include_router(router=news_router, tags=["news"])
api_router.include_router(router=finance_channel_router, tags=["finance-channel"])
api_router.include_router(router=funds_router, prefix="/funds", tags=["funds"])
api_router.include_router(router=fund_flow_router, prefix="/fundflow", tags=["fundflow"])
api_router.include_router(router=financial_report_router, tags=["financial-report"])
api_router.include_router(router=lhb_router, tags=["lhb"])
api_router.include_router(router=profit_forecast_router, tags=["profit-forecast"])
api_router.include_router(router=videos_router, tags=["videos"])

__all__ = ["api_router", "data_router", "quotes_router", "tushare_router", "market_router", "etf_router", "stock_router", "fundamentals_router", "news_router", "finance_channel_router", "funds_router", "fund_flow_router", "financial_report_router", "lhb_router", "profit_forecast_router", "videos_router"]

