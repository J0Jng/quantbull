"""
政策法规聚合服务
从证监会、央行等官方网站聚合金融政策法规信息
"""
import asyncio
import hashlib
import logging
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin

import html as html_lib
import httpx
from lxml import html
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.finance_channel_cache import FinanceChannelCache
from models.policy_regulation import PolicyRegulation

logger = logging.getLogger(__name__)


class PolicyAggregator:
    """政策法规聚合器"""
    
    # 缓存 TTL（秒）
    CACHE_TTL = 3600  # 1 小时
    CACHE_MAX_ITEMS = 50
    
    def __init__(
        self,
        cache_ttl: int = CACHE_TTL,
        timeout: int = 10,
        db_session: Optional[AsyncSession] = None
    ):
        """
        初始化政策法规聚合器
        
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
            'Referer': 'https://www.gov.cn/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

        self.policy_keywords = [
            "金融", "银行", "证券", "基金", "期货", "保险", "外汇", "债券", "资本市场",
            "支付", "反洗钱", "监管", "法规", "条例", "办法", "规定", "通知", "意见", "规则",
            "合规", "审慎", "风险", "宏观审慎"
        ]

    @staticmethod
    def _clean_text(value: str) -> str:
        text = value or ""
        text = html_lib.unescape(text)
        # 移除 CSS 规则、花括号内容等
        text = re.sub(r"\.[A-Za-z0-9_-]+\s*[A-Za-z0-9_-]*\s*\{[^}]*\}", " ", text)
        text = re.sub(r"\{[^}]*\}", " ", text)
        text = re.sub(r"TRS_Editor|font-size|line-height|margin-bottom|padding", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _contains_garbage(text: str) -> bool:
        if not text:
            return False
        return bool(re.search(r"TRS_Editor|font-size|line-height|margin-bottom|\.TRS_Editor\s*P\s*\{", text, re.IGNORECASE))

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
    def _extract_date(text: str) -> Optional[str]:
        return PolicyAggregator._normalize_date(text)

    @staticmethod
    def _extract_date_from_url(url: str) -> Optional[str]:
        if not url:
            return None
        match = re.search(r"(20\d{2})[/-]?(\d{2})[/-]?(\d{2})", url)
        if match:
            y, m, d = match.groups()
            return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
        return None

    @staticmethod
    def _generate_id(source: str, title: str, date: str, url: Optional[str]) -> str:
        raw = url or f"{source}|{title}|{date}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()

    async def _get_text_with_retry(self, client: httpx.AsyncClient, url: str, params: Optional[dict] = None) -> Optional[str]:
        for attempt in range(3):
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as exc:
                status_code = exc.response.status_code
                if status_code == 404:
                    logger.warning(f"政策列表地址不存在: {url}")
                    return None
                if attempt == 2:
                    logger.warning(f"获取政策列表失败: {exc}")
                    return None
                await asyncio.sleep(0.5 * (2 ** attempt))
            except Exception as exc:
                if attempt == 2:
                    logger.warning(f"获取政策列表失败: {exc}")
                    return None
                await asyncio.sleep(0.5 * (2 ** attempt))
        return None

    async def _fetch_detail_summary(self, client: httpx.AsyncClient, url: str) -> Optional[str]:
        html_text = await self._get_text_with_retry(client, url)
        if not html_text:
            return None
        try:
            doc = html.fromstring(html_text)
        except Exception:
            return None
        for node in doc.xpath("//style|//script"):
            try:
                node.drop_tree()
            except Exception:
                continue
        candidates = doc.xpath(
            "//div[contains(@class,'TRS_Editor') or contains(@class,'content') or contains(@class,'article') or contains(@id,'content') or contains(@id,'zoom')]"
        )
        if not candidates:
            candidates = doc.xpath("//article|//div[@class='article-content']")
        texts: List[str] = []
        for node in candidates:
            text = self._clean_text(" ".join(node.itertext()))
            if text:
                texts.append(text)
        if not texts:
            return None
        content = max(texts, key=len)
        content = self._clean_text(content)
        if self._contains_garbage(content):
            return None
        return content[:150]

    async def _save_to_database(self, items: List[Dict[str, Any]]) -> None:
        """
        将政策法规保存到数据库（upsert）
        """
        if not self.db_session or not items:
            return

        try:
            saved_count = 0
            updated_count = 0

            for item in items:
                policy_id = item.get("id") or self._generate_id(
                    item.get("source", "official"),
                    item.get("title", ""),
                    item.get("date", ""),
                    item.get("url"),
                )

                stmt = select(PolicyRegulation).where(PolicyRegulation.policy_id == policy_id)
                result = await self.db_session.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    existing.title = item.get("title", existing.title)
                    existing.summary = item.get("summary", existing.summary)
                    existing.source = item.get("source", existing.source)
                    existing.publish_date = item.get("date", existing.publish_date)
                    existing.url = item.get("url", existing.url)
                    existing.updated_at = datetime.now()
                    updated_count += 1
                else:
                    record = PolicyRegulation(
                        policy_id=policy_id,
                        title=item.get("title", ""),
                        summary=item.get("summary", ""),
                        source=item.get("source", "official"),
                        publish_date=item.get("date", ""),
                        url=item.get("url"),
                    )
                    self.db_session.add(record)
                    saved_count += 1

            await self.db_session.commit()
            logger.info(f"政策法规入库完成：新增 {saved_count} 条，更新 {updated_count} 条")

        except Exception as e:
            logger.error(f"政策法规入库失败：{e}", exc_info=True)
            await self.db_session.rollback()

    def _extract_items_from_html(self, html_text: str, list_url: str, source_name: str) -> List[Dict[str, Any]]:
        try:
            doc = html.fromstring(html_text)
        except Exception:
            return []
        for node in doc.xpath("//style|//script"):
            try:
                node.drop_tree()
            except Exception:
                continue
        anchors = doc.xpath("//a[@href and normalize-space(string()) != '']")
        ignore_titles = {"更多", "下一页", "上一页", "首页", "尾页"}
        items: List[Dict[str, Any]] = []
        seen: set[str] = set()
        for anchor in anchors:
            title = self._clean_text(anchor.text_content())
            if not title or title in ignore_titles or len(title) < 6:
                continue
            if re.search(r"TRS_Editor|font-|line-height|margin|padding", title, re.IGNORECASE):
                continue
            href = anchor.get("href")
            if not href:
                continue
            url = urljoin(list_url, href)
            if url in seen:
                continue
            parent_text = self._clean_text(" ".join(anchor.getparent().itertext())) if anchor.getparent() is not None else ""
            date_value = self._extract_date(parent_text)
            if not date_value:
                sibling_text = ""
                if anchor.getparent() is not None:
                    sibling_text = self._clean_text(" ".join(anchor.getparent().xpath("./span/text()|./em/text()|./p/text()")))
                date_value = self._extract_date(sibling_text)
            if not date_value:
                date_value = self._extract_date_from_url(url)
            if not date_value:
                continue
            items.append({
                "title": title,
                "date": date_value,
                "url": url,
                "source": source_name,
                "summary": ""
            })
            seen.add(url)
        return items
    
    async def fetch_policies(self, limit: int = 10, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        抓取政策法规
        
        Args:
            limit: 返回条数
            keyword: 关键词过滤
            
        Returns:
            政策列表
        """
        try:
            sources = [
                {
                    "name": "国务院",
                    "list_urls": [
                        "https://www.gov.cn/zhengce/zuixin.htm"
                    ]
                },
                {
                    "name": "中国证监会",
                    "list_urls": [
                        "http://www.csrc.gov.cn/csrc/c100028/common_list.shtml"
                    ]
                },
                {
                    "name": "中国人民银行",
                    "list_urls": [
                        "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html"
                    ]
                },
                {
                    "name": "财政部",
                    "list_urls": [
                        "http://www.mof.gov.cn/zhengwuxinxi/zhengcefabu/"
                    ]
                }
            ]

            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                items: List[Dict[str, Any]] = []
                for src in sources:
                    list_html = None
                    list_url_used = None
                    for list_url in src["list_urls"]:
                        list_html = await self._get_text_with_retry(client, list_url)
                        if list_html:
                            list_url_used = list_url
                            break
                    if not list_html or not list_url_used:
                        continue
                    items.extend(self._extract_items_from_html(list_html, list_url_used, src["name"]))

                if not items:
                    return []

                deduped: Dict[str, Dict[str, Any]] = {}
                for item in items:
                    key = item.get("url") or f"{item.get('source')}|{item.get('title')}|{item.get('date')}"
                    if key not in deduped:
                        deduped[key] = item

                items = list(deduped.values())
                items.sort(key=lambda x: x.get("date", ""), reverse=True)

                detail_targets = [item for item in items if not item.get("summary")][:max(limit, 10)]
                semaphore = asyncio.Semaphore(5)

                async def enrich(item: Dict[str, Any]) -> None:
                    if not item.get("url"):
                        return
                    async with semaphore:
                        summary = await self._fetch_detail_summary(client, item["url"])
                        if summary:
                            item["summary"] = summary

                await asyncio.gather(*(enrich(item) for item in detail_targets), return_exceptions=True)

                for item in items:
                    if not item.get("summary"):
                        item["summary"] = item.get("title", "")[:120]
                    item["title"] = self._clean_text(item.get("title", ""))
                    item["summary"] = self._clean_text(item.get("summary", ""))
                    item["id"] = self._generate_id(item["source"], item["title"], item["date"], item.get("url"))

                if keyword:
                    keyword_lower = keyword.lower()
                    items = [
                        item for item in items
                        if keyword_lower in item["title"].lower() or keyword_lower in item["summary"].lower()
                    ]
                else:
                    keyword_list = [k.lower() for k in self.policy_keywords]
                    filtered = []
                    for item in items:
                        title_lower = item.get("title", "").lower()
                        summary_lower = item.get("summary", "").lower()
                        if any(k in title_lower or k in summary_lower for k in keyword_list):
                            filtered.append(item)
                    items = filtered

                items = items[:limit]

                logger.info(f"成功抓取 {len(items)} 条政策法规")
                return items

        except Exception as e:
            logger.error(f"抓取政策法规失败：{e}")
            return []
    
    async def get_from_cache(self, keyword: Optional[str] = None, cache_limit: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        从数据库缓存获取数据
        
        Args:
            keyword: 关键词（用于构造缓存键）
            
        Returns:
            缓存数据或 None
        """
        if not self.db_session:
            return None
        
        try:
            cache_key = f"policies:{keyword or 'all'}:limit={cache_limit or self.CACHE_MAX_ITEMS}"
            
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
            logger.error(f"从缓存读取政策数据失败：{e}")
            return None
    
    async def save_to_cache(self, items: List[Dict[str, Any]], keyword: Optional[str] = None, source: str = "official", cache_limit: Optional[int] = None) -> None:
        """
        保存数据到数据库缓存
        
        Args:
            items: 政策列表
            keyword: 关键词
            source: 数据源
        """
        if not self.db_session:
            return
        
        try:
            cache_key = f"policies:{keyword or 'all'}:limit={cache_limit or self.CACHE_MAX_ITEMS}"
            now = datetime.now()
            expires_at = now + timedelta(seconds=self.cache_ttl)
            
            # 查找现有记录
            stmt = select(FinanceChannelCache).where(
                FinanceChannelCache.cache_key == cache_key
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
                    cache_key=cache_key,
                    module="policies",
                    payload_json={"items": items},
                    source=source,
                    fetched_at=now,
                    expires_at=expires_at
                )
                self.db_session.add(cache_record)
            
            await self.db_session.commit()
            logger.info(f"政策数据已保存到缓存（{cache_key}）")
            
        except Exception as e:
            logger.error(f"保存政策数据到缓存失败：{e}")
            await self.db_session.rollback()
    
    async def aggregate_policies(self, limit: int = 10, keyword: Optional[str] = None) -> Dict[str, Any]:
        """
        聚合政策法规数据（缓存优先，失败降级）
        
        Args:
            limit: 返回条数
            keyword: 关键词过滤
            
        Returns:
            政策数据响应字典
        """
        try:
            # 1. 尝试从缓存读取
            cache_limit = max(self.CACHE_MAX_ITEMS, limit)
            cached_data = await self.get_from_cache(keyword, cache_limit=cache_limit)
            
            if cached_data and not cached_data["stale"]:
                # 若缓存含乱码则强制刷新
                cached_items = cached_data.get("items", [])
                if any(self._contains_garbage(item.get("title", "")) or self._contains_garbage(item.get("summary", "")) for item in cached_items):
                    logger.warning("检测到缓存含乱码，触发重新抓取")
                else:
                    logger.info(f"使用有效缓存的政策数据（keyword={keyword}）")
                    cached_data["items"] = cached_items[:limit]
                    return cached_data
            
            # 2. 缓存过期或不存在，重新抓取
            logger.info(f"缓存过期或不存在，重新抓取政策数据（keyword={keyword}）")
            items = await self.fetch_policies(limit=cache_limit, keyword=keyword)
            
            if not items:
                # 抓取失败，返回过期缓存（如果有）
                if cached_data:
                    logger.warning("抓取失败，返回过期缓存数据")
                    cached_data["items"] = cached_data.get("items", [])[:limit]
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
            await self._save_to_database(items)
            await self.save_to_cache(items, keyword=keyword, source="official", cache_limit=cache_limit)
            
            # 4. 返回新数据
            return {
                "items": items[:limit],
                "cached": False,
                "stale": False,
                "source": "official",
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"聚合政策数据失败：{e}", exc_info=True)
            
            # 降级：尝试返回缓存
            cached_data = await self.get_from_cache(keyword, cache_limit=cache_limit)
            if cached_data:
                logger.warning("发生异常，返回缓存数据")
                cached_data["items"] = cached_data.get("items", [])[:limit]
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
_policy_aggregator: Optional[PolicyAggregator] = None


def get_policy_aggregator(db_session: Optional[AsyncSession] = None) -> PolicyAggregator:
    """获取政策法规聚合器单例"""
    global _policy_aggregator
    if _policy_aggregator is None or db_session is not None:
        _policy_aggregator = PolicyAggregator(db_session=db_session)
    return _policy_aggregator
