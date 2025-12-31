from core.config import settings
from core.logger import get_logger
from schemas.ai import ModelType, TaskType
from services.llm.llm_factory import LLMFactory

logger = get_logger(__name__)


class ModelRouter:
    """智能模型路由
    
    根据任务类型自动选择最适合的模型
    """
    
    def __init__(self):
        # 路由规则：任务类型 -> 默认模型
        self.routing_rules = {
            TaskType.NEWS: ModelType.DEEPSEEK,
            TaskType.SUMMARY: ModelType.QWEN,
            TaskType.STRATEGY: ModelType.DEEPSEEK,
            TaskType.CODE: ModelType.DEEPSEEK,
            TaskType.GENERAL: ModelType.DEEPSEEK,
        }
        
        # 从配置覆盖默认值
        if hasattr(settings, 'default_model_for_news'):
            self.routing_rules[TaskType.NEWS] = ModelType(settings.default_model_for_news)
        if hasattr(settings, 'default_model_for_summary'):
            self.routing_rules[TaskType.SUMMARY] = ModelType(settings.default_model_for_summary)
        if hasattr(settings, 'default_model_for_strategy'):
            self.routing_rules[TaskType.STRATEGY] = ModelType(settings.default_model_for_strategy)
    
    def route(
        self,
        task_type: TaskType,
        explicit_model: ModelType | None = None
    ) -> tuple[ModelType, str]:
        """
        路由到最适合的模型
        
        Args:
            task_type: 任务类型
            explicit_model: 显式指定的模型（优先级最高）
            
        Returns:
            tuple: (推荐的模型, 推荐理由)
        """
        recommended_model = explicit_model or self.routing_rules.get(task_type, ModelType.DEEPSEEK)

        reason_map = {
            TaskType.NEWS: "新闻/长文本生成任务，推荐使用 DeepSeek（文本生成能力强）",
            TaskType.SUMMARY: "摘要/报告生成任务，推荐使用 Qwen（结构化输出优秀）",
            TaskType.STRATEGY: "策略/代码生成任务，推荐使用 DeepSeek（推理与生成平衡）",
            TaskType.CODE: "代码生成任务，推荐使用 DeepSeek（推理能力强）",
            TaskType.GENERAL: "通用对话任务，使用默认模型 DeepSeek",
        }

        reason = reason_map.get(task_type, f"使用默认模型: {recommended_model}")
        available = LLMFactory.get_available_models()

        if recommended_model not in available and available:
            backup = ModelType.QWEN if recommended_model == ModelType.DEEPSEEK else ModelType.DEEPSEEK
            if backup in available:
                logger.warning(
                    f"模型 {recommended_model} 不可用，切换到备用模型 {backup} (task={task_type})"
                )
                recommended_model = backup
                reason = f"主模型不可用，使用备用模型: {backup}"

        logger.info(f"模型路由: 任务类型 {task_type} -> {recommended_model}, 理由: {reason}")

        return recommended_model, reason
