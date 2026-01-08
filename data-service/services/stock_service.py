import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, select

from core.database import SessionLocal
from core.response import success
from models.stock_basic import StockBasic
from schemas.stock import StockItem
from services.tushare_service import TushareService

logger = logging.getLogger(__name__)

# 简单内存缓存
_cache: Dict[str, List[Dict]] = {}
_cache_expiry: Dict[str, datetime] = {}


def _is_cache_valid(key: str, ttl_minutes: int = 5) -> bool:
    """检查缓存是否有效"""
    if key not in _cache_expiry:
        return False
    return datetime.now() < _cache_expiry[key]


def _set_cache(key: str, data: List[Dict], ttl_minutes: int = 5):
    """设置缓存"""
    _cache[key] = data
    _cache_expiry[key] = datetime.now() + timedelta(minutes=ttl_minutes)


def _find_latest_trade_date(tushare_api, max_days_back: int = 10) -> Optional[str]:
    """
    查找最近的交易日（返回 YYYYMMDD 格式）
    """
    for days_back in range(max_days_back):
        check_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
        try:
            df = tushare_api.index_daily(ts_code="000001.SH", trade_date=check_date)
            if df is not None and not df.empty:
                logger.info(f"找到最近交易日: {check_date}")
                return check_date
        except Exception as e:
            logger.debug(f"检查日期 {check_date} 失败: {e}")
            continue
    return None


def _save_stocks_to_db(stock_items: List[StockItem], trade_date: date) -> None:
    """将股票列表保存到数据库（upsert）"""
    try:
        with SessionLocal() as session:
            for item in stock_items:
                stmt = insert(StockBasic).values(
                    symbol=item.symbol,
                    name=item.name,
                    industry=item.industry,
                    trade_date=trade_date,
                    latest_price=item.latest_price,
                    pct_change=item.pct_change,
                    turnover_rate=item.turnover_rate,
                    amount=0.0,  # 可选字段
                )
                stmt = stmt.on_conflict_do_update(
                    constraint="uq_stock_symbol_trade_date",
                    set_=dict(
                        name=stmt.excluded.name,
                        industry=stmt.excluded.industry,
                        latest_price=stmt.excluded.latest_price,
                        pct_change=stmt.excluded.pct_change,
                        turnover_rate=stmt.excluded.turnover_rate,
                    ),
                )
                session.execute(stmt)
            session.commit()
            logger.info(f"成功保存 {len(stock_items)} 条股票数据到数据库")
    except Exception as e:
        logger.error(f"保存股票数据到数据库失败: {e}")


def _load_stocks_from_db(limit: int = 100) -> List[Dict]:
    """从数据库加载最新的股票列表（fallback）"""
    try:
        with SessionLocal() as session:
            # 查找最近的交易日数据
            stmt = (
                select(StockBasic)
                .order_by(StockBasic.trade_date.desc(), StockBasic.amount.desc())
                .limit(limit)
            )
            results = session.exec(stmt).all()
            
            if not results:
                return []
            
            # 转换为字典列表
            stock_list = []
            for stock in results:
                stock_list.append({
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "industry": stock.industry,
                    "latest_price": stock.latest_price,
                    "pct_change": stock.pct_change,
                    "turnover_rate": stock.turnover_rate,
                })
            
            logger.info(f"从数据库加载 {len(stock_list)} 条股票数据（交易日: {results[0].trade_date}）")
            return stock_list
    except Exception as e:
        logger.error(f"从数据库加载股票数据失败: {e}")
        return []


