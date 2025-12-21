from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.logger import configure_logging
from core.database import init_db
from routers import api_router
import models
from core.handlers import http_exception_handler, validation_exception_handler, generic_exception_handler, envelope_middleware
from core.response import success


def create_app() -> FastAPI:
    configure_logging(settings)
    app = FastAPI(title="data-service", version="0.1.0")
    
    app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段直接 *
    allow_credentials=True,
    allow_methods=["*"],  # ⭐ 包含 OPTIONS
    allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")
    from fastapi.exceptions import HTTPException as StarletteHTTPException, RequestValidationError
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    app.middleware("http")(envelope_middleware)
    
    # 初始化数据库表和 Tushare
    @app.on_event("startup")
    async def on_startup():
        await init_db()
        
        # 初始化 Tushare API（如果配置了 token）
        if settings.tushare_token:
            try:
                from services.tushare_service import get_tushare_api
                get_tushare_api()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Tushare 初始化失败: {e}")
    
    return app


app = create_app()


@app.get("/health")
async def health_check() -> dict:
    return success({"status": "ok", "service": "data-service", "env": settings.env})

