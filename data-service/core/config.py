from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    env: str = "local"
    log_level: str = "INFO"
    
    # 数据库配置
    database_url: str = "postgresql+asyncpg://quantbull:change_me@postgres:5432/quantbull_db"
    sync_database_url: str = "postgresql+psycopg2://quantbull:change_me@postgres:5432/quantbull_db"
    # Tushare 配置
    tushare_token: str = "ced0595b8c1603011a2fd4bee5e8cca551ce661fdf779a7bda47e66c"  # set via env TUSHARE_TOKEN when available
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

