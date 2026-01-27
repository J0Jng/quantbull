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


def _find_latest_trade_date(tushare_api, max_days_back: int = 10) -> Optional[str]:
    """
    查找最近的交易日（返回 YYYYMMDD 格式）
    从今天开始向前查找，直到找到有数据的交易日
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


class MarketService:
    """市场数据服务"""

    def __init__(self):
        self.tushare_service = TushareService()

    def get_market_overview(self, date: Optional[str] = None) -> Dict:
        """
        获取市场概览
        
        Args:
            date: 交易日期 YYYY-MM-DD，不传则使用最近交易日
        """
        cache_key = f"market_overview_{date}" if date else "market_overview_latest"

        # 检查缓存
        if _is_cache_valid(cache_key):
            logger.info(f"使用缓存的市场概览数据: {cache_key}")
            return success(_cache[cache_key])

        try:
            # 确定查询日期
            if date:
                # 将 YYYY-MM-DD 转换为 YYYYMMDD
                query_date = date.replace("-", "")
            else:
                query_date = datetime.now().strftime("%Y%m%d")

            # 获取上证指数数据 (000001.SH)
            indices_data = self.tushare_service.api.index_daily(ts_code="000001.SH", trade_date=query_date)

            # 如果无数据，尝试查找最近交易日
            if indices_data is None or indices_data.empty:
                logger.info(f"日期 {query_date} 无数据，尝试查找最近交易日")
                latest_trade_date = _find_latest_trade_date(self.tushare_service.api)
                if latest_trade_date:
                    indices_data = self.tushare_service.api.index_daily(ts_code="000001.SH", trade_date=latest_trade_date)
                    query_date = latest_trade_date

            if indices_data is not None and not indices_data.empty:
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

                # 格式化交易日期
                if len(query_date) == 8:
                    formatted_date = f"{query_date[:4]}-{query_date[4:6]}-{query_date[6:8]}"
                else:
                    formatted_date = query_date

                data = MarketOverviewData(
                    trade_date=formatted_date,
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
                    trade_date=date or datetime.now().strftime("%Y-%m-%d"),
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
                    trade_date=date or datetime.now().strftime("%Y-%m-%d"),
                    market_status="未知",
                    indices=[],
                    total_turnover=0.0
                )
                return success(empty_data)

    def is_trading_day(self, date: str) -> Dict:
        """
        判断给定日期是否为交易日（基于 Tushare 交易日历）

        Args:
            date: 日期 YYYY-MM-DD
        """
        query_date = date.replace("-", "")
        try:
            df = self.tushare_service.api.trade_cal(
                exchange="SSE",
                start_date=query_date,
                end_date=query_date,
            )

            if df is None or df.empty:
                return success(
                    {
                        "date": date,
                        "is_trading_day": False,
                        "source": "trade_cal",
                    }
                )

            row = df.iloc[0]
            is_open = int(row.get("is_open", 0)) == 1
            cal_date = str(row.get("cal_date") or query_date)
            if len(cal_date) == 8:
                formatted_date = f"{cal_date[:4]}-{cal_date[4:6]}-{cal_date[6:8]}"
            else:
                formatted_date = cal_date

            return success(
                {
                    "date": formatted_date,
                    "is_trading_day": is_open,
                    "source": "trade_cal",
                }
            )
        except Exception as e:
            logger.error(f"交易日判断失败: {e}")
            return success(
                {
                    "date": date,
                    "is_trading_day": False,
                    "source": "trade_cal_error",
                }
            )