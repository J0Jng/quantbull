import time
from typing import Optional

import httpx
from core.config import settings
from core.logger import get_logger
from schemas.gateway import ServiceHealth

logger = get_logger(__name__)


class ProxyService:
    """代理服务 - 转发请求到各个微服务"""
    
    SERVICE_URLS = {
        "data-service": settings.data_service_url,
        "ai-hub": settings.ai_hub_url,
        "quant-engine": settings.quant_engine_url,
        "daily-report": settings.daily_report_url,
        "user-service": settings.user_service_url,
    }
    
    @classmethod
    async def check_service_health(cls, service_name: str) -> ServiceHealth:
        """检查服务健康状态"""
        url = cls.SERVICE_URLS.get(service_name)
        if not url:
            return ServiceHealth(
                service_name=service_name,
                status="unknown",
                url="",
                error=f"Service {service_name} not configured"
            )
        
        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{url}/health")
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    return ServiceHealth(
                        service_name=service_name,
                        status="healthy",
                        url=url,
                        response_time_ms=response_time
                    )
                else:
                    return ServiceHealth(
                        service_name=service_name,
                        status="unhealthy",
                        url=url,
                        response_time_ms=response_time,
                        error=f"HTTP {response.status_code}"
                    )
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Health check failed for {service_name}: {e}")
            return ServiceHealth(
                service_name=service_name,
                status="unhealthy",
                url=url,
                response_time_ms=response_time,
                error=str(e)
            )
    
    @classmethod
    async def proxy_request(
        cls,
        service_name: str,
        method: str,
        path: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None
    ) -> httpx.Response:
        """代理请求到指定服务"""
        base_url = cls.SERVICE_URLS.get(service_name)
        if not base_url:
            raise ValueError(f"Service {service_name} not configured")
        
        url = f"{base_url}{path}"
        logger.info(f"Proxying {method} {url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data
            )
            return response
