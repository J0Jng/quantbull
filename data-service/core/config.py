from functools import lru_cache
import logging

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    env: str = "local"
    log_level: str = "INFO"
    
    # 数据库配置
    database_url: str = ""
    sync_database_url: str = ""
    
    # Tushare 配置 - 优先读取环境变量 TUSHARE_TOKEN
    tushare_token: str = ""  # 通过环境变量设置，不应在代码中硬编码

    # 内部刷新接口 Token（可选）
    finance_channel_refresh_token: str = ""

    # 视频中心配置
    video_upload_dir: str = "static/videos"
    video_cover_dir: str = "static/video_covers"
    video_max_size_mb: int = 200
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)
    
    def validate_tushare_token(self) -> None:
        """验证 Tushare Token 是否已配置"""
        if not self.tushare_token or self.tushare_token == "":
            error_msg = (
                "TUSHARE_TOKEN 未配置！请通过以下方式之一设置：\n"
                "1. 环境变量：export TUSHARE_TOKEN='your_token_here'\n"
                "2. .env 文件：TUSHARE_TOKEN=your_token_here\n"
                "获取 Token：https://tushare.pro/register"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

