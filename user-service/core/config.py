from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for user-service."""

    env: str = "local"
    host: str = "0.0.0.0"
    port: int = 8005

    # Database
    database_url: str = "sqlite:///./user.db"

    # JWT
    jwt_secret: str = "change-me-in-prod"
    jwt_algorithm: str = "HS256"
    access_token_expire_seconds: int = 3600

    # Seed admin
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # AI Token 配置
    default_ai_tokens: int = 1000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
