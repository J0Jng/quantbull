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
        
        # 初始化财经头条种子数据
        try:
            from services.headline_seed import seed_headline_news_if_empty
            from core.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                await seed_headline_news_if_empty(db)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"财经头条种子数据初始化失败: {e}")
        
        # 初始化 Tushare API（如果配置了 token）
        if settings.tushare_token:
            try:
                from services.tushare_service import get_tushare_api
                get_tushare_api()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Tushare 初始化失败: {e}")
        
        # 启动东方财富网新闻定时刷新任务
        try:
            from scheduler_eastmoney_news import get_eastmoney_news_scheduler
            scheduler = get_eastmoney_news_scheduler()
            scheduler.start(interval_minutes=5)  # 每 5 分钟刷新一次
            import logging
            logger = logging.getLogger(__name__)
            logger.info("东方财富网新闻定时刷新任务已启动")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"东方财富网新闻定时任务启动失败: {e}")
        
        # 启动财经频道数据定时刷新任务
        try:
            from scheduler_finance_channel import get_finance_channel_scheduler
            finance_scheduler = get_finance_channel_scheduler()
            finance_scheduler.start(interval_minutes=60)  # 每 60 分钟刷新一次
            import logging
            logger = logging.getLogger(__name__)
            logger.info("财经频道数据定时刷新任务已启动（每小时）")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"财经频道定时任务启动失败: {e}")
    
    @app.on_event("shutdown")
    async def on_shutdown():
        # 停止东方财富网新闻定时任务
        try:
            from scheduler_eastmoney_news import get_eastmoney_news_scheduler
            scheduler = get_eastmoney_news_scheduler()
            scheduler.stop()
        except Exception:
            pass
        
        # 停止财经频道定时任务
        try:
            from scheduler_finance_channel import get_finance_channel_scheduler
            finance_scheduler = get_finance_channel_scheduler()
            finance_scheduler.stop()
        except Exception:
            pass
    
    return app


app = create_app()


@app.get("/health")
async def health_check() -> dict:
    return success({"status": "ok", "service": "data-service", "env": settings.env})

