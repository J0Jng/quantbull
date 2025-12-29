from fastapi import APIRouter

from services.stock_service import StockService

router = APIRouter()


@router.get("/list")
async def get_stock_list():
    """获取股票候选池"""
    service = StockService()
    return service.get_stock_list()