from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

from core.config import settings
from core.database import get_session
from schemas.quote import RealtimeQuoteRequest, RealtimeQuoteResponse, QuoteItem
from services.eastmoney_spider import TushareQuoteService
from models.realtime_quote import RealtimeQuote

router = APIRouter()


@router.api_route("/realtime",methods=["POST", "OPTIONS"], response_model=RealtimeQuoteResponse)
async def get_realtime_quotes(
    request: RealtimeQuoteRequest,
    session: Annotated[Session, Depends(get_session)],
) -> RealtimeQuoteResponse:
    """获取实时行情数据（使用 Tushare API）
    
    支持沪深 A 股（000/002/300/600/601/603 等）
    自动根据股票代码判断交易所（深圳/上海）并转换为 Tushare 格式
    
    注意：需要配置环境变量 TUSHARE_TOKEN
    """
    # 验证并初始化 Tushare 服务
    settings.validate_tushare_token()
    service = TushareQuoteService(token=settings.tushare_token)
    
    # 获取行情数据
    success_items, failed_codes = service.fetch_quotes(request.codes)
    
    # 保存到数据库
    for item in success_items:
        db_quote = RealtimeQuote(
            code=item.code,
            name=item.name,
            price=item.price,
            pct_change=item.pct_change,
            turnover=item.turnover,
            update_time=item.update_time,
        )
        session.add(db_quote)
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        # 记录错误但不影响返回结果
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"保存数据库失败: {e}")
    
    # 构建成功代码列表
    success_codes = [item.code for item in success_items]
    
    return RealtimeQuoteResponse(
        data=success_items,
        success_codes=success_codes,
        failed_codes=failed_codes,
    )

