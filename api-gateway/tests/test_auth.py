import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "api-gateway"
    assert data["status"] == "running"


def test_health_check(client: TestClient):
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "api-gateway"


def test_login_json_success(client: TestClient):
    """测试 JSON 格式登录成功"""
    response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_json_failure(client: TestClient):
    """测试 JSON 格式登录失败"""
    response = client.post(
        "/api/auth/login/json",
        json={"username": "admin", "password": "wrong_password"}
    )
    assert response.status_code == 401
    assert "用户名或密码错误" in response.json()["detail"]


def test_login_oauth2_success(client: TestClient):
    """测试 OAuth2 格式登录成功"""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_oauth2_failure(client: TestClient):
    """测试 OAuth2 格式登录失败"""
    response = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "wrong_password"}
    )
    assert response.status_code == 401


def test_get_current_user_success(client: TestClient, auth_token: str):
    """测试获取当前用户信息成功"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert "user_id" in data
    assert data["username"] == "admin"


def test_get_current_user_no_token(client: TestClient):
    """测试获取当前用户信息 - 无令牌"""
    response = client.get("/api/auth/me")
    assert response.status_code == 401  # FastAPI OAuth2 返回 401


def test_get_current_user_invalid_token(client: TestClient):
    """测试获取当前用户信息 - 无效令牌"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401
