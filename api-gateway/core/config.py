from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API Gateway 配置"""
    env: str = "local"
    log_level: str = "INFO"
    
    # 服务端口
    port: int = 8001
    host: str = "0.0.0.0"
    
    # 微服务地址配置（Docker 环境使用服务名，本地使用 localhost）
    ai_hub_url: str = "http://ai-hub:8002"  # /news/* 转发到这里
    data_service_url: str = "http://data-service:8000"  # /data/* 转发到这里
    quant_engine_url: str = "http://quant-engine:8003"  # /quant/* 转发到这里
    daily_report_url: str = "http://daily-report:8004"  # /report/* 转发到这里
    
    # 路由映射配置
    route_mapping: dict = {
        "/news": "ai_hub_url",
        "/data": "data_service_url",
        "/quant": "quant_engine_url",
        "/report": "daily_report_url",
    }
    
    # 鉴权配置
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 30
    
    # 限流配置
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # 代理配置
    proxy_timeout: float = 5.0  # 下游请求超时时间（秒）
    proxy_max_retries: int = 2  # 最大重试次数
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    def get_service_url(self, route_prefix: str) -> str:
        """根据路由前缀获取服务地址"""
        service_key = self.route_mapping.get(route_prefix)
        if not service_key:
            raise ValueError(f"未知的路由前缀: {route_prefix}")
        return getattr(self, service_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
