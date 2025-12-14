import pytest
from fastapi.testclient import TestClient


def test_gateway_health(client: TestClient):
    """测试网关健康检查"""
    response = client.get("/api/gateway/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "api-gateway"


def test_services_health_check(client: TestClient):
    """测试所有服务健康状态检查"""
    response = client.get("/api/gateway/services/health")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # 应该包含所有服务的健康状态
    service_names = [item["service_name"] for item in data]
    assert "data-service" in service_names
    assert "ai-hub" in service_names
    assert "quant-engine" in service_names
    assert "daily-report" in service_names
    assert "user-service" in service_names
    
    # 检查每个服务都有必要的字段
    for service in data:
        assert "service_name" in service
        assert "status" in service
        assert "url" in service
