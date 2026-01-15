import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func, and_
from sqlmodel import Session, select

from core.database import SessionLocal
from core.response import success
from models.stock_basic import StockBasic
from models.realtime_quote import RealtimeQuote
from schemas.stock import StockItem, StockSnapshotItem
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
                payload = item.model_dump()
                amount_k = float(payload.pop("_amount_k", 0.0) or 0.0)
                stmt = insert(StockBasic).values(
                    symbol=item.symbol,
                    name=item.name,
                    industry=item.industry,
                    trade_date=trade_date,
                    latest_price=item.latest_price,
                    pct_change=item.pct_change,
                    turnover_rate=item.turnover_rate,
                    amount=amount_k,
                )
                stmt = stmt.on_conflict_do_update(
                    constraint="uq_stock_symbol_trade_date",
                    set_=dict(
                        name=stmt.excluded.name,
                        industry=stmt.excluded.industry,
                        latest_price=stmt.excluded.latest_price,
                        pct_change=stmt.excluded.pct_change,
                        turnover_rate=stmt.excluded.turnover_rate,
                        amount=stmt.excluded.amount,
                    ),
                )
                session.execute(stmt)
            session.commit()
            logger.info(f"成功保存 {len(stock_items)} 条股票数据到数据库")
    except Exception as e:
        logger.error(f"保存股票数据到数据库失败: {e}")


