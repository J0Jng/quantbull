"""
东方财富“年报季报/财报”数据抓取服务

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
from lxml import html as lxml_html
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.financial_yjbb import FinancialReportYjbb
from models.financial_yjkb import FinancialReportYjkb
from models.financial_yjyg import FinancialReportYjyg
from models.financial_yysj import FinancialReportYysj

logger = logging.getLogger(__name__)


class EastmoneyBbsjService:
    BASE_URL = "https://data.eastmoney.com/bbsj"

    REPORT_CONFIG = {
        "yjbb": {
            "report_name": "RPT_LICO_FN_CPD",
            "date_field": "REPORTDATE",
            "sort_columns": "UPDATE_DATE",
            "sort_types": "-1",
        },
        "yjkb": {
            "report_name": "RPT_FCI_PERFORMANCEE",
            "date_field": "REPORT_DATE",
            "sort_columns": "UPDATE_DATE",
            "sort_types": "-1",
        },
        "yjyg": {
            "report_name": "RPT_PUBLIC_OP_NEWPREDICT",
            "date_field": "REPORT_DATE",
            "sort_columns": "NOTICE_DATE",
            "sort_types": "-1",
        },
        "yysj": {
            "report_name": "RPT_PUBLIC_BS_APPOIN",
            "date_field": "REPORT_DATE",
            "sort_columns": "FIRST_APPOINT_DATE",
            "sort_types": "1",
        },
    }

    YJBB_TTL_SECONDS = 6 * 3600
    YJKB_TTL_SECONDS = 6 * 3600
    YJYG_TTL_SECONDS = 6 * 3600
    YYSJ_TTL_SECONDS = 12 * 3600

    MAX_RETRIES = 2

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
            "Referer": "https://data.eastmoney.com/bbsj/",
        }

    # ------------------------- 公共工具 -------------------------
    @staticmethod
    def _normalize_period(period: Optional[str]) -> str:
        if period:
            return str(period)
        now = datetime.now()
        year = now.year
        month = now.month
        if month >= 12:
            m = 12
        elif month >= 9:
            m = 9
        elif month >= 6:
            m = 6
        elif month >= 3:
            m = 3
        else:
            year -= 1
            m = 12
        return f"{year}{m:02d}"

    @staticmethod
    def _previous_periods(period: str, count: int = 6) -> List[str]:
        if not period or len(period) < 6:
            return []
        year = int(period[:4])
        month = int(period[4:6])
        periods: List[str] = []
        for _ in range(count):
            if month == 12:
                month = 9
            elif month == 9:
                month = 6
            elif month == 6:
                month = 3
            else:
                month = 12
                year -= 1
            periods.append(f"{year}{month:02d}")
        return periods

    @staticmethod
    def _period_end_date(period: str) -> Optional[str]:
        if not period or len(period) < 6:
            return None
        year = int(period[:4])
        month = int(period[4:6])
        if month == 12:
            return f"{year}-12-31"
        if month == 9:
            return f"{year}-09-30"
        if month == 6:
            return f"{year}-06-30"
        if month == 3:
            return f"{year}-03-31"
        return None

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
    def parse_range_to_low_high(raw: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
        if not raw:
            return None, None
        s = str(raw)
        nums = re.findall(r"-?\d+(?:\.\d+)?", s.replace(",", ""))
        if not nums:
            return None, None
        values = [float(x) for x in nums]
        if len(values) == 1:
            return values[0], values[0]
        return min(values), max(values)

    @staticmethod
    def _normalize_date(raw: Optional[str], period: Optional[str] = None) -> Optional[str]:
        if not raw:
            return None
        s = str(raw).strip()
        if not s or s in {"--", "-"}:
            return None
        if re.match(r"\d{4}-\d{2}-\d{2}", s):
            return s
        if re.match(r"\d{2}-\d{2}", s) and period and len(period) >= 4:
            return f"{period[:4]}-{s}"
        return s

    @staticmethod
    def _model_to_dict(obj: Any) -> Dict[str, Any]:
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        return dict(obj)

    @staticmethod
    def _split_codes(codes: Optional[str]) -> List[str]:
        if not codes:
            return []
        return [c.strip() for c in codes.split(",") if c.strip()]

    @staticmethod
    def _filter_by_market(items: List[Dict[str, Any]], market: str) -> List[Dict[str, Any]]:
        if not market or market == "all":
            return items
        def _match(code: str) -> bool:
            if market in {"hsa", "sha"}:
                return code.startswith("60")
            if market in {"sza"}:
                return code.startswith("00") or code.startswith("30")
            if market == "cyb":
                return code.startswith("30")
            if market == "kcb":
                return code.startswith("688")
            if market == "bja":
                return code.startswith("8") or code.startswith("43")
            return True
        return [item for item in items if _match(str(item.get("code", "")))]

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

    def _extract_report_name(self, html_text: str) -> Optional[str]:
        patterns = [
            r"reportName\"\s*:\s*\"(.*?)\"",
            r"reportName=([A-Za-z0-9_]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, html_text)
            if match:
                return match.group(1)
        return None

    async def _fetch_datacenter(
        self,
        report_name: str,
        period: str,
        page: int,
        page_size: int,
        date_field: str = "REPORT_DATE",
        sort_columns: str = "UPDATE_DATE",
        sort_types: str = "-1",
    ) -> Optional[List[Dict[str, Any]]]:
        url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
        period_end = self._period_end_date(period)
        params: Dict[str, Any] = {
            "reportName": report_name,
            "columns": "ALL",
            "pageNumber": page,
            "pageSize": page_size,
            "sortColumns": sort_columns,
            "sortTypes": sort_types,
        }
        if period_end:
            params["filter"] = f"({date_field}='{period_end}')"
        data = await self._request_json(url, params)
        if not data:
            return None
        result = data.get("result") or {}
        items = result.get("data") or []
        if not isinstance(items, list) or not items:
            return None
        return items

    def _map_yjbb_api_item(self, item: Dict[str, Any], period: str) -> Optional[Dict[str, Any]]:
        code = item.get("SECURITY_CODE") or item.get("SECUCODE")
        name = item.get("SECURITY_NAME_ABBR") or item.get("SECURITY_NAME")
        if not code or not name:
            return None
        return {
            "period": period,
            "code": str(code),
            "name": str(name),
            "eps": self._parse_number(item.get("BASIC_EPS")),
            "revenue": self._parse_number(item.get("TOTAL_OPERATE_INCOME")),
            "revenue_yoy": self._parse_percent(item.get("TOTAL_OPERATE_INCOME_YOY")),
            "net_profit": self._parse_number(item.get("PARENT_NETPROFIT")),
            "net_profit_yoy": self._parse_percent(item.get("PARENT_NETPROFIT_YOY")),
            "roe": self._parse_percent(item.get("WEIGHTAVG_ROE")),
            "bps": self._parse_number(item.get("BPS")),
            "cashflow_ps": self._parse_number(item.get("MGJYXJJE")),
            "industry": item.get("INDUSTRY_NAME") or item.get("PUBLISHNAME"),
            "notice_date": self._normalize_date(item.get("NOTICE_DATE"), period),
            "update_date": self._normalize_date(item.get("UPDATE_DATE"), period),
            "source_url": f"{self.BASE_URL}/{period}/yjbb.html",
            "as_of": datetime.now(),
        }

    def _map_yjkb_api_item(self, item: Dict[str, Any], period: str) -> Optional[Dict[str, Any]]:
        code = item.get("SECURITY_CODE") or item.get("SECUCODE")
        name = item.get("SECURITY_NAME_ABBR") or item.get("SECURITY_NAME")
        if not code or not name:
            return None
        return {
            "period": period,
            "code": str(code),
            "name": str(name),
            "eps": self._parse_number(item.get("BASIC_EPS")),
            "revenue": self._parse_number(item.get("TOTAL_OPERATE_INCOME")),
            "revenue_yoy": self._parse_percent(item.get("TOTAL_OPERATE_INCOME_YOY")),
            "net_profit": self._parse_number(item.get("PARENT_NETPROFIT")),
            "net_profit_yoy": self._parse_percent(item.get("PARENT_NETPROFIT_YOY")),
            "roe": self._parse_percent(item.get("WEIGHTAVG_ROE")),
            "industry": item.get("INDUSTRY_NAME") or item.get("PUBLISHNAME"),
            "notice_date": self._normalize_date(item.get("NOTICE_DATE"), period),
            "update_date": self._normalize_date(item.get("UPDATE_DATE"), period),
            "source_url": f"{self.BASE_URL}/{period}/yjkb.html",
            "as_of": datetime.now(),
        }

    def _map_yjyg_api_item(self, item: Dict[str, Any], period: str) -> Optional[Dict[str, Any]]:
        code = item.get("SECURITY_CODE") or item.get("SECUCODE")
        name = item.get("SECURITY_NAME_ABBR") or item.get("SECURITY_NAME")
        if not code or not name:
            return None
        return {
            "period": period,
            "code": str(code),
            "name": str(name),
            "forecast_indicator": self._truncate(item.get("FORECAST_INDICATOR") or item.get("FORECAST_CONTENT"), 100),
            "forecast_value_range": self._truncate(item.get("FORECAST_VALUE") or item.get("FORECAST_RANGE"), 100),
            "yoy_range": self._truncate(item.get("FORECAST_YOY"), 100),
            "forecast_type": self._truncate(item.get("FORECAST_TYPE"), 50),
            "last_year_value": self._truncate(item.get("LAST_YEAR"), 100),
            "brief_reason": self._truncate(item.get("CHANGE_REASON"), 500),
            "notice_date": self._normalize_date(item.get("NOTICE_DATE"), period),
            "source_url": f"{self.BASE_URL}/{period}/yjyg.html",
            "as_of": datetime.now(),
        }

    def _map_yysj_api_item(self, item: Dict[str, Any], period: str) -> Optional[Dict[str, Any]]:
        code = item.get("SECURITY_CODE") or item.get("SECUCODE")
        name = item.get("SECURITY_NAME_ABBR") or item.get("SECURITY_NAME")
        if not code or not name:
            return None
        return {
            "period": period,
            "code": str(code),
            "name": str(name),
            "first_appoint_date": self._normalize_date(item.get("FIRST_APPOINT_DATE"), period),
            "change_1_date": self._normalize_date(item.get("FIRST_CHANGE_DATE") or item.get("CHANGE_DATE_1"), period),
            "change_2_date": self._normalize_date(item.get("SECOND_CHANGE_DATE") or item.get("CHANGE_DATE_2"), period),
            "change_3_date": self._normalize_date(item.get("THIRD_CHANGE_DATE") or item.get("CHANGE_DATE_3"), period),
            "actual_date": self._normalize_date(item.get("ACTUAL_PUBLISH_DATE") or item.get("ACTUAL_DATE"), period),
            "notice_date": self._normalize_date(item.get("NOTICE_DATE"), period),
            "source_url": f"{self.BASE_URL}/{period}/yysj.html",
            "as_of": datetime.now(),
        }

    def _parse_table(self, html_text: str) -> Tuple[List[str], List[List[str]]]:
        doc = lxml_html.fromstring(html_text)
        tables = doc.xpath("//table")
        if not tables:
            return [], []
        # 选择列数最多的表
        best_table = max(tables, key=lambda t: len(t.xpath(".//tr")), default=tables[0])
        header_cells = best_table.xpath(".//tr[1]/th")
        if not header_cells:
            header_cells = best_table.xpath(".//tr[1]/td")
        headers = [cell.text_content().strip().replace("\n", "") for cell in header_cells]

        rows: List[List[str]] = []
        for tr in best_table.xpath(".//tr[position()>1]"):
            cells = [td.text_content().strip().replace("\n", " ") for td in tr.xpath("./td")]
            if not cells:
                continue
            rows.append(cells)
        return headers, rows

    def _get_value_by_keywords(self, headers: List[str], row: List[str], keywords: List[str]) -> Optional[str]:
        for idx, header in enumerate(headers):
            for key in keywords:
                if key in header:
                    if idx < len(row):
                        return row[idx]
        return None

    def _map_yjbb_row(self, headers: List[str], row: List[str], period: str, url: str) -> Optional[Dict[str, Any]]:
        code = self._get_value_by_keywords(headers, row, ["代码"]) or ""
        name = self._get_value_by_keywords(headers, row, ["名称"]) or ""
        if not code or not name:
            return None
        return {
            "period": period,
            "code": code,
            "name": name,
            "eps": self._parse_number(self._get_value_by_keywords(headers, row, ["每股收益", "EPS"])),
            "revenue": self._parse_number(self._get_value_by_keywords(headers, row, ["营业", "营收", "收入"])),
            "revenue_yoy": self._parse_percent(self._get_value_by_keywords(headers, row, ["营业", "营收", "同比"])),
            "net_profit": self._parse_number(self._get_value_by_keywords(headers, row, ["净利润"])),
            "net_profit_yoy": self._parse_percent(self._get_value_by_keywords(headers, row, ["净利润", "同比"])),
            "roe": self._parse_percent(self._get_value_by_keywords(headers, row, ["净资产收益率", "ROE"])),
            "bps": self._parse_number(self._get_value_by_keywords(headers, row, ["每股净资产"])),
            "cashflow_ps": self._parse_number(self._get_value_by_keywords(headers, row, ["每股经营现金流"])),
            "industry": self._get_value_by_keywords(headers, row, ["行业"]),
            "notice_date": self._normalize_date(self._get_value_by_keywords(headers, row, ["公告", "披露", "更新"]), period),
            "source_url": url,
            "as_of": datetime.now(),
        }

    def _map_yjkb_row(self, headers: List[str], row: List[str], period: str, url: str) -> Optional[Dict[str, Any]]:
        code = self._get_value_by_keywords(headers, row, ["代码"]) or ""
        name = self._get_value_by_keywords(headers, row, ["名称"]) or ""
        if not code or not name:
            return None
        return {
            "period": period,
            "code": code,
            "name": name,
            "eps": self._parse_number(self._get_value_by_keywords(headers, row, ["每股收益", "EPS"])),
            "revenue": self._parse_number(self._get_value_by_keywords(headers, row, ["营业", "营收", "收入"])),
            "revenue_yoy": self._parse_percent(self._get_value_by_keywords(headers, row, ["营业", "同比"])),
            "net_profit": self._parse_number(self._get_value_by_keywords(headers, row, ["净利润"])),
            "net_profit_yoy": self._parse_percent(self._get_value_by_keywords(headers, row, ["净利润", "同比"])),
            "roe": self._parse_percent(self._get_value_by_keywords(headers, row, ["净资产收益率", "ROE"])),
            "industry": self._get_value_by_keywords(headers, row, ["行业"]),
            "notice_date": self._normalize_date(self._get_value_by_keywords(headers, row, ["公告", "披露", "更新"]), period),
            "source_url": url,
            "as_of": datetime.now(),
        }

    def _map_yjyg_row(self, headers: List[str], row: List[str], period: str, url: str) -> Optional[Dict[str, Any]]:
        code = self._get_value_by_keywords(headers, row, ["代码"]) or ""
        name = self._get_value_by_keywords(headers, row, ["名称"]) or ""
        if not code or not name:
            return None
        indicator = self._get_value_by_keywords(headers, row, ["指标", "预告指标"])
        forecast_value = self._get_value_by_keywords(headers, row, ["预告数值", "预告值"])
        yoy_range = self._get_value_by_keywords(headers, row, ["同比", "增幅"])
        forecast_type = self._get_value_by_keywords(headers, row, ["预告类型", "类型"])
        last_year_value = self._get_value_by_keywords(headers, row, ["上年同期"])
        reason = self._get_value_by_keywords(headers, row, ["原因", "预告内容", "业绩变动"])
        notice = self._get_value_by_keywords(headers, row, ["公告", "披露", "日期"])
        return {
            "period": period,
            "code": code,
            "name": name,
            "forecast_indicator": self._truncate(indicator, 100),
            "forecast_value_range": self._truncate(forecast_value, 100),
            "yoy_range": self._truncate(yoy_range, 100),
            "forecast_type": self._truncate(forecast_type, 50),
            "last_year_value": self._truncate(last_year_value, 100),
            "brief_reason": self._truncate(reason, 500),
            "notice_date": self._normalize_date(notice, period),
            "source_url": url,
            "as_of": datetime.now(),
        }

    def _map_yysj_row(self, headers: List[str], row: List[str], period: str, url: str) -> Optional[Dict[str, Any]]:
        code = self._get_value_by_keywords(headers, row, ["代码"]) or ""
        name = self._get_value_by_keywords(headers, row, ["名称"]) or ""
        if not code or not name:
            return None
        first_date = self._get_value_by_keywords(headers, row, ["首次", "预约"])
        change_1 = self._get_value_by_keywords(headers, row, ["一次变更", "一变更", "变更1"])
        change_2 = self._get_value_by_keywords(headers, row, ["二次变更", "二变更", "变更2"])
        change_3 = self._get_value_by_keywords(headers, row, ["三次变更", "三变更", "变更3"])
        actual_date = self._get_value_by_keywords(headers, row, ["实际", "披露"])
        return {
            "period": period,
            "code": code,
            "name": name,
            "first_appoint_date": self._normalize_date(first_date, period),
            "change_1_date": self._normalize_date(change_1, period),
            "change_2_date": self._normalize_date(change_2, period),
            "change_3_date": self._normalize_date(change_3, period),
            "actual_date": self._normalize_date(actual_date, period),
            "source_url": url,
            "as_of": datetime.now(),
        }

    async def _is_stale(self, model: Any, period: str, ttl_seconds: int) -> bool:
        if not self.db_session:
            return True
        result = await self.db_session.execute(
            select(func.max(model.updated_at)).where(model.period == period)
        )
        latest = result.scalar()
        if not latest:
            return True
        return datetime.now() - latest > timedelta(seconds=ttl_seconds)

    async def _upsert_rows(self, model: Any, rows: List[Dict[str, Any]], index_elements: List[str]):
        if not self.db_session or not rows:
            return
        stmt = insert(model).values(rows)
        update_cols = {k: getattr(stmt.excluded, k) for k in rows[0].keys() if k not in {"id", "created_at"}}
        stmt = stmt.on_conflict_do_update(index_elements=index_elements, set_=update_cols)
        await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def _load_from_db(self, model: Any, period: str, page: int, page_size: int, codes: List[str]) -> Dict[str, Any]:
        if not self.db_session:
            return {"total": 0, "data": []}
        query = select(model).where(model.period == period)
        if codes:
            query = query.where(model.code.in_(codes))
        result = await self.db_session.execute(query)
        rows = [self._model_to_dict(item) for item in result.scalars().all()]
        total = len(rows)
        start = max((page - 1), 0) * page_size
        data = rows[start : start + page_size]
        return {"total": total, "data": data}

    async def _fetch_yjbb_from_web(self, period: str, page: int, page_size: int) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/{period}/yjbb.html"
        text = await self._request_text(url, params={"page": page, "pagesize": page_size})
        report_name = self._extract_report_name(text) or self.REPORT_CONFIG["yjbb"]["report_name"]
        if report_name:
            cfg = self.REPORT_CONFIG["yjbb"]
            api_items = await self._fetch_datacenter(
                report_name,
                period,
                page,
                page_size,
                date_field=cfg["date_field"],
                sort_columns=cfg["sort_columns"],
                sort_types=cfg["sort_types"],
            )
            if api_items:
                mapped = [self._map_yjbb_api_item(item, period) for item in api_items]
                mapped = [m for m in mapped if m]
                if mapped:
                    return mapped
        headers, rows = self._parse_table(text)
        items: List[Dict[str, Any]] = []
        for row in rows:
            mapped = self._map_yjbb_row(headers, row, period, url)
            if mapped:
                items.append(mapped)
        return items

    async def _fetch_yjkb_from_web(self, period: str, page: int, page_size: int) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/{period}/yjkb.html"
        text = await self._request_text(url, params={"page": page, "pagesize": page_size})
        report_name = self._extract_report_name(text) or self.REPORT_CONFIG["yjkb"]["report_name"]
        if report_name:
            cfg = self.REPORT_CONFIG["yjkb"]
            api_items = await self._fetch_datacenter(
                report_name,
                period,
                page,
                page_size,
                date_field=cfg["date_field"],
                sort_columns=cfg["sort_columns"],
                sort_types=cfg["sort_types"],
            )
            if api_items:
                mapped = [self._map_yjkb_api_item(item, period) for item in api_items]
                mapped = [m for m in mapped if m]
                if mapped:
                    return mapped
        headers, rows = self._parse_table(text)
        items: List[Dict[str, Any]] = []
        for row in rows:
            mapped = self._map_yjkb_row(headers, row, period, url)
            if mapped:
                items.append(mapped)
        return items

    async def _fetch_yjyg_from_web(self, period: str, page: int, page_size: int, indicator: Optional[str], forecast_type: Optional[str]) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/{period}/yjyg.html"
        params: Dict[str, Any] = {"page": page, "pagesize": page_size}
        if indicator:
            params["type"] = indicator
        if forecast_type:
            params["forecast"] = forecast_type
        text = await self._request_text(url, params=params)
        report_name = self._extract_report_name(text) or self.REPORT_CONFIG["yjyg"]["report_name"]
        if report_name:
            cfg = self.REPORT_CONFIG["yjyg"]
            api_items = await self._fetch_datacenter(
                report_name,
                period,
                page,
                page_size,
                date_field=cfg["date_field"],
                sort_columns=cfg["sort_columns"],
                sort_types=cfg["sort_types"],
            )
            if api_items:
                mapped_items = [self._map_yjyg_api_item(item, period) for item in api_items]
                mapped_items = [m for m in mapped_items if m]
                if mapped_items:
                    return mapped_items
        headers, rows = self._parse_table(text)
        items: List[Dict[str, Any]] = []
        for row in rows:
            mapped = self._map_yjyg_row(headers, row, period, url)
            if mapped:
                indicator_value = str(mapped.get("forecast_indicator") or "")
                if indicator and indicator not in indicator_value:
                    continue
                forecast_value = str(mapped.get("forecast_type") or "")
                if forecast_type and forecast_type not in forecast_value:
                    continue
                items.append(mapped)
        return items

    async def _fetch_yysj_from_web(self, period: str, page: int, page_size: int) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/{period}/yysj.html"
        text = await self._request_text(url, params={"page": page, "pagesize": page_size})
        report_name = self._extract_report_name(text) or self.REPORT_CONFIG["yysj"]["report_name"]
        if report_name:
            cfg = self.REPORT_CONFIG["yysj"]
            api_items = await self._fetch_datacenter(
                report_name,
                period,
                page,
                page_size,
                date_field=cfg["date_field"],
                sort_columns=cfg["sort_columns"],
                sort_types=cfg["sort_types"],
            )
            if api_items:
                mapped = [self._map_yysj_api_item(item, period) for item in api_items]
                mapped = [m for m in mapped if m]
                if mapped:
                    return mapped
        headers, rows = self._parse_table(text)
        items: List[Dict[str, Any]] = []
        for row in rows:
            mapped = self._map_yysj_row(headers, row, period, url)
            if mapped:
                items.append(mapped)
        return items

    # ------------------------- 对外接口 -------------------------
    async def fetch_yjbb(
        self,
        period: Optional[str],
        page: int = 1,
        page_size: int = 50,
        market: str = "all",
        industry: Optional[str] = None,
        sort: Optional[str] = None,
        refresh: bool = False,
        codes: Optional[str] = None,
    ) -> Dict[str, Any]:
        period_input = period
        period = self._normalize_period(period)
        codes_list = self._split_codes(codes)
        if refresh or await self._is_stale(FinancialReportYjbb, period, self.YJBB_TTL_SECONDS):
            try:
                items = await self._fetch_yjbb_from_web(period, page, page_size)
                await self._upsert_rows(FinancialReportYjbb, items, ["period", "code", "notice_date"])
            except Exception as exc:
                logger.warning(f"抓取业绩报表失败: {exc}")
        data = await self._load_from_db(FinancialReportYjbb, period, page, page_size, codes_list)
        if not period_input and data.get("total", 0) == 0:
            for fallback in self._previous_periods(period, 8):
                try:
                    if refresh or await self._is_stale(FinancialReportYjbb, fallback, self.YJBB_TTL_SECONDS):
                        items = await self._fetch_yjbb_from_web(fallback, page, page_size)
                        await self._upsert_rows(FinancialReportYjbb, items, ["period", "code", "notice_date"])
                except Exception as exc:
                    logger.warning(f"抓取业绩报表失败({fallback}): {exc}")
                data = await self._load_from_db(FinancialReportYjbb, fallback, page, page_size, codes_list)
                if data.get("total", 0) > 0:
                    period = fallback
                    break
        data["data"] = self._filter_by_market(data.get("data", []), market)
        if industry:
            data["data"] = [d for d in data["data"] if industry in str(d.get("industry", ""))]
        return {
            "period": period,
            "page": page,
            "page_size": page_size,
            "total": data.get("total", 0),
            "data": data.get("data", []),
        }

    async def fetch_yjkb(
        self,
        period: Optional[str],
        page: int = 1,
        page_size: int = 50,
        market: str = "all",
        industry: Optional[str] = None,
        sort: Optional[str] = None,
        refresh: bool = False,
        codes: Optional[str] = None,
    ) -> Dict[str, Any]:
        period_input = period
        period = self._normalize_period(period)
        codes_list = self._split_codes(codes)
        if refresh or await self._is_stale(FinancialReportYjkb, period, self.YJKB_TTL_SECONDS):
            try:
                items = await self._fetch_yjkb_from_web(period, page, page_size)
                await self._upsert_rows(FinancialReportYjkb, items, ["period", "code"])
            except Exception as exc:
                logger.warning(f"抓取业绩快报失败: {exc}")
        data = await self._load_from_db(FinancialReportYjkb, period, page, page_size, codes_list)
        if not period_input and data.get("total", 0) == 0:
            for fallback in self._previous_periods(period, 8):
                try:
                    if refresh or await self._is_stale(FinancialReportYjkb, fallback, self.YJKB_TTL_SECONDS):
                        items = await self._fetch_yjkb_from_web(fallback, page, page_size)
                        await self._upsert_rows(FinancialReportYjkb, items, ["period", "code"])
                except Exception as exc:
                    logger.warning(f"抓取业绩快报失败({fallback}): {exc}")
                data = await self._load_from_db(FinancialReportYjkb, fallback, page, page_size, codes_list)
                if data.get("total", 0) > 0:
                    period = fallback
                    break
        filtered = self._filter_by_market(data.get("data", []), market)
        if industry:
            filtered = [d for d in filtered if industry in str(d.get("industry", ""))]
        return {
            "period": period,
            "page": page,
            "page_size": page_size,
            "total": data.get("total", 0),
            "data": filtered,
        }

    async def fetch_yjyg(
        self,
        period: Optional[str],
        page: int = 1,
        page_size: int = 50,
        market: str = "all",
        indicator: Optional[str] = None,
        forecast_type: Optional[str] = None,
        refresh: bool = False,
        codes: Optional[str] = None,
    ) -> Dict[str, Any]:
        period_input = period
        period = self._normalize_period(period)
        codes_list = self._split_codes(codes)
        if refresh or await self._is_stale(FinancialReportYjyg, period, self.YJYG_TTL_SECONDS):
            try:
                items = await self._fetch_yjyg_from_web(period, page, page_size, indicator, forecast_type)
                await self._upsert_rows(
                    FinancialReportYjyg,
                    items,
                    ["period", "code", "forecast_indicator", "forecast_type", "notice_date"],
                )
            except Exception as exc:
                logger.warning(f"抓取业绩预告失败: {exc}")
        data = await self._load_from_db(FinancialReportYjyg, period, page, page_size, codes_list)
        if not period_input and data.get("total", 0) == 0:
            for fallback in self._previous_periods(period, 8):
                try:
                    if refresh or await self._is_stale(FinancialReportYjyg, fallback, self.YJYG_TTL_SECONDS):
                        items = await self._fetch_yjyg_from_web(fallback, page, page_size, indicator, forecast_type)
                        await self._upsert_rows(
                            FinancialReportYjyg,
                            items,
                            ["period", "code", "forecast_indicator", "forecast_type", "notice_date"],
                        )
                except Exception as exc:
                    logger.warning(f"抓取业绩预告失败({fallback}): {exc}")
                data = await self._load_from_db(FinancialReportYjyg, fallback, page, page_size, codes_list)
                if data.get("total", 0) > 0:
                    period = fallback
                    break
        filtered = self._filter_by_market(data.get("data", []), market)
        if indicator:
            filtered = [d for d in filtered if indicator in str(d.get("forecast_indicator", ""))]
        if forecast_type:
            filtered = [d for d in filtered if forecast_type in str(d.get("forecast_type", ""))]
        return {
            "period": period,
            "page": page,
            "page_size": page_size,
            "total": data.get("total", 0),
            "data": filtered,
        }

    async def fetch_yysj(
        self,
        period: Optional[str],
        page: int = 1,
        page_size: int = 50,
        market: str = "all",
        refresh: bool = False,
        codes: Optional[str] = None,
    ) -> Dict[str, Any]:
        period_input = period
        period = self._normalize_period(period)
        codes_list = self._split_codes(codes)
        if refresh or await self._is_stale(FinancialReportYysj, period, self.YYSJ_TTL_SECONDS):
            try:
                items = await self._fetch_yysj_from_web(period, page, page_size)
                await self._upsert_rows(FinancialReportYysj, items, ["period", "code"])
            except Exception as exc:
                logger.warning(f"抓取预约披露失败: {exc}")
        data = await self._load_from_db(FinancialReportYysj, period, page, page_size, codes_list)
        if not period_input and data.get("total", 0) == 0:
            for fallback in self._previous_periods(period, 8):
                try:
                    if refresh or await self._is_stale(FinancialReportYysj, fallback, self.YYSJ_TTL_SECONDS):
                        items = await self._fetch_yysj_from_web(fallback, page, page_size)
                        await self._upsert_rows(FinancialReportYysj, items, ["period", "code"])
                except Exception as exc:
                    logger.warning(f"抓取预约披露失败({fallback}): {exc}")
                data = await self._load_from_db(FinancialReportYysj, fallback, page, page_size, codes_list)
                if data.get("total", 0) > 0:
                    period = fallback
                    break
        filtered = self._filter_by_market(data.get("data", []), market)
        return {
            "period": period,
            "page": page,
            "page_size": page_size,
            "total": data.get("total", 0),
            "data": filtered,
        }
