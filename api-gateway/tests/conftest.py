import pytest
from fastapi.testclient import TestClient

from main import app
from services import auth_service


class MockResponse:
    def __init__(self, status_code: int = 200, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = ""
        import json
        self.content = json.dumps(self._payload).encode() if self._payload else b""
        self.headers = {"content-type": "application/json"}

    def json(self):
        return self._payload


class MockAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):  # pragma: no cover - required by context manager
        return False

    async def request(self, method, url, **kwargs):
        """通用请求方法，根据HTTP方法调用对应的方法"""
        if method == "POST":
            return await self.post(url, **kwargs)
        elif method == "GET":
            return await self.get(url, **kwargs)
        elif method == "PATCH":
            return await self.patch(url, **kwargs)
        elif method == "DELETE":
            return await self.delete(url, **kwargs)
        return MockResponse(status_code=404)

    async def post(self, url, data=None, json=None, content=None, **kwargs):
        body = json or data or {}
        
        # 如果是 content (bytes)，尝试解析
        if content and isinstance(content, bytes):
            try:
                import json as json_module
                body = json_module.loads(content.decode())
            except Exception:
                pass
        
        # 处理管理员创建用户接口
        if "/admin/users" in url:
            username = body.get("username", "testuser") if isinstance(body, dict) else "testuser"
            role = body.get("role", "user") if isinstance(body, dict) else "user"
            return MockResponse(payload={"code": 0, "message": "ok", "data": {"id": 2, "username": username, "role": role, "created_at": "2026-01-01T00:00:00"}})
        
        # 处理登录接口
        password = body.get("password") if isinstance(body, dict) else None
        if password != "admin123":
            return MockResponse(status_code=401, payload={"message": "invalid username or password"})
        return MockResponse(payload={"code": 0, "message": "ok", "data": {"access_token": "token", "token_type": "bearer", "expires_in": 3600, "user_id": 1}})

    async def get(self, url, headers=None, **kwargs):
        # 处理管理员接口 - 检查 Authorization header
        if "/admin/users" in url:
            # 检查是否有 Authorization header
            if not headers or "authorization" not in {k.lower(): v for k, v in headers.items()}:
                return MockResponse(status_code=401, payload={"detail": "Not authenticated"})
            
            if url.split("?")[0].endswith("/admin/users"):
                # 列出用户
                return MockResponse(payload={"code": 0, "message": "ok", "data": [{"id": 1, "username": "admin", "role": "admin", "created_at": "2026-01-01T00:00:00"}]})
            else:
                # 获取单个用户
                return MockResponse(payload={"code": 0, "message": "ok", "data": {"id": 1, "username": "admin", "role": "admin", "created_at": "2026-01-01T00:00:00"}})
        
        # 处理验证接口
        return MockResponse(payload={"code": 0, "message": "ok", "data": {"user_id": 1, "username": "admin", "role": "admin"}})

    async def patch(self, url, json=None, content=None, **kwargs):
        body = json or {}
        
        # 如果是 content (bytes)，尝试解析
        if content and isinstance(content, bytes):
            try:
                import json as json_module
                body = json_module.loads(content.decode())
            except Exception:
                pass
        
        # 处理管理员更新用户接口
        if "/admin/users" in url:
            return MockResponse(payload={"code": 0, "message": "ok", "data": {"id": 1, "username": "admin", "role": body.get("role", "admin"), "created_at": "2026-01-01T00:00:00"}})
        return MockResponse(status_code=404)

    async def delete(self, url, **kwargs):
        # 处理管理员删除用户接口
        if "/admin/users" in url:
            return MockResponse(payload={"code": 0, "message": "ok", "data": {"deleted_user_id": 2}})
        return MockResponse(status_code=404)


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
