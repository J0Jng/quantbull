import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from core.response import success
from schemas.market import IndexItem, MarketOverviewData
from services.tushare_service import TushareService

logger = logging.getLogger(__name__)

# 简单内存缓存
_cache: Dict[str, Dict] = {}
_cache_expiry: Dict[str, datetime] = {}


def _is_cache_valid(key: str, ttl_minutes: int = 10) -> bool:
    """检查缓存是否有效"""
    if key not in _cache_expiry:
        return False
    return datetime.now() < _cache_expiry[key]


def _set_cache(key: str, data: Dict, ttl_minutes: int = 10):
    """设置缓存"""
    _cache[key] = data
    _cache_expiry[key] = datetime.now() + timedelta(minutes=ttl_minutes)


class MarketService:
    """市场数据服务"""

    def __init__(self):
        self.tushare_service = TushareService()

    def get_market_overview(self) -> Dict:
        """获取市场概览"""
        cache_key = "market_overview"

        # 检查缓存
        if _is_cache_valid(cache_key):
            logger.info("使用缓存的市场概览数据")
            return success(_cache[cache_key])

        try:
            # 获取今日日期
            today = datetime.now().strftime("%Y%m%d")

            # 获取上证指数数据 (000001.SH)
            indices_data = self.tushare_service.api.index_daily(ts_code="000001.SH", trade_date=today)

            if indices_data.empty:
                # 如果今日无数据，尝试昨日
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
                indices_data = self.tushare_service.api.index_daily(ts_code="000001.SH", trade_date=yesterday)
                trade_date = yesterday
            else:
                trade_date = today

            if not indices_data.empty:
                row = indices_data.iloc[0]
                index_item = IndexItem(
                    symbol="000001.SH",
                    name="上证指数",
                    close=float(row['close']),
                    pct_change=float(row['pct_chg'])
                )
                indices = [index_item]

                # 简单判断市场状态
                pct_change = index_item.pct_change
                if pct_change > 1.0:
                    market_status = "bull"
                elif pct_change < -1.0:
                    market_status = "bear"
                else:
                    market_status = "震荡"

                # 总成交额（简化，从指数数据获取）
                total_turnover = float(row['amount']) * 10000  # 万元转元

                data = MarketOverviewData(
                    trade_date=datetime.strptime(trade_date, "%Y%m%d").strftime("%Y-%m-%d"),
                    market_status=market_status,
                    indices=indices,
                    total_turnover=total_turnover
                )

                # 缓存
                _set_cache(cache_key, data.model_dump())

                return success(data)
            else:
                # 降级：返回空数据
                logger.warning("无法获取指数数据，返回空数据")
                empty_data = MarketOverviewData(
                    trade_date=datetime.now().strftime("%Y-%m-%d"),
                    market_status="未知",
                    indices=[],
                    total_turnover=0.0
                )
                return success(empty_data)

        except Exception as e:
            logger.error(f"获取市场概览失败: {e}")
            # 降级：返回缓存或空数据
            if cache_key in _cache:
                logger.info("使用过期缓存的市场概览数据")
                return success(_cache[cache_key])
            else:
                empty_data = MarketOverviewData(
                    trade_date=datetime.now().strftime("%Y-%m-%d"),
                    market_status="未知",
                    indices=[],
                    total_turnover=0.0
                )
                return success(empty_data)