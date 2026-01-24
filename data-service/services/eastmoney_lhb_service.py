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
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.lhb_stock_item import LhbStockItem
from models.lhb_stock_summary import LhbStockSummary

logger = logging.getLogger(__name__)


class EastmoneyLhbService:
    BASE_URL = "https://data.eastmoney.com/stock/lhb.html"
    DATACENTER_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"

    LIST_TTL_SECONDS = 2 * 3600
    SUMMARY_TTL_SECONDS = 4 * 3600
    MAX_RETRIES = 2

    REPORT_NAME_HINTS = {
        "list": ["LHB", "LIST", "STOCK", "DETAIL"],
        "summary": ["LHB", "SUM", "SUMMARY", "STAT"],
    }

    PREFERRED_REPORTS = {
        "list": "RPT_ORGANIZATION_TRADE_DETAILSNEW",
        "summary": "RPT_BILLBOARD_TRADEALLNEW",
    }

    FALLBACK_REPORTS = {
        "list": ["RPT_LHB_LIST", "RPT_LHB_STOCK", "RPT_LHB_DETAIL"],
        "summary": ["RPT_LHB_SUMMARY", "RPT_LHB_STAT", "RPT_LHB_SUM"],
    }

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

    async def _discover_report_name(self, kind: str) -> Optional[str]:
        if kind in self._report_cache:
            return self._report_cache[kind]
        try:
            text = await self._request_text(self.BASE_URL)
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
            reason = "龙虎榜"
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
            "source_url": self.BASE_URL,
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
        query = select(LhbStockItem).where(LhbStockItem.trade_date == trade_date)
        result = await self.db_session.execute(query)
        rows = [self._model_to_dict(item) for item in result.scalars().all()]
        rows.sort(key=lambda x: x.get("updated_at") or x.get("created_at") or datetime.min, reverse=True)
        normalized: List[Dict[str, Any]] = []
        seen = set()
        for row in rows:
            reason = row.get("reason") or "龙虎榜"
            row["reason"] = reason
            key = (row.get("code"), reason)
            if key in seen:
                continue
            seen.add(key)
            normalized.append(row)
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

    async def _fetch_list_from_web(self, trade_date: str, page: int, page_size: int) -> List[Dict[str, Any]]:
        report_name = await self._discover_report_name("list")
        if not report_name:
            return []
        filter_expr = f"(TRADE_DATE='{trade_date}')"
        sort_columns = "NET_BUY_AMT,BILL_BOARD_NET_AMT"
        sort_types = "-1,-1"
        if report_name == "RPT_ORGANIZATION_TRADE_DETAILSNEW":
            sort_columns = "NET_BUY_AMT"
            sort_types = "-1"
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
        mapped.sort(key=lambda x: x.get("net_buy_amount") or 0.0, reverse=True)
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
        report_name = await self._discover_report_name("summary")
        if not report_name:
            return []
        filter_expr = f"(TRADE_DATE='{end_trade_date}')"
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
        mapped = [self._map_summary_item(item, window_days, end_trade_date) for item in api_items]
        mapped = [m for m in mapped if m]
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
            should_refresh = not has_detail
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
