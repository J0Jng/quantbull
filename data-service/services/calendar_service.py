"""
财经日历服务
从金十数据获取未来宏观经济事件日历
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.finance_channel_cache import FinanceChannelCache

logger = logging.getLogger(__name__)


class CalendarAggregator:
    """财经日历聚合器"""
    
    # 缓存 TTL（秒）
    CACHE_TTL = 21600  # 6 小时
    
    # 重要性映射
    IMPORTANCE_MAP = {
        "低": 1,
        "中": 3,
        "高": 4,
        "极高": 5,
    }
    
    def __init__(
        self,
        cache_ttl: int = CACHE_TTL,
        timeout: int = 15,
        db_session: Optional[AsyncSession] = None
    ):
        """
        初始化财经日历聚合器
        
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
        }
    
    async def fetch_calendar_events(self, days: int = 14) -> List[Dict[str, Any]]:
        """
        抓取财经日历事件（未来N天）
        
        Args:
            days: 查询未来多少天
            
        Returns:
            日历事件列表
        """
        try:
            # 构造模拟数据（真实场景需要对接金十数据或其他API）
            # 这里提供一个示例实现
            events = []
            base_date = datetime.now()
            
            # 模拟未来14天的重要经济事件
            sample_events = [
                {"days_offset": 1, "event": "美国CPI数据发布", "importance": 5, "importance_text": "极高"},
                {"days_offset": 2, "event": "欧央行利率决议", "importance": 4, "importance_text": "高"},
                {"days_offset": 3, "event": "中国制造业PMI数据", "importance": 3, "importance_text": "中"},
                {"days_offset": 5, "event": "美国非农就业数据", "importance": 5, "importance_text": "极高"},
                {"days_offset": 7, "event": "美联储利率决议", "importance": 5, "importance_text": "极高"},
                {"days_offset": 8, "event": "中国GDP季度数据", "importance": 5, "importance_text": "极高"},
                {"days_offset": 10, "event": "欧元区制造业PMI", "importance": 3, "importance_text": "中"},
                {"days_offset": 12, "event": "日本央行货币政策会议", "importance": 4, "importance_text": "高"},
                {"days_offset": 14, "event": "美国零售销售数据", "importance": 4, "importance_text": "高"},
            ]
            
            for evt in sample_events:
                event_date = base_date + timedelta(days=evt["days_offset"])
                events.append({
                    "date": event_date.strftime("%Y-%m-%d"),
                    "event": evt["event"],
                    "importance": evt["importance"],
                    "importance_text": evt["importance_text"],
                    "source": "simulated",
                    "url": None
                })
            
            logger.info(f"成功构造 {len(events)} 个日历事件")
            return events
            
        except Exception as e:
            logger.error(f"抓取财经日历失败：{e}")
            return []
    
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
                FinanceChannelCache.cache_key == "calendar"
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
            logger.error(f"从缓存读取日历数据失败：{e}")
            return None
    
    async def save_to_cache(self, items: List[Dict[str, Any]], source: str = "simulated") -> None:
        """
        保存数据到数据库缓存
        
        Args:
            items: 日历事件列表
            source: 数据源
        """
        if not self.db_session:
            return
        
        try:
            now = datetime.now()
            expires_at = now + timedelta(seconds=self.cache_ttl)
            
            # 查找现有记录
            stmt = select(FinanceChannelCache).where(
                FinanceChannelCache.cache_key == "calendar"
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
                    cache_key="calendar",
                    module="calendar",
                    payload_json={"items": items},
                    source=source,
                    fetched_at=now,
                    expires_at=expires_at
                )
                self.db_session.add(cache_record)
            
            await self.db_session.commit()
            logger.info("日历数据已保存到缓存")
            
        except Exception as e:
            logger.error(f"保存日历数据到缓存失败：{e}")
            await self.db_session.rollback()
    
    async def aggregate_calendar(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        聚合财经日历数据（缓存优先，失败降级）
        
        Args:
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            日历数据响应字典
        """
        try:
            # 1. 尝试从缓存读取
            cached_data = await self.get_from_cache()
            
            if cached_data and not cached_data["stale"]:
                # 缓存有效，直接返回
                logger.info("使用有效缓存的日历数据")
                return cached_data
            
            # 2. 缓存过期或不存在，重新抓取
            logger.info("缓存过期或不存在，重新抓取日历数据")
            items = await self.fetch_calendar_events(days=14)
            
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
            await self.save_to_cache(items, source="simulated")
            
            # 4. 返回新数据
            return {
                "items": items,
                "cached": False,
                "stale": False,
                "source": "simulated",
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"聚合日历数据失败：{e}", exc_info=True)
            
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
_calendar_aggregator: Optional[CalendarAggregator] = None


def get_calendar_aggregator(db_session: Optional[AsyncSession] = None) -> CalendarAggregator:
    """获取财经日历聚合器单例"""
    global _calendar_aggregator
    if _calendar_aggregator is None or db_session is not None:
        _calendar_aggregator = CalendarAggregator(db_session=db_session)
    return _calendar_aggregator
