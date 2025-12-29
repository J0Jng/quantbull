from fastapi import APIRouter

from services.etf_service import ETFService

router = APIRouter()


@router.get("/list")
async def get_etf_list():
    """获取 ETF 候选池"""
    service = ETFService()
    return service.get_etf_list()