import pytest
from fastapi.testclient import TestClient

from main import app
from services import auth_service


class MockResponse:
    def __init__(self, status_code: int = 200, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = ""

    def json(self):
        return self._payload


class MockAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):  # pragma: no cover - required by context manager
        return False

    async def post(self, url, data=None, json=None, **kwargs):
        body = json or data or {}
        password = body.get("password") if isinstance(body, dict) else None
        if password != "admin123":
            return MockResponse(status_code=401, payload={"message": "invalid username or password"})
        return MockResponse(payload={"code": 0, "message": "ok", "data": {"access_token": "token", "token_type": "bearer", "expires_in": 3600, "user_id": 1}})

    async def get(self, url, headers=None, **kwargs):
        return MockResponse(payload={"code": 0, "message": "ok", "data": {"user_id": 1, "username": "admin"}})


@pytest.fixture(autouse=True)
def mock_user_service(monkeypatch):
    monkeypatch.setattr(auth_service.httpx, "AsyncClient", lambda **kwargs: MockAsyncClient())


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]
