from core.config import settings
from core.logger import get_logger
from schemas.ai import ModelType, TaskType

logger = get_logger(__name__)


class ModelRouter:
    """智能模型路由
    
    根据任务类型自动选择最适合的模型
    """
    
    def __init__(self):
        # 路由规则：任务类型 -> 默认模型
        self.routing_rules = {
            TaskType.NEWS: ModelType.DEEPSEEK,      # 新闻/长文本生成 → DeepSeek
            TaskType.SUMMARY: ModelType.QWEN,        # 摘要/结构化输出 → Qwen
            TaskType.STRATEGY: ModelType.QWEN,       # 代码/策略生成 → Qwen
            TaskType.CODE: ModelType.QWEN,           # 代码生成 → Qwen
            TaskType.GENERAL: ModelType.DEEPSEEK,    # 通用对话 → DeepSeek
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
        # 如果显式指定了模型，直接使用
        if explicit_model:
            reason = f"使用显式指定的模型: {explicit_model}"
            logger.info(f"模型路由: {reason}")
            return explicit_model, reason
        
        # 根据任务类型自动路由
        recommended_model = self.routing_rules.get(
            task_type,
            ModelType.DEEPSEEK  # 默认使用 DeepSeek
        )
        
        reason_map = {
            TaskType.NEWS: "新闻/长文本生成任务，推荐使用 DeepSeek（文本生成能力强）",
            TaskType.SUMMARY: "摘要/结构化输出任务，推荐使用 Qwen（结构化输出优秀）",
            TaskType.STRATEGY: "策略/代码生成任务，推荐使用 Qwen（代码生成能力强）",
            TaskType.CODE: "代码生成任务，推荐使用 Qwen（代码生成能力强）",
            TaskType.GENERAL: "通用对话任务，使用默认模型 DeepSeek",
        }
        
        reason = reason_map.get(task_type, f"使用默认模型: {recommended_model}")
        logger.info(f"模型路由: 任务类型 {task_type} -> {recommended_model}, 理由: {reason}")
        
        return recommended_model, reason
