from schemas.ai import SummaryGenerationRequest, SummaryGenerationResponse, TaskType
from services.llm_service import LLMService
from services.model_router import ModelRouter

from core.logger import get_logger

logger = get_logger(__name__)


class SummaryService:
    """摘要生成服务"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.model_router = ModelRouter()
    
    async def generate_summary(self, request: SummaryGenerationRequest) -> SummaryGenerationResponse:
        """
        生成投研摘要
        
        默认使用 Qwen2.5（结构化输出、要点式输出能力强）
        """
        # 路由到最适合的模型
        model, reason = self.model_router.route(
            task_type=TaskType.SUMMARY,
            explicit_model=request.model
        )
        logger.info(f"摘要生成路由: {reason}")
        
        # 根据摘要类型构建系统提示词
        if request.summary_type == "structured":
            system_prompt = """你是资深证券分析师。
请基于以下内容，生成结构化的投研摘要，使用要点式输出。

内容必须包含：
- 核心要点（3-5条）
- 关键数据
- 风险因素
- 投资建议（如有）

要求：输出格式清晰，使用列表或分段形式。"""
        elif request.summary_type == "bullet":
            system_prompt = """你是资深证券分析师。
请基于以下内容，生成要点式投研摘要。

要求：
- 使用列表形式
- 每条要点简洁明了
- 突出关键信息"""
        else:  # paragraph
            system_prompt = """你是资深证券分析师。
请基于以下内容，生成一段简洁的投研摘要。

要求：
- 内容精炼
- 逻辑清晰
- 包含关键信息"""
        
        # 构建用户消息
        user_message = f"请为以下内容生成摘要：\n\n{request.content}"
        
        if request.max_length:
            user_message += f"\n\n要求：摘要长度控制在 {request.max_length} 字以内。"
        
        # 调用 LLM 生成（Qwen 支持结构化输出）
        response = await self.llm_service.generate_with_system_prompt(
            user_message=user_message,
            system_prompt=system_prompt,
            model=model,
            temperature=0.3,  # 摘要使用较低温度，更客观
            max_tokens=request.max_length * 2 if request.max_length else 1000,
        )
        
        summary = response.content
        
        # 尝试提取结构化章节（简单实现）
        sections = None
        if request.summary_type == "structured":
            lines = summary.split("\n")
            sections = [line.strip() for line in lines if line.strip().startswith(("-", "•", "*", "1.", "2.", "3."))]
        
        logger.info(f"摘要生成完成，模型: {response.model}")
        
        return SummaryGenerationResponse(
            summary=summary,
            model=response.model,
            tokens_used=response.tokens_used,
            sections=sections,
        )
