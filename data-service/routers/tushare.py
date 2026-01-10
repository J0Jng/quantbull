from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session

from core.database import get_session
from schemas.tushare import (
    DailyQuoteRequest,
    DailyQuoteResponse,
    DailyQuoteItem,
    StockBasicResponse,
    TopListRequest,
    TopListItem,
    TopListResponse,
)
from services.tushare_service import TushareService
from models.daily_quote import DailyQuote

router = APIRouter()


@router.api_route("/daily",methods=["POST", "OPTIONS"], response_model=DailyQuoteResponse)
async def get_daily_quotes(
    request: DailyQuoteRequest,
    session: Annotated[Session, Depends(get_session)],
) -> DailyQuoteResponse:
    """获取日线行情数据
    
    支持批量查询多只股票的日线行情数据
    数据会自动保存到数据库（upsert）
    """
    service = TushareService()
    
    # 获取行情数据
    success_items, failed_codes = service.fetch_daily(
        codes=request.codes,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    
    # 保存到数据库（使用 upsert）
    for item in success_items:
        # 转换 trade_date 字符串为 date 对象
        trade_date = datetime.strptime(item.trade_date, "%Y%m%d").date()
        
        # 使用 PostgreSQL 的 ON CONFLICT 实现 upsert
        stmt = insert(DailyQuote).values(
            code=item.code,
            trade_date=trade_date,
            open=item.open,
            high=item.high,
            low=item.low,
            close=item.close,
            vol=item.vol,
            amount=item.amount,
        )
        
        # ON CONFLICT 更新
        stmt = stmt.on_conflict_do_update(
            constraint="uq_code_trade_date",
            set_=dict(
                open=stmt.excluded.open,
                high=stmt.excluded.high,
                low=stmt.excluded.low,
                close=stmt.excluded.close,
                vol=stmt.excluded.vol,
                amount=stmt.excluded.amount,
            ),
        )
        
        session.execute(stmt) 
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"保存数据库失败: {e}")
        # 不影响返回结果
    
    # 构建成功代码列表（去重）
    success_codes = list(set(item.code for item in success_items))
    
    return DailyQuoteResponse(
        data=success_items,
        success_codes=success_codes,
        failed_codes=failed_codes,
    )


@router.get("/top_list", response_model=TopListResponse)
async def get_top_list(
    trade_date: str,
) -> TopListResponse:
    """获取龙虎榜数据
    
    获取指定日期的龙虎榜股票列表
    """
    # 验证日期格式
    if len(trade_date) != 8 or not trade_date.isdigit():
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="日期格式必须为 YYYYMMDD")
    
    service = TushareService()
    raw_data = service.fetch_top_list(trade_date=trade_date)
    
    # 转换为响应格式
    items = []
    for item in raw_data:
        items.append(TopListItem(
            ts_code=item.get("ts_code", ""),
            name=item.get("name", ""),
            close=item.get("close"),
            pct_change=item.get("pct_change"),
            turnover_rate=item.get("turnover_rate"),
            amount=item.get("amount"),
            l_sell=item.get("l_sell"),
            l_buy=item.get("l_buy"),
            net_amount=item.get("net_amount"),
            reason=item.get("reason", ""),
        ))
    
    return TopListResponse(
        data=items,
        trade_date=trade_date,
    )


@router.get("/top_inst")
async def get_top_inst(
    trade_date: str,
) -> dict:
    """获取龙虎榜机构交易明细
    
    获取指定日期的龙虎榜机构买卖明细
    """
    if len(trade_date) != 8 or not trade_date.isdigit():
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="日期格式必须为 YYYYMMDD")
    
    service = TushareService()
    data = service.fetch_top_inst(trade_date=trade_date)
    
    return {"data": data, "trade_date": trade_date}


@router.get("/top_list_summary")
async def get_top_list_summary(
    days: int = 5,
) -> dict:
    """获取多日龙虎榜汇总数据
    
    获取指定天数内的龙虎榜汇总，按净买入额排序
    
    Args:
        days: 天数（1, 5, 20）
    """
    if days not in [1, 5, 20]:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="days 必须为 1, 5 或 20")
    
    service = TushareService()
    
    if days == 1:
        # 单日数据使用原有接口
        from datetime import datetime, timedelta
        # 获取最近交易日
        today = datetime.now()
        trade_date = today
        while trade_date.weekday() >= 5:  # 跳过周末
            trade_date -= timedelta(days=1)
        trade_date_str = trade_date.strftime("%Y%m%d")
        
        raw_data = service.fetch_top_list(trade_date=trade_date_str)
        # 转换格式
        data = []
        for item in raw_data[:20]:
            data.append({
                "ts_code": item.get("ts_code", ""),
                "name": item.get("name", ""),
                "close": item.get("close"),
                "pct_change": item.get("pct_change"),
                "net_amount": item.get("net_amount"),
                "reason": item.get("reason", ""),
                "appear_count": 1,
            })
        return {"data": data, "days": days}
    else:
        # 多日汇总
        data = service.fetch_top_list_multi_days(days=days)
        return {"data": data, "days": days}


@router.get("/stock_basic", response_model=StockBasicResponse)
async def get_stock_basic(
    exchange: str = "",
) -> StockBasicResponse:
    """获取股票基础信息"""
    service = TushareService()
    data = service.fetch_stock_basic()
    
    return StockBasicResponse(data=data)


@router.post("/fund_daily", response_model=DailyQuoteResponse)
async def get_fund_daily(
    request: DailyQuoteRequest,
    session: Annotated[Session, Depends(get_session)],
) -> DailyQuoteResponse:
    """获取 ETF 日线行情"""
    service = TushareService()
    
    success_items, failed_codes = service.fetch_fund_daily(
        codes=request.codes,
        start_date=request.start_date,
        end_date=request.end_date,
    )
    
    # 保存到数据库（与股票日线使用相同表结构）
    for item in success_items:
        trade_date = datetime.strptime(item.trade_date, "%Y%m%d").date()
        
        stmt = insert(DailyQuote).values(
            code=item.code,
            trade_date=trade_date,
            open=item.open,
            high=item.high,
            low=item.low,
            close=item.close,
            vol=item.vol,
            amount=item.amount,
        )
        
        stmt = stmt.on_conflict_do_update(
            constraint="uq_code_trade_date",
            set_=dict(
                open=stmt.excluded.open,
                high=stmt.excluded.high,
                low=stmt.excluded.low,
                close=stmt.excluded.close,
                vol=stmt.excluded.vol,
                amount=stmt.excluded.amount,
            ),
        )
        
        session.execute(stmt) 
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"保存数据库失败: {e}")
    
    success_codes = list(set(item.code for item in success_items))
    
    return DailyQuoteResponse(
        data=success_items,
        success_codes=success_codes,
        failed_codes=failed_codes,
    )

