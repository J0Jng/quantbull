import pytest
from services.auth_service import AuthService
from services.proxy_service import ProxyService
from schemas.auth import TokenData


class TestAuthService:
    """认证服务测试"""
    
    def test_create_access_token(self):
        """测试创建访问令牌"""
        token = AuthService.create_access_token(data={"sub": "test_user", "user_id": 1})
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token_success(self):
        """测试验证令牌成功"""
        token = AuthService.create_access_token(data={"sub": "test_user", "user_id": 1})
        token_data = AuthService.verify_token(token)
        assert token_data is not None
        assert isinstance(token_data, TokenData)
        assert token_data.username == "test_user"
        assert token_data.user_id == 1
    
    def test_verify_token_invalid(self):
        """测试验证无效令牌"""
        token_data = AuthService.verify_token("invalid_token")
        assert token_data is None
    
    def test_authenticate_user_success(self):
        """测试用户认证成功"""
        result = AuthService.authenticate_user("admin", "admin123")
        assert result is True
    
    def test_authenticate_user_failure(self):
        """测试用户认证失败"""
        result = AuthService.authenticate_user("admin", "wrong_password")
        assert result is False


class TestProxyService:
    """代理服务测试"""
    
    def test_service_urls_configured(self):
        """测试服务 URL 配置"""
        assert "data-service" in ProxyService.SERVICE_URLS
        assert "ai-hub" in ProxyService.SERVICE_URLS
        assert "quant-engine" in ProxyService.SERVICE_URLS
        assert "daily-report" in ProxyService.SERVICE_URLS
        assert "user-service" in ProxyService.SERVICE_URLS
    
    @pytest.mark.asyncio
    async def test_check_service_health(self):
        """测试服务健康检查"""
        health = await ProxyService.check_service_health("data-service")
        assert health.service_name == "data-service"
        assert health.status in ["healthy", "unhealthy", "unknown"]
        assert health.url is not None
