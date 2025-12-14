from fastapi import APIRouter, HTTPException

from schemas.ai import (
    ChatRequest,
    ChatResponse,
    NewsGenerationRequest,
    NewsGenerationResponse,
    SummaryGenerationRequest,
    SummaryGenerationResponse,
    StrategyGenerationRequest,
    StrategyGenerationResponse,
    ReportGenerationRequest,
    ReportGenerationResponse,
    DigitalHumanRequest,
    DigitalHumanResponse,
    ModelRouteRequest,
    ModelRouteResponse,
)
from services.llm_service import LLMService
from services.model_router import ModelRouter
from services.news_service import NewsService
from services.summary_service import SummaryService
from services.strategy_service import StrategyService
from services.report_service import ReportService
from services.digital_human_service import DigitalHumanService

from core.logger import get_logger
from schemas.ai import TaskType, ModelType

logger = get_logger(__name__)

router = APIRouter()

# 初始化服务
llm_service = LLMService()
model_router = ModelRouter()
news_service = NewsService()
summary_service = SummaryService()
strategy_service = StrategyService()
report_service = ReportService()
digital_human_service = DigitalHumanService()


@router.post("/generate/news", response_model=NewsGenerationResponse, summary="生成新闻解读")
async def generate_news(request: NewsGenerationRequest) -> NewsGenerationResponse:
    """
    根据财经快讯生成新闻解读
    
    - 默认模型：DeepSeek R1（文本生成、新闻能力强）
    - 支持显式指定模型
    - 基于 README.md 中的 Prompt 模板
    """
    try:
        return await news_service.generate_news(request)
    except Exception as e:
        logger.error(f"新闻生成错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"新闻生成失败: {str(e)}")


@router.post("/generate/summary", response_model=SummaryGenerationResponse, summary="生成投研摘要")
async def generate_summary(request: SummaryGenerationRequest) -> SummaryGenerationResponse:
    """
    生成投研摘要（偏结构化、要点式输出）
    
    - 默认模型：Qwen2.5（结构化输出能力强）
    - 支持显式指定模型
    - 支持多种摘要类型：structured/bullet/paragraph
    """
    try:
        return await summary_service.generate_summary(request)
    except Exception as e:
        logger.error(f"摘要生成错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"摘要生成失败: {str(e)}")


@router.post("/generate/strategy", response_model=StrategyGenerationResponse, summary="生成策略代码")
async def generate_strategy(request: StrategyGenerationRequest) -> StrategyGenerationResponse:
    """
    生成 Backtrader 策略 Python 代码
    
    - 默认模型：Qwen2.5（代码生成能力强）
    - 支持显式指定模型
    - 基于 README.md 中的 Prompt 模板
    """
    try:
        return await strategy_service.generate_strategy(request)
    except Exception as e:
        logger.error(f"策略生成错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"策略生成失败: {str(e)}")


# ==================== 以下为兼容性接口（保留原有功能） ====================

@router.post("/chat", response_model=ChatResponse, summary="通用聊天接口")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    通用 AI 聊天接口
    
    支持指定模型或自动路由
    """
    try:
        model = request.model or ModelType.DEEPSEEK
        
        response = await llm_service.generate_with_system_prompt(
            user_message=request.message,
            system_prompt=request.system_prompt,
            model=model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        return ChatResponse(
            content=response.content,
            model=response.model,
            tokens_used=response.tokens_used,
            finish_reason=response.finish_reason,
        )
    except Exception as e:
        logger.error(f"聊天接口错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI 服务错误: {str(e)}")


@router.post("/report/generate", response_model=ReportGenerationResponse, summary="生成报告")
async def generate_report(request: ReportGenerationRequest) -> ReportGenerationResponse:
    """
    生成公司研究报告
    
    基于 README.md 中的 Prompt 模板生成投研摘要
    """
    try:
        return await report_service.generate_report(request)
    except Exception as e:
        logger.error(f"报告生成错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@router.post("/digital-human/generate", response_model=DigitalHumanResponse, summary="生成数字人视频")
async def generate_digital_human(request: DigitalHumanRequest) -> DigitalHumanResponse:
    """
    生成数字人视频
    
    将文本转换为数字人口播视频（需要配置第三方服务）
    """
    try:
        return await digital_human_service.generate_video(request)
    except Exception as e:
        logger.error(f"数字人视频生成错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"数字人视频生成失败: {str(e)}")


@router.post("/model/route", response_model=ModelRouteResponse, summary="模型路由推荐")
async def route_model(request: ModelRouteRequest) -> ModelRouteResponse:
    """
    智能模型路由推荐
    
    根据任务类型推荐最适合的 AI 模型
    """
    try:
        model, reason = model_router.route(request.task_type)
        return ModelRouteResponse(
            recommended_model=model,
            reason=reason,
        )
    except Exception as e:
        logger.error(f"模型路由错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"模型路由失败: {str(e)}")
