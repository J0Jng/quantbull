from schemas.ai import ReportGenerationRequest, ReportGenerationResponse, TaskType
from services.llm_service import LLMService
from services.model_router import ModelRouter

from core.logger import get_logger
from core.config import settings

logger = get_logger(__name__)

# 控制生成报告的最大字数，避免过长响应
MAX_REPORT_CHARS = min(settings.max_tokens, 2000)


class ReportService:
    """报告生成服务（兼容接口）"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.model_router = ModelRouter()
    
    async def generate_report(self, request: ReportGenerationRequest) -> ReportGenerationResponse:
        """
        生成公司研究报告
        
        根据 README.md 中的 Prompt 模板生成报告
        默认使用 Qwen（结构化输出能力强）
        """
        # 路由到最适合的模型
        model, reason = self.model_router.route(
            task_type=TaskType.SUMMARY,
            explicit_model=None
        )
        logger.info(f"报告生成路由: {reason}")
        
        # 构建系统提示词（基于 README.md 中的 Prompt）
        system_prompt = """你是资深证券分析师。
        请基于以下企业公开信息，生成一篇公司介绍与投研摘要：

        内容必须包含：
        - 公司主营业务
        - 行业地位
        - 最近动态
        - 风险因素"""
        
        if request.include_risks:
            system_prompt += "\n\n特别注意：必须包含详细的风险因素分析。"
        
        # 构建用户消息
        user_message = f"资料如下：\n{request.company_info}"
        
        # 调用 LLM 生成
        response = await self.llm_service.generate_with_system_prompt(
            user_message=user_message,
            system_prompt=system_prompt,
            model=model,
            task_type=TaskType.SUMMARY,
            temperature=0.6,  # 报告生成使用较低温度，更客观
            max_tokens=min(settings.max_tokens, 6000)
        )
        
        # 截断过长的输出，控制字数
        report_content = response.content[:MAX_REPORT_CHARS]
        
        # 简单提取章节（实际可以更智能）
        sections = []
        lines = report_content.split("\n")
        for line in lines:
            if line.strip().startswith(("#", "##", "###", "**", "-")):
                sections.append(line.strip())
        
        logger.info(f"报告生成完成，章节数: {len(sections)}, 模型: {response.model}")
        
        return ReportGenerationResponse(
            report_content=report_content,
            model=response.model,
            sections=sections if sections else ["报告正文"],
        )
