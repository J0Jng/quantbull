from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for user-service."""

    env: str = "local"
    host: str = "0.0.0.0"
    port: int = 8005

    # Database
    database_url: str = "sqlite:///./user.db"

    # CORS 配置（生产环境应配置白名单）
    cors_allow_origins: list[str] = []
    cors_allow_credentials: bool = False

    # 可信代理（用于登录/注册限流真实 IP）
    trusted_proxies: list[str] = []

    # Seed admin
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # AI Token 配置
    default_ai_tokens: int = 3000

    # JWT 配置
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 120

    # Investor ID hash salt
    investor_id_salt: str = "investor-salt"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def _validate_security(self):
        env = (self.env or "local").lower()
        if env != "local":
            if not self.cors_allow_origins:
                raise ValueError("CORS_ALLOW_ORIGINS is required in non-local env")
            if "*" in self.cors_allow_origins:
                raise ValueError("CORS_ALLOW_ORIGINS must be a whitelist in non-local env")
            if self.admin_password in {"admin123", "", None}:
                raise ValueError("ADMIN_PASSWORD must be set to a strong value in non-local env")
            if self.jwt_secret_key in {"change-this-in-production", "", None}:
                raise ValueError("JWT_SECRET_KEY must be set in non-local env")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
