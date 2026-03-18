from fastapi import APIRouter, HTTPException, Request, status
from typing import cast

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
from services.auth_service import auth_service

from core.logger import get_logger
from core.response import success, ApiResponse
from core.config import settings
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


@router.get("/health", summary="AI Hub 健康检查")
async def ai_health_check() -> dict:
    """健康检查（路由前缀为 /api/ai）"""
    return success({
        "status": "ok",
        "service": "ai-hub",
        "env": settings.env,
    })


@router.post("/generate/news", response_model=NewsGenerationResponse, summary="生成新闻解读")
async def generate_news(
    request: NewsGenerationRequest,
) -> NewsGenerationResponse:
    """
    根据财经快讯生成新闻解读
    
    - 默认模型：DeepSeek R1（文本生成、新闻能力强）
    - 支持显式指定模型
    - 基于 README.md 中的 Prompt 模板
    """
    try:
        result = await news_service.generate_news(request)
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"新闻生成错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"新闻生成失败: {str(e)}")


@router.post(
    "/generate/summary",
    response_model=ApiResponse[SummaryGenerationResponse],
    summary="生成投研摘要",
)
async def generate_summary(
    request: SummaryGenerationRequest,
) -> ApiResponse[SummaryGenerationResponse]:
    """
    生成投研摘要（偏结构化、要点式输出）
    
    - 默认模型：Qwen2.5（结构化输出能力强）
    - 支持显式指定模型
    - 支持多种摘要类型：structured/bullet/paragraph
    """
    try:
        result = await summary_service.generate_summary(request)
        return cast(ApiResponse[SummaryGenerationResponse], success(data=result))
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"摘要生成错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"摘要生成失败: {str(e)}")


@router.post("/generate/strategy", response_model=StrategyGenerationResponse, summary="生成策略代码")
async def generate_strategy(
    request: StrategyGenerationRequest,
) -> StrategyGenerationResponse:
    """
    生成 Backtrader 策略 Python 代码
    
    - 默认模型：Qwen2.5（代码生成能力强）
    - 支持显式指定模型
    - 基于 README.md 中的 Prompt 模板
    """
    try:
        result = await strategy_service.generate_strategy(request)
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"策略生成错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"策略生成失败: {str(e)}")


# ==================== 以下为兼容性接口（保留原有功能） ====================

@router.post("/chat", response_model=ChatResponse, summary="通用聊天接口")
async def chat(
    request_http: Request,
    request: ChatRequest,
) -> ChatResponse:
    """
    通用 AI 聊天接口
    
    支持指定模型或自动路由
    """
    try:
        internal_service = (request_http.headers.get("x-internal-service") or "").strip().lower()
        allowed_internal_services = settings.get_internal_chat_allowed_services()
        skip_auth_for_internal = internal_service in allowed_internal_services

        if skip_auth_for_internal:
            logger.info(f"聊天接口识别到内部服务调用，跳过用户鉴权: service={internal_service}")
        else:
            user = await auth_service.verify_access_token(request_http.headers.get("authorization"))
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="not authenticated")

        model = request.model or ModelType.DEEPSEEK
        
        response = await llm_service.generate_with_system_prompt(
            user_message=request.message,
            system_prompt=request.system_prompt,
            model=model,
            task_type=TaskType.GENERAL,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        
        result = ChatResponse(
            content=response.content,
            model=response.model,
            tokens_used=response.total_tokens,
            finish_reason=response.finish_reason,
        )
        
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"聊天接口错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI 服务错误: {str(e)}")


@router.post("/report/generate", response_model=ReportGenerationResponse, summary="生成报告")
async def generate_report(
    request: ReportGenerationRequest,
) -> ReportGenerationResponse:
    """
    生成公司研究报告
    
    基于 README.md 中的 Prompt 模板生成投研摘要
    """
    try:
        result = await report_service.generate_report(request)
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"报告生成错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@router.post("/digital-human/generate", summary="生成数字人视频（占位）")
async def generate_digital_human(request: DigitalHumanRequest) -> dict:
    """
    数字人服务占位，暂未实现
    """
    logger.info("数字人服务占位调用，返回未实现提示")
    return success(data=None, message="digital human service not implemented yet")


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
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"模型路由错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"模型路由失败: {str(e)}")
