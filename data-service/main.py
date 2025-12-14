from fastapi import FastAPI
from core.config import settings
from core.logger import configure_logging
from core.database import init_db
from routers import api_router


def create_app() -> FastAPI:
    configure_logging(settings)
    app = FastAPI(title="data-service", version="0.1.0")
    app.include_router(api_router, prefix="/api")
    
    # 初始化数据库表和 Tushare
    @app.on_event("startup")
    def on_startup():
        init_db()
        
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
    return {"status": "ok", "service": "data-service", "env": settings.env}