class StockService:
    """股票数据服务"""

    def __init__(self):
        self.tushare_service = TushareService()

    def get_stock_list(
        self, 
        date: Optional[str] = None, 
        limit: int = 100,
        min_turnover: float = 0
    ) -> Dict:
        """
        获取股票候选池
        
        Args:
            date: 交易日期 YYYY-MM-DD，不传则使用最近交易日
            limit: 返回数量限制
            min_turnover: 最小成交额过滤（元）
        """
        cache_key = f"stock_list_{date}_{limit}_{min_turnover}" if date else f"stock_list_latest_{limit}_{min_turnover}"

        # 检查缓存
        if _is_cache_valid(cache_key):
            logger.info(f"使用缓存的股票列表: {cache_key}")
            return success(_cache[cache_key])

        try:
            # 确定查询日期
            if date:
                query_date = date.replace("-", "")
            else:
                query_date = datetime.now().strftime("%Y%m%d")

            # 直接用 trade_date 获取全市场当日行情（不传 ts_code）
            # 这是 tushare daily 接口的正确用法
            logger.info(f"开始获取 {query_date} 的股票日行情")
            daily_df = self.tushare_service.api.daily(trade_date=query_date)

            # 如果无数据，尝试查找最近交易日
            if daily_df is None or daily_df.empty:
                logger.info(f"日期 {query_date} 无数据，尝试查找最近交易日")
                latest_trade_date = _find_latest_trade_date(self.tushare_service.api)
                if latest_trade_date:
                    daily_df = self.tushare_service.api.daily(trade_date=latest_trade_date)
                    query_date = latest_trade_date
                    logger.info(f"使用最近交易日 {query_date} 的数据")

            if daily_df is None or daily_df.empty:
                logger.warning("未获取到股票日行情数据")
                return success([])

            logger.info(f"获取到 {len(daily_df)} 条股票日行情数据")

            # 成交额过滤（tushare 的 amount 单位是千元）
            if min_turnover > 0:
                min_amount = min_turnover / 1000  # 转换为千元
                daily_df = daily_df[daily_df['amount'] >= min_amount]
                logger.info(f"成交额过滤后剩余 {len(daily_df)} 条")

            # 按成交额排序，取 top N
            daily_df = daily_df.sort_values('amount', ascending=False).head(limit)

            # 获取股票基础信息用于补充名称和行业
            stock_basic_df = self.tushare_service.api.stock_basic(list_status='L')
            name_dict = {}
            industry_dict = {}
            if stock_basic_df is not None and not stock_basic_df.empty:
                for _, row in stock_basic_df.iterrows():
                    ts_code = str(row['ts_code'])
                    name_dict[ts_code] = str(row.get('name', ''))
                    industry_dict[ts_code] = str(row.get('industry', '未知'))

            stock_items = []
            for _, row in daily_df.iterrows():
                ts_code = str(row['ts_code'])
                name = name_dict.get(ts_code, "未知")
                industry = industry_dict.get(ts_code, "未知")

                item = StockItem(
                    symbol=ts_code.split('.')[0],  # 移除 .SH/.SZ
                    name=name,
                    industry=industry,
                    latest_price=float(row['close']),
                    pct_change=float(row['pct_chg']) if 'pct_chg' in row else 0.0,
                    turnover_rate=float(row.get('turnover_rate', 0.0))
                )
                stock_items.append(item)

            logger.info(f"生成 {len(stock_items)} 条股票数据")

            # 保存到数据库（异步，不阻塞响应）
            trade_date_obj = datetime.strptime(query_date, "%Y%m%d").date()
            _save_stocks_to_db(stock_items, trade_date_obj)

            # 缓存
            _set_cache(cache_key, [item.model_dump() for item in stock_items])

            return success(stock_items)

        except Exception as e:
            logger.error(f"获取股票列表失败: {e}", exc_info=True)
            # 降级策略：1. 内存缓存 -> 2. 数据库 -> 3. 空列表
            if cache_key in _cache:
                logger.info("使用过期缓存的股票列表")
                return success(_cache[cache_key])
            
            # 尝试从数据库加载
            db_stocks = _load_stocks_from_db(limit)
            if db_stocks:
                logger.info(f"从数据库降级加载 {len(db_stocks)} 条股票数据")
                _set_cache(cache_key, db_stocks, ttl_minutes=60)  # 延长缓存时间
                return success(db_stocks)
            
            return success([])