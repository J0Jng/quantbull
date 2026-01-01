"""测试管理员接口"""
import pytest
from fastapi.testclient import TestClient


def test_admin_list_users_success(client: TestClient, auth_token: str):
    """测试管理员获取用户列表成功"""
    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert isinstance(data["data"], list)


def test_admin_list_users_with_pagination(client: TestClient, auth_token: str):
    """测试管理员获取用户列表（分页）"""
    response = client.get(
        "/api/admin/users?limit=10&offset=0",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert isinstance(data["data"], list)


def test_admin_list_users_unauthorized(client: TestClient):
    """测试未授权访问管理员接口返回 401"""
    response = client.get("/api/admin/users")
    assert response.status_code == 401


def test_admin_get_user_by_id_success(client: TestClient, auth_token: str):
    """测试管理员获取单个用户成功"""
    response = client.get(
        "/api/admin/users/1",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "username" in data["data"]
    assert "role" in data["data"]


def test_admin_create_user_success(client: TestClient, auth_token: str):
    """测试管理员创建用户成功"""
    response = client.post(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"username": "testuser", "password": "test123", "role": "user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["username"] == "testuser"
    assert data["data"]["role"] == "user"


def test_admin_update_user_password(client: TestClient, auth_token: str):
    """测试管理员重置用户密码"""
    response = client.patch(
        "/api/admin/users/1",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"password": "newpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0


def test_admin_update_user_role(client: TestClient, auth_token: str):
    """测试管理员修改用户角色"""
    response = client.patch(
        "/api/admin/users/2",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"role": "admin"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0


def test_admin_delete_user_success(client: TestClient, auth_token: str):
    """测试管理员删除用户成功"""
    response = client.delete(
        "/api/admin/users/2",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert "deleted_user_id" in data["data"]
