"""
东方财富龙虎榜数据抓取服务

合规原则：
1. 只采集公开可访问内容的结构化摘要数据
2. 不模拟登录、不使用 Cookie、不绕过反爬
3. 控制并发与请求频率，遵守礼貌爬虫原则
4. 文本字段进行长度截断
"""
from __future__ import annotations

import asyncio
import logging
import random
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.lhb_stock_item import LhbStockItem
from models.lhb_stock_summary import LhbStockSummary

logger = logging.getLogger(__name__)


class EastmoneyLhbService:
    BASE_URL = "https://data.eastmoney.com/stock/lhb.html"
    LIST_PAGE_URL = "https://data.eastmoney.com/stock/tradedetail.html"
    STOCK_STAT_PAGE_URL = "https://data.eastmoney.com/stock/stockstatistic.html"
    INST_SEAT_TRACK_PAGE_URL = "https://data.eastmoney.com/stock/jgstatistic.html"
    ACTIVE_BROKER_PAGE_URL = "https://data.eastmoney.com/stock/hyyyb.html"
    BROKER_RANK_PAGE_URL = "https://data.eastmoney.com/stock/yybph.html"
    BROKER_STATS_PAGE_URL = "https://data.eastmoney.com/stock/traderstatistic.html"
    DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

    LIST_TTL_SECONDS = 2 * 3600
    SUMMARY_TTL_SECONDS = 4 * 3600
    INSTITUTION_TTL_SECONDS = 2 * 3600
    BROKER_TTL_SECONDS = 2 * 3600
    MAX_RETRIES = 2

    REPORT_NAME_HINTS = {
        "list": ["LHB", "LIST", "STOCK", "DETAIL"],
        "summary": ["LHB", "SUM", "SUMMARY", "STAT"],
        "inst_trades": ["LHB", "ORG", "INST", "TRADE"],
        "inst_seat_track": ["LHB", "ORG", "SEAT", "TRACK", "STAT"],
        "broker_active": ["LHB", "BROKER", "ACTIVE", "DEPT"],
        "broker_rank": ["LHB", "BROKER", "RANK"],
        "broker_stats": ["LHB", "BROKER", "STAT", "TRADER"],
    }

    PREFERRED_REPORTS = {
        "list": "RPT_ORGANIZATION_TRADE_DETAILSNEW",
        "summary": "RPT_BILLBOARD_TRADEALLNEW",
        "inst_trades": "RPT_ORGANIZATION_TRADE_DETAILSNEW",
        "inst_seat_track": "RPT_ORGANIZATION_SEATNEW",
        "broker_active": "RPT_OPERATEDEPT_ACTIVE",
        "broker_rank": "RPT_RATEDEPT_RETURNT_RANKING",
        "broker_stats": "RPT_OPERATEDEPT_LIST_STATISTICS",
    }

    FALLBACK_REPORTS = {
        "list": ["RPT_LHB_LIST", "RPT_LHB_STOCK", "RPT_LHB_DETAIL"],
        "summary": ["RPT_LHB_SUMMARY", "RPT_LHB_STAT", "RPT_LHB_SUM"],
        "inst_trades": ["RPT_LHB_JGMMTJ", "RPT_LHB_ORG_TRADE", "RPT_LHB_JGMM"],
        "inst_seat_track": [
            "RPT_ORGANIZATION_SEATNEW",
            "RPT_LHB_JGSTAT",
            "RPT_LHB_JGTRACK",
            "RPT_LHB_SEAT_TRACK",
        ],
        "broker_active": [
            "RPT_OPERATEDEPT_ACTIVE",
            "RPT_LHB_HYYYB",
            "RPT_LHB_ACTIVE_BROKER",
            "RPT_LHB_BROKER_ACTIVE",
        ],
        "broker_rank": [
            "RPT_RATEDEPT_RETURNT_RANKING",
            "RPT_LHB_YYBPH",
            "RPT_LHB_BROKER_RANK",
            "RPT_LHB_YYB_RANK",
        ],
        "broker_stats": [
            "RPT_OPERATEDEPT_LIST_STATISTICS",
            "RPT_LHB_TRADERSTAT",
            "RPT_LHB_BROKER_STAT",
            "RPT_LHB_TRADER_STAT",
        ],
    }

    _memory_cache: Dict[str, Dict[str, Any]] = {}

    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        timeout: int = 12,
        max_concurrent_requests: int = 3,
    ):
        self.db_session = db_session
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://data.eastmoney.com/stock/",
        }
        self._report_cache: Dict[str, str] = {}

    # ------------------------- 公共工具 -------------------------
    @staticmethod
    def _normalize_trade_date(raw: Optional[str]) -> Optional[str]:
        if not raw:
            return None
        s = str(raw).strip()
        if not s:
            return None
        if re.match(r"\d{4}-\d{2}-\d{2}$", s):
            return s
        if re.match(r"\d{8}$", s):
            return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
        return s

    @staticmethod
    def _date_to_ymd(date_obj: datetime) -> str:
        return date_obj.strftime("%Y-%m-%d")

    @staticmethod
    def _truncate(text: Optional[str], limit: int = 300) -> Optional[str]:
        if not text:
            return text
        value = str(text).strip()
        if len(value) <= limit:
            return value
        return value[: limit - 3] + "..."

    @staticmethod
    def _parse_number(raw: Any) -> Optional[float]:
        if raw is None:
            return None
        s = str(raw).strip().replace(",", "")
        if not s or s in {"--", "-"}:
            return None
        s = s.replace("亿元", "亿").replace("万元", "万")
        m = re.search(r"-?\d+(?:\.\d+)?", s)
        if not m:
            return None
        value = float(m.group(0))
        if "亿" in s:
            return value * 100000000
        if "万" in s:
            return value * 10000
        return value

    @staticmethod
    def _parse_percent(raw: Any) -> Optional[float]:
        if raw is None:
            return None
        s = str(raw).strip().replace("%", "")
        if not s or s in {"--", "-"}:
            return None
        try:
            return float(s)
        except Exception:
            return None

    @staticmethod
    def _pick(item: Dict[str, Any], keys: List[str]) -> Any:
        for key in keys:
            if key in item and item.get(key) not in (None, ""):
                return item.get(key)
        return None

    async def _request_text(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        last_error: Optional[Exception] = None
        for attempt in range(1, self.MAX_RETRIES + 2):
            try:
                async with self.semaphore:
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                        resp = await client.get(url, params=params, follow_redirects=True)
                        resp.raise_for_status()
                        return resp.text
            except Exception as exc:
                last_error = exc
                logger.warning(f"请求失败（{attempt}）: {url} - {exc}")
        if last_error:
            raise last_error
        return ""

    async def _request_json(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            async with self.semaphore:
                await asyncio.sleep(random.uniform(0.1, 0.3))
                async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                    resp = await client.get(url, params=params, follow_redirects=True)
                    if resp.status_code != 200:
                        return None
                    return resp.json()
        except Exception as exc:
            logger.warning(f"JSON 请求失败: {url} - {exc}")
            return None

    def _extract_report_names(self, html_text: str) -> List[str]:
        patterns = [
            r"reportName\"\s*:\s*\"(.*?)\"",
            r"reportName=([A-Za-z0-9_]+)",
        ]
        names: List[str] = []
        for pattern in patterns:
            for match in re.findall(pattern, html_text):
                if match and match not in names:
                    names.append(match)
        return names

    def _select_report_name(self, kind: str, candidates: List[str]) -> Optional[str]:
        if not candidates:
            return None
        preferred = self.PREFERRED_REPORTS.get(kind)
        if preferred and preferred in candidates:
            return preferred
        hints = self.REPORT_NAME_HINTS.get(kind, [])
        for name in candidates:
            name_upper = name.upper()
            if "LHB" in name_upper and any(h in name_upper for h in hints):
                return name
        for name in candidates:
            if "LHB" in name.upper():
                return name
        return candidates[0]

    async def _discover_report_name(self, kind: str, page_url: Optional[str] = None) -> Optional[str]:
        if kind in self._report_cache:
            return self._report_cache[kind]
        target_url = page_url or self.BASE_URL
        try:
            text = await self._request_text(target_url)
            candidates = self._extract_report_names(text)
            report_name = self._select_report_name(kind, candidates)
            if report_name:
                self._report_cache[kind] = report_name
                return report_name
        except Exception as exc:
            logger.warning(f"获取龙虎榜页面失败，无法解析 reportName: {exc}")
        for fallback in self.FALLBACK_REPORTS.get(kind, []):
            if fallback:
                logger.warning(f"使用 reportName 兜底值 {fallback} ({kind})")
                self._report_cache[kind] = fallback
                return fallback
        return None

    async def _fetch_datacenter(
        self,
        report_name: str,
        filter_expr: Optional[str],
        page: int,
        page_size: int,
        sort_columns: str,
        sort_types: str = "-1",
    ) -> Optional[List[Dict[str, Any]]]:
        params: Dict[str, Any] = {
            "reportName": report_name,
            "columns": "ALL",
            "pageNumber": page,
            "pageSize": page_size,
            "sortColumns": sort_columns,
            "sortTypes": sort_types,
        }
        if filter_expr:
            params["filter"] = filter_expr
        data = await self._request_json(self.DATACENTER_URL, params)
        if not data:
            return None
        result = data.get("result") or {}
        items = result.get("data") or []
        if not isinstance(items, list) or not items:
            return None
        return items

    def _map_list_item(self, item: Dict[str, Any], trade_date: str) -> Optional[Dict[str, Any]]:
        code = self._pick(item, ["SECURITY_CODE", "SECUCODE", "SECURITY_CODE_A", "CODE"])
        name = self._pick(item, ["SECURITY_NAME_ABBR", "SECURITY_NAME", "NAME"])
        if not code or not name:
            return None
        close = self._parse_number(self._pick(item, ["CLOSE_PRICE", "CLOSE"]))
        pct_change = self._parse_percent(self._pick(item, ["CHANGE_RATE", "PCT_CHANGE", "ZDF"]))
        buy_amount = self._parse_number(self._pick(item, ["BUY_AMT", "BUY_AMOUNT", "BILL_BOARD_BUY_AMT"]))
        sell_amount = self._parse_number(self._pick(item, ["SELL_AMT", "SELL_AMOUNT", "BILL_BOARD_SELL_AMT"]))
        net_buy_amount = self._parse_number(self._pick(item, ["NET_BUY_AMT", "NET_AMT", "BILL_BOARD_NET_AMT", "BILLBOARD_NET_AMT"]))
        turnover = self._parse_number(self._pick(item, ["ACCUM_AMOUNT", "TURNOVER", "TURNOVER_AMT", "TURNOVER_VALUE"]))
        reason = self._truncate(self._pick(item, ["EXPLANATION", "REASON", "REASON_TEXT", "LISTING_REASON"]))
        if not reason:
            return None
        if reason == "龙虎榜":
            return None
        rank = self._pick(item, ["RANK", "RANKING", "NO"])
        try:
            rank = int(rank) if rank is not None else None
        except Exception:
            rank = None
        return {
            "trade_date": trade_date,
            "code": str(code),
            "name": str(name),
            "close": close,
            "pct_change": pct_change,
            "buy_amount": buy_amount,
            "sell_amount": sell_amount,
            "net_buy_amount": net_buy_amount,
            "turnover": turnover,
            "reason": reason,
            "rank": rank,
            "source_url": self.LIST_PAGE_URL,
            "as_of": datetime.now(),
        }

    def _map_summary_item(self, item: Dict[str, Any], window_days: int, end_trade_date: str) -> Optional[Dict[str, Any]]:
        code = self._pick(item, ["SECURITY_CODE", "SECUCODE", "SECURITY_CODE_A", "CODE"])
        name = self._pick(item, ["SECURITY_NAME_ABBR", "SECURITY_NAME", "NAME"])
        if not code or not name:
            return None
        appear_count = self._pick(item, ["APPEAR_COUNT", "COUNT", "APPEAR_NUM", "CNT"])
        try:
            appear_count = int(appear_count) if appear_count is not None else None
        except Exception:
            appear_count = None
        buy_amount = self._parse_number(self._pick(item, ["BUY_AMOUNT", "BUY_AMT"]))
        sell_amount = self._parse_number(self._pick(item, ["SELL_AMOUNT", "SELL_AMT"]))
        net_buy_amount = self._parse_number(self._pick(item, ["NET_BUY_AMT", "NET_AMOUNT", "NET_AMT"]))
        total_amount = self._parse_number(self._pick(item, ["TOTAL_AMOUNT", "TOTAL_AMT", "AMOUNT"]))
        rank = self._pick(item, ["RANK", "RANKING", "NO"])
        try:
            rank = int(rank) if rank is not None else None
        except Exception:
            rank = None
        return {
            "window_days": window_days,
            "end_trade_date": end_trade_date,
            "code": str(code),
            "name": str(name),
            "appear_count": appear_count,
            "net_buy_amount": net_buy_amount,
            "buy_amount": buy_amount,
            "sell_amount": sell_amount,
            "total_amount": total_amount,
            "rank": rank,
            "source_url": self.BASE_URL,
            "as_of": datetime.now(),
        }

    async def _is_stale_list(self, trade_date: str) -> bool:
        if not self.db_session:
            return True
        result = await self.db_session.execute(
            select(func.max(LhbStockItem.updated_at)).where(LhbStockItem.trade_date == trade_date)
        )
        latest = result.scalar()
        if not latest:
            return True
        return datetime.now() - latest > timedelta(seconds=self.LIST_TTL_SECONDS)

    async def _is_stale_summary(self, window_days: int, end_trade_date: str) -> bool:
        if not self.db_session:
            return True
        result = await self.db_session.execute(
            select(func.max(LhbStockSummary.updated_at)).where(
                (LhbStockSummary.window_days == window_days)
                & (LhbStockSummary.end_trade_date == end_trade_date)
            )
        )
        latest = result.scalar()
        if not latest:
            return True
        return datetime.now() - latest > timedelta(seconds=self.SUMMARY_TTL_SECONDS)

    async def _upsert_rows(self, model: Any, rows: List[Dict[str, Any]], index_elements: List[str]):
        if not self.db_session or not rows:
            return
        stmt = insert(model).values(rows)
        update_cols = {k: getattr(stmt.excluded, k) for k in rows[0].keys() if k not in {"id", "created_at"}}
        stmt = stmt.on_conflict_do_update(index_elements=index_elements, set_=update_cols)
        await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def _load_list_from_db(self, trade_date: str, page: int, page_size: int) -> Dict[str, Any]:
        if not self.db_session:
            return {"total": 0, "data": []}
        try:
            await self.db_session.execute(
                delete(LhbStockItem).where(
                    (LhbStockItem.trade_date == trade_date)
                    & (LhbStockItem.reason == "龙虎榜")
                )
            )
            await self.db_session.commit()
        except Exception as exc:
            logger.warning(f"清理上榜原因为龙虎榜的数据失败: {exc}")
        query = select(LhbStockItem).where(LhbStockItem.trade_date == trade_date)
        result = await self.db_session.execute(query)
        rows = [self._model_to_dict(item) for item in result.scalars().all()]
        def sort_key(item: Dict[str, Any]):
            code = str(item.get("code") or "")
            return code

        rows.sort(key=sort_key)
        normalized: List[Dict[str, Any]] = []
        seen = set()
        for row in rows:
            reason = row.get("reason")
            if not reason or reason == "龙虎榜":
                continue
            row["reason"] = reason
            key = (row.get("code"), reason)
            if key in seen:
                continue
            seen.add(key)
            normalized.append(row)
        normalized.sort(key=sort_key)
        total = len(normalized)
        start = max((page - 1), 0) * page_size
        data = normalized[start : start + page_size]
        return {"total": total, "data": data}

    async def _load_summary_from_db(self, window_days: int, end_trade_date: str, page: int, page_size: int) -> Dict[str, Any]:
        if not self.db_session:
            return {"total": 0, "data": []}
        query = select(LhbStockSummary).where(
            (LhbStockSummary.window_days == window_days)
            & (LhbStockSummary.end_trade_date == end_trade_date)
        )
        result = await self.db_session.execute(query)
        rows = [self._model_to_dict(item) for item in result.scalars().all()]
        total = len(rows)
        start = max((page - 1), 0) * page_size
        data = rows[start : start + page_size]
        return {"total": total, "data": data}

    @staticmethod
    def _model_to_dict(obj: Any) -> Dict[str, Any]:
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        return dict(obj)

    @classmethod
    def _cache_key(cls, kind: str, **kwargs: Any) -> str:
        segments = [kind]
        for key in sorted(kwargs.keys()):
            segments.append(f"{key}={kwargs.get(key)}")
        return "|".join(segments)

    @classmethod
    def _get_cache(cls, key: str, ttl_seconds: int) -> Optional[Dict[str, Any]]:
        cached = cls._memory_cache.get(key)
        if not cached:
            return None
        ts = cached.get("ts")
        if not ts:
            return None
        if datetime.now() - ts > timedelta(seconds=ttl_seconds):
            return None
        return cached.get("data")

    @classmethod
    def _set_cache(cls, key: str, data: Dict[str, Any]) -> None:
        cls._memory_cache[key] = {"ts": datetime.now(), "data": data}

    async def _fetch_list_from_web(self, trade_date: str, page: int, page_size: int) -> List[Dict[str, Any]]:
        report_name = await self._discover_report_name("list", page_url=self.LIST_PAGE_URL)
        if not report_name:
            return []
        filter_expr = f"(TRADE_DATE='{trade_date}')"
        sort_columns = "SECURITY_CODE"
        sort_types = "1"
        if report_name == "RPT_ORGANIZATION_TRADE_DETAILSNEW":
            sort_columns = "SECURITY_CODE"
            sort_types = "1"
        api_items = await self._fetch_datacenter(
            report_name=report_name,
            filter_expr=filter_expr,
            page=page,
            page_size=page_size,
            sort_columns=sort_columns,
            sort_types=sort_types,
        )
        if not api_items:
            return []
        mapped = [self._map_list_item(item, trade_date) for item in api_items]
        mapped = [m for m in mapped if m]
        mapped.sort(key=lambda x: str(x.get("code") or ""))
        for idx, item in enumerate(mapped, start=1):
            item["rank"] = item.get("rank") or idx
        return mapped

    async def _fetch_summary_from_web(
        self,
        window_days: int,
        end_trade_date: str,
        page: int,
        page_size: int,
    ) -> List[Dict[str, Any]]:
        report_name = await self._discover_report_name(
            "summary",
            page_url=self.STOCK_STAT_PAGE_URL if window_days == 30 else None,
        )
        if not report_name:
            return []
        filter_expr = f"(TRADE_DATE='{end_trade_date}')"
        api_items = await self._fetch_datacenter(
            report_name=report_name,
            filter_expr=filter_expr,
            page=page,
            page_size=page_size,
            sort_columns="APPEAR_COUNT,NET_BUY_AMT",
            sort_types="-1,-1",
        )
        if not api_items:
            return []
        mapped = [self._map_summary_item(item, window_days, end_trade_date) for item in api_items]
        mapped = [m for m in mapped if m]
        mapped.sort(key=lambda x: x.get("appear_count") or 0, reverse=True)
        return mapped

    def _map_institution_trade_item(self, item: Dict[str, Any], trade_date: str) -> Optional[Dict[str, Any]]:
        code = self._pick(item, ["SECURITY_CODE", "SECUCODE", "SECURITY_CODE_A", "CODE"])
        name = self._pick(item, ["SECURITY_NAME_ABBR", "SECURITY_NAME", "NAME"])
        if not code or not name:
            return None
        close = self._parse_number(self._pick(item, ["CLOSE_PRICE", "CLOSE", "PRICE"]))
        pct_change = self._parse_percent(self._pick(item, ["CHANGE_RATE", "PCT_CHANGE", "ZDF"]))
        buy_count = self._pick(item, ["BUY_COUNT", "BUY_NUM", "BUY_CNT"])
        sell_count = self._pick(item, ["SELL_COUNT", "SELL_NUM", "SELL_CNT"])
        try:
            buy_count = int(buy_count) if buy_count is not None else None
        except Exception:
            buy_count = None
        try:
            sell_count = int(sell_count) if sell_count is not None else None
        except Exception:
            sell_count = None
        buy_amount = self._parse_number(self._pick(item, ["BUY_AMT", "BUY_AMOUNT", "BILL_BOARD_BUY_AMT"]))
        sell_amount = self._parse_number(self._pick(item, ["SELL_AMT", "SELL_AMOUNT", "BILL_BOARD_SELL_AMT"]))
        net_buy_amount = self._parse_number(self._pick(item, ["NET_BUY_AMT", "NET_AMT", "BILL_BOARD_NET_AMT"]))
        turnover = self._parse_number(self._pick(item, ["TURNOVER", "TURNOVER_AMT", "ACCUM_AMOUNT", "AMOUNT"]))
        reason = self._truncate(self._pick(item, ["EXPLANATION", "REASON", "REASON_TEXT", "LISTING_REASON"]))
        rank = self._pick(item, ["RANK", "RANKING", "NO"])
        try:
            rank = int(rank) if rank is not None else None
        except Exception:
            rank = None
        return {
            "trade_date": trade_date,
            "code": str(code),
            "name": str(name),
            "close": close,
            "pct_change": pct_change,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "buy_amount": buy_amount,
            "sell_amount": sell_amount,
            "net_buy_amount": net_buy_amount,
            "turnover": turnover,
            "reason": reason,
            "rank": rank,
            "source_url": self.BASE_URL,
            "as_of": datetime.now(),
        }

    def _map_institution_seat_track_item(
        self, item: Dict[str, Any], window_days: int, end_trade_date: str
    ) -> Optional[Dict[str, Any]]:
        code = self._pick(item, ["SECURITY_CODE", "SECUCODE", "SECURITY_CODE_A", "CODE"])
        name = self._pick(item, ["SECURITY_NAME_ABBR", "SECURITY_NAME", "NAME"])
        if not code or not name:
            return None
        close = self._parse_number(self._pick(item, ["CLOSE_PRICE", "CLOSE", "PRICE"]))
        pct_change = self._parse_percent(self._pick(item, ["CHANGE_RATE", "PCT_CHANGE", "ZDF"]))
        buy_amount = self._parse_number(self._pick(item, ["BUY_AMT", "BUY_AMOUNT", "ORG_BUY_AMT"]))
        sell_amount = self._parse_number(self._pick(item, ["SELL_AMT", "SELL_AMOUNT", "ORG_SELL_AMT"]))
        net_buy_amount = self._parse_number(self._pick(item, ["NET_BUY_AMT", "NET_AMT", "ORG_NET_AMT"]))
        buy_count = self._pick(
            item,
            ["BUY_COUNT", "BUY_NUM", "BUY_CNT", "BUY_TIMES", "ORG_BUY_CNT"],
        )
        sell_count = self._pick(
            item,
            ["SELL_COUNT", "SELL_NUM", "SELL_CNT", "SELL_TIMES", "ORG_SELL_CNT"],
        )
        try:
            buy_count = int(buy_count) if buy_count is not None else None
        except Exception:
            buy_count = None
        try:
            sell_count = int(sell_count) if sell_count is not None else None
        except Exception:
            sell_count = None
        net_buy_ratio = self._parse_percent(self._pick(item, ["NET_BUY_RATIO", "NET_RATIO", "NET_BUY_RATE"]))
        rank = self._pick(item, ["RANK", "RANKING", "NO"])
        try:
            rank = int(rank) if rank is not None else None
        except Exception:
            rank = None
        return {
            "window_days": window_days,
            "end_trade_date": end_trade_date,
            "code": str(code),
            "name": str(name),
            "close": close,
            "pct_change": pct_change,
            "net_buy_amount": net_buy_amount,
            "buy_amount": buy_amount,
            "buy_count": buy_count,
            "sell_amount": sell_amount,
            "sell_count": sell_count,
            "net_buy_ratio": net_buy_ratio,
            "rank": rank,
            "source_url": self.BASE_URL,
            "as_of": datetime.now(),
        }

    def _map_active_broker_item(self, item: Dict[str, Any], trade_date: str) -> Optional[Dict[str, Any]]:
        broker_name = self._pick(item, ["OPERATEDEPT_NAME", "BROKER_NAME", "BRANCH_NAME", "SEAT_NAME", "NAME"])
        if not broker_name:
            return None
        buy_count = self._pick(item, ["BUYER_APPEAR_NUM", "BUY_COUNT", "BUY_NUM", "BUY_CNT"])
        sell_count = self._pick(item, ["SELLER_APPEAR_NUM", "SELL_COUNT", "SELL_NUM", "SELL_CNT"])
        try:
            buy_count = int(buy_count) if buy_count is not None else None
        except Exception:
            buy_count = None
        try:
            sell_count = int(sell_count) if sell_count is not None else None
        except Exception:
            sell_count = None
        buy_amount = self._parse_number(self._pick(item, ["TOTAL_BUYAMT", "BUY_AMT", "BUY_AMOUNT"]))
        sell_amount = self._parse_number(self._pick(item, ["TOTAL_SELLAMT", "SELL_AMT", "SELL_AMOUNT"]))
        net_buy_amount = self._parse_number(self._pick(item, ["TOTAL_NETAMT", "NET_BUY_AMT", "NET_AMT"]))
        stocks = self._truncate(
            self._pick(item, ["BUY_STOCK", "SECURITY_NAME", "STOCK_LIST", "STOCKS"]),
            limit=200,
        )
        rank = self._pick(item, ["RANK", "RANKING", "NO"])
        try:
            rank = int(rank) if rank is not None else None
        except Exception:
            rank = None
        return {
            "trade_date": trade_date,
            "broker_name": str(broker_name),
            "buy_count": buy_count,
            "sell_count": sell_count,
            "buy_amount": buy_amount,
            "sell_amount": sell_amount,
            "net_buy_amount": net_buy_amount,
            "stocks": stocks,
            "rank": rank,
            "source_url": self.ACTIVE_BROKER_PAGE_URL,
            "as_of": datetime.now(),
        }

    def _map_broker_rank_item(self, item: Dict[str, Any], window_days: int, end_trade_date: str) -> Optional[Dict[str, Any]]:
        broker_name = self._pick(item, ["OPERATEDEPT_NAME", "BROKER_NAME", "BRANCH_NAME", "SEAT_NAME", "NAME"])
        if not broker_name:
            return None
        buy_times_1d = self._pick(item, ["TOTAL_BUYER_SALESTIMES_1DAY", "BUY_TIMES_1DAY"])
        buy_times_2d = self._pick(item, ["TOTAL_BUYER_SALESTIMES_2DAY", "BUY_TIMES_2DAY"])
        buy_times_3d = self._pick(item, ["TOTAL_BUYER_SALESTIMES_3DAY", "BUY_TIMES_3DAY"])
        buy_times_5d = self._pick(item, ["TOTAL_BUYER_SALESTIMES_5DAY", "BUY_TIMES_5DAY"])
        buy_times_10d = self._pick(item, ["TOTAL_BUYER_SALESTIMES_10DAY", "BUY_TIMES_10DAY"])
        try:
            buy_times_1d = int(buy_times_1d) if buy_times_1d is not None else None
        except Exception:
            buy_times_1d = None
        try:
            buy_times_2d = int(buy_times_2d) if buy_times_2d is not None else None
        except Exception:
            buy_times_2d = None
        try:
            buy_times_3d = int(buy_times_3d) if buy_times_3d is not None else None
        except Exception:
            buy_times_3d = None
        try:
            buy_times_5d = int(buy_times_5d) if buy_times_5d is not None else None
        except Exception:
            buy_times_5d = None
        try:
            buy_times_10d = int(buy_times_10d) if buy_times_10d is not None else None
        except Exception:
            buy_times_10d = None
        avg_increase_1d = self._parse_percent(self._pick(item, ["AVERAGE_INCREASE_1DAY", "AVG_INCREASE_1DAY"]))
        avg_increase_2d = self._parse_percent(self._pick(item, ["AVERAGE_INCREASE_2DAY", "AVG_INCREASE_2DAY"]))
        avg_increase_3d = self._parse_percent(self._pick(item, ["AVERAGE_INCREASE_3DAY", "AVG_INCREASE_3DAY"]))
        avg_increase_5d = self._parse_percent(self._pick(item, ["AVERAGE_INCREASE_5DAY", "AVG_INCREASE_5DAY"]))
        avg_increase_10d = self._parse_percent(self._pick(item, ["AVERAGE_INCREASE_10DAY", "AVG_INCREASE_10DAY"]))
        rise_probability_1d = self._parse_percent(self._pick(item, ["RISE_PROBABILITY_1DAY", "UP_PROBABILITY_1DAY"]))
        rise_probability_2d = self._parse_percent(self._pick(item, ["RISE_PROBABILITY_2DAY", "UP_PROBABILITY_2DAY"]))
        rise_probability_3d = self._parse_percent(self._pick(item, ["RISE_PROBABILITY_3DAY", "UP_PROBABILITY_3DAY"]))
        rise_probability_5d = self._parse_percent(self._pick(item, ["RISE_PROBABILITY_5DAY", "UP_PROBABILITY_5DAY"]))
        rise_probability_10d = self._parse_percent(self._pick(item, ["RISE_PROBABILITY_10DAY", "UP_PROBABILITY_10DAY"]))
        rank = self._pick(item, ["RANK", "RANKING", "NO"])
        try:
            rank = int(rank) if rank is not None else None
        except Exception:
            rank = None
        return {
            "window_days": window_days,
            "end_trade_date": end_trade_date,
            "broker_name": str(broker_name),
            "buy_times_1d": buy_times_1d,
            "avg_increase_1d": avg_increase_1d,
            "rise_probability_1d": rise_probability_1d,
            "buy_times_2d": buy_times_2d,
            "avg_increase_2d": avg_increase_2d,
            "rise_probability_2d": rise_probability_2d,
            "buy_times_3d": buy_times_3d,
            "avg_increase_3d": avg_increase_3d,
            "rise_probability_3d": rise_probability_3d,
            "buy_times_5d": buy_times_5d,
            "avg_increase_5d": avg_increase_5d,
            "rise_probability_5d": rise_probability_5d,
            "buy_times_10d": buy_times_10d,
            "avg_increase_10d": avg_increase_10d,
            "rise_probability_10d": rise_probability_10d,
            "rank": rank,
            "source_url": self.BROKER_RANK_PAGE_URL,
            "as_of": datetime.now(),
        }

    def _map_broker_onlist_item(self, item: Dict[str, Any], window_days: int, end_trade_date: str) -> Optional[Dict[str, Any]]:
        broker_name = self._pick(item, ["OPERATEDEPT_NAME", "BROKER_NAME", "BRANCH_NAME", "SEAT_NAME", "NAME"])
        if not broker_name:
            return None
        total_amount = self._parse_number(self._pick(item, ["AMOUNT", "TOTAL_AMOUNT", "TOTAL_AMT"]))
        buy_amount = self._parse_number(self._pick(item, ["ACT_BUY", "BUY_AMT", "BUY_AMOUNT"]))
        sell_amount = self._parse_number(self._pick(item, ["ACT_SELL", "SELL_AMT", "SELL_AMOUNT"]))
        buy_count = self._pick(item, ["TOTAL_BUYER_SALESTIMES", "BUY_COUNT", "BUY_NUM", "BUY_CNT"])
        sell_count = self._pick(item, ["TOTAL_SELLER_SALESTIMES", "SELL_COUNT", "SELL_NUM", "SELL_CNT"])
        try:
            buy_count = int(buy_count) if buy_count is not None else None
        except Exception:
            buy_count = None
        try:
            sell_count = int(sell_count) if sell_count is not None else None
        except Exception:
            sell_count = None
        rank = self._pick(item, ["RANK", "RANKING", "NO"])
        try:
            rank = int(rank) if rank is not None else None
        except Exception:
            rank = None
        return {
            "window_days": window_days,
            "end_trade_date": end_trade_date,
            "broker_name": str(broker_name),
            "total_amount": total_amount,
            "buy_amount": buy_amount,
            "buy_count": buy_count,
            "sell_amount": sell_amount,
            "sell_count": sell_count,
            "rank": rank,
            "source_url": self.BROKER_STATS_PAGE_URL,
            "as_of": datetime.now(),
        }

    async def _fetch_institution_trades_from_web(self, trade_date: str, page: int, page_size: int) -> List[Dict[str, Any]]:
        report_name = await self._discover_report_name("inst_trades")
        if not report_name:
            return []
        filter_expr = f"(TRADE_DATE='{trade_date}')"
        api_items = await self._fetch_datacenter(
            report_name=report_name,
            filter_expr=filter_expr,
            page=page,
            page_size=page_size,
            sort_columns="NET_BUY_AMT",
            sort_types="-1",
        )
        if not api_items:
            return []
        mapped = [self._map_institution_trade_item(item, trade_date) for item in api_items]
        mapped = [m for m in mapped if m]
        for idx, item in enumerate(mapped, start=1):
            item["rank"] = item.get("rank") or idx
        return mapped

    async def _fetch_institution_seat_track_from_web(
        self, window_days: int, end_trade_date: str, page: int, page_size: int
    ) -> List[Dict[str, Any]]:
        cycle_map = {
            30: "01",
            90: "02",
            180: "03",
            365: "04",
        }
        cycle_code = cycle_map.get(window_days)
        if not cycle_code:
            if window_days <= 30:
                cycle_code = "01"
            elif window_days <= 90:
                cycle_code = "02"
            elif window_days <= 180:
                cycle_code = "03"
            else:
                cycle_code = "04"
        report_name = await self._discover_report_name(
            "inst_seat_track",
            page_url=self.INST_SEAT_TRACK_PAGE_URL if window_days == 30 else None,
        )
        filter_expr = f"(STATISTICSCYCLE=\"{cycle_code}\")"
        candidates: List[str] = []
        if report_name:
            candidates.append(report_name)
        candidates.extend(self.FALLBACK_REPORTS.get("inst_seat_track", []))
        seen = set()
        for candidate in candidates:
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            api_items = await self._fetch_datacenter(
                report_name=candidate,
                filter_expr=filter_expr,
                page=page,
                page_size=page_size,
                sort_columns="ONLIST_TIMES",
                sort_types="-1",
            )
            if not api_items:
                continue
            mapped = [self._map_institution_seat_track_item(item, window_days, end_trade_date) for item in api_items]
            mapped = [m for m in mapped if m]
            if not mapped:
                continue
            for idx, item in enumerate(mapped, start=1):
                item["rank"] = item.get("rank") or idx
            return mapped
        return []

    async def _fetch_active_brokers_from_web(self, trade_date: str, page: int, page_size: int) -> List[Dict[str, Any]]:
        report_name = await self._discover_report_name("broker_active", page_url=self.ACTIVE_BROKER_PAGE_URL)
        if not report_name:
            return []
        filter_expr = f"(ONLIST_DATE='{trade_date}')"
        api_items = await self._fetch_datacenter(
            report_name=report_name,
            filter_expr=filter_expr,
            page=page,
            page_size=page_size,
            sort_columns="TOTAL_NETAMT",
            sort_types="-1",
        )
        if not api_items:
            return []
        mapped = [self._map_active_broker_item(item, trade_date) for item in api_items]
        mapped = [m for m in mapped if m]
        for idx, item in enumerate(mapped, start=1):
            item["rank"] = item.get("rank") or idx
        return mapped

    async def _fetch_broker_rank_from_web(
        self, window_days: int, end_trade_date: str, page: int, page_size: int
    ) -> List[Dict[str, Any]]:
        cycle_map = {
            30: "01",
            90: "02",
            180: "03",
            365: "04",
        }
        cycle_code = cycle_map.get(window_days)
        if not cycle_code:
            if window_days <= 30:
                cycle_code = "01"
            elif window_days <= 90:
                cycle_code = "02"
            elif window_days <= 180:
                cycle_code = "03"
            else:
                cycle_code = "04"
        report_name = await self._discover_report_name("broker_rank", page_url=self.BROKER_RANK_PAGE_URL)
        if not report_name:
            return []
        filter_expr = f"(STATISTICSCYCLE=\"{cycle_code}\")"
        api_items = await self._fetch_datacenter(
            report_name=report_name,
            filter_expr=filter_expr,
            page=page,
            page_size=page_size,
            sort_columns="TOTAL_BUYER_SALESTIMES_1DAY",
            sort_types="-1",
        )
        if not api_items:
            return []
        mapped = [self._map_broker_rank_item(item, window_days, end_trade_date) for item in api_items]
        mapped = [m for m in mapped if m]
        for idx, item in enumerate(mapped, start=1):
            item["rank"] = item.get("rank") or idx
        return mapped

    async def _fetch_broker_onlist_from_web(
        self, window_days: int, end_trade_date: str, page: int, page_size: int
    ) -> List[Dict[str, Any]]:
        cycle_map = {
            30: "01",
            90: "02",
            180: "03",
            365: "04",
        }
        cycle_code = cycle_map.get(window_days)
        if not cycle_code:
            if window_days <= 30:
                cycle_code = "01"
            elif window_days <= 90:
                cycle_code = "02"
            elif window_days <= 180:
                cycle_code = "03"
            else:
                cycle_code = "04"
        report_name = await self._discover_report_name("broker_stats", page_url=self.BROKER_STATS_PAGE_URL)
        if not report_name:
            return []
        filter_expr = f"(STATISTICSCYCLE=\"{cycle_code}\")"
        api_items = await self._fetch_datacenter(
            report_name=report_name,
            filter_expr=filter_expr,
            page=page,
            page_size=page_size,
            sort_columns="AMOUNT",
            sort_types="-1",
        )
        if not api_items:
            return []
        mapped = [self._map_broker_onlist_item(item, window_days, end_trade_date) for item in api_items]
        mapped = [m for m in mapped if m]
        for idx, item in enumerate(mapped, start=1):
            item["rank"] = item.get("rank") or idx
        return mapped

    async def _latest_trade_date_from_db(self) -> Optional[str]:
        if not self.db_session:
            return None
        result = await self.db_session.execute(select(func.max(LhbStockItem.trade_date)))
        latest = result.scalar()
        return latest

    async def _guess_latest_trade_date(self) -> Optional[str]:
        today = datetime.now()
        for offset in range(0, 10):
            day = today - timedelta(days=offset)
            candidate = self._date_to_ymd(day)
            try:
                items = await self._fetch_list_from_web(candidate, page=1, page_size=20)
                if items:
                    return candidate
            except Exception as exc:
                logger.warning(f"尝试获取交易日失败 {candidate}: {exc}")
        return None

    async def _aggregate_summary_from_db(self, window_days: int, end_trade_date: str) -> List[Dict[str, Any]]:
        if not self.db_session:
            return []
        result = await self.db_session.execute(
            select(LhbStockItem.trade_date)
            .where(LhbStockItem.trade_date <= end_trade_date)
            .distinct()
            .order_by(LhbStockItem.trade_date.desc())
            .limit(window_days)
        )
        trade_dates = [row[0] for row in result.all()]
        if not trade_dates:
            return []
        rows_result = await self.db_session.execute(
            select(LhbStockItem).where(LhbStockItem.trade_date.in_(trade_dates))
        )
        rows = rows_result.scalars().all()
        summary_map: Dict[str, Dict[str, Any]] = {}
        for row in rows:
            key = str(row.code)
            data = summary_map.setdefault(
                key,
                {
                    "window_days": window_days,
                    "end_trade_date": end_trade_date,
                    "code": str(row.code),
                    "name": str(row.name),
                    "appear_count": 0,
                    "net_buy_amount": 0.0,
                    "buy_amount": 0.0,
                    "sell_amount": 0.0,
                    "total_amount": 0.0,
                    "rank": None,
                    "source_url": self.BASE_URL,
                    "as_of": datetime.now(),
                },
            )
            data["appear_count"] = (data.get("appear_count") or 0) + 1
            data["net_buy_amount"] = (data.get("net_buy_amount") or 0.0) + float(row.net_buy_amount or 0.0)
            data["buy_amount"] = (data.get("buy_amount") or 0.0) + float(row.buy_amount or 0.0)
            data["sell_amount"] = (data.get("sell_amount") or 0.0) + float(row.sell_amount or 0.0)
            total = float(row.buy_amount or 0.0) + float(row.sell_amount or 0.0)
            data["total_amount"] = (data.get("total_amount") or 0.0) + total
        items = list(summary_map.values())
        items.sort(key=lambda x: x.get("net_buy_amount") or 0.0, reverse=True)
        for idx, item in enumerate(items, start=1):
            item["rank"] = idx
        return items

    # ------------------------- 对外接口 -------------------------
    async def find_latest_trade_date(self, refresh: bool = False) -> Optional[str]:
        if not refresh:
            latest = await self._latest_trade_date_from_db()
            if latest:
                return latest
        return await self._guess_latest_trade_date()

    async def fetch_stocks(
        self,
        trade_date: Optional[str],
        page: int = 1,
        page_size: int = 50,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        trade_date = self._normalize_trade_date(trade_date)
        if not trade_date:
            trade_date = await self.find_latest_trade_date(refresh=refresh) or self._date_to_ymd(datetime.now())
        should_refresh = refresh or await self._is_stale_list(trade_date)
        data = await self._load_list_from_db(trade_date, page, page_size)
        if not should_refresh and data.get("data"):
            has_detail = any(
                (row.get("buy_amount") is not None)
                or (row.get("sell_amount") is not None)
                or (row.get("close") is not None)
                or (row.get("turnover") is not None)
                for row in data.get("data", [])
            )
            has_source = all(row.get("source_url") == self.LIST_PAGE_URL for row in data.get("data", []))
            should_refresh = (not has_detail) or (not has_source)
        if should_refresh:
            try:
                items = await self._fetch_list_from_web(trade_date, page, page_size)
                await self._upsert_rows(LhbStockItem, items, ["trade_date", "code", "reason"])
                data = await self._load_list_from_db(trade_date, page, page_size)
            except Exception as exc:
                logger.warning(f"抓取龙虎榜上榜个股失败: {exc}")
        return {
            "trade_date": trade_date,
            "page": page,
            "page_size": page_size,
            "total": data.get("total", 0),
            "data": data.get("data", []),
        }

    async def fetch_summary(
        self,
        window_days: int,
        end_trade_date: Optional[str],
        page: int = 1,
        page_size: int = 50,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        end_trade_date = self._normalize_trade_date(end_trade_date)
        if not end_trade_date:
            end_trade_date = await self.find_latest_trade_date(refresh=refresh) or self._date_to_ymd(datetime.now())
        if refresh or await self._is_stale_summary(window_days, end_trade_date):
            items: List[Dict[str, Any]] = []
            try:
                items = await self._fetch_summary_from_web(window_days, end_trade_date, page, page_size)
            except Exception as exc:
                logger.warning(f"抓取龙虎榜汇总失败: {exc}")
            if not items:
                try:
                    items = await self._aggregate_summary_from_db(window_days, end_trade_date)
                except Exception as exc:
                    logger.warning(f"本地汇总龙虎榜失败: {exc}")
            if items:
                await self._upsert_rows(LhbStockSummary, items, ["window_days", "end_trade_date", "code"])
        data = await self._load_summary_from_db(window_days, end_trade_date, page, page_size)
        return {
            "window_days": window_days,
            "end_trade_date": end_trade_date,
            "page": page,
            "page_size": page_size,
            "total": data.get("total", 0),
            "data": data.get("data", []),
        }

    async def fetch_institution_trades(
        self,
        trade_date: Optional[str],
        page: int = 1,
        page_size: int = 50,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        trade_date = self._normalize_trade_date(trade_date)
        if not trade_date:
            trade_date = await self.find_latest_trade_date(refresh=refresh) or self._date_to_ymd(datetime.now())
        cache_key = self._cache_key("inst_trades", trade_date=trade_date, page=page, page_size=page_size)
        cached = None if refresh else self._get_cache(cache_key, self.INSTITUTION_TTL_SECONDS)
        if cached:
            return cached
        items: List[Dict[str, Any]] = []
        try:
            items = await self._fetch_institution_trades_from_web(trade_date, page, page_size)
        except Exception as exc:
            logger.warning(f"抓取机构买卖情况失败: {exc}")
        data = {
            "trade_date": trade_date,
            "page": page,
            "page_size": page_size,
            "total": len(items),
            "data": items,
        }
        if items:
            self._set_cache(cache_key, data)
        return data

    async def fetch_institution_seat_track(
        self,
        window_days: int,
        end_trade_date: Optional[str],
        page: int = 1,
        page_size: int = 50,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        end_trade_date = self._normalize_trade_date(end_trade_date)
        if not end_trade_date:
            end_trade_date = await self.find_latest_trade_date(refresh=False)
            if not end_trade_date:
                end_trade_date = await self.find_latest_trade_date(refresh=refresh)
            if not end_trade_date:
                end_trade_date = self._date_to_ymd(datetime.now())
        cache_key = self._cache_key(
            "inst_seat_track", window_days=window_days, end_trade_date=end_trade_date, page=page, page_size=page_size
        )
        cached = None if refresh else self._get_cache(cache_key, self.INSTITUTION_TTL_SECONDS)
        if cached:
            return cached
        items: List[Dict[str, Any]] = []
        try:
            items = await self._fetch_institution_seat_track_from_web(window_days, end_trade_date, page, page_size)
        except Exception as exc:
            logger.warning(f"抓取机构席位追踪失败: {exc}")
        data = {
            "window_days": window_days,
            "end_trade_date": end_trade_date,
            "page": page,
            "page_size": page_size,
            "total": len(items),
            "data": items,
        }
        if items:
            self._set_cache(cache_key, data)
        return data

    async def fetch_active_brokers(
        self,
        trade_date: Optional[str],
        page: int = 1,
        page_size: int = 50,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        trade_date = self._normalize_trade_date(trade_date)
        if not trade_date:
            trade_date = await self.find_latest_trade_date(refresh=refresh) or self._date_to_ymd(datetime.now())
        cache_key = self._cache_key("broker_active", trade_date=trade_date, page=page, page_size=page_size)
        cached = None if refresh else self._get_cache(cache_key, self.BROKER_TTL_SECONDS)
        if cached:
            return cached
        items: List[Dict[str, Any]] = []
        try:
            items = await self._fetch_active_brokers_from_web(trade_date, page, page_size)
        except Exception as exc:
            logger.warning(f"抓取每日活跃营业部失败: {exc}")
        data = {
            "trade_date": trade_date,
            "page": page,
            "page_size": page_size,
            "total": len(items),
            "data": items,
        }
        if items:
            self._set_cache(cache_key, data)
        return data

    async def fetch_broker_rank(
        self,
        window_days: int,
        end_trade_date: Optional[str],
        page: int = 1,
        page_size: int = 50,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        end_trade_date = self._normalize_trade_date(end_trade_date)
        if not end_trade_date:
            end_trade_date = await self.find_latest_trade_date(refresh=refresh) or self._date_to_ymd(datetime.now())
        cache_key = self._cache_key(
            "broker_rank", window_days=window_days, end_trade_date=end_trade_date, page=page, page_size=page_size
        )
        cached = None if refresh else self._get_cache(cache_key, self.BROKER_TTL_SECONDS)
        if cached:
            return cached
        items: List[Dict[str, Any]] = []
        try:
            items = await self._fetch_broker_rank_from_web(window_days, end_trade_date, page, page_size)
        except Exception as exc:
            logger.warning(f"抓取营业部排行失败: {exc}")
        data = {
            "window_days": window_days,
            "end_trade_date": end_trade_date,
            "page": page,
            "page_size": page_size,
            "total": len(items),
            "data": items,
        }
        if items:
            self._set_cache(cache_key, data)
        return data

    async def fetch_broker_onlist_stats(
        self,
        window_days: int,
        end_trade_date: Optional[str],
        page: int = 1,
        page_size: int = 50,
        refresh: bool = False,
    ) -> Dict[str, Any]:
        end_trade_date = self._normalize_trade_date(end_trade_date)
        if not end_trade_date:
            end_trade_date = await self.find_latest_trade_date(refresh=refresh) or self._date_to_ymd(datetime.now())
        cache_key = self._cache_key(
            "broker_stats", window_days=window_days, end_trade_date=end_trade_date, page=page, page_size=page_size
        )
        cached = None if refresh else self._get_cache(cache_key, self.BROKER_TTL_SECONDS)
        if cached:
            return cached
        items: List[Dict[str, Any]] = []
        try:
            items = await self._fetch_broker_onlist_from_web(window_days, end_trade_date, page, page_size)
        except Exception as exc:
            logger.warning(f"抓取营业部上榜统计失败: {exc}")
        data = {
            "window_days": window_days,
            "end_trade_date": end_trade_date,
            "page": page,
            "page_size": page_size,
            "total": len(items),
            "data": items,
        }
        if items:
            self._set_cache(cache_key, data)
        return data
