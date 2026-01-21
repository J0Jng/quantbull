"""
市场数据聚合服务
从东方财富网获取市场指数、汇率、黄金等实时行情数据
"""
import asyncio
import hashlib
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.finance_channel_cache import FinanceChannelCache

logger = logging.getLogger(__name__)


class MarketDataAggregator:
    """市场数据聚合器"""
    
    # 东方财富网行情接口配置
    MARKET_QUOTES = [
        {"code": "1.000001", "title": "上证指数", "url_code": "sh000001"},
        {"code": "0.399001", "title": "深证成指", "url_code": "sz399001"},
        {"code": "0.399006", "title": "创业板指", "url_code": "sz399006"},
        {"code": "1.000300", "title": "沪深300", "url_code": "sh000300"},
        {"code": "1.000016", "title": "上证50", "url_code": "sh000016"},
        {"code": "0.399005", "title": "中小板指", "url_code": "sz399005"},
    ]
    
    # 缓存 TTL（秒）
    CACHE_TTL = 300  # 5 分钟
    
    def __init__(
        self,
        cache_ttl: int = CACHE_TTL,
        timeout: int = 10,
        db_session: Optional[AsyncSession] = None
    ):
        """
        初始化市场数据聚合器
        
        Args:
            cache_ttl: 缓存过期时间（秒）
            timeout: HTTP 请求超时时间（秒）
            db_session: 数据库会话
        """
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.db_session = db_session
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/',
        }
    
    async def fetch_quote(self, quote_config: Dict[str, str], client: httpx.AsyncClient) -> Optional[Dict[str, Any]]:
        """
        抓取单个行情数据
        
        Args:
            quote_config: 行情配置 {code, title, url_code}
            client: httpx 客户端
            
        Returns:
            行情数据字典或 None
        """
        code = quote_config.get("code")
        title = quote_config.get("title")
        url_code = quote_config.get("url_code", "")
        
        try:
            # 东方财富网实时行情接口
            url = f"http://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": code,
                "fields": "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f60,f107,f152,f169,f170,f171",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            }
            
            response = await client.get(url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            if not data or data.get("rc") != 0:
                logger.warning(f"行情接口返回错误：{code} - {data}")
                return None
            
            quote_data = data.get("data")
            if not quote_data:
                logger.warning(f"行情数据为空：{code}")
                return None
            
            # 解析字段
            current_price = quote_data.get("f43")  # 当前价
            change_pct = quote_data.get("f170")     # 涨跌幅
            
            if current_price is None or change_pct is None:
                logger.warning(f"行情数据不完整：{code} - price={current_price}, change={change_pct}")
                return None
            
            # 格式化返回
            return {
                "code": code,
                "title": title,
                "value": f"{current_price / 100:.2f}" if current_price > 1000 else f"{current_price:.2f}",
                "change_pct": round(change_pct / 100, 2),
                "updated_at": datetime.now().isoformat()
            }
            
        except httpx.TimeoutException:
            logger.warning(f"行情请求超时：{code}")
            return None
        except Exception as e:
            logger.error(f"抓取行情失败：{code} - {e}")
            return None
    
    async def fetch_all_quotes(self) -> List[Dict[str, Any]]:
        """
        抓取所有配置的行情数据
        
        Returns:
            行情数据列表
        """
        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_quote(config, client) for config in self.MARKET_QUOTES]
            results = await asyncio.gather(*tasks)
            
            # 过滤掉 None
            valid_results = [r for r in results if r is not None]
            
            logger.info(f"成功抓取 {len(valid_results)}/{len(self.MARKET_QUOTES)} 个行情数据")
            return valid_results
    
    async def get_from_cache(self) -> Optional[Dict[str, Any]]:
        """
        从数据库缓存获取数据
        
        Returns:
            缓存数据或 None
        """
        if not self.db_session:
            return None
        
        try:
            stmt = select(FinanceChannelCache).where(
                FinanceChannelCache.cache_key == "market"
            ).order_by(FinanceChannelCache.fetched_at.desc())
            
            result = await self.db_session.execute(stmt)
            cache_record = result.scalars().first()
            
            if not cache_record:
                return None
            
            now = datetime.now()
            is_stale = now > cache_record.expires_at
            
            return {
                "items": cache_record.payload_json.get("items", []),
                "cached": True,
                "stale": is_stale,
                "source": cache_record.source,
                "updated_at": cache_record.fetched_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"从缓存读取市场数据失败：{e}")
            return None
    
    async def save_to_cache(self, items: List[Dict[str, Any]], source: str = "eastmoney") -> None:
        """
        保存数据到数据库缓存
        
        Args:
            items: 行情数据列表
            source: 数据源
        """
        if not self.db_session:
            return
        
        try:
            now = datetime.now()
            expires_at = now + timedelta(seconds=self.cache_ttl)
            
            # 查找现有记录
            stmt = select(FinanceChannelCache).where(
                FinanceChannelCache.cache_key == "market"
            )
            result = await self.db_session.execute(stmt)
            cache_record = result.scalars().first()
            
            if cache_record:
                # 更新现有记录
                cache_record.payload_json = {"items": items}
                cache_record.source = source
                cache_record.fetched_at = now
                cache_record.expires_at = expires_at
                cache_record.updated_at = now
            else:
                # 创建新记录
                cache_record = FinanceChannelCache(
                    cache_key="market",
                    module="market",
                    payload_json={"items": items},
                    source=source,
                    fetched_at=now,
                    expires_at=expires_at
                )
                self.db_session.add(cache_record)
            
            await self.db_session.commit()
            logger.info("市场数据已保存到缓存")
            
        except Exception as e:
            logger.error(f"保存市场数据到缓存失败：{e}")
            await self.db_session.rollback()
    
    async def aggregate_market_data(self) -> Dict[str, Any]:
        """
        聚合市场数据（缓存优先，失败降级）
        
        Returns:
            市场数据响应字典
        """
        try:
            # 1. 尝试从缓存读取
            cached_data = await self.get_from_cache()
            
            if cached_data and not cached_data["stale"]:
                # 缓存有效，直接返回
                logger.info("使用有效缓存的市场数据")
                return cached_data
            
            # 2. 缓存过期或不存在，重新抓取
            logger.info("缓存过期或不存在，重新抓取市场数据")
            items = await self.fetch_all_quotes()
            
            if not items:
                # 抓取失败，返回过期缓存（如果有）
                if cached_data:
                    logger.warning("抓取失败，返回过期缓存数据")
                    return cached_data
                else:
                    logger.error("抓取失败且无缓存数据")
                    return {
                        "items": [],
                        "cached": False,
                        "stale": True,
                        "source": "none",
                        "updated_at": datetime.now().isoformat()
                    }
            
            # 3. 保存到缓存
            await self.save_to_cache(items, source="eastmoney")
            
            # 4. 返回新数据
            return {
                "items": items,
                "cached": False,
                "stale": False,
                "source": "eastmoney",
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"聚合市场数据失败：{e}", exc_info=True)
            
            # 降级：尝试返回缓存
            cached_data = await self.get_from_cache()
            if cached_data:
                logger.warning("发生异常，返回缓存数据")
                return cached_data
            
            # 无缓存，返回空数据
            return {
                "items": [],
                "cached": False,
                "stale": True,
                "source": "none",
                "updated_at": datetime.now().isoformat()
            }


# 全局单例
_market_data_aggregator: Optional[MarketDataAggregator] = None


def get_market_data_aggregator(db_session: Optional[AsyncSession] = None) -> MarketDataAggregator:
    """获取市场数据聚合器单例"""
    global _market_data_aggregator
    if _market_data_aggregator is None or db_session is not None:
        _market_data_aggregator = MarketDataAggregator(db_session=db_session)
    return _market_data_aggregator
