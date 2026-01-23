"""
财经日历服务
从金十数据获取未来宏观经济事件日历
"""
import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Iterable
from urllib.parse import urljoin

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

    @staticmethod
    def _normalize_date(value: Optional[str]) -> Optional[str]:
        if not value:
            return None
        value = value.strip()
        if not value:
            return None
        value = value.replace('/', '-').replace('.', '-')
        match = re.search(r"(\d{4})[-年](\d{1,2})[-月](\d{1,2})", value)
        if match:
            y, m, d = match.groups()
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", value)
        if match:
            y, m, d = match.groups()
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        return None

    @staticmethod
    def _importance_from_raw(raw: Any) -> int:
        if raw is None:
            return 3
        if isinstance(raw, (int, float)):
            value = int(raw)
            return max(1, min(5, value))
        raw_text = str(raw).strip()
        if raw_text.isdigit():
            return max(1, min(5, int(raw_text)))
        mapping = {
            "低": 1,
            "较低": 2,
            "中": 3,
            "高": 4,
            "极高": 5,
            "重要": 4,
            "非常重要": 5,
        }
        for key, value in mapping.items():
            if key in raw_text:
                return value
        return 3

    @staticmethod
    def _importance_text(level: int) -> str:
        if level <= 2:
            return "低"
        if level == 3:
            return "中"
        if level == 4:
            return "高"
        return "极高"

    @staticmethod
    def _safe_pick(data: Dict[str, Any], keys: Iterable[str]) -> Optional[Any]:
        for key in keys:
            if key in data and data[key] not in (None, ""):
                return data[key]
        return None

    async def _get_json_with_retry(self, client: httpx.AsyncClient, url: str, params: Optional[dict] = None) -> Optional[dict]:
        for attempt in range(3):
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except Exception as exc:
                if attempt == 2:
                    logger.warning(f"获取日历数据失败: {exc}")
                    return None
                await asyncio.sleep(0.5 * (2 ** attempt))
        return None

    async def _get_text_with_retry(self, client: httpx.AsyncClient, url: str, params: Optional[dict] = None) -> Optional[str]:
        for attempt in range(3):
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.text
            except Exception as exc:
                if attempt == 2:
                    logger.warning(f"获取日历文本失败: {exc}")
                    return None
                await asyncio.sleep(0.5 * (2 ** attempt))
        return None

    async def _fetch_eastmoney_calendar(self, client: httpx.AsyncClient, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        params = {
            "reportName": "RPT_ECONOMIC_CALENDAR",
            "columns": "ALL",
            "pageNumber": 1,
            "pageSize": 200,
            "sortColumns": "EVENT_DATE",
            "sortTypes": "1",
            "filter": f"(EVENT_DATE>='{start_date}')(EVENT_DATE<='{end_date}')"
        }
        payload = await self._get_json_with_retry(client, url, params=params)
        if not payload:
            return []
        data = payload.get("result", {}).get("data") or payload.get("data") or []
        items: List[Dict[str, Any]] = []
        for row in data:
            date_raw = self._safe_pick(row, ["EVENT_DATE", "DATE", "REPORT_DATE", "PUBLISH_DATE", "PUB_DATE"])
            date_value = self._normalize_date(str(date_raw) if date_raw else None)
            if not date_value:
                continue
            title = self._safe_pick(row, ["EVENT_NAME", "EVENT", "TITLE", "INDICATOR_NAME", "NAME"])
            if not title:
                continue
            country = self._safe_pick(row, ["COUNTRY", "COUNTRY_NAME", "AREA", "REGION"])
            event = f"{country} {title}".strip() if country else str(title).strip()
            importance_raw = self._safe_pick(row, ["IMPORTANCE", "STAR", "LEVEL", "IMPORTANCE_LEVEL"])
            importance = self._importance_from_raw(importance_raw)
            items.append({
                "date": date_value,
                "event": event,
                "importance": importance,
                "importance_text": self._importance_text(importance),
                "source": "eastmoney",
                "url": self._safe_pick(row, ["URL", "INFO_URL", "DETAIL_URL", "LINK"]) or None
            })
        return items

    async def _fetch_jin10_calendar(self, client: httpx.AsyncClient, dates: List[str]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []

        async def fetch_day(day: str) -> List[Dict[str, Any]]:
            url = "https://rili.jin10.com/datas"
            payload = await self._get_json_with_retry(client, url, params={"date": day})
            if not payload:
                return []
            data = payload.get("data") if isinstance(payload, dict) else payload
            if not isinstance(data, list):
                return []
            day_items: List[Dict[str, Any]] = []
            for row in data:
                title = row.get("name") or row.get("event") or row.get("title") or row.get("indicator")
                if not title:
                    continue
                country = row.get("country") or row.get("country_name")
                event = f"{country} {title}".strip() if country else str(title).strip()
                importance_raw = row.get("star") or row.get("importance") or row.get("level")
                importance = self._importance_from_raw(importance_raw)
                url_value = row.get("link") or row.get("url")
                day_items.append({
                    "date": day,
                    "event": event,
                    "importance": importance,
                    "importance_text": self._importance_text(importance),
                    "source": "jin10",
                    "url": urljoin("https://rili.jin10.com/", url_value) if url_value else None
                })
            return day_items

        tasks = [fetch_day(day) for day in dates]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for result in results:
            if isinstance(result, Exception):
                continue
            items.extend(result)
        return items
    
    async def fetch_calendar_events(
        self,
        days: int = 14,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        抓取财经日历事件（未来N天）
        
        Args:
            days: 查询未来多少天
            
        Returns:
            日历事件列表
        """
        try:
            base_date = datetime.now().date()
            start_value = self._normalize_date(start_date) if start_date else None
            end_value = self._normalize_date(end_date) if end_date else None
            if start_value and end_value:
                start_obj = datetime.strptime(start_value, "%Y-%m-%d").date()
                end_obj = datetime.strptime(end_value, "%Y-%m-%d").date()
            elif start_value:
                start_obj = datetime.strptime(start_value, "%Y-%m-%d").date()
                end_obj = start_obj + timedelta(days=days)
            else:
                start_obj = base_date
                end_obj = base_date + timedelta(days=days)

            if end_obj < start_obj:
                start_obj, end_obj = end_obj, start_obj

            start_str = start_obj.strftime("%Y-%m-%d")
            end_str = end_obj.strftime("%Y-%m-%d")
            total_days = (end_obj - start_obj).days
            date_list = [
                (start_obj + timedelta(days=offset)).strftime("%Y-%m-%d")
                for offset in range(total_days + 1)
            ]

            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                items = await self._fetch_eastmoney_calendar(client, start_str, end_str)
                if not items:
                    items = await self._fetch_jin10_calendar(client, date_list)

            logger.info(f"成功抓取 {len(items)} 个日历事件")
            return items

        except Exception as e:
            logger.error(f"抓取财经日历失败：{e}")
            return []

    def _filter_by_date(self, items: List[Dict[str, Any]], start_date: Optional[str], end_date: Optional[str]) -> List[Dict[str, Any]]:
        if not items:
            return []
        start_value = self._normalize_date(start_date) if start_date else None
        end_value = self._normalize_date(end_date) if end_date else None
        if not start_value and not end_value:
            return items
        start_obj = datetime.strptime(start_value, "%Y-%m-%d").date() if start_value else None
        end_obj = datetime.strptime(end_value, "%Y-%m-%d").date() if end_value else None
        filtered: List[Dict[str, Any]] = []
        for item in items:
            item_date = self._normalize_date(item.get("date"))
            if not item_date:
                continue
            item_obj = datetime.strptime(item_date, "%Y-%m-%d").date()
            if start_obj and item_obj < start_obj:
                continue
            if end_obj and item_obj > end_obj:
                continue
            item["date"] = item_date
            filtered.append(item)
        return filtered
    
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
                cached_data["items"] = self._filter_by_date(cached_data.get("items", []), start_date, end_date)
                return cached_data
            
            # 2. 缓存过期或不存在，重新抓取
            logger.info("缓存过期或不存在，重新抓取日历数据")
            items = await self.fetch_calendar_events(days=14, start_date=start_date, end_date=end_date)
            items = self._filter_by_date(items, start_date, end_date)
            
            if not items:
                # 抓取失败，返回过期缓存（如果有）
                if cached_data:
                    logger.warning("抓取失败，返回过期缓存数据")
                    cached_data["items"] = self._filter_by_date(cached_data.get("items", []), start_date, end_date)
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
            await self.save_to_cache(items, source="aggregated")
            
            # 4. 返回新数据
            return {
                "items": items,
                "cached": False,
                "stale": False,
                "source": "aggregated",
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"聚合日历数据失败：{e}", exc_info=True)
            
            # 降级：尝试返回缓存
            cached_data = await self.get_from_cache()
            if cached_data:
                logger.warning("发生异常，返回缓存数据")
                cached_data["items"] = self._filter_by_date(cached_data.get("items", []), start_date, end_date)
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
