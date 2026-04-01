"""
东方财富资金流向服务

数据来源（HTML 兜底策略）：
- 大盘资金流向：https://data.eastmoney.com/zjlx/dpzjlx.html
- 板块资金流向：
  - 行业：https://data.eastmoney.com/bkzj/hy.html
  - 概念：https://data.eastmoney.com/bkzj/gn.html
  - 地域：https://data.eastmoney.com/bkzj/dy.html
- 个股资金流向排行：https://data.eastmoney.com/zjlx/detail.html

说明：优先读库；缺失/过期时抓取并回写数据库。
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
from lxml import html as lxml_html
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.response import success, error
from models.fund_flow import MarketFundFlow, SectorFundFlow, StockFundFlow

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    expires_at: datetime
    payload: Dict[str, Any]


_cache: Dict[str, CacheEntry] = {}


def _cache_key(prefix: str, **kwargs: Any) -> str:
    parts = [f"{k}={kwargs.get(k, '')}" for k in sorted(kwargs.keys())]
    return f"fundflow:{prefix}:" + "|".join(parts)


class EastmoneyFundFlowService:
    CACHE_TTL_SECONDS = 120
    DB_TTL_SECONDS = 300
    MAX_RETRIES = 2

    MARKET_URL = "https://data.eastmoney.com/zjlx/dpzjlx.html"
    SECTOR_URLS = {
        "industry": "https://data.eastmoney.com/bkzj/hy.html",
        "concept": "https://data.eastmoney.com/bkzj/gn.html",
        "region": "https://data.eastmoney.com/bkzj/dy.html",
    }
    STOCK_URL = "https://data.eastmoney.com/zjlx/detail.html"
    QUOTE_URL = "https://push2.eastmoney.com/"

    MARKET_SECIDS = {
        "hs": "1.000001,0.399001",
        "sh": "1.000001",
        "sz": "0.399001",
        "cyb": "0.399006",
        "kcb": "1.000688",
        "zxb": "0.399005",
    }

    STOCK_MKT_VALUES = {
        "all": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2",
        "hsa": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2",
        "sha": "m:1+t:2+f:!2,m:1+t:23+f:!2",
        "kcb": "m:1+t:23+f:!2",
        "sza": "m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2",
        "cyb": "m:0+t:80+f:!2",
        "zxb": "m:0+t:13+f:!2",
        "hb": "m:1+t:3+f:!2",
        "sb": "m:0+t:7+f:!2",
        "bja": "m:0+t:81+s:262144+f:!2",
    }

    SECTOR_VALUES = {
        "industry": "m:90 t:2",
        "concept": "m:90 t:3",
        "region": "m:90 t:1",
    }

    STAT_FIELDS = {
        1: {
            "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13",
            "zdf": "f3",
            "main_net": "f62",
            "main_ratio": "f184",
            "super_net": "f66",
            "super_ratio": "f69",
            "large_net": "f72",
            "large_ratio": "f75",
            "medium_net": "f78",
            "medium_ratio": "f81",
            "small_net": "f84",
            "small_ratio": "f87",
        },
        3: {
            "fields": "f12,f14,f2,f127,f267,f268,f269,f270,f271,f272,f273,f274,f275,f276,f257,f258,f124,f1,f13",
            "zdf": "f127",
            "main_net": "f267",
            "main_ratio": "f268",
            "super_net": "f269",
            "super_ratio": "f270",
            "large_net": "f271",
            "large_ratio": "f272",
            "medium_net": "f273",
            "medium_ratio": "f274",
            "small_net": "f275",
            "small_ratio": "f276",
        },
        5: {
            "fields": "f12,f14,f2,f109,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f257,f258,f124,f1,f13",
            "zdf": "f109",
            "main_net": "f164",
            "main_ratio": "f165",
            "super_net": "f166",
            "super_ratio": "f167",
            "large_net": "f168",
            "large_ratio": "f169",
            "medium_net": "f170",
            "medium_ratio": "f171",
            "small_net": "f172",
            "small_ratio": "f173",
        },
        10: {
            "fields": "f12,f14,f2,f160,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f260,f261,f124,f1,f13",
            "zdf": "f160",
            "main_net": "f174",
            "main_ratio": "f175",
            "super_net": "f176",
            "super_ratio": "f177",
            "large_net": "f178",
            "large_ratio": "f179",
            "medium_net": "f180",
            "medium_ratio": "f181",
            "small_net": "f182",
            "small_ratio": "f183",
        },
    }

    def __init__(
        self,
        db_session: Optional[AsyncSession] = None,
        timeout: int = 10,
        max_concurrent_requests: int = 3,
    ):
        self.db_session = db_session
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Referer": "https://data.eastmoney.com/zjlx/",
        }

    async def _safe_rollback(self) -> None:
        if not self.db_session:
            return
        try:
            if self.db_session.in_transaction():
                await self.db_session.rollback()
        except Exception as rollback_error:
            logger.warning(f"资金流向事务回滚失败: {rollback_error}")

    # ---------------------- 公共工具 ----------------------
    def _decode_response_text(self, resp: httpx.Response) -> str:
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

    def _parse_amount(self, raw: str) -> Optional[float]:
        if raw is None:
            return None
        s = str(raw).strip()
        if not s or s == "--":
            return None
        s = s.replace(",", "")
        m = re.search(r"-?\d+(?:\.\d+)?", s)
        if not m:
            return None
        value = float(m.group(0))
        if "万" in s and "亿" in s:
            return value * 1_0000_0000_0000
        if "亿" in s:
            return value * 1_0000_0000
        if "万" in s:
            return value * 1_0000
        return value

    def _parse_percent(self, raw: str) -> Optional[float]:
        if raw is None:
            return None
        s = str(raw).strip().replace("%", "")
        if not s or s == "--":
            return None
        try:
            return float(s)
        except Exception:
            return None

    def _extract_as_of(self, text: str) -> datetime:
        match = re.search(r"(20\d{2}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?)", text)
        if match:
            try:
                raw = match.group(0)
                if " " in raw:
                    return datetime.strptime(raw, "%Y-%m-%d %H:%M")
                return datetime.strptime(raw, "%Y-%m-%d")
            except Exception:
                pass
        return datetime.now()

    def _to_float(self, value: Any) -> Optional[float]:
        if value is None or value == "-":
            return None
        try:
            return float(value)
        except Exception:
            return None

    def _to_datetime_from_ts(self, value: Any) -> Optional[datetime]:
        if value is None:
            return None
        try:
            ts = float(value)
            if ts > 10_000_000_000:
                ts = ts / 1000.0
            return datetime.fromtimestamp(ts)
        except Exception:
            return None

    def _is_stale(self, updated_at: Optional[datetime]) -> bool:
        if not updated_at:
            return True
        return datetime.now() - updated_at > timedelta(seconds=self.DB_TTL_SECONDS)

    async def _request(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        last_error: Optional[Exception] = None
        for attempt in range(1, self.MAX_RETRIES + 2):
            try:
                async with self.semaphore:
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
                        resp = await client.get(url, params=params, follow_redirects=True)
                        resp.raise_for_status()
                        return self._decode_response_text(resp)
            except Exception as e:
                last_error = e
                if attempt < self.MAX_RETRIES + 1:
                    await asyncio.sleep(0.2 * attempt)
                    continue
                raise
        if last_error:
            raise last_error
        raise httpx.HTTPError("request failed")

    async def _request_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        text = await self._request(url, params=params)
        payload = text.strip()
        if not payload:
            return {}
        if "(" in payload and payload.endswith(")"):
            payload = payload[payload.find("(") + 1 : payload.rfind(")")]
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return {}

    # ---------------------- DB 操作 ----------------------
    async def _query_market_from_db(self, market: str) -> Optional[Tuple[datetime, List[Dict[str, Any]], datetime]]:
        if not self.db_session:
            return None

        max_asof_stmt = select(func.max(MarketFundFlow.as_of)).where(MarketFundFlow.market == market)
        max_asof = (await self.db_session.execute(max_asof_stmt)).scalar_one_or_none()
        if not max_asof:
            return None

        rows_stmt = select(MarketFundFlow).where(
            MarketFundFlow.market == market,
            MarketFundFlow.as_of == max_asof,
        ).order_by(MarketFundFlow.bucket)
        rows = (await self.db_session.execute(rows_stmt)).scalars().all()
        if not rows:
            return None

        updated_at = max((row.updated_at for row in rows), default=max_asof)
        items = [
            {
                "bucket": row.bucket,
                "inflow": row.inflow,
                "outflow": row.outflow,
                "net": row.net,
            }
            for row in rows
        ]
        return max_asof, items, updated_at

    async def _query_sector_from_db(self, sector_type: str, page: int, page_size: int) -> Optional[Dict[str, Any]]:
        if not self.db_session:
            return None

        max_asof_stmt = select(func.max(SectorFundFlow.as_of)).where(SectorFundFlow.sector_type == sector_type)
        max_asof = (await self.db_session.execute(max_asof_stmt)).scalar_one_or_none()
        if not max_asof:
            return None

        count_stmt = select(func.count()).select_from(SectorFundFlow).where(
            SectorFundFlow.sector_type == sector_type,
            SectorFundFlow.as_of == max_asof,
        )
        total = (await self.db_session.execute(count_stmt)).scalar_one() or 0
        if total <= 0:
            return None

        offset = (page - 1) * page_size
        if offset >= total:
            return None

        rows_stmt = (
            select(SectorFundFlow)
            .where(SectorFundFlow.sector_type == sector_type, SectorFundFlow.as_of == max_asof)
            .order_by(SectorFundFlow.rank.asc())
            .offset(offset)
            .limit(page_size)
        )
        rows = (await self.db_session.execute(rows_stmt)).scalars().all()
        updated_at = max((row.updated_at for row in rows), default=max_asof)

        items = [
            {
                "rank": row.rank,
                "name": row.name,
                "pct_change": row.pct_change,
                "main_net_inflow": row.main_net_inflow,
                "main_net_ratio": row.main_net_ratio,
                "super_net_inflow": row.super_net_inflow,
                "super_net_ratio": row.super_net_ratio,
                "large_net_inflow": row.large_net_inflow,
                "large_net_ratio": row.large_net_ratio,
                "medium_net_inflow": row.medium_net_inflow,
                "medium_net_ratio": row.medium_net_ratio,
                "small_net_inflow": row.small_net_inflow,
                "small_net_ratio": row.small_net_ratio,
                "leader": row.leader,
            }
            for row in rows
        ]

        return {
            "as_of": max_asof,
            "items": items,
            "total": int(total),
            "updated_at": updated_at,
        }

    async def _query_stock_from_db(self, market: str, stat: int, page: int, page_size: int) -> Optional[Dict[str, Any]]:
        if not self.db_session:
            return None

        max_asof_stmt = select(func.max(StockFundFlow.as_of)).where(
            StockFundFlow.market == market,
            StockFundFlow.stat == stat,
        )
        max_asof = (await self.db_session.execute(max_asof_stmt)).scalar_one_or_none()
        if not max_asof:
            return None

        count_stmt = select(func.count()).select_from(StockFundFlow).where(
            StockFundFlow.market == market,
            StockFundFlow.stat == stat,
            StockFundFlow.as_of == max_asof,
        )
        total = (await self.db_session.execute(count_stmt)).scalar_one() or 0
        if total <= 0:
            return None

        offset = (page - 1) * page_size
        if offset >= total:
            return None

        rows_stmt = (
            select(StockFundFlow)
            .where(
                StockFundFlow.market == market,
                StockFundFlow.stat == stat,
                StockFundFlow.as_of == max_asof,
            )
            .order_by(StockFundFlow.rank.asc())
            .offset(offset)
            .limit(page_size)
        )
        rows = (await self.db_session.execute(rows_stmt)).scalars().all()
        updated_at = max((row.updated_at for row in rows), default=max_asof)

        items = [
            {
                "rank": row.rank,
                "code": row.code,
                "name": row.name,
                "price": row.price,
                "pct_change": row.pct_change,
                "main_net_inflow": row.main_net_inflow,
                "main_net_ratio": row.main_net_ratio,
                "super_net_inflow": row.super_net_inflow,
                "super_net_ratio": row.super_net_ratio,
                "large_net_inflow": row.large_net_inflow,
                "large_net_ratio": row.large_net_ratio,
                "medium_net_inflow": row.medium_net_inflow,
                "medium_net_ratio": row.medium_net_ratio,
                "small_net_inflow": row.small_net_inflow,
                "small_net_ratio": row.small_net_ratio,
                "industry": row.industry,
            }
            for row in rows
        ]

        return {
            "as_of": max_asof,
            "items": items,
            "total": int(total),
            "updated_at": updated_at,
        }

    async def _upsert_market(self, market: str, as_of: datetime, items: List[Dict[str, Any]]) -> None:
        if not self.db_session:
            return
        for item in items:
            stmt = insert(MarketFundFlow).values(
                market=market,
                as_of=as_of,
                bucket=item["bucket"],
                inflow=item.get("inflow") or 0.0,
                outflow=item.get("outflow") or 0.0,
                net=item.get("net") or 0.0,
                updated_at=datetime.now(),
            )
            stmt = stmt.on_conflict_do_update(
                constraint="uq_market_fund_flow_market_asof_bucket",
                set_={
                    "inflow": stmt.excluded.inflow,
                    "outflow": stmt.excluded.outflow,
                    "net": stmt.excluded.net,
                    "updated_at": stmt.excluded.updated_at,
                },
            )
            await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def _upsert_sector(self, sector_type: str, as_of: datetime, items: List[Dict[str, Any]]) -> None:
        if not self.db_session:
            return
        for item in items:
            stmt = insert(SectorFundFlow).values(
                sector_type=sector_type,
                as_of=as_of,
                rank=item.get("rank") or 0,
                name=item.get("name") or "",
                pct_change=item.get("pct_change"),
                main_net_inflow=item.get("main_net_inflow"),
                main_net_ratio=item.get("main_net_ratio"),
                super_net_inflow=item.get("super_net_inflow"),
                super_net_ratio=item.get("super_net_ratio"),
                large_net_inflow=item.get("large_net_inflow"),
                large_net_ratio=item.get("large_net_ratio"),
                medium_net_inflow=item.get("medium_net_inflow"),
                medium_net_ratio=item.get("medium_net_ratio"),
                small_net_inflow=item.get("small_net_inflow"),
                small_net_ratio=item.get("small_net_ratio"),
                leader=item.get("leader"),
                updated_at=datetime.now(),
            )
            stmt = stmt.on_conflict_do_update(
                constraint="uq_sector_fund_flow_type_asof_rank",
                set_={
                    "name": stmt.excluded.name,
                    "pct_change": stmt.excluded.pct_change,
                    "main_net_inflow": stmt.excluded.main_net_inflow,
                    "main_net_ratio": stmt.excluded.main_net_ratio,
                    "super_net_inflow": stmt.excluded.super_net_inflow,
                    "super_net_ratio": stmt.excluded.super_net_ratio,
                    "large_net_inflow": stmt.excluded.large_net_inflow,
                    "large_net_ratio": stmt.excluded.large_net_ratio,
                    "medium_net_inflow": stmt.excluded.medium_net_inflow,
                    "medium_net_ratio": stmt.excluded.medium_net_ratio,
                    "small_net_inflow": stmt.excluded.small_net_inflow,
                    "small_net_ratio": stmt.excluded.small_net_ratio,
                    "leader": stmt.excluded.leader,
                    "updated_at": stmt.excluded.updated_at,
                },
            )
            await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def _upsert_stock(self, market: str, stat: int, as_of: datetime, items: List[Dict[str, Any]]) -> None:
        if not self.db_session:
            return
        for item in items:
            stmt = insert(StockFundFlow).values(
                market=market,
                stat=stat,
                as_of=as_of,
                rank=item.get("rank") or 0,
                code=item.get("code") or "",
                name=item.get("name") or "",
                price=item.get("price"),
                pct_change=item.get("pct_change"),
                main_net_inflow=item.get("main_net_inflow"),
                main_net_ratio=item.get("main_net_ratio"),
                super_net_inflow=item.get("super_net_inflow"),
                super_net_ratio=item.get("super_net_ratio"),
                large_net_inflow=item.get("large_net_inflow"),
                large_net_ratio=item.get("large_net_ratio"),
                medium_net_inflow=item.get("medium_net_inflow"),
                medium_net_ratio=item.get("medium_net_ratio"),
                small_net_inflow=item.get("small_net_inflow"),
                small_net_ratio=item.get("small_net_ratio"),
                industry=item.get("industry"),
                updated_at=datetime.now(),
            )
            stmt = stmt.on_conflict_do_update(
                constraint="uq_stock_fund_flow_market_stat_asof_rank",
                set_={
                    "code": stmt.excluded.code,
                    "name": stmt.excluded.name,
                    "price": stmt.excluded.price,
                    "pct_change": stmt.excluded.pct_change,
                    "main_net_inflow": stmt.excluded.main_net_inflow,
                    "main_net_ratio": stmt.excluded.main_net_ratio,
                    "super_net_inflow": stmt.excluded.super_net_inflow,
                    "super_net_ratio": stmt.excluded.super_net_ratio,
                    "large_net_inflow": stmt.excluded.large_net_inflow,
                    "large_net_ratio": stmt.excluded.large_net_ratio,
                    "medium_net_inflow": stmt.excluded.medium_net_inflow,
                    "medium_net_ratio": stmt.excluded.medium_net_ratio,
                    "small_net_inflow": stmt.excluded.small_net_inflow,
                    "small_net_ratio": stmt.excluded.small_net_ratio,
                    "industry": stmt.excluded.industry,
                    "updated_at": stmt.excluded.updated_at,
                },
            )
            await self.db_session.execute(stmt)
        await self.db_session.commit()

    # ---------------------- 解析逻辑 ----------------------
    def _parse_market_flow_html(self, text: str) -> Tuple[datetime, List[Dict[str, Any]]]:
        doc = lxml_html.fromstring(text)
        tables = doc.xpath("//table")
        target_table = None
        for table in tables:
            content = "".join(table.xpath(".//text()"))
            if "超大单" in content and "小单" in content:
                target_table = table
                break
        if target_table is None:
            return datetime.now(), []

        bucket_map = {
            "超大单": "super",
            "大单": "large",
            "中单": "medium",
            "小单": "small",
        }

        items: List[Dict[str, Any]] = []
        rows = target_table.xpath(".//tr")
        for row in rows:
            cells = ["".join(c.xpath(".//text()")) for c in row.xpath("./td")]
            cells = [c.strip() for c in cells if c and c.strip()]
            if len(cells) < 3:
                continue
            name = cells[0]
            if name not in bucket_map:
                continue
            inflow = self._parse_amount(cells[1]) or 0.0
            outflow = self._parse_amount(cells[2]) or 0.0
            items.append(
                {
                    "bucket": bucket_map[name],
                    "inflow": inflow,
                    "outflow": outflow,
                    "net": inflow - outflow,
                }
            )

        as_of = self._extract_as_of(text)
        return as_of, items

    def _normalize_cells(self, cells: List[str]) -> List[str]:
        filtered: List[str] = []
        for cell in cells:
            text = cell.strip()
            if not text:
                continue
            if any(k in text for k in ["详情", "股吧", "研报", "数据"]):
                continue
            filtered.append(text)
        return filtered

    def _parse_sector_flow_html(self, text: str) -> Tuple[datetime, List[Dict[str, Any]]]:
        doc = lxml_html.fromstring(text)
        tables = doc.xpath("//table")
        target_table = None
        for table in tables:
            header_text = "".join(table.xpath(".//th//text()"))
            if "排名" in header_text and "主力" in header_text:
                target_table = table
                break
        if target_table is None and tables:
            target_table = tables[0]
        items: List[Dict[str, Any]] = []
        if not target_table:
            return datetime.now(), items

        for row in target_table.xpath(".//tr"):
            tds = ["".join(td.xpath(".//text()")) for td in row.xpath("./td")]
            cells = self._normalize_cells(tds)
            if len(cells) < 10:
                continue
            try:
                idx = 0
                rank = int(float(cells[idx]))
                idx += 1
                name = cells[idx]
                idx += 1
                pct_change = self._parse_percent(cells[idx])
                idx += 1
                main_net = self._parse_amount(cells[idx])
                idx += 1
                main_ratio = self._parse_percent(cells[idx])
                idx += 1
                super_net = self._parse_amount(cells[idx])
                idx += 1
                super_ratio = self._parse_percent(cells[idx])
                idx += 1
                large_net = self._parse_amount(cells[idx])
                idx += 1
                large_ratio = self._parse_percent(cells[idx])
                idx += 1
                medium_net = self._parse_amount(cells[idx])
                idx += 1
                medium_ratio = self._parse_percent(cells[idx])
                idx += 1
                small_net = self._parse_amount(cells[idx]) if idx < len(cells) else None
                idx += 1
                small_ratio = self._parse_percent(cells[idx]) if idx < len(cells) else None
                idx += 1
                leader = cells[idx] if idx < len(cells) else None

                items.append(
                    {
                        "rank": rank,
                        "name": name,
                        "pct_change": pct_change,
                        "main_net_inflow": main_net,
                        "main_net_ratio": main_ratio,
                        "super_net_inflow": super_net,
                        "super_net_ratio": super_ratio,
                        "large_net_inflow": large_net,
                        "large_net_ratio": large_ratio,
                        "medium_net_inflow": medium_net,
                        "medium_net_ratio": medium_ratio,
                        "small_net_inflow": small_net,
                        "small_net_ratio": small_ratio,
                        "leader": leader,
                    }
                )
            except Exception:
                continue

        as_of = self._extract_as_of(text)
        return as_of, items

    def _parse_stock_flow_html(self, text: str) -> Tuple[datetime, List[Dict[str, Any]]]:
        doc = lxml_html.fromstring(text)
        tables = doc.xpath("//table")
        target_table = None
        for table in tables:
            header_text = "".join(table.xpath(".//th//text()"))
            if "排名" in header_text and "主力" in header_text:
                target_table = table
                break
        if target_table is None and tables:
            target_table = tables[0]
        items: List[Dict[str, Any]] = []
        if not target_table:
            return datetime.now(), items

        for row in target_table.xpath(".//tr"):
            tds = ["".join(td.xpath(".//text()")) for td in row.xpath("./td")]
            cells = self._normalize_cells(tds)
            if len(cells) < 12:
                continue
            try:
                idx = 0
                rank = int(float(cells[idx]))
                idx += 1
                code = cells[idx]
                idx += 1
                name = cells[idx]
                idx += 1
                price = self._parse_amount(cells[idx])
                idx += 1
                pct_change = self._parse_percent(cells[idx])
                idx += 1
                main_net = self._parse_amount(cells[idx])
                idx += 1
                main_ratio = self._parse_percent(cells[idx])
                idx += 1
                super_net = self._parse_amount(cells[idx])
                idx += 1
                super_ratio = self._parse_percent(cells[idx])
                idx += 1
                large_net = self._parse_amount(cells[idx])
                idx += 1
                large_ratio = self._parse_percent(cells[idx])
                idx += 1
                medium_net = self._parse_amount(cells[idx]) if idx < len(cells) else None
                idx += 1
                medium_ratio = self._parse_percent(cells[idx]) if idx < len(cells) else None
                idx += 1
                small_net = self._parse_amount(cells[idx]) if idx < len(cells) else None
                idx += 1
                small_ratio = self._parse_percent(cells[idx]) if idx < len(cells) else None

                items.append(
                    {
                        "rank": rank,
                        "code": code,
                        "name": name,
                        "price": price,
                        "pct_change": pct_change,
                        "main_net_inflow": main_net,
                        "main_net_ratio": main_ratio,
                        "super_net_inflow": super_net,
                        "super_net_ratio": super_ratio,
                        "large_net_inflow": large_net,
                        "large_net_ratio": large_ratio,
                        "medium_net_inflow": medium_net,
                        "medium_net_ratio": medium_ratio,
                        "small_net_inflow": small_net,
                        "small_net_ratio": small_ratio,
                    }
                )
            except Exception:
                continue

        as_of = self._extract_as_of(text)
        return as_of, items

    # ---------------------- API 解析逻辑 ----------------------
    def _stat_config(self, stat: int) -> Dict[str, str]:
        return self.STAT_FIELDS.get(stat, self.STAT_FIELDS[1])

    def _sum_numeric_fields(self, items: List[Dict[str, Any]], keys: List[str]) -> Dict[str, float]:
        total: Dict[str, float] = {k: 0.0 for k in keys}
        for item in items:
            for key in keys:
                val = item.get(key)
                if isinstance(val, (int, float)):
                    total[key] += float(val)
        return total

    async def _fetch_market_flow_api(self, market: str) -> Tuple[datetime, List[Dict[str, Any]]]:
        secids = self.MARKET_SECIDS.get(market, self.MARKET_SECIDS["hs"])
        params = {
            "fltt": "2",
            "secids": secids,
            "fields": "f64,f65,f70,f71,f76,f77,f82,f83,f124",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
        }
        url = f"{self.QUOTE_URL}api/qt/ulist.np/get"
        data = await self._request_json(url, params=params)
        diffs = (data.get("data") or {}).get("diff") or []
        if not isinstance(diffs, list) or len(diffs) == 0:
            return datetime.now(), []

        keys = ["f64", "f65", "f70", "f71", "f76", "f77", "f82", "f83"]
        merged = self._sum_numeric_fields(diffs, keys)
        as_of = self._to_datetime_from_ts(diffs[0].get("f124")) or datetime.now()

        items = [
            {
                "bucket": "super",
                "inflow": merged["f64"],
                "outflow": merged["f65"],
                "net": merged["f64"] - merged["f65"],
            },
            {
                "bucket": "large",
                "inflow": merged["f70"],
                "outflow": merged["f71"],
                "net": merged["f70"] - merged["f71"],
            },
            {
                "bucket": "medium",
                "inflow": merged["f76"],
                "outflow": merged["f77"],
                "net": merged["f76"] - merged["f77"],
            },
            {
                "bucket": "small",
                "inflow": merged["f82"],
                "outflow": merged["f83"],
                "net": merged["f82"] - merged["f83"],
            },
        ]
        return as_of, items

    async def _fetch_sector_flow_api(
        self, sector_type: str, page: int, page_size: int
    ) -> Tuple[datetime, List[Dict[str, Any]], int]:
        config = self._stat_config(1)
        fs = self.SECTOR_VALUES.get(sector_type, self.SECTOR_VALUES["industry"])
        params = {
            "pn": page,
            "pz": page_size,
            "po": 1,
            "np": 1,
            "fltt": "2",
            "invt": "2",
            "fid": config["main_net"],
            "fs": fs,
            "fields": config["fields"],
            "ut": "8dec03ba335b81bf4ebdf7b29ec27d15",
        }
        url = f"{self.QUOTE_URL}api/qt/clist/get"
        data = await self._request_json(url, params=params)
        dat = data.get("data") or {}
        diffs = dat.get("diff") or []
        total = int(dat.get("total") or 0)
        if not isinstance(diffs, list) or len(diffs) == 0:
            return datetime.now(), [], total

        as_of = self._to_datetime_from_ts(diffs[0].get("f124")) or datetime.now()
        items: List[Dict[str, Any]] = []
        offset = (page - 1) * page_size
        for idx, item in enumerate(diffs):
            items.append(
                {
                    "rank": offset + idx + 1,
                    "name": item.get("f14"),
                    "pct_change": self._to_float(item.get(config["zdf"])),
                    "main_net_inflow": self._to_float(item.get(config["main_net"])),
                    "main_net_ratio": self._to_float(item.get(config["main_ratio"])),
                    "super_net_inflow": self._to_float(item.get(config["super_net"])),
                    "super_net_ratio": self._to_float(item.get(config["super_ratio"])),
                    "large_net_inflow": self._to_float(item.get(config["large_net"])),
                    "large_net_ratio": self._to_float(item.get(config["large_ratio"])),
                    "medium_net_inflow": self._to_float(item.get(config["medium_net"])),
                    "medium_net_ratio": self._to_float(item.get(config["medium_ratio"])),
                    "small_net_inflow": self._to_float(item.get(config["small_net"])),
                    "small_net_ratio": self._to_float(item.get(config["small_ratio"])),
                    "leader": item.get("f204"),
                }
            )
        return as_of, items, total

    async def _fetch_stock_flow_api(
        self, market: str, stat: int, page: int, page_size: int
    ) -> Tuple[datetime, List[Dict[str, Any]], int]:
        config = self._stat_config(stat)
        fs = self.STOCK_MKT_VALUES.get(market, self.STOCK_MKT_VALUES["all"])
        params = {
            "pn": page,
            "pz": page_size,
            "po": 1,
            "np": 1,
            "fltt": "2",
            "invt": "2",
            "fid": config["main_net"],
            "fs": fs,
            "fields": config["fields"],
            "ut": "8dec03ba335b81bf4ebdf7b29ec27d15",
        }
        url = f"{self.QUOTE_URL}api/qt/clist/get"
        data = await self._request_json(url, params=params)
        dat = data.get("data") or {}
        diffs = dat.get("diff") or []
        total = int(dat.get("total") or 0)
        if not isinstance(diffs, list) or len(diffs) == 0:
            return datetime.now(), [], total

        as_of = self._to_datetime_from_ts(diffs[0].get("f124")) or datetime.now()
        items: List[Dict[str, Any]] = []
        offset = (page - 1) * page_size
        for idx, item in enumerate(diffs):
            items.append(
                {
                    "rank": offset + idx + 1,
                    "code": item.get("f12"),
                    "name": item.get("f14"),
                    "price": self._to_float(item.get("f2")),
                    "pct_change": self._to_float(item.get(config["zdf"])),
                    "main_net_inflow": self._to_float(item.get(config["main_net"])),
                    "main_net_ratio": self._to_float(item.get(config["main_ratio"])),
                    "super_net_inflow": self._to_float(item.get(config["super_net"])),
                    "super_net_ratio": self._to_float(item.get(config["super_ratio"])),
                    "large_net_inflow": self._to_float(item.get(config["large_net"])),
                    "large_net_ratio": self._to_float(item.get(config["large_ratio"])),
                    "medium_net_inflow": self._to_float(item.get(config["medium_net"])),
                    "medium_net_ratio": self._to_float(item.get(config["medium_ratio"])),
                    "small_net_inflow": self._to_float(item.get(config["small_net"])),
                    "small_net_ratio": self._to_float(item.get(config["small_ratio"])),
                }
            )
        return as_of, items, total

    # ---------------------- 外部接口 ----------------------
    async def get_market_flow(self, market: str = "hs", refresh: bool = False) -> dict:
        cache_key = _cache_key("market", market=market)
        if not refresh:
            db_payload = None
            try:
                db_payload = await self._query_market_from_db(market)
            except Exception as db_error:
                logger.warning(f"查询大盘资金流向缓存失败: {db_error}")
                await self._safe_rollback()
            if db_payload:
                as_of, items, updated_at = db_payload
                payload = {"as_of": as_of, "market": market, "items": items}
                _cache[cache_key] = CacheEntry(datetime.now() + timedelta(seconds=self.CACHE_TTL_SECONDS), payload)
                if not self._is_stale(updated_at):
                    return success(payload)

        try:
            as_of, items = await self._fetch_market_flow_api(market)
            if not items:
                text = await self._request(self.MARKET_URL, params={"m": market})
                as_of, items = self._parse_market_flow_html(text)
            if items:
                try:
                    await self._upsert_market(market, as_of, items)
                except Exception as db_error:
                    logger.warning(f"写入大盘资金流向失败，改为直接返回上游数据: {db_error}")
                    await self._safe_rollback()
                    payload = {"as_of": as_of, "market": market, "items": items}
                    _cache[cache_key] = CacheEntry(datetime.now() + timedelta(seconds=self.CACHE_TTL_SECONDS), payload)
                    return success(payload, message="db降级：返回实时数据")
            db_payload = None
            try:
                db_payload = await self._query_market_from_db(market)
            except Exception as db_error:
                logger.warning(f"查询大盘资金流向回写结果失败，改为直接返回上游数据: {db_error}")
                await self._safe_rollback()
            if db_payload:
                as_of, items, _ = db_payload
                payload = {"as_of": as_of, "market": market, "items": items}
                _cache[cache_key] = CacheEntry(datetime.now() + timedelta(seconds=self.CACHE_TTL_SECONDS), payload)
                return success(payload)
            return success({"as_of": as_of, "market": market, "items": items})
        except Exception as e:
            logger.warning(f"资金流向抓取失败: {e}")
            db_payload = None
            try:
                db_payload = await self._query_market_from_db(market)
            except Exception as db_error:
                logger.warning(f"抓取失败后读取大盘资金流向缓存失败: {db_error}")
                await self._safe_rollback()
            if db_payload:
                as_of, items, _ = db_payload
                return success({"as_of": as_of, "market": market, "items": items, "message": "刷新失败已降级"})
            return error("上游资金流向获取失败，请稍后重试")

    async def get_sector_flow(
        self,
        sector_type: str = "industry",
        page: int = 1,
        page_size: int = 50,
        order: str = "desc",
        refresh: bool = False,
    ) -> dict:
        cache_key = _cache_key("sector", type=sector_type, page=page, page_size=page_size)
        if not refresh:
            db_payload = None
            try:
                db_payload = await self._query_sector_from_db(sector_type, page, page_size)
            except Exception as db_error:
                logger.warning(f"查询板块资金流向缓存失败: {db_error}")
                await self._safe_rollback()
            if db_payload:
                payload = {
                    "as_of": db_payload["as_of"],
                    "type": sector_type,
                    "page": page,
                    "page_size": page_size,
                    "total": db_payload["total"],
                    "items": db_payload["items"],
                }
                _cache[cache_key] = CacheEntry(datetime.now() + timedelta(seconds=self.CACHE_TTL_SECONDS), payload)
                if not self._is_stale(db_payload.get("updated_at")):
                    return success(payload)

        try:
            as_of, items, total = await self._fetch_sector_flow_api(sector_type, page, page_size)
            if not items:
                url = self.SECTOR_URLS.get(sector_type, self.SECTOR_URLS["industry"])
                text = await self._request(url, params={"p": page})
                as_of, items = self._parse_sector_flow_html(text)
                total = len(items)
            if items:
                try:
                    await self._upsert_sector(sector_type, as_of, items)
                except Exception as db_error:
                    logger.warning(f"写入板块资金流向失败，改为直接返回上游数据: {db_error}")
                    await self._safe_rollback()
                    payload = {
                        "as_of": as_of,
                        "type": sector_type,
                        "page": page,
                        "page_size": page_size,
                        "total": total,
                        "items": items,
                    }
                    _cache[cache_key] = CacheEntry(datetime.now() + timedelta(seconds=self.CACHE_TTL_SECONDS), payload)
                    return success(payload, message="db降级：返回实时数据")
            db_payload = None
            try:
                db_payload = await self._query_sector_from_db(sector_type, page, page_size)
            except Exception as db_error:
                logger.warning(f"查询板块资金流向回写结果失败，改为直接返回上游数据: {db_error}")
                await self._safe_rollback()
            if db_payload:
                payload = {
                    "as_of": db_payload["as_of"],
                    "type": sector_type,
                    "page": page,
                    "page_size": page_size,
                    "total": db_payload["total"],
                    "items": db_payload["items"],
                }
                _cache[cache_key] = CacheEntry(datetime.now() + timedelta(seconds=self.CACHE_TTL_SECONDS), payload)
                return success(payload)
            payload = {"as_of": as_of, "type": sector_type, "page": page, "page_size": page_size, "total": total, "items": items}
            _cache[cache_key] = CacheEntry(datetime.now() + timedelta(seconds=self.CACHE_TTL_SECONDS), payload)
            return success(payload)
        except Exception as e:
            logger.warning(f"板块资金流向抓取失败: {e}")
            db_payload = None
            try:
                db_payload = await self._query_sector_from_db(sector_type, page, page_size)
            except Exception as db_error:
                logger.warning(f"抓取失败后读取板块资金流向缓存失败: {db_error}")
                await self._safe_rollback()
            if db_payload:
                payload = {
                    "as_of": db_payload["as_of"],
                    "type": sector_type,
                    "page": page,
                    "page_size": page_size,
                    "total": db_payload["total"],
                    "items": db_payload["items"],
                    "message": "刷新失败已降级",
                }
                return success(payload)
            return error("上游板块资金流向获取失败，请稍后重试")

    async def get_stock_flow(
        self,
        market: str = "all",
        stat: int = 1,
        page: int = 1,
        page_size: int = 50,
        refresh: bool = False,
    ) -> dict:
        cache_key = _cache_key("stock", market=market, stat=stat, page=page, page_size=page_size)
        if not refresh:
            db_payload = None
            try:
                db_payload = await self._query_stock_from_db(market, stat, page, page_size)
            except Exception as db_error:
                logger.warning(f"查询个股资金流向缓存失败: {db_error}")
                await self._safe_rollback()
            if db_payload:
                payload = {
                    "as_of": db_payload["as_of"],
                    "market": market,
                    "stat": stat,
                    "page": page,
                    "page_size": page_size,
                    "total": db_payload["total"],
                    "items": db_payload["items"],
                }
                _cache[cache_key] = CacheEntry(datetime.now() + timedelta(seconds=self.CACHE_TTL_SECONDS), payload)
                if not self._is_stale(db_payload.get("updated_at")):
                    return success(payload)

        try:
            as_of, items, total = await self._fetch_stock_flow_api(market, stat, page, page_size)
            if not items:
                params = {"mkt": market, "stat": stat, "p": page}
                text = await self._request(self.STOCK_URL, params=params)
                as_of, items = self._parse_stock_flow_html(text)
                total = len(items)
            if items:
                try:
                    await self._upsert_stock(market, stat, as_of, items)
                except Exception as db_error:
                    logger.warning(f"写入个股资金流向失败，改为直接返回上游数据: {db_error}")
                    await self._safe_rollback()
                    payload = {
                        "as_of": as_of,
                        "market": market,
                        "stat": stat,
                        "page": page,
                        "page_size": page_size,
                        "total": total,
                        "items": items,
                    }
                    _cache[cache_key] = CacheEntry(datetime.now() + timedelta(seconds=self.CACHE_TTL_SECONDS), payload)
                    return success(payload, message="db降级：返回实时数据")
            db_payload = None
            try:
                db_payload = await self._query_stock_from_db(market, stat, page, page_size)
            except Exception as db_error:
                logger.warning(f"查询个股资金流向回写结果失败，改为直接返回上游数据: {db_error}")
                await self._safe_rollback()
            if db_payload:
                payload = {
                    "as_of": db_payload["as_of"],
                    "market": market,
                    "stat": stat,
                    "page": page,
                    "page_size": page_size,
                    "total": db_payload["total"],
                    "items": db_payload["items"],
                }
                _cache[cache_key] = CacheEntry(datetime.now() + timedelta(seconds=self.CACHE_TTL_SECONDS), payload)
                return success(payload)
            payload = {"as_of": as_of, "market": market, "stat": stat, "page": page, "page_size": page_size, "total": total, "items": items}
            _cache[cache_key] = CacheEntry(datetime.now() + timedelta(seconds=self.CACHE_TTL_SECONDS), payload)
            return success(payload)
        except Exception as e:
            logger.warning(f"个股资金流向抓取失败: {e}")
            db_payload = None
            try:
                db_payload = await self._query_stock_from_db(market, stat, page, page_size)
            except Exception as db_error:
                logger.warning(f"抓取失败后读取个股资金流向缓存失败: {db_error}")
                await self._safe_rollback()
            if db_payload:
                payload = {
                    "as_of": db_payload["as_of"],
                    "market": market,
                    "stat": stat,
                    "page": page,
                    "page_size": page_size,
                    "total": db_payload["total"],
                    "items": db_payload["items"],
                    "message": "刷新失败已降级",
                }
                return success(payload)
            return error("上游个股资金流向获取失败，请稍后重试")
