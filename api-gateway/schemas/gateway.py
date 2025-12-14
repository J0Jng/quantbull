from typing import Any, Optional

from pydantic import BaseModel


class ServiceHealth(BaseModel):
    """服务健康状态"""
    service_name: str
    status: str
    url: str
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


class GatewayResponse(BaseModel):
    """网关统一响应格式"""
    success: bool = True
    message: str = "ok"
    data: Optional[Any] = None
    timestamp: Optional[str] = None
