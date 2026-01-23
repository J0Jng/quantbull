from __future__ import annotations

import json
import logging
import random
import re
from datetime import datetime
from typing import Dict, List, Literal, Optional, Tuple

import httpx

from schemas.funds import PublicFundRankingItem

logger = logging.getLogger(__name__)


PublicSortBy = Literal["default", "return1w", "return1m", "return3m", "return6m", "return1y", "return3y"]
Order = Literal["desc", "asc"]


class EastmoneyFundRankingService:
    """东方财富基金排行榜抓取服务（rankhandler 接口）

    说明：
    - 该接口需要带 Referer/UA，否则可能返回“无访问权限”。
    - 返回为 JS 变量：var rankData = {...}; 其中 datas 为字符串数组。
    """

    BASE_URL = "https://fund.eastmoney.com/data/rankhandler.aspx"

    _SORT_MAP: Dict[str, str] = {
        "default": "1nzf",  # 默认使用近1年
        "return1w": "1zzf",
        "return1m": "1yzf",
        "return3m": "3yzf",
        "return6m": "6yzf",
        "return1y": "1nzf",
        "return3y": "3nzf",
    }

    _FUND_TYPE_MAP: Dict[str, str] = {
        "": "all",
        "stock": "gp",
        "hybrid": "hh",
        "bond": "zq",
        "monetary": "hb",
    }

    _FUND_TYPE_LABEL: Dict[str, str] = {
        "stock": "股票型基金",
        "hybrid": "混合型基金",
        "bond": "债券型基金",
        "monetary": "货币型基金",
        "": "基金",
    }

    def __init__(self, timeout: float = 12.0, max_retries: int = 2):
        self.timeout = timeout
        self.max_retries = max_retries

    def _decode_response_text(self, resp: httpx.Response) -> str:
        """东方财富该接口经常不返回 charset，http 客户端可能按 latin-1 解码导致中文乱码。

        这里基于 bytes 进行解码探测，并在必要时做 latin1→utf8 纠偏。
        """

        content = resp.content or b""

        for enc in ("utf-8", "gb18030"):
            try:
                text = content.decode(enc)
            except UnicodeDecodeError:
                continue
            if "rankData" in text:
                return text

        text = resp.text
        if text and "rankData" not in text:
            try:
                fixed = text.encode("latin-1").decode("utf-8")
                if "rankData" in fixed:
                    return fixed
            except Exception:
                pass

        return text

    async def fetch_public_ranking(
        self,
        *,
        fund_type: str = "",
        sort_by: PublicSortBy = "default",
        order: Order = "desc",
        page: int = 1,
        page_size: int = 50,
        keyword: str = "",
    ) -> Tuple[List[PublicFundRankingItem], int, datetime]:
        """抓取公募基金排行榜。

        Returns:
            (items, total, asof_datetime)
        """
        ft = self._FUND_TYPE_MAP.get(fund_type, "all")
        sc = self._SORT_MAP.get(sort_by, "1nzf")
        st = "desc" if order != "asc" else "asc"

        params = {
            "op": "ph",
            "dt": "kf",
            "ft": ft,
            "rs": "",
            "gs": "0",
            "sc": sc,
            "st": st,
            "sd": "",
            "ed": "",
            "qdii": "",
            "tabSubtype": ",,,,,",
            "pi": str(page),
            "pn": str(page_size),
            "dx": "1",
            "v": f"{random.random():.6f}",
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/plain,*/*",
            "Referer": "https://fund.eastmoney.com/data/fundranking.html",
        }

        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, headers=headers) as client:
                    resp = await client.get(self.BASE_URL, params=params)
                    resp.raise_for_status()
                    text = self._decode_response_text(resp)

                if "无访问权限" in text:
                    raise RuntimeError("eastmoney rankhandler: no permission")

                datas, meta = self._parse_rankhandler(text)

                items: List[PublicFundRankingItem] = []
                for row in datas:
                    item = self._parse_item(row, fund_type=fund_type)
                    if item is None:
                        continue
                    if keyword:
                        kw = keyword.strip()
                        if kw and (kw not in item.code) and (kw not in item.name):
                            continue
                    items.append(item)

                total = int(meta.get("allRecords") or meta.get("allRecords".lower()) or 0)
                asof = datetime.now()
                return items, total, asof

            except Exception as e:
                last_err = e
                logger.warning(f"Eastmoney 抓取失败 attempt={attempt + 1}/{self.max_retries + 1}: {e}")

        assert last_err is not None
        raise last_err

    def _parse_rankhandler(self, text: str) -> Tuple[List[str], Dict[str, int]]:
        m = re.search(r"var\s+rankData\s*=\s*\{(.*)\};\s*$", text.strip(), re.S)
        if not m:
            raise ValueError("eastmoney rankhandler: unexpected response")

        body = m.group(1)

        datas_match = re.search(r"datas\s*:\s*\[(.*?)\]\s*,\s*allRecords\s*:\s*(\d+)", body, re.S)
        if not datas_match:
            # 尝试更宽松地提取 datas
            datas_match = re.search(r"datas\s*:\s*\[(.*?)\]", body, re.S)
        if not datas_match:
            raise ValueError("eastmoney rankhandler: datas not found")

        datas_raw = datas_match.group(1)
        try:
            datas = json.loads("[" + datas_raw + "]")
        except Exception as e:
            raise ValueError(f"eastmoney rankhandler: datas json parse failed: {e}")

        meta: Dict[str, int] = {}
        for key in ["allRecords", "pageIndex", "pageNum", "allPages", "allNum"]:
            km = re.search(rf"\b{key}\s*:\s*(\d+)", body)
            if km:
                meta[key] = int(km.group(1))

        return datas, meta

    def _to_float(self, v: str) -> float:
        if v is None:
            return 0.0
        s = str(v).strip()
        if s == "" or s == "--":
            return 0.0
        s = s.replace("%", "")
        try:
            return float(s)
        except Exception:
            return 0.0

    def _parse_item(self, row: str, fund_type: str) -> Optional[PublicFundRankingItem]:
        parts = [p.strip() for p in row.split(",")]
        if len(parts) < 12:
            return None

        code = parts[0]
        name = parts[1]

        # 常见字段位置（东方财富 rankhandler）
        # 0:code 1:name 3:date 4:unit_nav 6:day_growth 7:1w 8:1m 9:3m 10:6m 11:1y 13:3y
        as_of_str = parts[3] if len(parts) > 3 else ""
        try:
            as_of_date = datetime.strptime(as_of_str, "%Y-%m-%d").date() if as_of_str else datetime.now().date()
        except Exception:
            as_of_date = datetime.now().date()

        nav = self._to_float(parts[4] if len(parts) > 4 else "")
        change = self._to_float(parts[6] if len(parts) > 6 else "")
        r1w = self._to_float(parts[7] if len(parts) > 7 else "")
        r1m = self._to_float(parts[8] if len(parts) > 8 else "")
        r3m = self._to_float(parts[9] if len(parts) > 9 else "")
        r6m = self._to_float(parts[10] if len(parts) > 10 else "")
        r1y = self._to_float(parts[11] if len(parts) > 11 else "")
        r3y = self._to_float(parts[13] if len(parts) > 13 else "")

        return PublicFundRankingItem(
            code=code,
            name=name,
            type=self._FUND_TYPE_LABEL.get(fund_type, "基金"),
            nav=nav,
            change=change,
            return1w=r1w,
            return1m=r1m,
            return3m=r3m,
            return6m=r6m,
            return1y=r1y,
            return3y=r3y,
            as_of=as_of_date,
            source="eastmoney",
            cached=False,
        )
