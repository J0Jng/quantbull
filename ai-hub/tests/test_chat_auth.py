import sys
from pathlib import Path
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

import routers.ai as ai_router_module

router = ai_router_module.router


def test_chat_requires_login():
    app = FastAPI()
    app.include_router(router, prefix="/api/ai")
    client = TestClient(app)

    resp = client.post(
        "/api/ai/chat",
        json={"message": "hello", "temperature": 0.7, "max_tokens": 64},
    )

    assert resp.status_code == 401


def test_chat_allows_internal_daily_report_without_login(monkeypatch):
    app = FastAPI()
    app.include_router(router, prefix="/api/ai")
    client = TestClient(app)

    async def fake_generate_with_system_prompt(**kwargs):
        return SimpleNamespace(
            content='{"ok": true}',
            model="deepseek",
            total_tokens=12,
            finish_reason="stop",
        )

    monkeypatch.setattr(
        ai_router_module.llm_service,
        "generate_with_system_prompt",
        fake_generate_with_system_prompt,
    )

    resp = client.post(
        "/api/ai/chat",
        headers={"X-Internal-Service": "daily-report"},
        json={"message": "hello", "temperature": 0.7, "max_tokens": 64},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["content"] == '{"ok": true}'
