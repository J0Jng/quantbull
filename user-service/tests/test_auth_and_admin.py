import os
import sys
from pathlib import Path
import importlib

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _build_app(tmp_path: Path):
    os.environ["ENV"] = "local"
    os.environ["ADMIN_USERNAME"] = "admin"
    os.environ["ADMIN_PASSWORD"] = "admin123"

    models = importlib.import_module("models")
    main_module = importlib.import_module("main")

    db_file = tmp_path / "test_user_service.db"
    test_engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False}, echo=False)
    setattr(models, "auth_engine", test_engine)
    setattr(main_module, "auth_engine", test_engine)
    SQLModel.metadata.create_all(getattr(models, "auth_engine"))

    return main_module.create_app()


def _login(client: TestClient, username: str, password: str) -> str:
    resp = client.post("/api/auth/login/json", json={"username": username, "password": password})
    assert resp.status_code == 200
    payload = resp.json()
    token = payload["data"]["access_token"]
    return token


def test_login_success_and_failure(tmp_path: Path):
    with TestClient(_build_app(tmp_path)) as client:
        ok = client.post("/api/auth/login/json", json={"username": "admin", "password": "admin123"})
        assert ok.status_code == 200
        assert ok.json()["data"]["token_type"] == "bearer"

        bad = client.post("/api/auth/login/json", json={"username": "admin", "password": "wrong"})
        assert bad.status_code == 401



def test_user_cannot_access_admin_endpoint(tmp_path: Path):
    with TestClient(_build_app(tmp_path)) as client:
        admin_token = _login(client, "admin", "admin123")
        create_resp = client.post(
            "/api/admin/users",
            json={"username": "normal_user", "password": "abc12345", "role": "user"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert create_resp.status_code == 200

        user_token = _login(client, "normal_user", "abc12345")
        denied = client.get("/api/admin/users", headers={"Authorization": f"Bearer {user_token}"})
        assert denied.status_code == 403



def test_admin_create_user_success_and_role_forced_user(tmp_path: Path):
    with TestClient(_build_app(tmp_path)) as client:
        admin_token = _login(client, "admin", "admin123")
        resp = client.post(
            "/api/admin/users",
            json={"username": "created_by_admin", "password": "abc12345", "role": "admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )

        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["username"] == "created_by_admin"
        assert data["role"] == "user"
