"""
东方财富盈利预测数据服务

数据来源：
- https://data.eastmoney.com/report/profitforecast.jshtml
- 数据接口：https://datacenter-web.eastmoney.com/api/data/v1/get
  reportName: RPT_WEB_RESPREDICT
  columns: WEB_RESPREDICT
- 板块列表接口（行业/概念/地域）：https://reportapi.eastmoney.com/report/bk?bkCode=...&cb=cb
"""
from __future__ import annotations

import asyncio
import json
import logging
import random
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    expires_at: datetime
    payload: Dict[str, Any]


_cache: Dict[str, CacheEntry] = {}


def _cache_key(prefix: str, **kwargs: Any) -> str:
    parts = [f"{k}={kwargs.get(k, '')}" for k in sorted(kwargs.keys())]
    return f"profitforecast:{prefix}:" + "|".join(parts)


class EastmoneyProfitForecastService:
    DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    REPORT_API_URL = "https://reportapi.eastmoney.com/report/bk"

    REPORT_NAME = "RPT_WEB_RESPREDICT"
    COLUMNS = "WEB_RESPREDICT"
    DEFAULT_SORT_COLUMNS = "RATING_ORG_NUM"
    DEFAULT_SORT_TYPES = "-1"

    CACHE_TTL_SECONDS = 120
    SCOPE_TTL_SECONDS = 6 * 3600
    MAX_RETRIES = 2

    BK_CODES = {
        "industry": "016",
        "concept": "007",
        "region": "020",
    }

    MARKET_FILTERS = {
        "sha": '(MARKET_BOARD in ("069001001001","069001001006"))',
        "kcb": '(MARKET_BOARD="069001001006")',
        "sza": '(MARKET_BOARD in ("069001002002","069001002001"))',
        "cyb": '(MARKET_BOARD="069001002002")',
        "bja": '(MARKET_BOARD="069001017")',
        "沪市A股": '(MARKET_BOARD in ("069001001001","069001001006"))',
        "科创板": '(MARKET_BOARD="069001001006")',
        "深市A股": '(MARKET_BOARD in ("069001002002","069001002001"))',
        "创业板": '(MARKET_BOARD="069001002002")',
        "北交所": '(MARKET_BOARD="069001017")',
    }

    def __init__(
        self,
        timeout: int = 12,
        max_concurrent_requests: int = 3,
    ):
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://data.eastmoney.com/report/profitforecast.jshtml",
        }

    # ---------------------- cache ----------------------
    def _cache_get(self, key: str) -> Optional[Dict[str, Any]]:
        entry = _cache.get(key)
        if not entry:
            return None
        if entry.expires_at <= datetime.now():
            _cache.pop(key, None)
            return None
        return entry.payload

    def _cache_set(self, key: str, payload: Dict[str, Any], ttl: int) -> None:
        _cache[key] = CacheEntry(expires_at=datetime.now() + timedelta(seconds=ttl), payload=payload)

    # ---------------------- http ----------------------
    async def _request_json(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        last_error: Optional[Exception] = None
        for attempt in range(1, self.MAX_RETRIES + 2):
            try:
                async with self.semaphore:
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                        resp = await client.get(url, params=params, follow_redirects=True)
                        if resp.status_code != 200:
                            raise RuntimeError(f"HTTP {resp.status_code}")
                        return resp.json()
            except Exception as exc:
                last_error = exc
                logger.warning(f"盈利预测请求失败（{attempt}）: {url} - {exc}")
        if last_error:
            raise last_error
        return None

    @staticmethod
    def _decode_response_text(resp: httpx.Response) -> str:
        content = resp.content or b""
        for enc in ("utf-8", "gb18030"):
            try:
                text = content.decode(enc)
            except UnicodeDecodeError:
                continue
            if text:
                return text
        text = resp.text
        if text:
            try:
                fixed = text.encode("latin-1").decode("utf-8")
                return fixed
            except Exception:
                return text
        return ""

    async def _request_jsonp(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        last_error: Optional[Exception] = None
        for attempt in range(1, self.MAX_RETRIES + 2):
            try:
                async with self.semaphore:
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                        resp = await client.get(url, params=params, follow_redirects=True)
                        if resp.status_code != 200:
                            raise RuntimeError(f"HTTP {resp.status_code}")
                        text = self._decode_response_text(resp)
                        match = re.search(r"cb\((.*)\)", text)
                        if not match:
                            raise ValueError("invalid jsonp")
                        return json.loads(match.group(1))
            except Exception as exc:
                last_error = exc
                logger.warning(f"盈利预测板块列表请求失败（{attempt}）: {url} - {exc}")
        if last_error:
            raise last_error
        return None

    # ---------------------- scopes ----------------------
    async def _fetch_scope_list(self, scope_type: str) -> List[Dict[str, Any]]:
        bk_code = self.BK_CODES.get(scope_type)
        if not bk_code:
            return []
        data = await self._request_jsonp(self.REPORT_API_URL, {"bkCode": bk_code, "cb": "cb"})
        items = data.get("data") if isinstance(data, dict) else None
        if not isinstance(items, list):
            return []
        results = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = item.get("bkName")
            code = item.get("bkCode")
            first_letter = item.get("firstLetter")
            if not name or not code:
                continue
            results.append({
                "code": str(code),
                "name": str(name),
                "first_letter": str(first_letter) if first_letter else "",
            })
        return results

    async def get_scopes(self, refresh: bool = False) -> Dict[str, Any]:
        cache_key = _cache_key("scopes")
        if not refresh:
            cached = self._cache_get(cache_key)
            if cached:
                return cached
        industry = await self._fetch_scope_list("industry")
        concept = await self._fetch_scope_list("concept")
        region = await self._fetch_scope_list("region")
        payload = {
            "industry": industry,
            "concept": concept,
            "region": region,
            "market": [
                {"code": "sha", "name": "沪市A股"},
                {"code": "kcb", "name": "科创板"},
                {"code": "sza", "name": "深市A股"},
                {"code": "cyb", "name": "创业板"},
                {"code": "bja", "name": "北交所"},
            ],
        }
        self._cache_set(cache_key, payload, self.SCOPE_TTL_SECONDS)
        return payload

    def _resolve_scope_name(
        self,
        scope_type: str,
        scope_value: Optional[str],
        scopes: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> Optional[str]:
        if not scope_value or scope_value in {"*", "all"}:
            return None
        if scope_type == "market":
            return scope_value
        if not scopes:
            return scope_value
        options = scopes.get(scope_type) or []
        if scope_value.isdigit():
            for item in options:
                if str(item.get("code")) == scope_value:
                    return str(item.get("name"))
        return scope_value

    def _build_filter(
        self,
        scope_type: str,
        scope_value: Optional[str],
        keyword: Optional[str],
        scopes: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> Optional[str]:
        filters: List[str] = []
        name = self._resolve_scope_name(scope_type, scope_value, scopes)
        if name:
            name = str(name).replace('"', '')
            if scope_type in {"industry", "hy"}:
                filters.append(f'(INDUSTRY_BOARD="{name}")')
            elif scope_type in {"region", "dy"}:
                filters.append(f'(REGION_BOARD="{name}")')
            elif scope_type in {"concept", "gn"}:
                filters.append(f'(CONCEPTINDEX_BOARD like "%{name}%")')
            elif scope_type == "market":
                market_filter = self.MARKET_FILTERS.get(name)
                if market_filter:
                    filters.append(market_filter)
        if keyword:
            kw = str(keyword).replace('"', '').strip()
            if kw:
                filters.append(f'(SECURITY_CODE like "%{kw}%" or SECURITY_NAME_ABBR like "%{kw}%")')
        if not filters:
            return None
        if len(filters) == 1:
            return filters[0]
        return "(" + " and ".join(filters) + ")"

    # ---------------------- main api ----------------------
    async def fetch_profit_forecast(
        self,
        scope_type: str = "all",
        scope_value: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        keyword: Optional[str] = None,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        cache_key = _cache_key(
            "list",
            scope_type=scope_type,
            scope_value=scope_value or "",
            page=page,
            page_size=page_size,
            keyword=keyword or "",
        )
        if not refresh:
            cached = self._cache_get(cache_key)
            if cached:
                return cached

        scopes: Optional[Dict[str, List[Dict[str, Any]]]] = None
        if scope_type in {"industry", "concept", "region"} and scope_value and scope_value.isdigit():
            scopes = await self.get_scopes(refresh=False)

        filter_expr = self._build_filter(scope_type, scope_value, keyword, scopes)
        params: Dict[str, Any] = {
            "reportName": self.REPORT_NAME,
            "columns": self.COLUMNS,
            "pageNumber": page,
            "pageSize": page_size,
            "sortColumns": self.DEFAULT_SORT_COLUMNS,
            "sortTypes": self.DEFAULT_SORT_TYPES,
        }
        if filter_expr:
            params["filter"] = filter_expr

        data = await self._request_json(self.DATACENTER_URL, params)
        if not data or not data.get("success"):
            message = data.get("message") if isinstance(data, dict) else "数据加载失败"
            raise RuntimeError(message or "数据加载失败")
        result = data.get("result") or {}
        rows = result.get("data") or []
        total = result.get("count") or 0
        payload = {
            "page": page,
            "page_size": page_size,
            "total": total,
            "data": rows,
            "source": "eastmoney",
            "scope_type": scope_type,
            "scope_value": scope_value,
        }
        self._cache_set(cache_key, payload, self.CACHE_TTL_SECONDS)
        return payload
