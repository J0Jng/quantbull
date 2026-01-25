from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Daily Report 服务配置"""
    env: str = "local"
    log_level: str = "INFO"
    
    # 服务端口
    port: int = 8004
    host: str = "0.0.0.0"
    
    # 外部服务地址（Docker 网络中使用服务名）
    # 优先使用 DATA_SERVICE_URL 完整地址（docker-compose 提供）
    data_service_url: str = ""  # 例如: http://data-service:8001
    data_service_host: str = "data-service"
    data_service_port: int = 8001  # 修正：与 docker-compose 一致
    ai_hub_host: str = "ai-hub"
    ai_hub_port: int = 8002
    
    # 数据库配置
    db_type: str = "sqlite"  # postgresql / sqlite / memory
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "quantbull"
    postgres_schema: str = "public"
    sqlite_path: str = "daily_report.db"  # SQLite 数据库文件路径（相对路径或绝对路径）
    
    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""

    # 东方财富研报配置
    eastmoney_report_base_url: str = "https://data.eastmoney.com/report"
    eastmoney_report_timeout: float = 20.0
    eastmoney_report_retries: int = 2
    eastmoney_report_rate_limit_rps: int = 25
    eastmoney_report_cache_enabled: bool = True
    eastmoney_report_cache_ttl: int = 30900  # 515 分钟
    
    # 日报配置
    report_cache_ttl: int = 3600  # 日报缓存时间（秒）
    default_timezone: str = "Asia/Shanghai"  # 默认时区
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
