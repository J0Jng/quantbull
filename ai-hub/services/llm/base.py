import asyncio
import time
from abc import ABC, abstractmethod
from collections import deque
from typing import Optional

from pydantic import BaseModel

from core.logger import get_logger
from schemas.ai import TaskType

logger = get_logger(__name__)


class RateLimitExceeded(Exception):
    """表示达到限流上限"""


class InMemoryRateLimiter:
    """基于内存的简单 RPM 限流器"""

    def __init__(self, rpm: int):
        self.rpm = rpm
        self.window = 60
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.time()
            window_start = now - self.window
            while self._timestamps and self._timestamps[0] < window_start:
                self._timestamps.popleft()

            if len(self._timestamps) >= self.rpm:
                raise RateLimitExceeded("LLM rate limit exceeded")

            self._timestamps.append(now)


class LLMResult(BaseModel):
    """LLM 调用的统一结果结构"""

    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    finish_reason: Optional[str] = None


class BaseLLMClient(ABC):
    """统一的 LLM Client 抽象层"""

    def __init__(self, model_name: str, rpm: int, max_concurrency: int):
        self.model_name = model_name
        self.rate_limiter = InMemoryRateLimiter(rpm)
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def chat(
        self,
        messages: list[dict[str, str]],
        task_type: TaskType,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResult:
        if not self.is_available():
            raise ValueError(f"model {self.model_name} is not configured")

        start = time.perf_counter()
        result: Optional[LLMResult] = None
        error: Optional[Exception] = None

        try:
            await self.rate_limiter.acquire()
            async with self.semaphore:
                result = await self._chat(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                )
                return result
        except Exception as exc:  # 捕获以便统一记录
            error = exc
            raise
        finally:
            latency_ms = int((time.perf_counter() - start) * 1000)
            self._log_call(task_type=task_type, result=result, latency_ms=latency_ms, error=error)

    @abstractmethod
    async def _chat(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResult:
        """模型具体实现"""
        raise NotImplementedError

    @abstractmethod
    def get_model_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    def _log_call(
        self,
        task_type: TaskType,
        result: Optional[LLMResult],
        latency_ms: int,
        error: Optional[Exception],
    ) -> None:
        success = error is None
        token_info = "0/0/0"
        if result:
            token_info = f"{result.total_tokens}/{result.prompt_tokens}+{result.completion_tokens}"

        status = "success" if success else "failure"
        message = (
            f"LLM call {status} | model={self.model_name} task={task_type} "
            f"latency_ms={latency_ms} tokens={token_info}"
        )
        if success:
            logger.info(message)
        else:
            logger.warning(f"{message} error={error}")
