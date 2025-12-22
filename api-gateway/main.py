from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import settings
from core.logger import configure_logging
from middlewares import AuthMiddleware, LoggingMiddleware, RateLimitMiddleware
from routers import proxy, auth, gateway
import uvicorn
import os
import json
from core.handlers import http_exception_handler, validation_exception_handler, generic_exception_handler, envelope_middleware
from core.response import success
from core.openapi_aggregator import OpenAPIAggregator


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
        openapi_version="3.0.0",
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
    
    # 加载服务配置并创建 OpenAPI 聚合器
    services_config_path = os.path.join(os.path.dirname(__file__), "services.json")
    services_config = []
    if os.path.exists(services_config_path):
        try:
            with open(services_config_path, "r", encoding="utf-8") as f:
                services_config = json.load(f)
        except Exception as e:
            app.logger.warning(f"Failed to load services config: {e}")
    
    aggregator = OpenAPIAggregator(services_config)
    
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
    
    # 全局异常处理与响应封装中间件
    from fastapi.exceptions import HTTPException as StarletteHTTPException, RequestValidationError
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    app.middleware("http")(envelope_middleware)
    
    # 应用启动事件：执行 OpenAPI 聚合
    @app.on_event("startup")
    async def startup_event():
        await aggregator.aggregate()
    
    # 自定义 OpenAPI 生成器
    def custom_openapi():
        if aggregator.get_aggregated_openapi():
            return aggregator.get_aggregated_openapi()
        # 降级到默认行为
        return app.openapi_schema
    
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

# 2. 认证路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])

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