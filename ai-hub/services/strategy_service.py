from schemas.ai import StrategyGenerationRequest, StrategyGenerationResponse, TaskType
from services.llm_service import LLMService
from services.model_router import ModelRouter

from core.logger import get_logger

logger = get_logger(__name__)


class StrategyService:
    """策略生成服务"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.model_router = ModelRouter()
    
    async def generate_strategy(self, request: StrategyGenerationRequest) -> StrategyGenerationResponse:
        """
        生成量化策略代码
        
        根据 README.md 中的 Prompt 模板生成策略
        默认使用 Qwen2.5（代码生成能力强）
        """
        # 路由到最适合的模型
        model, reason = self.model_router.route(
            task_type=TaskType.STRATEGY,
            explicit_model=request.model
        )
        logger.info(f"策略生成路由: {reason}")
        
        # 构建系统提示词（基于 README.md 中的 Prompt）
        system_prompt = f"""你是量化研究员。
        请根据我的描述，生成适用于 {request.framework} 的策略代码，
        包含：买卖逻辑、风险控制、参数解释。

        要求：输出完整可运行策略代码。"""
        
        if request.include_risk_control:
            system_prompt += "\n\n特别注意：必须包含完善的风险控制机制（止损、仓位管理等）。"
        
        # 构建用户消息
        user_message = f"策略描述：\n{request.user_description}"
        
        # 调用 LLM 生成
        response = await self.llm_service.generate_with_system_prompt(
            user_message=user_message,
            system_prompt=system_prompt,
            model=model,
            task_type=TaskType.STRATEGY,
            temperature=0.3,  # 代码生成使用较低温度，更准确
            max_tokens=4000,
        )
        
        strategy_code = response.content
        
        # 提取策略说明和参数（简单实现，实际可以更智能）
        explanation = "策略代码已生成，请根据实际需求调整参数。"
        parameters = {
            "framework": request.framework,
            "include_risk_control": request.include_risk_control,
        }
        
        # 尝试从代码中提取参数（简单示例）
        if "params" in strategy_code.lower() or "parameters" in strategy_code.lower():
            explanation = "策略包含可配置参数，请查看代码中的参数定义。"
        
        logger.info(f"策略生成完成，模型: {response.model}")
        
        return StrategyGenerationResponse(
            strategy_code=strategy_code,
            model=response.model,
            explanation=explanation,
            parameters=parameters,
            tokens_used=response.total_tokens,
        )
