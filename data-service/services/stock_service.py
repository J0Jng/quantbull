import logging
from datetime import datetime, timedelta
from typing import Dict, List

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


class StockService:
    """股票数据服务"""

    def __init__(self):
        self.tushare_service = TushareService()

    def get_stock_list(self, limit: int = 100) -> Dict:
        """获取股票候选池"""
        cache_key = "stock_list"

        # 检查缓存
        if _is_cache_valid(cache_key):
            logger.info("使用缓存的股票列表")
            return success(_cache[cache_key])

        try:
            # 获取股票基础信息
            stock_basic_df = self.tushare_service.api.stock_basic(list_status='L')  # L 为上市

            if stock_basic_df.empty:
                logger.warning("未获取到股票基础数据")
                return success([])

            # 过滤一些行业（简化：选择市值较大的）
            stock_codes = []
            for _, row in stock_basic_df.iterrows():
                ts_code = str(row['ts_code'])
                stock_codes.append(ts_code)
                if len(stock_codes) >= limit * 2:
                    break

            if not stock_codes:
                return success([])

            # 获取最新日行情
            today = datetime.now().strftime("%Y%m%d")
            daily_df = self.tushare_service.api.daily(ts_code=','.join(stock_codes[:limit]), trade_date=today)

            if daily_df.empty:
                # 尝试昨日
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
                daily_df = self.tushare_service.api.daily(ts_code=','.join(stock_codes[:limit]), trade_date=yesterday)

            stock_items = []
            for _, row in daily_df.iterrows():
                ts_code = str(row['ts_code'])
                name = str(row['name']) if 'name' in row else "未知"
                # 行业简化（Tushare 有 industry，但这里简化）
                industry = "未知"  # 可扩展

                item = StockItem(
                    symbol=ts_code.split('.')[0],  # 移除 .SH/.SZ
                    name=name,
                    industry=industry,
                    latest_price=float(row['close']),
                    pct_change=float(row['pct_chg']),
                    turnover_rate=float(row['turnover_rate']) if 'turnover_rate' in row else 0.0
                )
                stock_items.append(item)

            # 缓存
            _set_cache(cache_key, [item.model_dump() for item in stock_items])

            return success(stock_items)

        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            # 降级：返回缓存或空列表
            if cache_key in _cache:
                logger.info("使用过期缓存的股票列表")
                return success(_cache[cache_key])
            else:
                return success([])