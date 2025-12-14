from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """LLM 统一响应格式"""
    content: str
    model: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None


class LLMAdapter(ABC):
    """LLM 适配器抽象基类
    
    所有模型适配器必须实现此接口，便于后续扩展新模型
    """
    
    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        生成文本
        
        Args:
            messages: 消息列表，格式为 [{"role": "system/user/assistant", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他模型特定参数
            
        Returns:
            LLMResponse: 统一响应格式
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """获取模型名称"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查模型是否可用（API Key 是否配置）"""
        pass
