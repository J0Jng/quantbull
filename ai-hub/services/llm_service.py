from typing import Optional

from core.config import settings
from core.logger import get_logger
from schemas.ai import ModelType
from services.llm.base import LLMResponse
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
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        统一生成接口
        
        Args:
            messages: 消息列表，格式为 [{"role": "system/user/assistant", "content": "..."}]
            model: 指定模型，不指定则使用默认模型
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他模型特定参数
            
        Returns:
            LLMResponse: 统一响应格式
        """
        # 确定使用的模型
        model_type = model or ModelType(settings.default_model)
        
        try:
            # 获取适配器
            adapter = self.factory.get_adapter(model_type)
            
            # 调用生成
            response = await adapter.generate(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            logger.info(f"LLM 生成成功，模型: {response.model}, tokens: {response.tokens_used}")
            return response
            
        except Exception as e:
            logger.error(f"LLM 生成失败: {e}", exc_info=True)
            raise
    
    async def generate_with_system_prompt(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        model: Optional[ModelType] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        带系统提示词的生成接口（便捷方法）
        
        Args:
            user_message: 用户消息
            system_prompt: 系统提示词
            model: 指定模型
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他模型特定参数
            
        Returns:
            LLMResponse: 统一响应格式
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_message})
        
        return await self.generate(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def get_available_models(self) -> list[ModelType]:
        """获取所有可用的模型"""
        return self.factory.get_available_models()
