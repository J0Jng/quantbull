from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from core.config import settings
from models import auth_engine, init_db, seed_admin_user
from auth.jwt import hash_password
from routers.auth import router as auth_router
from routers.admin import router as admin_router
from routers.ai_tokens import router as ai_tokens_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    # 迁移：确保 role 列存在
    from models import migrate_add_role_column, migrate_add_ai_tokens_column
    migrate_add_role_column()
    migrate_add_ai_tokens_column()
    
    with Session(auth_engine) as session:
        seed_admin_user(
            session,
            username=settings.admin_username,
            password_hash=hash_password(settings.admin_password),
        )
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="user-service", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict:
        return {"code": 0, "message": "ok", "data": {"service": "user-service"}}

    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(ai_tokens_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)
