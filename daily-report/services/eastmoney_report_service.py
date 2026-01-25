"""东方财富研报聚合服务"""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import time
from html.parser import HTMLParser
from urllib.parse import parse_qs, unquote, urlparse
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EastmoneyCategory:
    key: str
    label: str
    list_url: str


EASTMONEY_CATEGORIES: Dict[str, EastmoneyCategory] = {
    "stock": EastmoneyCategory("stock", "个股研报", f"{settings.eastmoney_report_base_url}/stock.jshtml"),
    "industry": EastmoneyCategory("industry", "行业研报", f"{settings.eastmoney_report_base_url}/industry.jshtml"),
    "profitforecast": EastmoneyCategory("profitforecast", "盈利预测", f"{settings.eastmoney_report_base_url}/profitforecast.jshtml"),
    "macro": EastmoneyCategory("macro", "宏观研究", f"{settings.eastmoney_report_base_url}/macresearch.jshtml"),
    "newstock": EastmoneyCategory("newstock", "新股研究", f"{settings.eastmoney_report_base_url}/newstock.jshtml"),
    "strategy": EastmoneyCategory("strategy", "策略报告", f"{settings.eastmoney_report_base_url}/strategyreport.jshtml"),
}


class SimpleTTLCache:
    def __init__(self, ttl_seconds: int, enabled: bool = True) -> None:
        self._ttl = ttl_seconds
        self._enabled = enabled
        self._store: Dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if not self._enabled:
            return None
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if time.time() > expires_at:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        if not self._enabled:
            return
        self._store[key] = (time.time() + self._ttl, value)


class AsyncRateLimiter:
    def __init__(self, rps: int) -> None:
        self._rps = max(0, rps)
        self._lock = asyncio.Lock()
        self._timestamps: deque[float] = deque()

    async def acquire(self) -> None:
        if self._rps <= 0:
            return
        async with self._lock:
            now = time.monotonic()
            while self._timestamps and now - self._timestamps[0] >= 1:
                self._timestamps.popleft()
            if len(self._timestamps) >= self._rps:
                wait_seconds = 1 - (now - self._timestamps[0])
                if wait_seconds > 0:
                    await asyncio.sleep(wait_seconds)
                now = time.monotonic()
                while self._timestamps and now - self._timestamps[0] >= 1:
                    self._timestamps.popleft()
            self._timestamps.append(now)


