from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import settings
from core.logger import configure_logging
from middlewares import AuthMiddleware, LoggingMiddleware, RateLimitMiddleware
from routers import proxy
import uvicorn
import os
import json
from core.handlers import http_exception_handler, validation_exception_handler, generic_exception_handler, envelope_middleware
from core.response import success

def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    configure_logging(settings)
    
    app = FastAPI(
        title="API Gateway",
        description="量化牛牛统一 API 网关",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
        {
            "name": "health",
            "description": "健康检查相关接口"
        },
        {
            "name": "auth",
            "description": "认证相关接口"
        },
        {
            "name": "quant",
            "description": "量化分析相关接口"
        }
        ]
    )
    
    # 添加中间件（注意顺序：后添加的先执行）
    # 1. CORS 中间件（最外层）
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境应限制具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 2. 限流中间件
    app.add_middleware(RateLimitMiddleware)
    
    # 3. 日志中间件
    app.add_middleware(LoggingMiddleware)
    
    # 4. 鉴权中间件（最内层，最后执行）
    app.add_middleware(AuthMiddleware)
    
    # 注册代理路由（统一转发）
    app.include_router(proxy.router)

    # 全局异常处理与响应封装中间件
    from fastapi.exceptions import HTTPException as StarletteHTTPException, RequestValidationError
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    app.middleware("http")(envelope_middleware)

    # 如果存在合并后的 openapi 文件（由 CI 生成），在启动时加载并覆盖 app.openapi
    # 便于在生产/测试环境直接使用统一文档
    import os
    unified_path = os.getenv("UNIFIED_OPENAPI_PATH", "./unified-openapi.json")
    if os.path.exists(unified_path):
        try:
            with open(unified_path, "r", encoding="utf-8") as f:
                merged = json.load(f)

            def _openapi_override():
                return merged

            app.openapi = _openapi_override
        except Exception:
            # 保持原有行为，如果加载失败则使用自动生成的 openapi
            pass
    
    return app


app = create_app()


@app.get("/")
async def root() -> dict:
    """根路径"""
    return success({
        "service": "api-gateway",
        "version": "1.0.0",
        "status": "running",
        "port": settings.port,
        "docs": "/docs"
    })


@app.get("/health")
async def health_check() -> dict:
    """健康检查（不需要鉴权）"""
    return success({
        "status": "ok",
        "service": "api-gateway",
        "env": settings.env,
        "port": settings.port
    }
    )