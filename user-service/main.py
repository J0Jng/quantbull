from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from core.config import settings
from models import auth_engine, init_db, seed_admin_user, seed_products
from routers.admin import router as admin_router
from routers.ai_tokens import router as ai_tokens_router
from routers.products import router as products_router
from routers.investor import router as investor_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if settings.env != "local":
        if settings.admin_password in {"admin123", "", None}:
            raise RuntimeError("Admin password must be changed in non-local environments.")
    init_db()
    # 迁移：确保所有必要的列存在
    from models import migrate_add_role_column, migrate_add_ai_tokens_column, migrate_product_detail_columns, migrate_add_investor_columns, migrate_add_user_profile_columns
    migrate_add_role_column()
    migrate_add_ai_tokens_column()
    migrate_product_detail_columns()
    migrate_add_investor_columns()
    migrate_add_user_profile_columns()
    
    with Session(auth_engine) as session:
        seed_admin_user(
            session,
            username=settings.admin_username,
            password_hash=settings.admin_password,
        )
        # 初始化商品种子数据
        seed_products(session)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="user-service", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.env == "local" else settings.cors_allow_origins,
        allow_credentials=True if settings.env == "local" else settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-site")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Embedder-Policy", "require-corp")
        if settings.env != "local" and not request.url.path.startswith(("/docs", "/redoc", "/openapi")):
            response.headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        return response

    @app.get("/health")
    async def health() -> dict:
        return {"code": 0, "message": "ok", "data": {"service": "user-service"}}

    app.include_router(admin_router)
    app.include_router(ai_tokens_router)
    app.include_router(products_router)
    app.include_router(investor_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)
