import pytest
from fastapi import HTTPException

from services import auth_service
from services.auth_service import AuthService
from services.proxy_service import ProxyService


class MockResponse:
    def __init__(self, status_code: int = 200, payload: dict | None = None, text: str = ""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload


class MockAsyncClient:
    def __init__(self, post_response: MockResponse | None = None, get_response: MockResponse | None = None):
        self.post_response = post_response or MockResponse()
        self.get_response = get_response or MockResponse()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):  # pragma: no cover - required by context manager
        return False

    async def post(self, *args, **kwargs):
        return self.post_response

    async def get(self, *args, **kwargs):
        return self.get_response


class TestAuthService:
    @pytest.mark.asyncio
    async def test_login_with_form_success(self, monkeypatch):
        payload = {"code": 0, "message": "ok", "data": {"access_token": "token", "token_type": "bearer", "expires_in": 3600, "user_id": 1}}
        monkeypatch.setattr(auth_service.httpx, "AsyncClient", lambda **kwargs: MockAsyncClient(post_response=MockResponse(payload=payload)))

        result = await AuthService.login_with_form("admin", "admin123")
        assert result["data"]["access_token"] == "token"

    @pytest.mark.asyncio
    async def test_login_with_form_failure(self, monkeypatch):
        payload = {"message": "invalid"}
        monkeypatch.setattr(auth_service.httpx, "AsyncClient", lambda **kwargs: MockAsyncClient(post_response=MockResponse(status_code=401, payload=payload)))

        with pytest.raises(HTTPException):
            await AuthService.login_with_form("admin", "bad")

    @pytest.mark.asyncio
    async def test_verify_token_success(self, monkeypatch):
        payload = {"code": 0, "message": "ok", "data": {"user_id": 9, "username": "alice"}}
        monkeypatch.setattr(auth_service.httpx, "AsyncClient", lambda **kwargs: MockAsyncClient(get_response=MockResponse(payload=payload)))

        token_data = await AuthService.verify_token("token")
        assert token_data is not None
        assert token_data.username == "alice"
        assert token_data.user_id == 9

    @pytest.mark.asyncio
    async def test_verify_token_failure(self, monkeypatch):
        monkeypatch.setattr(auth_service.httpx, "AsyncClient", lambda **kwargs: MockAsyncClient(get_response=MockResponse(status_code=401, payload={"message": "invalid"})))

        token_data = await AuthService.verify_token("bad")
        assert token_data is None


class TestProxyService:
    def test_service_urls_configured(self):
        assert "data-service" in ProxyService.SERVICE_URLS
        assert "ai-hub" in ProxyService.SERVICE_URLS
        assert "quant-engine" in ProxyService.SERVICE_URLS
        assert "daily-report" in ProxyService.SERVICE_URLS
        assert "user-service" in ProxyService.SERVICE_URLS

    @pytest.mark.asyncio
    async def test_check_service_health(self):
        health = await ProxyService.check_service_health("data-service")
        assert health.service_name == "data-service"
        assert health.status in ["healthy", "unhealthy", "unknown"]
        assert health.url is not None
