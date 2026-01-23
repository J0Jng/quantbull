import json
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logger import configure_logging
from routers import api_router
from core.handlers import http_exception_handler, validation_exception_handler, generic_exception_handler, envelope_middleware
from core.response import success
from services.llm.llm_factory import LLMFactory


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
    """创建 FastAPI 应用"""
    configure_logging(settings)

    # 如果所有模型都不可用，启动直接失败，避免“假在线”
    LLMFactory.ensure_any_available()
    
    app = FastAPI(
        title="AI Hub",
        description="量化牛牛 AI 能力中台 - LLM 网关、文本生成、视频合成",
        version="0.1.0"
    )
    
    # CORS 中间件
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

    # 注册全局异常处理与响应封装中间件
    from fastapi.exceptions import HTTPException as StarletteHTTPException, RequestValidationError
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    app.middleware("http")(envelope_middleware)
    
    return app


app = create_app()


@app.get("/")
async def root() -> dict:
    """根路径"""
    return success({
        "service": "ai-hub",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "description": "AI 能力中台 - LLM 网关、文本生成、视频合成"
    })


@app.get("/health")
async def health_check() -> dict:
    """健康检查"""
    return success({
        "status": "ok",
        "service": "ai-hub",
        "env": settings.env
    })
