from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AI Hub 服务配置"""
    env: str = "local"
    log_level: str = "INFO"
    
    # 服务端口
    port: int = 8002
    host: str = "0.0.0.0"
    
    # DeepSeek R1 API 配置（偏文本生成、新闻、逻辑推理）
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
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
    openai_api_key: str = "sk-d0a22a6a95534cb4b168e2e8e020d1fd"
    openai_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 数字人服务配置（示例）
    digital_human_api_url: str = ""
    digital_human_api_key: str = ""
    
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
    
    # 超时配置
    request_timeout: int = 60
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
