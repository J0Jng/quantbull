from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logger import configure_logging
from routers import api_router
from core.handlers import http_exception_handler, validation_exception_handler, generic_exception_handler
from core.response import success


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    configure_logging(settings)
    
    app = FastAPI(
        title="Quant Engine",
        description="量化牛牛 量化引擎 - 回测、因子库、策略执行",
        version="0.1.0"
    )
    
    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应限制具体域名
        allow_credentials=True,
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
