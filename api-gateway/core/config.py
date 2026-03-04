from functools import lru_cache

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API Gateway 配置"""
    env: str = "local"
    log_level: str = "INFO"
    
    # 服务端口
    port: int = 8000
    host: str = "0.0.0.0"
    
    # 微服务地址配置（Docker 环境使用服务名，本地使用 localhost）
    ai_hub_url: str = "http://ai-hub:8002"  # /ai/* 转发到这里
    data_service_url: str = "http://data-service:8001"  # /data/* 转发到这里
    quant_engine_url: str = "http://quant-engine:8003"  # /quant/* 转发到这里
    daily_report_url: str = "http://daily-report:8004"  # /report/* 转发到这里
    user_service_url: str = Field(
        default="http://user-service:8005",
        validation_alias=AliasChoices(
            "USER_SERVICE_BASE_URL",
            "USER_SERVICE_URL",
            "user_service_url",
        ),
        description="User service base URL (Docker: http://user-service:8005)",
    )
    user_service_timeout: float = 5.0
    task_service_url: str = "http://task-service:9000"
    
    # 路由映射配置（键为网关暴露的一级路径，值为目标服务 URL 配置名）
    # 注意：使用下游真实的首段路径，避免重复前缀导致 404。
    route_mapping: dict = {
        # ai-hub
        "/ai": "ai_hub_url",

        # data-service（包含所有首段）
        "/data": "data_service_url",
        "/quotes": "data_service_url",
        "/tushare": "data_service_url",
        "/market": "data_service_url",
        "/etf": "data_service_url",
        "/stock": "data_service_url",
        "/fundamentals": "data_service_url",
        "/news": "data_service_url",  # 新增：微博财经媒体新闻
        "/finance-channel": "data_service_url",  # 新增：财经频道聚合
        "/videos": "data_service_url",  # 新增：视频中心
        "/static": "data_service_url",  # 静态资源（视频/封面）
        "/fundflow": "data_service_url",  # 新增：资金流向
        "/financial-report": "data_service_url",  # 新增：财报数据
        "/lhb": "data_service_url",  # 新增：龙虎榜数据
        "/profit-forecast": "data_service_url",  # 新增：盈利预测

        # funds
        "/funds": "data_service_url",

        # quant-engine（下游首段：backtest/strategy/factor）
        "/backtest": "quant_engine_url",
        "/strategy": "quant_engine_url",
        "/factor": "quant_engine_url",

        # daily-report
        "/report": "daily_report_url",
        "/daily-report": "daily_report_url",
        "/company-research": "daily_report_url",

        # task-service
        "/tasks": "task_service_url",

        # user-service
        "/auth": "user_service_url",
        "/admin": "user_service_url",
        "/tokens": "user_service_url",
        "/products": "user_service_url",
        "/investor": "user_service_url",
    }
    
    # 认证 Cookie 配置
    auth_cookie_name: str = "quantbull_access"
    csrf_cookie_name: str = "quantbull_csrf"
    cookie_secure: bool = True
    cookie_samesite: str = "Lax"
    cookie_domain: str | None = None

    # CORS 配置（生产环境应配置白名单）
    cors_allow_origins: list[str] = []
    cors_allow_credentials: bool = False
    
    # 限流配置
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # 可信代理（仅当请求来自这些 IP 时才读取 X-Forwarded-For）
    trusted_proxies: list[str] = []
    
    # 代理配置
    proxy_timeout: float = 200.0  # 下游请求超时时间（秒）
    proxy_max_retries: int = 2  # 最大重试次数
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # 忽略未定义的环境变量，避免 Pydantic 验证错误
    )

    @model_validator(mode="after")
    def _validate_security(self):
        env = (self.env or "local").lower()
        if env != "local":
            if not self.cors_allow_origins:
                raise ValueError("CORS_ALLOW_ORIGINS is required in non-local env")
            if "*" in self.cors_allow_origins:
                raise ValueError("CORS_ALLOW_ORIGINS must be a whitelist in non-local env")
        return self
    
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
