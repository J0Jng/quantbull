from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.logger import configure_logging
from middlewares import AuthMiddleware, LoggingMiddleware, RateLimitMiddleware
from routers import proxy

def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    configure_logging(settings)
    
    app = FastAPI(
        title="API Gateway",
        description="量化牛牛统一 API 网关",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
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
    
    return app


app = create_app()


@app.get("/")
async def root() -> dict:
    """根路径"""
    return {
        "service": "api-gateway",
        "version": "1.0.0",
        "status": "running",
        "port": settings.port,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check() -> dict:
    """健康检查（不需要鉴权）"""
    return {
        "status": "ok",
        "service": "api-gateway",
        "env": settings.env,
        "port": settings.port
    }
