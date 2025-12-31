from core.logger import get_logger
from schemas.ai import ModelType
from services.llm.base import BaseLLMClient
from services.llm.deepseek_adapter import DeepSeekAdapter
from services.llm.qwen_adapter import QwenAdapter

logger = get_logger(__name__)


class LLMFactory:
    """LLM 工厂类
    
    负责创建和管理 LLM 客户端实例
    """

    _adapters: dict[ModelType, BaseLLMClient] = {}

    @classmethod
    def get_adapter(cls, model_type: ModelType) -> BaseLLMClient:
        if model_type not in cls._adapters:
            if model_type == ModelType.DEEPSEEK:
                cls._adapters[model_type] = DeepSeekAdapter()
            elif model_type == ModelType.QWEN:
                cls._adapters[model_type] = QwenAdapter()
            else:
                raise ValueError(f"不支持的模型类型: {model_type}")

        adapter = cls._adapters[model_type]
        if not adapter.is_available():
            raise ValueError(f"模型 {model_type} 未配置或不可用")

        return adapter

    @classmethod
    def ensure_any_available(cls) -> None:
        """Fail fast when所有模型都不可用"""
        available = cls.get_available_models()
        if not available:
            raise RuntimeError("No LLM models are available. Please configure DEEPSEEK_API_KEY or QWEN_API_KEY.")

    @classmethod
    def get_available_models(cls) -> list[ModelType]:
        available: list[ModelType] = []
        for model_type in [ModelType.DEEPSEEK, ModelType.QWEN]:
            try:
                adapter = cls.get_adapter(model_type)
                if adapter.is_available():
                    available.append(model_type)
            except Exception:
                continue
        return available
