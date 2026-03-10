import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[1]))

from routers.ai import router


def test_chat_requires_login():
    app = FastAPI()
    app.include_router(router, prefix="/api/ai")
    client = TestClient(app)

    resp = client.post(
        "/api/ai/chat",
        json={"message": "hello", "temperature": 0.7, "max_tokens": 64},
    )

    assert resp.status_code == 401