class EastmoneyReportService:
    INITDATA_PATTERN = re.compile(r"initdata\w*\s*=\s*(\{.*?\});", re.S)
    ZWINFO_PATTERN = re.compile(r"var\s+zwinfo\s*=\s*(\{.*?\});", re.S)

    def __init__(self) -> None:
        self._cache = SimpleTTLCache(
            ttl_seconds=settings.eastmoney_report_cache_ttl,
            enabled=settings.eastmoney_report_cache_enabled,
        )
        self._rate_limiter = AsyncRateLimiter(settings.eastmoney_report_rate_limit_rps)

    async def fetch_eastmoney_reports(
        self,
        category: str,
        keyword: Optional[str],
        page: int,
        page_size: int,
    ) -> Dict[str, Any]:
        category_key = category or "stock"
        if category_key not in EASTMONEY_CATEGORIES:
            raise ValueError(f"不支持的栏目: {category_key}")

        cache_key = f"eastmoney:list:{category_key}"
        cached = self._cache.get(cache_key)
        if cached is None:
            html = await self._request_text(EASTMONEY_CATEGORIES[category_key].list_url)
            init_data = self._extract_initdata(html)
            raw_items: List[Dict[str, Any]] = []
            if init_data:
                raw_items = init_data.get("data", []) or []
                if not raw_items and isinstance(init_data.get("result"), dict):
                    raw_items = init_data.get("result", {}).get("data", []) or []
            if raw_items:
                items = [self._normalize_item(item, category_key) for item in raw_items if isinstance(item, dict)]
            elif category_key == "profitforecast":
                items = self._parse_profitforecast_table(html)
            else:
                raise ValueError("未解析到东方财富研报列表数据")
            cached = items
            self._cache.set(cache_key, cached)

        filtered = self._filter_items(cached, keyword)
        total = len(filtered)
        start = max(0, (page - 1) * page_size)
        end = start + page_size
        return {
            "total": total,
            "items": filtered[start:end],
            "category": category_key,
            "category_label": EASTMONEY_CATEGORIES[category_key].label,
        }

    async def fetch_eastmoney_report_detail(
        self,
        report_id_or_url: str,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        url_candidates = self._build_detail_urls(report_id_or_url, category)
        cached_title = self._find_cached_title(report_id_or_url, category)
        last_error: Optional[Exception] = None
        for url in url_candidates:
            try:
                html = await self._request_text(url)
                zwinfo = self._extract_zwinfo(html)
                if not zwinfo:
                    continue
                content = zwinfo.get("notice_content") or ""
                content = self._normalize_text(content)
                summary = content[:300] if content else ""
                return {
                    "id": zwinfo.get("info_code") or report_id_or_url,
                    "title": zwinfo.get("title") or cached_title or "东方财富研报",
                    "source": "eastmoney",
                    "publish_time": zwinfo.get("publish_date"),
                    "org_name": zwinfo.get("org_name"),
                    "rating": zwinfo.get("rating"),
                    "summary": summary,
                    "content": content,
                    "url": url,
                    "pdf_url": zwinfo.get("attach_url"),
                    "stock_code": zwinfo.get("stock_code") or zwinfo.get("code"),
                    "stock_name": zwinfo.get("short_name") or zwinfo.get("short_name_ch"),
                }
            except Exception as exc:
                last_error = exc
                continue
        logger.error("东方财富研报详情解析失败: %s", last_error)
        return {
            "id": report_id_or_url,
            "title": cached_title or "东方财富研报",
            "source": "eastmoney",
            "summary": "",
            "content": "",
            "url": url_candidates[0] if url_candidates else self._normalize_report_url(report_id_or_url),
        }

    def _filter_items(self, items: List[Dict[str, Any]], keyword: Optional[str]) -> List[Dict[str, Any]]:
        if not keyword:
            return items
        kw = keyword.strip().lower()
        if not kw:
            return items
        def _hit(item: Dict[str, Any]) -> bool:
            return any(
                kw in (str(item.get(field, "")).lower())
                for field in ["title", "stock_name", "stock_code", "org_name", "industry", "rating", "category_label"]
            )
        return [item for item in items if _hit(item)]

    def _normalize_report_url(self, report_id_or_url: str) -> str:
        if report_id_or_url.startswith("http://") or report_id_or_url.startswith("https://"):
            return report_id_or_url
        return f"{settings.eastmoney_report_base_url}/{report_id_or_url}.html"

    def _build_detail_urls(self, report_id_or_url: str, category: Optional[str]) -> List[str]:
        if report_id_or_url.startswith("http://") or report_id_or_url.startswith("https://"):
            parsed = urlparse(report_id_or_url)
            qs = parse_qs(parsed.query)
            encode_url = qs.get("encodeUrl", [None])[0]
            decoded = None
            if encode_url:
                decoded = unquote(encode_url)
                if decoded.startswith("http://") or decoded.startswith("https://"):
                    return [decoded, report_id_or_url]
                if decoded.startswith("/report/"):
                    return [f"https://data.eastmoney.com{decoded}", report_id_or_url]
                if decoded.startswith("report/"):
                    return [f"https://data.eastmoney.com/{decoded}", report_id_or_url]
            return [report_id_or_url]
        base = settings.eastmoney_report_base_url
        raw = str(report_id_or_url)
        decoded_raw = unquote(raw)
        if decoded_raw.startswith("http://") or decoded_raw.startswith("https://"):
            return [decoded_raw]
        if decoded_raw.startswith("/report/"):
            return [f"https://data.eastmoney.com{decoded_raw}"]
        if decoded_raw.startswith("report/"):
            return [f"https://data.eastmoney.com/{decoded_raw}"]

        is_info_code = raw.startswith("AP")
        candidates: List[str] = []
        if category == "industry":
            candidates.append(f"{base}/zw_industry.jshtml?infocode={report_id_or_url}")
        if category == "macro":
            candidates.append(f"{base}/zw_macresearch.jshtml?encodeUrl={report_id_or_url}")
        if category == "strategy":
            candidates.append(f"{base}/zw_strategy.jshtml?encodeUrl={report_id_or_url}")
        if category == "newstock":
            candidates.append(f"{base}/info/{report_id_or_url}.html")
        if category == "profitforecast":
            candidates.append(f"{base}/info/{report_id_or_url}.html")
        if category == "stock":
            candidates.append(f"{base}/info/{report_id_or_url}.html")
        if is_info_code:
            candidates.append(f"{base}/info/{report_id_or_url}.html")
        # 兜底尝试
        candidates.extend([
            f"{base}/info/{report_id_or_url}.html",
            f"{base}/zw_industry.jshtml?infocode={report_id_or_url}",
            f"{base}/zw_macresearch.jshtml?encodeUrl={report_id_or_url}",
            f"{base}/zw_strategy.jshtml?encodeUrl={report_id_or_url}",
        ])
        deduped: List[str] = []
        for url in candidates:
            if url not in deduped:
                deduped.append(url)
        return deduped

    def _find_cached_title(self, report_id: str, category: Optional[str]) -> Optional[str]:
        if category and category in EASTMONEY_CATEGORIES:
            items = self._cache.get(f"eastmoney:list:{category}") or []
            for item in items:
                if item.get("id") == report_id:
                    return item.get("title")
        # 尝试遍历所有缓存
        for key, value in list(self._cache._store.items()):
            if not key.startswith("eastmoney:list:"):
                continue
            items = value[1] if isinstance(value, tuple) else []
            for item in items:
                if item.get("id") == report_id:
                    return item.get("title")
        return None

    async def _request_text(self, url: str) -> str:
        await self._rate_limiter.acquire()
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        last_error: Optional[Exception] = None
        for attempt in range(settings.eastmoney_report_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=settings.eastmoney_report_timeout) as client:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    return response.text
            except Exception as exc:
                last_error = exc
                if attempt < settings.eastmoney_report_retries:
                    await asyncio.sleep(0.6 * (2 ** attempt))
                    continue
                break
        logger.error("东方财富请求失败: %s", last_error)
        raise RuntimeError(f"东方财富请求失败: {last_error}")

    def _extract_initdata(self, html: str) -> Optional[Dict[str, Any]]:
        if not html:
            return None
        match = self.INITDATA_PATTERN.search(html)
        if not match:
            return None
        raw = match.group(1)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def _extract_zwinfo(self, html: str) -> Optional[Dict[str, Any]]:
        if not html:
            return None
        match = self.ZWINFO_PATTERN.search(html)
        if not match:
            return None
        raw = match.group(1)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def _normalize_item(self, item: Dict[str, Any], category_key: str) -> Dict[str, Any]:
        info_code = item.get("infoCode") or item.get("INFOCODE") or item.get("info_code")
        encode_url = item.get("encodeUrl") or item.get("ENCODEURL")
        title = item.get("title") or item.get("TITLE") or item.get("reportTitle")
        stock_code = (
            item.get("stockCode")
            or item.get("STOCKCODE")
            or item.get("SECURITY_CODE")
            or item.get("security_code")
        )
        stock_name = (
            item.get("stockName")
            or item.get("STOCKNAME")
            or item.get("SECURITY_NAME_ABBR")
            or item.get("security_name_abbr")
        )
        org_name = item.get("orgSName") or item.get("orgName") or item.get("ORG_NAME")
        rating = item.get("emRatingName") or item.get("sRatingName") or item.get("rating")
        publish_time = item.get("publishDate") or item.get("PUBLISHDATE")
        industry = item.get("indvInduName") or item.get("industryName") or item.get("INDUSTRY_BOARD")

        if not info_code and encode_url:
            decoded = unquote(str(encode_url))
            match = re.search(r"AP\d+", decoded)
            if match:
                info_code = match.group(0)

        report_id = info_code or encode_url or item.get("SECUCODE") or stock_code
        if not report_id:
            uniq = f"{title}-{publish_time}-{stock_code}-{org_name}".encode("utf-8")
            report_id = hashlib.md5(uniq).hexdigest()

        detail_url = self._build_detail_urls(report_id, category_key)[0]

        return {
            "id": report_id,
            "title": title or stock_name or stock_code or "东方财富研报",
            "category": category_key,
            "category_label": EASTMONEY_CATEGORIES[category_key].label,
            "publish_time": publish_time,
            "source": "eastmoney",
            "stock_code": stock_code,
            "stock_name": stock_name,
            "industry": industry,
            "org_name": org_name,
            "rating": rating,
            "summary": "",
            "url": detail_url,
            "info_code": info_code,
            "encode_url": encode_url,
        }

    def _parse_profitforecast_table(self, html: str) -> List[Dict[str, Any]]:
        if not html:
            return []

        class _TableParser(HTMLParser):
            def __init__(self) -> None:
                super().__init__()
                self.in_table = False
                self.in_tr = False
                self.in_cell = False
                self.rows: List[tuple[List[str], List[List[str]]]] = []
                self._current_row: List[str] = []
                self._current_links_row: List[List[str]] = []
                self._current_text: List[str] = []
                self._current_links: List[str] = []

            def handle_starttag(self, tag: str, attrs: List[tuple[str, Optional[str]]]) -> None:
                if tag == "table":
                    self.in_table = True
                if not self.in_table:
                    return
                if tag == "tr":
                    self.in_tr = True
                    self._current_row = []
                    self._current_links_row = []
                if tag in ("td", "th") and self.in_tr:
                    self.in_cell = True
                    self._current_text = []
                    self._current_links = []
                if tag == "a" and self.in_cell:
                    for key, value in attrs:
                        if key == "href" and value:
                            self._current_links.append(value)

            def handle_data(self, data: str) -> None:
                if self.in_table and self.in_tr and self.in_cell:
                    self._current_text.append(data)

            def handle_endtag(self, tag: str) -> None:
                if not self.in_table:
                    return
                if tag in ("td", "th") and self.in_tr:
                    text = re.sub(r"\s+", " ", "".join(self._current_text)).strip()
                    self._current_row.append(text)
                    self._current_links_row.append(self._current_links)
                    self.in_cell = False
                if tag == "tr" and self.in_tr:
                    if self._current_row:
                        self.rows.append((self._current_row, self._current_links_row))
                    self.in_tr = False
                if tag == "table" and self.in_table:
                    self.in_table = False

        parser = _TableParser()
        parser.feed(html)

        if not parser.rows:
            return []

        header_index = None
        for idx, (cells, _links) in enumerate(parser.rows):
            if any("代码" in cell or "名称" in cell for cell in cells):
                header_index = idx
                break

        data_rows = parser.rows[header_index + 1:] if header_index is not None else parser.rows

        items: List[Dict[str, Any]] = []
        for cells, links in data_rows:
            if len(cells) < 3:
                continue
            stock_code = cells[1]
            stock_name = cells[2]
            if not stock_code and not stock_name:
                continue

            href = None
            for link_group in links:
                for link in link_group:
                    if "/report/" in link or "data.eastmoney.com/report" in link:
                        href = link
                        break
                if href:
                    break

            normalized_href = None
            encode_url = None
            if href:
                if href.startswith("//"):
                    normalized_href = f"https:{href}"
                elif href.startswith("/"):
                    normalized_href = f"https://data.eastmoney.com{href}"
                elif href.startswith("http://") or href.startswith("https://"):
                    normalized_href = href
                else:
                    normalized_href = f"https://data.eastmoney.com/{href}"

                parsed = urlparse(normalized_href)
                qs = parse_qs(parsed.query)
                encode_url = qs.get("encodeUrl", [None])[0]

            report_id = encode_url or stock_code
            items.append({
                "id": report_id,
                "title": stock_name or stock_code or "盈利预测",
                "category": "profitforecast",
                "category_label": EASTMONEY_CATEGORIES["profitforecast"].label,
                "publish_time": None,
                "source": "eastmoney",
                "stock_code": stock_code,
                "stock_name": stock_name,
                "industry": None,
                "org_name": None,
                "rating": None,
                "summary": "",
                "url": normalized_href or "",
                "info_code": None,
                "encode_url": encode_url,
            })

        return items
