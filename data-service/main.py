import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.logger import configure_logging
from core.database import init_db
from routers import api_router
import models
from core.handlers import http_exception_handler, validation_exception_handler, generic_exception_handler, envelope_middleware
from core.response import success


def _parse_cors_origins(raw: str) -> list[str]:
    raw = (raw or "").strip()
    if not raw:
        return []
    if raw.startswith("["):
        try:
            val = json.loads(raw)
            return [str(x) for x in val] if isinstance(val, list) else []
        except Exception:
            return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def _cors_config() -> tuple[list[str], bool]:
    env = (os.getenv("ENV", "local") or "local").lower()
    if env == "local":
        return ["*"], True
    origins = _parse_cors_origins(os.getenv("CORS_ALLOW_ORIGINS", ""))
    credentials = (os.getenv("CORS_ALLOW_CREDENTIALS", "false") or "false").lower() in {"1", "true", "yes"}
    return origins, credentials


def create_app() -> FastAPI:
    configure_logging(settings)
    app = FastAPI(title="data-service", version="0.1.0")
    
    cors_origins, cors_credentials = _cors_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=cors_credentials,
        allow_methods=["*"],  # ⭐ 包含 OPTIONS
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")
    static_dir = Path(__file__).resolve().parent / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    app.mount("/api/static", StaticFiles(directory=str(static_dir)), name="api-static")
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

        # 启动公募基金排行榜预热与清理任务
        try:
            from scheduler_public_fund_ranking import get_public_fund_ranking_scheduler
            fund_scheduler = get_public_fund_ranking_scheduler(interval_minutes=60, retention_days=30)
            fund_scheduler.start()
            import logging
            logger = logging.getLogger(__name__)
            logger.info("公募基金排行榜定时任务已启动（预热每小时，清理每日03:30）")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"公募基金排行榜定时任务启动失败: {e}")

        # 启动资金流向预热任务
        try:
            from scheduler_fund_flow import get_fund_flow_scheduler
            flow_scheduler = get_fund_flow_scheduler(interval_minutes=15)
            flow_scheduler.start()
            import logging
            logger = logging.getLogger(__name__)
            logger.info("资金流向定时任务已启动（预热每15分钟）")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"资金流向定时任务启动失败: {e}")

        # 启动财报（年报季报）定时任务
        try:
            from scheduler_financial_report import get_financial_report_scheduler
            report_scheduler = get_financial_report_scheduler()
            report_scheduler.start(cron_hour=3, cron_minute=20, yysj_interval_hours=6)
            import logging
            logger = logging.getLogger(__name__)
            logger.info("财报定时任务已启动（每日预热 + 预约披露定时更新）")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"财报定时任务启动失败: {e}")

        # 启动龙虎榜定时任务
        try:
            from scheduler_lhb import get_lhb_scheduler
            lhb_scheduler = get_lhb_scheduler()
            lhb_scheduler.start(cron_hour=18, cron_minute=10)
            import logging
            logger = logging.getLogger(__name__)
            logger.info("龙虎榜定时任务已启动（每日收盘后预热）")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"龙虎榜定时任务启动失败: {e}")

        # 启动每日财经头条生成任务（每日 03:00）
        try:
            from scheduler_headlines import get_daily_headlines_scheduler
            headlines_scheduler = get_daily_headlines_scheduler(hour=3, minute=0, limit=10, hours=24)
            headlines_scheduler.start()
            import logging
            logger = logging.getLogger(__name__)
            logger.info("每日财经头条生成任务已启动（每日 03:00）")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"每日财经头条生成任务启动失败: {e}")
    
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

        # 停止公募基金排行榜定时任务
        try:
            from scheduler_public_fund_ranking import get_public_fund_ranking_scheduler
            fund_scheduler = get_public_fund_ranking_scheduler()
            fund_scheduler.stop()
        except Exception:
            pass

        # 停止资金流向定时任务
        try:
            from scheduler_fund_flow import get_fund_flow_scheduler
            flow_scheduler = get_fund_flow_scheduler()
            flow_scheduler.stop()
        except Exception:
            pass

        # 停止财报定时任务
        try:
            from scheduler_financial_report import get_financial_report_scheduler
            report_scheduler = get_financial_report_scheduler()
            report_scheduler.stop()
        except Exception:
            pass

        # 停止龙虎榜定时任务
        try:
            from scheduler_lhb import get_lhb_scheduler
            lhb_scheduler = get_lhb_scheduler()
            lhb_scheduler.stop()
        except Exception:
            pass

        # 停止每日财经头条生成任务
        try:
            from scheduler_headlines import get_daily_headlines_scheduler
            headlines_scheduler = get_daily_headlines_scheduler()
            headlines_scheduler.stop()
        except Exception:
            pass
    
    return app


app = create_app()


@app.get("/health")
async def health_check() -> dict:
    return success({"status": "ok", "service": "data-service", "env": settings.env})

