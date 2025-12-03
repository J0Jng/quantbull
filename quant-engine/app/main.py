"""
Quant Engine - Main Application Entry Point.

This module initializes the FastAPI application and sets up all routes,
middleware, and startup/shutdown events.
"""
from datetime import datetime
from typing import Any, Dict, Optional

import redis
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.config import settings
from app.utils.logger import logger

# Initialize FastAPI app
app = FastAPI(
    title="QuantBull Quant Engine",
    version=settings.service_version,
    description="Quantitative trading strategy engine and backtesting service for QuantBull platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Global connection objects (initialized on startup)
redis_client: Optional[redis.Redis] = None
postgres_engine: Optional[Engine] = None


@app.on_event("startup")
async def startup_event() -> None:
    """
    Initialize connections and resources on application startup.
    """
    global redis_client, postgres_engine
    
    logger.info(f"Starting {settings.service_name} v{settings.service_version}")
    
    try:
        # Initialize Redis connection
        redis_client = redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
        )
        redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}")
        redis_client = None
    
    try:
        # Initialize PostgreSQL connection
        postgres_engine = create_engine(
            settings.postgres_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
        # Test connection
        with postgres_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("PostgreSQL connection established")
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed: {e}")
        postgres_engine = None


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """
    Clean up resources on application shutdown.
    """
    logger.info("Shutting down quant engine")
    
    global redis_client, postgres_engine
    
    if redis_client:
        redis_client.close()
        logger.info("Redis connection closed")
    
    if postgres_engine:
        postgres_engine.dispose()
        logger.info("PostgreSQL connection closed")


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Health status dictionary
    """
    return {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.service_version,
    }


@app.get("/status", status_code=status.HTTP_200_OK)
async def status_check() -> JSONResponse:
    """
    Detailed status check endpoint with dependency health.
    
    Checks the health of:
    - Redis connection
    - PostgreSQL connection
    - Data service connectivity
    
    Returns:
        Detailed status JSON response
    """
    global redis_client, postgres_engine
    
    status_info: Dict[str, Any] = {
        "service": settings.service_name,
        "version": settings.service_version,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "status": "healthy",
        "dependencies": {},
    }
    
    # Check Redis
    redis_status = {"status": "unknown", "error": None}
    if redis_client:
        try:
            redis_client.ping()
            redis_status["status"] = "healthy"
        except Exception as e:
            redis_status["status"] = "unhealthy"
            redis_status["error"] = str(e)
            status_info["status"] = "degraded"
    else:
        redis_status["status"] = "not_configured"
    
    status_info["dependencies"]["redis"] = redis_status
    
    # Check PostgreSQL
    postgres_status = {"status": "unknown", "error": None}
    if postgres_engine:
        try:
            with postgres_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            postgres_status["status"] = "healthy"
        except Exception as e:
            postgres_status["status"] = "unhealthy"
            postgres_status["error"] = str(e)
            status_info["status"] = "degraded"
    else:
        postgres_status["status"] = "not_configured"
    
    status_info["dependencies"]["postgresql"] = postgres_status
    
    # Check Data Service connectivity
    data_service_status = {"status": "unknown", "error": None}
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.data_service_url}/health")
            if response.status_code == 200:
                data_service_status["status"] = "healthy"
            else:
                data_service_status["status"] = "unhealthy"
    except ImportError:
        data_service_status["status"] = "not_configured"
        data_service_status["error"] = "httpx not installed"
    except Exception as e:
        data_service_status["status"] = "unhealthy"
        data_service_status["error"] = str(e)
        status_info["status"] = "degraded"
    
    status_info["dependencies"]["data_service"] = data_service_status
    
    # Determine overall HTTP status code
    http_status = status.HTTP_200_OK
    if status_info["status"] == "degraded":
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        content=status_info,
        status_code=http_status,
    )


@app.get("/")
async def root() -> Dict[str, str]:
    """
    Root endpoint providing service information.
    
    Returns:
        Service information dictionary
    """
    return {
        "service": settings.service_name,
        "version": settings.service_version,
        "description": "Quantitative trading strategy engine and backtesting service",
        "docs": "/docs",
        "status": "/status",
    }
