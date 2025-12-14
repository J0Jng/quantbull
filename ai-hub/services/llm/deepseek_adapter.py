import httpx
from typing import Optional

from core.config import settings
from core.logger import get_logger
from services.llm.base import LLMAdapter, LLMResponse

logger = get_logger(__name__)


class DeepSeekAdapter(LLMAdapter):
    """DeepSeek R1 适配器
    
    特点：偏文本生成、新闻、逻辑推理
    """
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url
        self.model = settings.deepseek_model
        self.timeout = settings.request_timeout
    
    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """调用 DeepSeek R1 API"""
        if not self.is_available():
            raise ValueError("DeepSeek API Key 未配置")
        
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or settings.temperature,
            "max_tokens": max_tokens or settings.max_tokens,
        }
        
        # 支持 DeepSeek R1 特定参数
        if "reasoning" in kwargs:
            payload["reasoning"] = kwargs["reasoning"]
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                return LLMResponse(
                    content=data["choices"][0]["message"]["content"],
                    model="deepseek",
                    tokens_used=data.get("usage", {}).get("total_tokens"),
                    finish_reason=data["choices"][0].get("finish_reason"),
                )
        except httpx.HTTPStatusError as e:
            logger.error(f"DeepSeek API 调用失败: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"DeepSeek API 调用异常: {e}", exc_info=True)
            raise
    
    def get_model_name(self) -> str:
        return "deepseek"
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())
