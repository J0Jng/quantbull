import logging
from datetime import datetime, timedelta
from typing import Dict, List

from core.response import success
from schemas.etf import ETFItem
from services.tushare_service import TushareService
from services.eastmoney_spider import EastMoneySpider

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


class ETFService:
    """ETF 数据服务"""

    def __init__(self):
        self.tushare_service = TushareService()
        self.spider = EastMoneySpider()

    def get_etf_list(self, limit: int = 50) -> Dict:
        """获取 ETF 候选池"""
        cache_key = "etf_list"

        # 检查缓存
        if _is_cache_valid(cache_key):
            logger.info("使用缓存的 ETF 列表")
            return success(_cache[cache_key])

        try:
            # 获取 ETF 基础信息
            logger.info("开始获取 ETF 基础信息")
            fund_basic_df = self.tushare_service.api.fund_basic(market='E')  # E 为场内 ETF
            logger.info(f"获取到 ETF 基础数据: {len(fund_basic_df)} 条")

            if fund_basic_df.empty:
                logger.warning("未获取到 ETF 基础数据")
                return success([])

            # 过滤宽基 ETF（名称包含 '300' 或 '500' 或 '沪深' 等）
            etf_codes = []
            for _, row in fund_basic_df.iterrows():
                name = str(row['name'])
                ts_code = str(row['ts_code'])
                logger.debug(f"检查 ETF: {ts_code} - {name}")
                if '300' in name or '500' in name or '沪深' in name or '上证' in name or '创业板' in name:
                    etf_codes.append(ts_code)
                    logger.debug(f"添加 ETF: {ts_code}")
                    if len(etf_codes) >= limit * 2:  # 多取一些
                        break

            logger.info(f"过滤后 ETF 代码数量: {len(etf_codes)}")
            if not etf_codes:
                logger.warning("无符合条件的 ETF")
                return success([])

            # 使用东方财富获取实时行情
            logger.info(f"获取 ETF 实时行情，代码: {etf_codes[:limit]}")
            # 转换为纯数字代码
            pure_codes = [code.split('.')[0] for code in etf_codes[:limit]]
            success_items, failed_codes = self.spider.fetch_quotes(pure_codes)
            logger.info(f"获取到 ETF 实时数据: {len(success_items)} 条")

            # 合并名称
            name_dict = {row['ts_code']: row['name'] for _, row in fund_basic_df.iterrows() if row['ts_code'] in etf_codes}

            etf_items = []
            for item in success_items:
                ts_code = item.code + ('.SZ' if item.code.startswith(('0', '1', '3')) else '.SH')
                name = name_dict.get(ts_code, "未知")
                # 类别简化
                if '300' in name:
                    category = "宽基"
                elif '500' in name:
                    category = "宽基"
                else:
                    category = "行业"

                etf_item = ETFItem(
                    symbol=item.code,
                    name=name,
                    category=category,
                    latest_price=item.price,
                    pct_change=item.pct_change,
                    volume=item.turnover  # 使用成交额作为成交量近似 # type: ignore
                )
                etf_items.append(etf_item)

            logger.info(f"生成 ETF 项数量: {len(etf_items)}")

            # 缓存
            _set_cache(cache_key, [item.model_dump() for item in etf_items])

            return success(etf_items)

        except Exception as e:
            logger.error(f"获取 ETF 列表失败: {e}")
            # 降级：返回缓存或空列表
            if cache_key in _cache:
                logger.info("使用过期缓存的 ETF 列表")
                return success(_cache[cache_key])
            else:
                return success([])