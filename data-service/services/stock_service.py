import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.response import success
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

            # 缓存
            _set_cache(cache_key, [item.model_dump() for item in stock_items])

            return success(stock_items)

        except Exception as e:
            logger.error(f"获取股票列表失败: {e}", exc_info=True)
            # 降级：返回缓存或空列表
            if cache_key in _cache:
                logger.info("使用过期缓存的股票列表")
                return success(_cache[cache_key])
            else:
                return success([])