"""严格日期校验相关测试"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import httpx

from services.data_client import DataServiceClient, MarketDataDateMismatchError
import services.report_service as report_service_module
from services.report_service import ReportService


class MockResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


class MockAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, params=None):
        if url.endswith("/market/overview"):
            return MockResponse(
                {
                    "data": {
                        "trade_date": "2026-01-24",
                        "market_status": "closed",
                        "indices": [],
                        "total_turnover": 0,
                    }
                }
            )
        if url.endswith("/etf/list"):
            return MockResponse({"data": []})
        if url.endswith("/stock/list"):
            return MockResponse({"data": []})
        return MockResponse({"data": {}})


@pytest.mark.asyncio
async def test_fetch_market_data_strict_date_mismatch(monkeypatch):
    """当市场概览日期非请求日时应抛出错误"""
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    client = DataServiceClient()
    with pytest.raises(MarketDataDateMismatchError) as exc:
        await client.fetch_market_data("2026-01-25", strict_date=True)

    assert exc.value.expected_date == "2026-01-25"
    assert exc.value.actual_trade_date == "2026-01-24"


class FakeQuery:
    def __init__(self, session):
        self._session = session

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._session.report


class FakeSession:
    def __init__(self):
        self.report = None

    def query(self, model):
        return FakeQuery(self)

    def add(self, report):
        self.report = report

    def commit(self):
        return None

    def refresh(self, report):
        self.report = report

    def close(self):
        return None


@pytest.mark.asyncio
async def test_generate_daily_report_uses_get_china_today(monkeypatch):
    """report_date=None 时应使用 get_china_today"""
    fixed_today = "2026-01-25"
    monkeypatch.setattr(report_service_module, "get_china_today", lambda: fixed_today)
    monkeypatch.setattr(report_service_module, "SessionLocal", lambda: FakeSession())

    service = ReportService()
    captured = {}

    async def fake_fetch_market_data(report_date, strict_date=True):
        captured["report_date"] = report_date
        raise MarketDataDateMismatchError(
            expected_date=report_date,
            actual_trade_date=report_date,
        )

    monkeypatch.setattr(service.data_client, "fetch_market_data", fake_fetch_market_data)

    with pytest.raises(MarketDataDateMismatchError):
        await service.generate_daily_report(report_date=None, force=False)

    assert captured["report_date"] == fixed_today
