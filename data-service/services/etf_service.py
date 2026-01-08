import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, select

from core.database import SessionLocal
from core.response import success
from models.etf_basic import ETFBasic
from schemas.etf import ETFItem
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


def _save_etfs_to_db(etf_items: List[ETFItem], trade_date: date) -> None:
    """将 ETF 列表保存到数据库（upsert）"""
    try:
        with SessionLocal() as session:
            for item in etf_items:
                stmt = insert(ETFBasic).values(
                    symbol=item.symbol,
                    name=item.name,
                    category=item.category,
                    trade_date=trade_date,
                    latest_price=item.latest_price,
                    pct_change=item.pct_change,
                    volume=item.volume,
                    amount=0.0,
                )
                stmt = stmt.on_conflict_do_update(
                    constraint="uq_etf_symbol_trade_date",
                    set_=dict(
                        name=stmt.excluded.name,
                        category=stmt.excluded.category,
                        latest_price=stmt.excluded.latest_price,
                        pct_change=stmt.excluded.pct_change,
                        volume=stmt.excluded.volume,
                    ),
                )
                session.execute(stmt)
            session.commit()
            logger.info(f"成功保存 {len(etf_items)} 条 ETF 数据到数据库")
    except Exception as e:
        logger.error(f"保存 ETF 数据到数据库失败: {e}")


def _load_etfs_from_db(limit: int = 50) -> List[Dict]:
    """从数据库加载最新的 ETF 列表（fallback）"""
    try:
        with SessionLocal() as session:
            # 查找最近的交易日数据
            stmt = (
                select(ETFBasic)
                .order_by(ETFBasic.trade_date.desc(), ETFBasic.volume.desc())
                .limit(limit)
            )
            results = session.exec(stmt).all()
            
            if not results:
                return []
            
            # 转换为字典列表
            etf_list = []
            for etf in results:
                etf_list.append({
                    "symbol": etf.symbol,
                    "name": etf.name,
                    "category": etf.category,
                    "latest_price": etf.latest_price,
                    "pct_change": etf.pct_change,
                    "volume": etf.volume,
                })
            
            logger.info(f"从数据库加载 {len(etf_list)} 条 ETF 数据（交易日: {results[0].trade_date}）")
            return etf_list
    except Exception as e:
        logger.error(f"从数据库加载 ETF 数据失败: {e}")
        return []


class ETFService:
    """ETF 数据服务"""

    def __init__(self):
        self.tushare_service = TushareService()

    def get_etf_list(self, date: Optional[str] = None, limit: int = 50) -> Dict:
        """
        获取 ETF 候选池（使用 tushare fund_daily 获取日行情）
        
        Args:
            date: 交易日期 YYYY-MM-DD，不传则使用最近交易日
            limit: 返回数量限制
        """
        cache_key = f"etf_list_{date}_{limit}" if date else f"etf_list_latest_{limit}"

        # 检查缓存
        if _is_cache_valid(cache_key):
            logger.info(f"使用缓存的 ETF 列表: {cache_key}")
            return success(_cache[cache_key])

        try:
            # 确定查询日期
            if date:
                query_date = date.replace("-", "")
            else:
                query_date = datetime.now().strftime("%Y%m%d")

            # 获取 ETF 基础信息
            logger.info("开始获取 ETF 基础信息")
            fund_basic_df = self.tushare_service.api.fund_basic(market='E')  # E 为场内 ETF
            
            if fund_basic_df is None or fund_basic_df.empty:
                logger.warning("未获取到 ETF 基础数据")
                return success([])
            
            logger.info(f"获取到 ETF 基础数据: {len(fund_basic_df)} 条")

            # 构建名称和类型字典
            name_dict = {}
            fund_type_dict = {}
            for _, row in fund_basic_df.iterrows():
                ts_code = str(row['ts_code'])
                name_dict[ts_code] = str(row.get('name', ''))
                fund_type_dict[ts_code] = str(row.get('fund_type', ''))

            # 使用 fund_daily 获取 ETF 日行情（按交易日期拉取全市场 ETF）
            logger.info(f"开始获取 {query_date} 的 ETF 日行情")
            fund_daily_df = self.tushare_service.api.fund_daily(trade_date=query_date)
            
            # 如果无数据，尝试查找最近交易日
            if fund_daily_df is None or fund_daily_df.empty:
                logger.info(f"日期 {query_date} 无 ETF 数据，尝试查找最近交易日")
                latest_trade_date = _find_latest_trade_date(self.tushare_service.api)
                if latest_trade_date:
                    fund_daily_df = self.tushare_service.api.fund_daily(trade_date=latest_trade_date)
                    query_date = latest_trade_date
                    logger.info(f"使用最近交易日 {query_date} 的 ETF 数据")

            if fund_daily_df is None or fund_daily_df.empty:
                logger.warning("未获取到 ETF 日行情数据")
                return success([])

            logger.info(f"获取到 {len(fund_daily_df)} 条 ETF 日行情数据")

            # 按成交额排序，筛选宽基/行业 ETF
            fund_daily_df = fund_daily_df.sort_values('amount', ascending=False)

            etf_items = []
            for _, row in fund_daily_df.iterrows():
                if len(etf_items) >= limit:
                    break
                    
                ts_code = str(row['ts_code'])
                name = name_dict.get(ts_code, "")
                
                # 过滤：只保留名称包含常见 ETF 关键词的
                if not name:
                    continue
                
                # 确定类别
                if any(kw in name for kw in ['300', '500', '沪深', '上证', '创业板', '科创', 'A50']):
                    category = "宽基"
                elif any(kw in name for kw in ['银行', '证券', '保险', '医药', '消费', '科技', '新能源', '芯片', '半导体', '军工', '医疗', '食品']):
                    category = "行业"
                else:
                    category = "其他"

                etf_item = ETFItem(
                    symbol=ts_code.split('.')[0],
                    name=name,
                    category=category,
                    latest_price=float(row['close']) if 'close' in row else 0.0,
                    pct_change=float(row['pct_chg']) if 'pct_chg' in row else 0.0,
                    volume=int(float(row['vol'])) if 'vol' in row else 0
                )
                etf_items.append(etf_item)

            logger.info(f"生成 {len(etf_items)} 条 ETF 数据")

            # 保存到数据库
            trade_date_obj = datetime.strptime(query_date, "%Y%m%d").date()
            _save_etfs_to_db(etf_items, trade_date_obj)

            # 缓存
            _set_cache(cache_key, [item.model_dump() for item in etf_items])

            return success(etf_items)

        except Exception as e:
            logger.error(f"获取 ETF 列表失败: {e}", exc_info=True)
            # 降级策略：1. 内存缓存 -> 2. 数据库 -> 3. 空列表
            if cache_key in _cache:
                logger.info("使用过期缓存的 ETF 列表")
                return success(_cache[cache_key])
            
            # 尝试从数据库加载
            db_etfs = _load_etfs_from_db(limit)
            if db_etfs:
                logger.info(f"从数据库降级加载 {len(db_etfs)} 条 ETF 数据")
                _set_cache(cache_key, db_etfs, ttl_minutes=60)  # 延长缓存时间
                return success(db_etfs)
            
            return success([])