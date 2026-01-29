import json
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logger import configure_logging, get_logger
from routers import api_router
from scheduler import create_scheduler, start_scheduler, shutdown_scheduler
from db.session import init_db
from core.handlers import http_exception_handler, validation_exception_handler, generic_exception_handler, envelope_middleware
from core.response import success

# 配置日志
configure_logging(settings)
logger = get_logger(__name__)


def _should_run_scheduler() -> bool:
    raw = (os.getenv("RUN_SCHEDULER", "true") or "true").strip().lower()
    return raw in {"1", "true", "yes", "y", "on"}


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("=" * 50)
    logger.info("Daily Report Service 启动中...")
    logger.info("=" * 50)
    
    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}", exc_info=True)
        # SQLite 和内存数据库允许继续运行，PostgreSQL 失败时根据环境决定
        if settings.db_type == "postgresql" and settings.env != "local":
            raise
        else:
            logger.warning("数据库初始化失败，但允许继续运行（可能使用内存数据库）")
    
    # 启动定时任务调度器
    if _should_run_scheduler():
        try:
            scheduler = create_scheduler()
            start_scheduler()
            logger.info("定时任务调度器已启动")
        except Exception as e:
            logger.error(f"调度器启动失败: {e}", exc_info=True)
            # 开发环境允许继续运行
            if settings.env != "local":
                raise
    else:
        logger.info("已禁用内置调度器（RUN_SCHEDULER=false）")
    
    logger.info("=" * 50)
    logger.info("Daily Report Service 启动完成")
    logger.info("=" * 50)
    
    yield
    
    # 关闭时执行
    logger.info("Daily Report Service 关闭中...")
    shutdown_scheduler()
    logger.info("Daily Report Service 已关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="Daily Report Service",
        description="每日 AI 投资方案生成服务",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,  # 生命周期管理
    )
    
    # 配置 CORS（生产必须显式白名单；local 才允许 *）
    cors_origins, cors_credentials = _cors_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=cors_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(api_router, prefix="/api")

    # 全局异常处理与响应封装中间件
    from fastapi.exceptions import HTTPException as StarletteHTTPException, RequestValidationError
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    app.middleware("http")(envelope_middleware)
    
    return app


app = create_app()


@app.get("/health", tags=["健康检查"])
async def health_check() -> dict:
    """健康检查接口"""
    return success({
        "status": "ok",
        "service": "daily-report",
        "version": "1.0.0",
        "env": settings.env,
    })


@app.get("/", tags=["根路径"])
async def root() -> dict:
    """根路径"""
    return success({
        "message": "Daily Report Service API",
        "docs": "/docs",
        "health": "/health",
    })


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "local",
        log_level=settings.log_level.lower(),
    )
