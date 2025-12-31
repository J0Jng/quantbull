import httpx
from typing import Optional

from core.config import settings
from core.logger import get_logger
from services.llm.base import BaseLLMClient, LLMResult

logger = get_logger(__name__)


class QwenAdapter(BaseLLMClient):
    """通义千问 Qwen2.5 适配器
    
    特点：偏结构化输出、代码生成、投研摘要
    """

    def __init__(self):
        super().__init__(
            model_name="qwen",
            rpm=settings.qwen_rpm,
            max_concurrency=settings.qwen_max_concurrency,
        )
        self.api_key = settings.qwen_api_key
        self.base_url = settings.qwen_base_url
        self.model = settings.qwen_model
        self.timeout = settings.request_timeout

    async def _chat(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResult:
        if not self.is_available():
            raise ValueError("通义千问 API Key 未配置")

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

        if "response_format" in kwargs:
            payload["response_format"] = kwargs["response_format"]

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            usage = data.get("usage", {}) or {}
            prompt_tokens = usage.get("prompt_tokens") or 0
            completion_tokens = usage.get("completion_tokens") or 0
            total_tokens = usage.get("total_tokens") or prompt_tokens + completion_tokens

            return LLMResult(
                content=data["choices"][0]["message"]["content"],
                model=self.model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                finish_reason=data["choices"][0].get("finish_reason"),
            )

    def get_model_name(self) -> str:
        return self.model_name

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())
