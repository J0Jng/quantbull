from typing import List

from fastapi import APIRouter

from schemas.gateway import ServiceHealth
from services.proxy_service import ProxyService

router = APIRouter()


@router.get("/health", response_model=dict)
async def gateway_health() -> dict:
    """网关健康检查"""
    return {
        "status": "ok",
        "service": "api-gateway",
        "version": "0.1.0"
    }


@router.get("/services/health", response_model=List[ServiceHealth])
async def check_all_services() -> List[ServiceHealth]:
    """检查所有微服务的健康状态"""
    services = [
        "data-service",
        "ai-hub",
        "quant-engine",
        "daily-report",
        "task-service",
        "user-service"
    ]
    
    health_checks = []
    for service_name in services:
        health = await ProxyService.check_service_health(service_name)
        health_checks.append(health)
    
    return health_checks
