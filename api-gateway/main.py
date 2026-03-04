from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.handlers import generic_exception_handler, http_exception_handler, envelope_middleware, validation_exception_handler
from core.logger import configure_logging
from core.openapi_aggregator import OpenAPIAggregator, load_service_configs
from core.response import success
from middlewares import CsrfMiddleware, LoggingMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware
from routers import gateway, proxy, admin
import uvicorn


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    configure_logging(settings)
    
    app = FastAPI(
        title="API Gateway",
        description="脑科学研究室统一 API 网关",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_version="3.0.0",
        openapi_tags=[
            {
                "name": "health",
                "description": "健康检查相关接口"
            },
            {
                "name": "admin",
                "description": "管理员相关接口（用户管理）"
            },
            {
                "name": "quant",
                "description": "量化分析相关接口"
            }
        ]
    )
    
    # 加载服务配置并创建 OpenAPI 聚合器
    services_config_path = Path(__file__).resolve().parent / "services.yaml"
    services = load_service_configs(services_config_path)
    aggregator = OpenAPIAggregator(app, services)
    
    # 添加中间件（注意顺序：后添加的先执行）
    # 1. CORS 中间件（最外层）
    cors_allow_origins = ["*"] if settings.env == "local" else settings.cors_allow_origins
    cors_allow_credentials = True if settings.env == "local" else settings.cors_allow_credentials
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_allow_origins,
        allow_credentials=cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 2. 安全响应头中间件
    app.add_middleware(SecurityHeadersMiddleware)

    # 3. CSRF 中间件
    app.add_middleware(CsrfMiddleware)

    # 4. 限流中间件
    app.add_middleware(RateLimitMiddleware)

    # 5. 日志中间件
    app.add_middleware(LoggingMiddleware)

    # 全局异常处理与响应封装中间件
    from fastapi.exceptions import HTTPException as StarletteHTTPException, RequestValidationError
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    app.middleware("http")(envelope_middleware)
    
    # 应用启动事件：执行 OpenAPI 聚合
    @app.on_event("startup")
    async def startup_event():
        aggregated = await aggregator.aggregate()
        app.openapi_schema = aggregated
    
    # 自定义 OpenAPI 生成器
    def custom_openapi() -> Dict[str, Any]:
        aggregated = aggregator.get_aggregated_openapi()
        if aggregated is not None:
            return aggregated
        if app.openapi_schema is not None:
            return app.openapi_schema
        # 降级到空字典以满足类型要求
        return {}
    
    app.openapi = custom_openapi
    
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
    })


# 注册其他路由 - 注意顺序：先注册网关自身的路由，最后注册代理路由
# 1. 网关管理路由
app.include_router(gateway.router, prefix="/api/gateway", tags=["网关管理"])

# 2. 管理员路由
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# 3. 代理路由（最后注册，最低优先级）
app.include_router(proxy.router, prefix="/api", tags=["代理"])


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    """自定义 404 错误处理"""
    return JSONResponse(
        status_code=404,
        content={
            "code": 404,
            "message": f"路径 {request.url.path} 不存在。请检查路径或查看 /docs 获取API文档",
            "data": None
        }
    )