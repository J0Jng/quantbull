from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Literal, Optional, Tuple

from core.config import settings
from core.response import success
from models.public_fund_ranking_item import PublicFundRankingItemModel
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.funds import (
    PrivateFundRankingItem,
    PublicFundRankingItem,
)
from services.eastmoney_fund_ranking_service import EastmoneyFundRankingService

logger = logging.getLogger(__name__)


PublicSortBy = Literal["default", "return1w", "return1m", "return3m", "return6m", "return1y", "return3y"]
Order = Literal["desc", "asc"]


@dataclass
class CacheEntry:
    expires_at: datetime
    payload: Dict[str, Any]


_public_cache: Dict[str, CacheEntry] = {}


def _cache_key(**kwargs: Any) -> str:
    parts = [f"{k}={kwargs.get(k, '')}" for k in sorted(kwargs.keys())]
    return "funds:public:ranking:" + "|".join(parts)


class FundRankingService:
    """基金排行榜服务

    - 公募：优先尝试 Tushare（当前若数据不足则回退），兜底使用东方财富 rankhandler。
    - 私募：先用后端内置数据（可后续替换为 DB/配置）。
    """

    PUBLIC_CACHE_TTL_SECONDS = 600  # 10 分钟

    def __init__(self, db_session: Optional[AsyncSession] = None):
        self.eastmoney = EastmoneyFundRankingService()
        self.db_session = db_session

    async def _query_public_from_db(
        self,
        *,
        fund_type: str,
        return_sign: str,
        sort_by: str,
        order: str,
        keyword: str,
        page: int,
        page_size: int,
    ) -> Optional[dict]:
        if not self.db_session:
            return None

        base_query = select(PublicFundRankingItemModel)
        filters = []

        if fund_type:
            filters.append(PublicFundRankingItemModel.fund_type_key == fund_type)
        if return_sign == "positive":
            filters.append(PublicFundRankingItemModel.return1y >= 0)
        elif return_sign == "negative":
            filters.append(PublicFundRankingItemModel.return1y < 0)
        if keyword:
            kw = f"%{keyword.strip()}%"
            filters.append(
                or_(
                    PublicFundRankingItemModel.code.ilike(kw),
                    PublicFundRankingItemModel.name.ilike(kw),
                )
            )

        if filters:
            base_query = base_query.where(*filters)

        count_query = select(func.count()).select_from(base_query.subquery())
        total = (await self.db_session.execute(count_query)).scalar_one() or 0
        if total <= 0:
            return None

        sort_map = {
            "default": PublicFundRankingItemModel.return1y,
            "return1w": PublicFundRankingItemModel.return1w,
            "return1m": PublicFundRankingItemModel.return1m,
            "return3m": PublicFundRankingItemModel.return3m,
            "return6m": PublicFundRankingItemModel.return6m,
            "return1y": PublicFundRankingItemModel.return1y,
            "return3y": PublicFundRankingItemModel.return3y,
        }
        sort_col = sort_map.get(sort_by, PublicFundRankingItemModel.return1y)
        order_expr = sort_col.asc() if order == "asc" else sort_col.desc()

        query = (
            base_query.order_by(order_expr)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        rows = (await self.db_session.execute(query)).scalars().all()

        max_query = select(func.max(PublicFundRankingItemModel.fetched_at))
        if filters:
            max_query = max_query.where(*filters)
        updated_at = (await self.db_session.execute(max_query)).scalar_one()

        items = [self._row_to_public_item(r) for r in rows]
        payload = {
            "total": int(total),
            "page": page,
            "page_size": page_size,
            "items": items,
            "source_used": rows[0].source if rows else "eastmoney",
            "updated_at": (updated_at or datetime.now()).isoformat(),
        }
        return payload

    def _row_to_public_item(self, row: PublicFundRankingItemModel) -> Dict[str, Any]:
        return {
            "code": row.code,
            "name": row.name,
            "type": row.type_label,
            "nav": row.nav,
            "change": row.change,
            "return1w": row.return1w,
            "return1m": row.return1m,
            "return3m": row.return3m,
            "return6m": row.return6m,
            "return1y": row.return1y,
            "return3y": row.return3y,
            "as_of": row.as_of,
            "source": row.source,
            "cached": True,
        }

    async def _upsert_public_items(self, items: List[PublicFundRankingItem], fund_type: str) -> None:
        if not self.db_session:
            return

        now = datetime.now()
        for item in items:
            existing = await self.db_session.execute(
                select(PublicFundRankingItemModel).where(
                    PublicFundRankingItemModel.code == item.code,
                    PublicFundRankingItemModel.as_of == item.as_of,
                    PublicFundRankingItemModel.source == item.source,
                    PublicFundRankingItemModel.fund_type_key == fund_type,
                )
            )
            row = existing.scalar_one_or_none()
            if row:
                row.name = item.name
                row.type_label = item.type
                row.nav = item.nav
                row.change = item.change
                row.return1w = item.return1w
                row.return1m = item.return1m
                row.return3m = item.return3m
                row.return6m = item.return6m
                row.return1y = item.return1y
                row.return3y = item.return3y
                row.fetched_at = now
            else:
                self.db_session.add(
                    PublicFundRankingItemModel(
                        code=item.code,
                        name=item.name,
                        fund_type_key=fund_type,
                        type_label=item.type,
                        nav=item.nav,
                        change=item.change,
                        return1w=item.return1w,
                        return1m=item.return1m,
                        return3m=item.return3m,
                        return6m=item.return6m,
                        return1y=item.return1y,
                        return3y=item.return3y,
                        as_of=item.as_of,
                        source=item.source,
                        fetched_at=now,
                    )
                )

        await self.db_session.commit()

    async def cleanup_public_funds(self, retention_days: int = 30) -> int:
        if not self.db_session:
            return 0
        cutoff = datetime.now() - timedelta(days=retention_days)
        result = await self.db_session.execute(
            delete(PublicFundRankingItemModel).where(PublicFundRankingItemModel.fetched_at < cutoff)
        )
        await self.db_session.commit()
        return result.rowcount or 0

    async def get_public_ranking(
        self,
        *,
        fund_type: str = "",
        return_sign: str = "",
        sort_by: str = "default",
        order: str = "desc",
        keyword: str = "",
        page: int = 1,
        page_size: int = 50,
        refresh: bool = False,
    ) -> dict:
        fund_type = (fund_type or "").strip().lower()
        if fund_type in {"all"}:
            fund_type = ""

        return_sign = (return_sign or "").strip().lower()
        if return_sign in {"all"}:
            return_sign = ""

        allowed_sort: set[str] = {"default", "return1w", "return1m", "return3m", "return6m", "return1y", "return3y"}
        if sort_by not in allowed_sort:
            sort_by = "default"
        if order not in ["desc", "asc"]:
            order = "desc"

        page = max(1, int(page))
        page_size = max(1, min(int(page_size), 200))

        key = _cache_key(
            fund_type=fund_type,
            return_sign=return_sign,
            sort_by=sort_by,
            order=order,
            keyword=keyword.strip(),
            page=page,
            page_size=page_size,
        )

        if not refresh:
            if self.db_session:
                cached_payload = await self._query_public_from_db(
                    fund_type=fund_type,
                    return_sign=return_sign,
                    sort_by=sort_by,
                    order=order,
                    keyword=keyword,
                    page=page,
                    page_size=page_size,
                )
                if cached_payload:
                    return success(cached_payload)
            else:
                now = datetime.now(timezone.utc)
                entry = _public_cache.get(key)
                if entry and entry.expires_at > now:
                    cached_payload = dict(entry.payload)
                    # 标注每条 item 的 cached
                    items = cached_payload.get("items", [])
                    for it in items:
                        it["cached"] = True
                    cached_payload["source_used"] = cached_payload.get("source_used", "eastmoney")
                    return success(cached_payload)

        # 1) 尝试 Tushare（务实：当前难以可靠产出排行，若不可用则回退）
        tushare_reason = None
        if settings.tushare_token:
            try:
                # 这里保留“优先尝试”的入口：若未来补全 fund_basic/nav 计算，可在此返回。
                raise RuntimeError("Tushare 公募排行数据不足，回退到 Eastmoney")
            except Exception as e:
                tushare_reason = str(e)
                logger.info(f"公募排行回退到 Eastmoney：{tushare_reason}")
        else:
            logger.info("未配置 TUSHARE_TOKEN，公募排行直接使用 Eastmoney")

        # 2) Eastmoney 兜底
        items, total, asof_dt = await self.eastmoney.fetch_public_ranking(
            fund_type=fund_type,
            sort_by=sort_by,  # type: ignore[arg-type]
            order=order,  # type: ignore[arg-type]
            page=page,
            page_size=page_size,
            keyword=keyword,
        )

        # return_sign 过滤（按近1年收益率）
        if return_sign in ["positive", "negative"]:
            filtered: List[PublicFundRankingItem] = []
            for it in items:
                if return_sign == "positive" and it.return1y >= 0:
                    filtered.append(it)
                elif return_sign == "negative" and it.return1y < 0:
                    filtered.append(it)
            items = filtered

        updated_at = datetime.now().astimezone()

        payload = {
            "total": int(total),
            "page": page,
            "page_size": page_size,
            "items": [i.model_dump() for i in items],
            "source_used": "eastmoney",
            "updated_at": updated_at.isoformat(),
        }

        if self.db_session:
            await self._upsert_public_items(items, fund_type)
            cached_payload = await self._query_public_from_db(
                fund_type=fund_type,
                return_sign=return_sign,
                sort_by=sort_by,
                order=order,
                keyword=keyword,
                page=page,
                page_size=page_size,
            )
            return success(cached_payload or payload)

        _public_cache[key] = CacheEntry(
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=self.PUBLIC_CACHE_TTL_SECONDS),
            payload=payload,
        )

        return success(payload)

    async def get_private_ranking(
        self,
        *,
        strategy: str = "",
        risk_level: str = "",
        sort_by: str = "default",
        order: str = "desc",
        page: int = 1,
        page_size: int = 50,
        refresh: bool = False,
    ) -> dict:
        strategy = (strategy or "").strip().lower()
        if strategy in {"all"}:
            strategy = ""

        risk_level = (risk_level or "").strip().lower()
        if risk_level in {"all"}:
            risk_level = ""

        if order not in ["desc", "asc"]:
            order = "desc"

        page = max(1, int(page))
        page_size = max(1, min(int(page_size), 200))

        items = self._seed_private_items()

        if strategy:
            items = [i for i in items if self._match_strategy(strategy, i.strategy)]
        if risk_level:
            items = [i for i in items if str(i.risk_level).lower() == str(risk_level).lower()]

        reverse = order != "asc"
        if sort_by == "return1y":
            items.sort(key=lambda x: x.return1y, reverse=reverse)
        elif sort_by == "sharpe":
            items.sort(key=lambda x: x.sharpeRatio, reverse=reverse)
        elif sort_by == "maxdrawdown":
            # 最大回撤通常数值为负，按“更小(更负)更差”，所以 desc 时让 -5 优于 -20
            items.sort(key=lambda x: x.maxDrawdown, reverse=not reverse)
        else:
            items.sort(key=lambda x: x.return1y, reverse=True)

        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = items[start:end]

        updated_at = datetime.now().astimezone().isoformat()
        payload = {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [i.model_dump() for i in page_items],
            "source_used": "internal",
            "updated_at": updated_at,
        }
        return success(payload)

    def _match_strategy(self, strategy_key: str, label: str) -> bool:
        s = str(strategy_key).lower()
        if s == "equity":
            return "股票" in label
        if s == "futures":
            return "期货" in label
        if s == "hedge":
            return "对冲" in label
        if s == "composite":
            return ("复合" in label) or ("宏观" in label) or ("多" in label)
        return True

    def _seed_private_items(self) -> List[PrivateFundRankingItem]:
        today = datetime.now().date()
        return [
            PrivateFundRankingItem(
                id="private_qilin_equity",
                name="启林量化精选",
                strategy="股票策略",
                risk_level="medium",
                established="2018-03-15",
                return1m=2.3,
                return3m=5.6,
                return1y=18.2,
                annualizedReturn=16.8,
                maxDrawdown=-8.2,
                sharpeRatio=1.8,
                as_of=today,
            ),
            PrivateFundRankingItem(
                id="private_jiukun_hedge",
                name="九坤量化对冲",
                strategy="对冲策略",
                risk_level="low",
                established="2017-06-20",
                return1m=1.8,
                return3m=4.2,
                return1y=15.7,
                annualizedReturn=14.3,
                maxDrawdown=-6.5,
                sharpeRatio=2.1,
                as_of=today,
            ),
            PrivateFundRankingItem(
                id="private_minghong_equity",
                name="明汯量化100",
                strategy="股票策略",
                risk_level="medium",
                established="2016-09-12",
                return1m=1.5,
                return3m=3.8,
                return1y=17.4,
                annualizedReturn=15.9,
                maxDrawdown=-7.1,
                sharpeRatio=1.9,
                as_of=today,
            ),
            PrivateFundRankingItem(
                id="private_yanfu_macro",
                name="衍复宏观对冲",
                strategy="宏观策略",
                risk_level="medium",
                established="2019-01-08",
                return1m=0.9,
                return3m=2.1,
                return1y=12.8,
                annualizedReturn=13.2,
                maxDrawdown=-5.3,
                sharpeRatio=1.6,
                as_of=today,
            ),
            PrivateFundRankingItem(
                id="private_chengqi_composite",
                name="诚奇多策略",
                strategy="复合策略",
                risk_level="high",
                established="2018-11-30",
                return1m=2.1,
                return3m=4.9,
                return1y=16.5,
                annualizedReturn=15.7,
                maxDrawdown=-6.8,
                sharpeRatio=1.7,
                as_of=today,
            ),
        ]
