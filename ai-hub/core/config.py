from functools import lru_cache
from pathlib import Path
import os

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_env_file() -> str | None:
    """Find the most appropriate .env file.

    Priority:
    1) Explicit AI_HUB_ENV_FILE
    2) Nearest parent that contains docker-compose.yml and has a .env
    3) Local ai-hub/.env (backwards compatibility)
    """
    explicit = (os.getenv("AI_HUB_ENV_FILE") or "").strip()
    if explicit:
        return explicit

    here = Path(__file__).resolve()

    for parent in [here.parent, *here.parents]:
        compose = parent / "docker-compose.yml"
        if compose.exists():
            candidate = parent / ".env"
            return str(candidate) if candidate.exists() else None

    local_candidate = here.parents[1] / ".env"  # ai-hub/.env
    return str(local_candidate) if local_candidate.exists() else None


class Settings(BaseSettings):
    """AI Hub 服务配置"""
    env: str = Field(default="local", validation_alias=AliasChoices("AI_HUB_ENV", "ENV"))
    log_level: str = Field(default="INFO", validation_alias=AliasChoices("AI_HUB_LOG_LEVEL", "LOG_LEVEL"))
    
    # 服务端口
    port: int = Field(default=8002, validation_alias=AliasChoices("AI_HUB_PORT", "PORT", "SERVICE_PORT"))
    host: str = Field(default="0.0.0.0", validation_alias=AliasChoices("AI_HUB_HOST", "HOST"))
    
    # DeepSeek R1 API 配置（偏文本生成、新闻、逻辑推理）
    # 默认使用阿里云 DashScope 的 OpenAI 兼容接口
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    deepseek_model: str = "deepseek-chat"  # 或 "deepseek-r1" 根据实际模型名称调整
    deepseek_max_concurrency: int = 5
    deepseek_rpm: int = 60
    
    # 通义千问 Qwen2.5 API 配置（偏结构化输出、代码生成、投研摘要）
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-turbo"  # 或 "qwen2.5-7b-chat" 根据实际模型名称调整
    qwen_max_concurrency: int = 3
    qwen_rpm: int = 60
    
    # OpenAI 兼容配置（用于其他模型）
    openai_api_key: str = ""
    openai_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 数字人服务配置（示例）
    digital_human_api_url: str = ""
    digital_human_api_key: str = ""
    
    # Data Service 配置
    data_service_url: str = "http://data-service:8001"
    
    # User Service 配置（用于 AI Token 扣减）
    user_service_url: str = "http://user-service:8005"

    # 内部服务调用白名单（逗号分隔）
    # 允许这些服务在调用 /api/ai/chat 时跳过用户 Bearer 鉴权
    internal_chat_allowed_services: str = "daily-report"
    
    # 模型路由配置
    default_model: str = "deepseek"  # deepseek, qwen
    max_tokens: int = 4096
    temperature: float = 0.7
    
    # 默认模型映射（任务类型 -> 模型）
    default_model_for_news: str = "deepseek"  # 新闻生成默认使用 DeepSeek
    default_model_for_summary: str = "qwen"    # 摘要生成默认使用 Qwen
    default_model_for_strategy: str = "deepseek"   # 策略生成默认使用 DeepSeek
    
    # 限流配置
    rate_limit_per_minute: int = 30
    rate_limit_per_hour: int = 500
    
    # 超时配置（秒）- AI 生成需要较长时间
    request_timeout: int = 180
    
    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def _validate_secrets(self):
        if (self.env or "").lower() != "local":
            missing = []
            if not self.deepseek_api_key:
                missing.append("DEEPSEEK_API_KEY")
            if not self.qwen_api_key:
                missing.append("QWEN_API_KEY")
            if not self.openai_api_key:
                missing.append("OPENAI_API_KEY")
            if missing:
                raise ValueError(f"Missing required secrets for non-local env: {', '.join(missing)}")
        return self

    def get_internal_chat_allowed_services(self) -> set[str]:
        """返回允许免用户鉴权访问聊天接口的内部服务集合。"""
        raw = (self.internal_chat_allowed_services or "").strip()
        if not raw:
            return set()
        return {
            item.strip().lower()
            for item in raw.split(",")
            if item and item.strip()
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
