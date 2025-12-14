from typing import Optional

from core.logger import get_logger
from schemas.ai import ModelType
from services.llm.base import LLMAdapter
from services.llm.deepseek_adapter import DeepSeekAdapter
from services.llm.qwen_adapter import QwenAdapter

logger = get_logger(__name__)


class LLMFactory:
    """LLM 工厂类
    
    负责创建和管理 LLM 适配器实例
    """
    
    _adapters: dict[ModelType, LLMAdapter] = {}
    
    @classmethod
    def get_adapter(cls, model_type: ModelType) -> LLMAdapter:
        """
        获取模型适配器（单例模式）
        
        Args:
            model_type: 模型类型
            
        Returns:
            LLMAdapter: 模型适配器实例
        """
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
    def get_available_models(cls) -> list[ModelType]:
        """获取所有可用的模型"""
        available = []
        for model_type in [ModelType.DEEPSEEK, ModelType.QWEN]:
            try:
                adapter = cls.get_adapter(model_type)
                if adapter.is_available():
                    available.append(model_type)
            except Exception:
                continue
        return available
