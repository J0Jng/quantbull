import json
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logger import configure_logging, get_logger
from routers import api_router
from core.handlers import http_exception_handler, validation_exception_handler, generic_exception_handler
from core.response import success
from db import init_db, get_session
from models import backtest_record  # ensure models are imported for SQLModel metadata
from models.factor import Factor
from services.indicator_engine import BUILTIN_INDICATORS

logger = get_logger(__name__)


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


async def seed_builtin_factors():
    """
    初始化内设因子
    
    在启动时将 BUILTIN_INDICATORS 中定义的内设因子写入数据库。
    如果因子已存在（按 name 匹配），则跳过。
    """
    try:
        with get_session() as session:
            for indicator in BUILTIN_INDICATORS:
                # 检查是否已存在
                from sqlmodel import select
                stmt = select(Factor).where(Factor.name == indicator["name"])
                existing = session.exec(stmt).first()
                
                if existing:
                    continue
                
                # 创建新因子
                factor = Factor(
                    id=f"builtin_{indicator['name']}",
                    name=indicator["name"],
                    description=indicator.get("description", ""),
                    expression=indicator["expression"],
                    data_source="price",
                    category=indicator.get("category", "technical"),
                    formula=indicator["expression"],
                    parameters={},
                )
                session.add(factor)
            
            session.commit()
            logger.info(f"内设因子初始化完成，共 {len(BUILTIN_INDICATORS)} 个因子")
    except Exception as e:
        logger.error(f"内设因子初始化失败: {e}")
        # 不抛出异常，允许服务继续启动


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    configure_logging(settings)
    
    app = FastAPI(
        title="Quant Engine",
        description="量化牛牛 量化引擎 - 回测、因子库、策略执行",
        version="0.1.0"
    )

    @app.on_event("startup")
    async def _startup():
        init_db()
        # 初始化内设因子
        await seed_builtin_factors()
    
    # CORS 中间件（生产必须显式白名单；local 才允许 *）
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

    # 全局异常处理，保证所有异常响应都符合统一 envelope
    app.add_exception_handler(Exception, generic_exception_handler)
    from fastapi.exceptions import HTTPException as StarletteHTTPException, RequestValidationError
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # 注册根路径和健康检查
    @app.get("/")
    async def root() -> dict:
        """根路径"""
        return success({
            "service": "quant-engine",
            "version": "0.1.0",
            "status": "running",
            "docs": "/docs",
            "description": "量化引擎 - 回测、因子库、策略执行"
        })
    
    @app.get("/health")
    async def health_check() -> dict:
        """健康检查"""
        return success({
            "status": "ok",
            "service": "quant-engine",
            "env": settings.env
        })
    
    return app


app = create_app()