def _load_stocks_from_db(
    limit: int = 100,
    trade_date: Optional[date] = None,
    min_amount_k: float = 0.0,
) -> List[StockItem]:
    """从数据库加载股票列表（DB优先）

    Args:
        limit: 返回数量
        trade_date: 指定交易日；不传则使用库中最新交易日
        min_amount_k: 最小成交额过滤（单位：千元）
    """
    try:
        with SessionLocal() as session:
            query_trade_date = trade_date
            if query_trade_date is None:
                latest_stmt = select(StockBasic.trade_date).order_by(StockBasic.trade_date.desc()).limit(1)
                result = session.execute(latest_stmt)
                query_trade_date = result.scalar()

            if query_trade_date is None:
                return []

            stmt = select(StockBasic).where(StockBasic.trade_date == query_trade_date)
            if min_amount_k and min_amount_k > 0:
                stmt = stmt.where(StockBasic.amount >= min_amount_k)

            stmt = stmt.order_by(StockBasic.amount.desc()).limit(limit)
            results = session.execute(stmt).scalars().all()
            
            if not results:
                return []
            
            items: List[StockItem] = []
            for stock in results:
                items.append(
                    StockItem(
                        symbol=stock.symbol,
                        name=stock.name,
                        industry=stock.industry,
                        latest_price=stock.latest_price,
                        pct_change=stock.pct_change,
                        turnover_rate=stock.turnover_rate,
                    )
                )

            logger.info(f"从数据库加载 {len(items)} 条股票数据（交易日: {query_trade_date}）")
            return items
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

        # DB 优先：先尝试从数据库读取
        try:
            db_trade_date: Optional[date] = None
            if date:
                db_trade_date = datetime.strptime(date, "%Y-%m-%d").date()
            min_amount_k = (min_turnover / 1000) if min_turnover > 0 else 0.0
            db_items = _load_stocks_from_db(limit=limit, trade_date=db_trade_date, min_amount_k=min_amount_k)
            if db_items:
                _set_cache(cache_key, [item.model_dump() for item in db_items])
                return success(db_items)
        except Exception as e:
            logger.warning(f"数据库读取失败，继续尝试 Tushare: {e}")

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
                # 用于入库排序/过滤（StockItem schema 不包含成交额）
                setattr(item, "_amount_k", float(row.get('amount', 0.0) or 0.0))
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
            # 降级策略：1. 数据库 -> 2. 内存缓存 -> 3. 空列表
            try:
                db_trade_date: Optional[date] = None
                if date:
                    db_trade_date = datetime.strptime(date, "%Y-%m-%d").date()
                min_amount_k = (min_turnover / 1000) if min_turnover > 0 else 0.0
                db_items = _load_stocks_from_db(limit=limit, trade_date=db_trade_date, min_amount_k=min_amount_k)
                if db_items:
                    _set_cache(cache_key, [item.model_dump() for item in db_items], ttl_minutes=60)
                    return success(db_items)
            except Exception:
                pass

            if cache_key in _cache:
                logger.info("使用过期缓存的股票列表")
                return success(_cache[cache_key])

            return success([])

    def get_stock_snapshot_list(
        self,
        date: Optional[str] = None,
        limit: int = 200,
        min_turnover: float = 0,
        sort: str = "amount",
        refresh: bool = False
    ) -> Dict:
        """
        获取聚合股票快照列表（DB 侧整合 stock_basic + realtime_quotes）
        
        Args:
            date: 交易日期 YYYY-MM-DD，不传则使用最近交易日
            limit: 返回数量限制
            min_turnover: 最小成交额过滤（元）
            sort: 排序方式 (rise/fall/amount/volume)
            refresh: 是否触发后台数据刷新
        
        Returns:
            聚合后的股票快照列表，包含完整字段
        """
        # 1. 如果 refresh=true，先触发数据拉取
        if refresh:
            logger.info("触发数据刷新")
            try:
                # 触发 stock_list 拉取并落库
                self.get_stock_list(date=date, limit=limit, min_turnover=min_turnover)
                
                # 触发实时行情拉取（这里需要先从 DB 获取 codes）
                with SessionLocal() as session:
                    db_trade_date: Optional[date] = None
                    if date:
                        db_trade_date = datetime.strptime(date, "%Y-%m-%d").date()
                    else:
                        # 获取最新交易日
                        latest_stmt = select(StockBasic.trade_date).order_by(
                            StockBasic.trade_date.desc()
                        ).limit(1)
                        result = session.execute(latest_stmt)
                        db_trade_date = result.scalar()
                    
                    if db_trade_date:
                        stmt = select(StockBasic.symbol).where(
                            StockBasic.trade_date == db_trade_date
                        ).limit(limit)
                        result = session.execute(stmt)
                        codes = list(result.scalars().all())
                        
                        if codes:
                            # 调用 Tushare 获取实时行情并落库
                            from services.eastmoney_spider import TushareQuoteService
                            from core.config import settings
                            
                            # 验证并初始化 Tushare 服务
                            settings.validate_tushare_token()
                            quote_service = TushareQuoteService(token=settings.tushare_token)
                            success_items, _ = quote_service.fetch_quotes(codes)
                            
                            # 保存实时行情到数据库
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
                            session.commit()
                            logger.info(f"刷新了 {len(success_items)} 条实时行情数据")
            except Exception as e:
                logger.error(f"数据刷新失败: {e}", exc_info=True)
        
        # 2. 从数据库查询聚合数据
        try:
            with SessionLocal() as session:
                # 确定查询交易日
                db_trade_date: Optional[date] = None
                if date:
                    db_trade_date = datetime.strptime(date, "%Y-%m-%d").date()
                else:
                    # 获取最新交易日
                    latest_stmt = select(StockBasic.trade_date).order_by(
                        StockBasic.trade_date.desc()
                    ).limit(1)
                    result = session.execute(latest_stmt)
                    db_trade_date = result.scalar()
                
                if not db_trade_date:
                    logger.warning("数据库中无股票数据")
                    return success([])
                
                logger.info(f"查询交易日: {db_trade_date}")
                
                # 构建子查询：获取每个 code 的最新实时行情
                # 使用窗口函数或分组方式获取最新记录
                latest_realtime_subquery = (
                    select(
                        RealtimeQuote.code,
                        RealtimeQuote.name,
                        RealtimeQuote.price,
                        RealtimeQuote.pct_change,
                        RealtimeQuote.turnover,
                        RealtimeQuote.update_time,
                        func.row_number().over(
                            partition_by=RealtimeQuote.code,
                            order_by=RealtimeQuote.update_time.desc()
                        ).label('rn')
                    )
                ).subquery()
                
                # 主查询：JOIN stock_basic 和最新的 realtime_quotes
                query = (
                    select(
                        StockBasic.symbol,
                        StockBasic.name.label('basic_name'),
                        StockBasic.industry,
                        StockBasic.latest_price.label('basic_price'),
                        StockBasic.pct_change.label('basic_pct_change'),
                        StockBasic.turnover_rate,
                        StockBasic.amount,
                        latest_realtime_subquery.c.name.label('realtime_name'),
                        latest_realtime_subquery.c.price.label('realtime_price'),
                        latest_realtime_subquery.c.pct_change.label('realtime_pct_change'),
                        latest_realtime_subquery.c.turnover,
                        latest_realtime_subquery.c.update_time,
                    )
                    .select_from(StockBasic)
                    .outerjoin(
                        latest_realtime_subquery,
                        and_(
                            StockBasic.symbol == latest_realtime_subquery.c.code,
                            latest_realtime_subquery.c.rn == 1
                        )
                    )
                    .where(StockBasic.trade_date == db_trade_date)
                )
                
                # 成交额过滤
                if min_turnover > 0:
                    min_amount_k = min_turnover / 1000
                    query = query.where(
                        func.coalesce(latest_realtime_subquery.c.turnover, StockBasic.amount * 1000) >= min_turnover
                    )
                
                # 排序逻辑
                if sort == "rise":
                    query = query.order_by(
                        func.coalesce(
                            latest_realtime_subquery.c.pct_change,
                            StockBasic.pct_change
                        ).desc()
                    )
                elif sort == "fall":
                    query = query.order_by(
                        func.coalesce(
                            latest_realtime_subquery.c.pct_change,
                            StockBasic.pct_change
                        ).asc()
                    )
                elif sort in ["amount", "volume"]:
                    query = query.order_by(
                        func.coalesce(
                            latest_realtime_subquery.c.turnover,
                            StockBasic.amount * 1000
                        ).desc()
                    )
                else:
                    # 默认按成交额排序
                    query = query.order_by(
                        func.coalesce(
                            latest_realtime_subquery.c.turnover,
                            StockBasic.amount * 1000
                        ).desc()
                    )
                
                # 限制数量
                query = query.limit(limit)
                
                # 执行查询
                results = session.execute(query).all()
                
                if not results:
                    logger.warning("查询结果为空")
                    return success([])
                
                # 构建返回数据
                snapshot_items = []
                for row in results:
                    # 优先使用实时数据，其次使用基础数据
                    final_name = row.realtime_name if row.realtime_name else row.basic_name
                    final_price = row.realtime_price if row.realtime_price is not None else row.basic_price
                    final_pct_change = (
                        row.realtime_pct_change 
                        if row.realtime_pct_change is not None 
                        else row.basic_pct_change
                    )
                    final_turnover = (
                        row.turnover 
                        if row.turnover is not None 
                        else (row.amount * 1000 if row.amount else 0)
                    )
                    final_update_time = (
                        row.update_time.strftime("%Y-%m-%d %H:%M:%S")
                        if row.update_time
                        else ""
                    )
                    
                    snapshot_items.append(
                        StockSnapshotItem(
                            symbol=row.symbol,
                            code=row.symbol,  # 兼容字段
                            name=final_name or "未知",
                            industry=row.industry or "未知",
                            price=final_price or 0.0,
                            latest_price=final_price or 0.0,  # 兼容字段
                            pct_change=final_pct_change or 0.0,
                            turnover_rate=row.turnover_rate,
                            turnover=final_turnover,
                            update_time=final_update_time,
                        )
                    )
                
                logger.info(f"返回 {len(snapshot_items)} 条聚合快照数据")
                return success(snapshot_items)
                
        except Exception as e:
            logger.error(f"获取股票快照列表失败: {e}", exc_info=True)
            return success([])