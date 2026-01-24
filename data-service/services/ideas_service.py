"""
投资观点聚合服务
抓取同花顺原创“独家公告解读”列表页
"""
import asyncio
import hashlib
import logging
import random
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from urllib.parse import urljoin

import html as html_lib
import httpx
from lxml import html as lxml_html
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.finance_channel_cache import FinanceChannelCache
from models.finance_channel_idea import FinanceChannelIdea

logger = logging.getLogger(__name__)


class IdeasAggregator:
    """投资观点聚合器"""

    # 缓存 TTL（秒）
    CACHE_TTL = 1800  # 30 分钟
    CACHE_MAX_ITEMS = 50

    BASE_LIST_URL = "https://yuanchuang.10jqka.com.cn/djggjd_list/"
    LIST_URL_TEMPLATE = "https://yuanchuang.10jqka.com.cn/djggjd_list/index_{page}.shtml"
    SOURCE_NAME = "10jqka-独家公告解读"

    retry_statuses = {429, 502, 503, 504}
    max_retries = 3
    base_backoff = 0.5

    def __init__(
        self,
        cache_ttl: int = CACHE_TTL,
        timeout: int = 10,
        db_session: Optional[AsyncSession] = None
    ):
        """
        初始化投资观点聚合器

        Args:
            cache_ttl: 缓存过期时间（秒）
            timeout: HTTP 请求超时时间（秒）
            db_session: 数据库会话
        """
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.db_session = db_session

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": self.BASE_LIST_URL,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    @staticmethod
    def _clean_text(value: str) -> str:
        text = value or ""
        text = html_lib.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _generate_id(source: str, title: str, publish_time: str, url: Optional[str]) -> str:
        raw = url or f"{source}|{title}|{publish_time}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _extract_date_from_url(url: str) -> Optional[Tuple[int, int, int]]:
        match = re.search(r"(20\d{2})[/-]?(\d{2})[/-]?(\d{2})", url)
        if not match:
            return None
        year, month, day = match.groups()
        return int(year), int(month), int(day)

    @staticmethod
    def _extract_time_from_text(text: str) -> Optional[Tuple[int, int, Optional[str]]]:
        match = re.search(r"(\d{1,2})月(\d{1,2})日\s*(\d{1,2}:\d{2})?", text)
        if not match:
            return None
        month, day, time_part = match.groups()
        return int(month), int(day), time_part

    def _compose_publish_time(self, url: str, text: str) -> str:
        now = datetime.now()
        url_date = self._extract_date_from_url(url)
        text_time = self._extract_time_from_text(text)

        if text_time:
            month, day, time_part = text_time
            year = url_date[0] if url_date else now.year
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            if time_part:
                return f"{date_str} {time_part}"
            return date_str

        if url_date:
            year, month, day = url_date
            return f"{year:04d}-{month:02d}-{day:02d}"

        return now.strftime("%Y-%m-%d")

    def _extract_summary(self, text: str) -> Optional[str]:
        if not text:
            return None
        match = re.search(r"\[(.{10,200}?)\]", text)
        if match:
            return self._clean_text(match.group(1))
        match = re.search(r"【(.{10,200}?)】", text)
        if match:
            return self._clean_text(match.group(1))
        return None

    def _build_list_url(self, page: int) -> str:
        if page <= 1:
            return self.BASE_LIST_URL
        return self.LIST_URL_TEMPLATE.format(page=page)

    async def _get_text_with_retry(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout,
                    follow_redirects=True,
                )
                if response.status_code in self.retry_statuses:
                    raise httpx.HTTPStatusError(
                        f"Retryable status {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 404:
                    logger.warning(f"观点列表地址不存在: {url}")
                    return None
                last_exc = exc
            except httpx.TimeoutException as exc:
                last_exc = exc
            except Exception as exc:
                last_exc = exc

            if attempt < self.max_retries:
                backoff = self.base_backoff * (2 ** (attempt - 1))
                backoff += random.uniform(0, 0.2)
                await asyncio.sleep(backoff)
                continue
            break

        logger.warning(f"获取观点列表失败: {last_exc}")
        return None

    def _extract_items_from_html(self, html_text: str, list_url: str) -> List[Dict[str, Any]]:
        try:
            doc = lxml_html.fromstring(html_text)
        except Exception:
            return []

        for node in doc.xpath("//style|//script"):
            try:
                node.drop_tree()
            except Exception:
                continue

        items: List[Dict[str, Any]] = []
        seen: set[str] = set()

        list_nodes = doc.xpath("//div[contains(@class,'list-con')]//li")
        if not list_nodes:
            list_nodes = doc.xpath("//li")

        for li in list_nodes:
            title_anchor = li.xpath(".//span[contains(@class,'arc-title')]/a[contains(@class,'news-link')]")
            if not title_anchor:
                continue
            title_anchor = title_anchor[0]

            href = title_anchor.get("href")
            if not href:
                continue

            url = urljoin(list_url, href)
            if url in seen:
                continue

            title = self._clean_text(title_anchor.text_content())
            if not title or len(title) < 6:
                continue

            time_text = ""
            time_nodes = li.xpath(".//span[contains(@class,'arc-title')]/span/text()")
            if time_nodes:
                time_text = self._clean_text(" ".join(time_nodes))

            summary_anchor = li.xpath(".//a[contains(@class,'arc-cont')]")
            summary_text = ""
            if summary_anchor:
                summary_text = self._clean_text(summary_anchor[0].text_content())

            context_text = self._clean_text(" ".join([time_text, summary_text]))
            publish_time = self._compose_publish_time(url, context_text)

            summary = summary_text or self._extract_summary(context_text) or title
            content = self._clean_text(summary)[:260]

            item = {
                "id": self._generate_id(self.SOURCE_NAME, title, publish_time, url),
                "title": title,
                "author": "",
                "source": self.SOURCE_NAME,
                "content": content,
                "date": publish_time,
                "url": url,
            }
            items.append(item)
            seen.add(url)

        return items

    async def fetch_ideas(self, limit: int = 10, keyword: Optional[str] = None, page: int = 1) -> List[Dict[str, Any]]:
        """
        抓取投资观点

        Args:
            limit: 返回条数
            keyword: 关键词过滤
            page: 页码

        Returns:
            观点列表
        """
        try:
            url = self._build_list_url(page)
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                html_text = await self._get_text_with_retry(client, url)
                if not html_text:
                    return []

            items = self._extract_items_from_html(html_text, url)
            if not items:
                return []

            if keyword:
                keyword_lower = keyword.lower()
                items = [
                    item for item in items
                    if keyword_lower in item["title"].lower() or keyword_lower in item["content"].lower()
                ]

            items.sort(key=lambda x: x.get("date", ""), reverse=True)
            items = items[:limit]

            logger.info(f"成功抓取 {len(items)} 条投资观点（page={page}）")
            return items

        except Exception as e:
            logger.error(f"抓取投资观点失败：{e}", exc_info=True)
            return []

    async def _save_to_database(self, items: List[Dict[str, Any]]) -> Tuple[int, int]:
        if not self.db_session or not items:
            return 0, 0

        saved_count = 0
        updated_count = 0

        try:
            for item in items:
                idea_id = item.get("id") or self._generate_id(
                    item.get("source", self.SOURCE_NAME),
                    item.get("title", ""),
                    item.get("date", ""),
                    item.get("url"),
                )

                stmt = select(FinanceChannelIdea).where(FinanceChannelIdea.idea_id == idea_id)
                result = await self.db_session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    existing.title = item.get("title", existing.title)
                    existing.content = item.get("content", existing.content)
                    existing.source = item.get("source", existing.source)
                    existing.author = item.get("author", existing.author)
                    existing.publish_time = item.get("date", existing.publish_time)
                    existing.url = item.get("url", existing.url)
                    existing.updated_at = datetime.now()
                    updated_count += 1
                else:
                    record = FinanceChannelIdea(
                        idea_id=idea_id,
                        title=item.get("title", ""),
                        content=item.get("content", ""),
                        source=item.get("source", self.SOURCE_NAME),
                        author=item.get("author"),
                        publish_time=item.get("date", ""),
                        url=item.get("url"),
                    )
                    self.db_session.add(record)
                    saved_count += 1

            await self.db_session.commit()
            logger.info(f"投资观点入库完成：新增 {saved_count} 条，更新 {updated_count} 条")
            return saved_count, updated_count

        except Exception as e:
            logger.error(f"投资观点入库失败：{e}", exc_info=True)
            await self.db_session.rollback()
            return 0, 0

    async def get_from_cache(self, keyword: Optional[str] = None, page: int = 1, cache_limit: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        从数据库缓存获取数据

        Args:
            keyword: 关键词（用于构造缓存键）
            page: 页码

        Returns:
            缓存数据或 None
        """
        if not self.db_session:
            return None

        try:
            cache_key = f"ideas:page={page}:keyword={keyword or 'all'}:limit={cache_limit or self.CACHE_MAX_ITEMS}"

            stmt = select(FinanceChannelCache).where(
                FinanceChannelCache.cache_key == cache_key
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
            logger.error(f"从缓存读取观点数据失败：{e}")
            return None

    async def save_to_cache(
        self,
        items: List[Dict[str, Any]],
        keyword: Optional[str] = None,
        page: int = 1,
        source: str = SOURCE_NAME,
        cache_limit: Optional[int] = None
    ) -> None:
        """
        保存数据到数据库缓存

        Args:
            items: 观点列表
            keyword: 关键词
            page: 页码
            source: 数据源
        """
        if not self.db_session:
            return

        try:
            cache_key = f"ideas:page={page}:keyword={keyword or 'all'}:limit={cache_limit or self.CACHE_MAX_ITEMS}"
            now = datetime.now()
            expires_at = now + timedelta(seconds=self.cache_ttl)

            stmt = select(FinanceChannelCache).where(
                FinanceChannelCache.cache_key == cache_key
            )
            result = await self.db_session.execute(stmt)
            cache_record = result.scalars().first()

            payload = {"items": items}

            if cache_record:
                cache_record.payload_json = payload
                cache_record.source = source
                cache_record.fetched_at = now
                cache_record.expires_at = expires_at
                cache_record.updated_at = now
            else:
                cache_record = FinanceChannelCache(
                    cache_key=cache_key,
                    module="ideas",
                    payload_json=payload,
                    source=source,
                    fetched_at=now,
                    expires_at=expires_at
                )
                self.db_session.add(cache_record)

            await self.db_session.commit()
            logger.info(f"观点数据已保存到缓存（{cache_key}）")

        except Exception as e:
            logger.error(f"保存观点数据到缓存失败：{e}")
            await self.db_session.rollback()

    async def aggregate_ideas(self, limit: int = 10, keyword: Optional[str] = None, page: int = 1) -> Dict[str, Any]:
        """
        聚合投资观点数据（缓存优先，失败降级）

        Args:
            limit: 返回条数
            keyword: 关键词过滤
            page: 页码

        Returns:
            观点数据响应字典
        """
        try:
            cached_data = await self.get_from_cache(keyword=keyword, page=page, cache_limit=limit)

            if cached_data and not cached_data["stale"]:
                logger.info(f"使用有效缓存的观点数据（keyword={keyword}, page={page}）")
                return cached_data

            logger.info(f"缓存过期或不存在，重新抓取观点数据（keyword={keyword}, page={page}）")
            items = await self.fetch_ideas(limit=limit, keyword=keyword, page=page)

            if not items:
                if cached_data:
                    logger.warning("抓取失败，返回过期缓存数据")
                    return cached_data
                logger.error("抓取失败且无缓存数据")
                return {
                    "items": [],
                    "cached": False,
                    "stale": True,
                    "source": "none",
                    "updated_at": datetime.now().isoformat()
                }

            await self._save_to_database(items)
            await self.save_to_cache(items, keyword=keyword, page=page, source=self.SOURCE_NAME, cache_limit=limit)

            return {
                "items": items,
                "cached": False,
                "stale": False,
                "source": self.SOURCE_NAME,
                "updated_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"聚合观点数据失败：{e}", exc_info=True)

            cached_data = await self.get_from_cache(keyword=keyword, page=page, cache_limit=limit)
            if cached_data:
                logger.warning("发生异常，返回缓存数据")
                return cached_data

            return {
                "items": [],
                "cached": False,
                "stale": True,
                "source": "none",
                "updated_at": datetime.now().isoformat()
            }

    async def refresh_ideas(self, pages: int = 1, limit: int = 50) -> Dict[str, Any]:
        """
        手动刷新投资观点数据（忽略缓存）
        """
        start_time = datetime.now()
        all_items: List[Dict[str, Any]] = []

        pages = max(1, min(pages, 5))
        per_page_limit = max(1, min(limit, self.CACHE_MAX_ITEMS))

        for page in range(1, pages + 1):
            items = await self.fetch_ideas(limit=per_page_limit, keyword=None, page=page)
            if items:
                all_items.extend(items)
            await asyncio.sleep(0.2)

        deduped: Dict[str, Dict[str, Any]] = {}
        for item in all_items:
            key = item.get("id") or item.get("url")
            if key and key not in deduped:
                deduped[key] = item

        items = list(deduped.values())
        items.sort(key=lambda x: x.get("date", ""), reverse=True)

        saved, updated = await self._save_to_database(items)

        if items:
            await self.save_to_cache(items[:per_page_limit], keyword=None, page=1, source=self.SOURCE_NAME, cache_limit=per_page_limit)

        duration = (datetime.now() - start_time).total_seconds()
        return {
            "items": items[:per_page_limit],
            "saved": saved,
            "updated": updated,
            "pages": pages,
            "duration": duration,
        }


# 全局单例
_ideas_aggregator: Optional[IdeasAggregator] = None


def get_ideas_aggregator(db_session: Optional[AsyncSession] = None) -> IdeasAggregator:
    """获取投资观点聚合器单例"""
    global _ideas_aggregator
    if _ideas_aggregator is None or db_session is not None:
        _ideas_aggregator = IdeasAggregator(db_session=db_session)
    return _ideas_aggregator
