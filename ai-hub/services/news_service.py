from schemas.ai import NewsGenerationRequest, NewsGenerationResponse, TaskType
from services.llm_service import LLMService
from services.model_router import ModelRouter

from core.logger import get_logger

logger = get_logger(__name__)


class NewsService:
    """新闻生成服务"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.model_router = ModelRouter()
    
    async def generate_news(self, request: NewsGenerationRequest) -> NewsGenerationResponse:
        """
        生成新闻内容
        
        根据 README.md 中的 Prompt 模板生成新闻
        默认使用 DeepSeek R1（文本生成能力强）
        """
        # 路由到最适合的模型
        model, reason = self.model_router.route(
            task_type=TaskType.NEWS,
            explicit_model=request.model
        )
        logger.info(f"新闻生成路由: {reason}")
        
        # 构建系统提示词（基于 README.md 中的 Prompt）
        system_prompt = f"""你是专业金融编辑。请根据以下快讯和最新行情数据，
生成一篇约{request.target_length}字的财经新闻，包含：
- 客观描述
- 行业背景
- 逻辑分析
- 风险提示

要求：不能虚构信息，不要给推荐性意见。"""
        
        # 构建用户消息
        user_message = f"快讯：{request.news_flash}"
        
        if request.stock_code:
            user_message += f"\n股票：{request.stock_code}"
        
        if request.quote_data:
            user_message += f"\n今日行情：{request.quote_data}"
        
        # 调用 LLM 生成
        response = await self.llm_service.generate_with_system_prompt(
            user_message=user_message,
            system_prompt=system_prompt,
            model=model,
            temperature=0.7,
            max_tokens=request.target_length * 2,  # 预留足够token
        )
        
        news_content = response.content
        word_count = len(news_content)
        
        logger.info(f"新闻生成完成，字数: {word_count}, 模型: {response.model}")
        
        return NewsGenerationResponse(
            news_content=news_content,
            model=response.model,
            word_count=word_count,
            tokens_used=response.tokens_used,
        )
