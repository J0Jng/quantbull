from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logger import configure_logging, get_logger
from routers import api_router
from scheduler import create_scheduler, start_scheduler, shutdown_scheduler
from db.session import init_db

# 配置日志
configure_logging(settings)
logger = get_logger(__name__)


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
    try:
        scheduler = create_scheduler()
        start_scheduler()
        logger.info("定时任务调度器已启动")
    except Exception as e:
        logger.error(f"调度器启动失败: {e}", exc_info=True)
        # 开发环境允许继续运行
        if settings.env != "local":
            raise
    
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
    
    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应配置具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(api_router, prefix="/api")
    
    return app


app = create_app()


@app.get("/health", tags=["健康检查"])
async def health_check() -> dict:
    """健康检查接口"""
    return {
        "status": "ok",
        "service": "daily-report",
        "version": "1.0.0",
        "env": settings.env,
    }


@app.get("/", tags=["根路径"])
async def root() -> dict:
    """根路径"""
    return {
        "message": "Daily Report Service API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "local",
        log_level=settings.log_level.lower(),
    )
