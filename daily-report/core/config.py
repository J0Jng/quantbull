from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Daily Report 服务配置"""
    env: str = "local"
    log_level: str = "INFO"
    
    # 服务端口
    port: int = 8004
    host: str = "0.0.0.0"
    
    # 数据库配置
    db_type: str = "sqlite"  # postgresql / sqlite / memory
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "quantbull"
    sqlite_path: str = "daily_report.db"  # SQLite 数据库文件路径（相对路径或绝对路径）
    
    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    
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
