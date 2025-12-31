from typing import Optional

import httpx
from fastapi import HTTPException

from core.config import settings
from core.logger import get_logger
from schemas.ai import ModelType, TaskType
from services.llm import RateLimitExceeded
from services.llm.base import LLMResult
from services.llm.llm_factory import LLMFactory

logger = get_logger(__name__)


class LLMService:
    """LLM 网关服务（统一 AI 中台）
    
    上层服务无需感知具体模型，通过此服务统一调用
    """

    def __init__(self):
        self.factory = LLMFactory()

    async def generate(
        self,
        messages: list[dict[str, str]],
        model: Optional[ModelType] = None,
        task_type: TaskType = TaskType.GENERAL,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResult:
        model_type = model or ModelType(settings.default_model)

        candidates = [model_type] + self._fallback_candidates(model_type)
        last_error: Optional[Exception] = None

        for candidate in candidates:
            try:
                adapter = self.factory.get_adapter(candidate)
                return await adapter.chat(
                    messages=messages,
                    task_type=task_type,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
            except RateLimitExceeded as exc:
                last_error = exc
                logger.warning(f"模型 {candidate} 触发限流，尝试降级: {exc}")
                continue
            except httpx.HTTPStatusError as exc:
                last_error = exc
                status = exc.response.status_code
                if status == 429 or status >= 500:
                    logger.warning(f"模型 {candidate} 异常 {status}，尝试降级")
                    continue
                raise
            except httpx.TimeoutException as exc:
                last_error = exc
                logger.warning(f"模型 {candidate} 超时，尝试降级")
                continue
            except Exception as exc:
                last_error = exc
                logger.error(f"模型 {candidate} 调用失败: {exc}", exc_info=True)
                continue

        if isinstance(last_error, RateLimitExceeded):
            raise HTTPException(status_code=429, detail="LLM rate limit exceeded")

        if isinstance(last_error, httpx.HTTPStatusError):
            status = last_error.response.status_code
            message = last_error.response.text
            if status == 429:
                raise HTTPException(status_code=429, detail="LLM rate limit exceeded")
            if status >= 500:
                raise HTTPException(status_code=502, detail=f"LLM upstream error: {status}")
            raise HTTPException(status_code=status, detail=message)

        if isinstance(last_error, httpx.TimeoutException):
            raise HTTPException(status_code=504, detail="LLM request timeout")

        if last_error:
            raise last_error

        raise HTTPException(status_code=500, detail="LLM 调用失败：无可用模型")

    async def generate_with_system_prompt(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        model: Optional[ModelType] = None,
        task_type: TaskType = TaskType.GENERAL,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResult:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})

        return await self.generate(
            messages=messages,
            model=model,
            task_type=task_type,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    def get_available_models(self) -> list[ModelType]:
        return self.factory.get_available_models()

    def _fallback_candidates(self, primary: ModelType) -> list[ModelType]:
        backup = ModelType.QWEN if primary == ModelType.DEEPSEEK else ModelType.DEEPSEEK
        return [backup]
