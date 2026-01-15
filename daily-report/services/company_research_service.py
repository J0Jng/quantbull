"""公司研报服务层"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from models.company_research import CompanyResearchReport
from schemas.company_research import (
    CompanyResearchGenerateRequest,
    CompanyResearchQueryRequest,
    CompanyResearchReportResponse,
    CompanyResearchListResponse,
)
from services.ai_client import AIHubClient
from core.logger import get_logger

logger = get_logger(__name__)


class CompanyResearchService:
    """公司研报服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_client = AIHubClient()
    
    def _build_company_info(self, company_name: str, stock_code: Optional[str]) -> str:
        """
        构造 company_info（当用户未提供时）
        
        Args:
            company_name: 公司名称
            stock_code: 股票代码
            
        Returns:
            str: 构造的 company_info
        """
        if stock_code:
            return f"目标公司：{company_name}（{stock_code}）"
        else:
            return f"目标公司：{company_name}"
    
    def _build_research_prompt(
        self,
        company_name: str,
        stock_code: Optional[str],
        rating: str,
        report_type: str,
        company_info: str,
        include_risks: bool,
        tags: Optional[List[str]]
    ) -> str:
        """
        构建公司研报生成 Prompt
        
        Args:
            company_name: 公司名称
            stock_code: 股票代码
            rating: 评级
            report_type: 报告类型
            company_info: 公司信息
            include_risks: 是否包含风险
            tags: 标签列表
            
        Returns:
            str: Prompt
        """
        # 评级映射
        rating_map = {
            "buy": "买入",
            "add": "增持",
            "hold": "持有",
            "reduce": "减持",
            "sell": "卖出"
        }
        rating_cn = rating_map.get(rating, "持有")
        
        # 报告类型映射
        type_map = {
            "summary": "简要摘要",
            "analysis": "深度分析"
        }
        type_cn = type_map.get(report_type, "简要摘要")
        
        prompt = f"""你是一位专业的证券分析师。请基于以下信息生成一份公司研报（{type_cn}）。

公司信息：
{company_info}

研报要求：
- 评级：{rating_cn}
- 报告类型：{type_cn}
- {'需要' if include_risks else '无需'}包含风险提示
"""
        
        if tags:
            prompt += f"- 关注领域：{', '.join(tags)}\n"
        
        prompt += """
输出要求：
1. 使用 Markdown 格式
2. 包含以下章节（根据报告类型调整详细程度）：
   - 公司概况
   - 核心业务与竞争力
   - 财务表现
   - 投资亮点
"""
        
        if include_risks:
            prompt += "   - 风险提示\n"
        
        prompt += """3. 语言专业、客观，避免情绪化表达
4. 基于公司名称自行补全必要背景信息（如行业、主营业务等）
5. 输出结构化研报，章节清晰

请直接输出 Markdown 格式的研报正文，不要包含 JSON 或其他格式。
"""
        return prompt
    
    async def generate_report(self, request: CompanyResearchGenerateRequest) -> CompanyResearchReportResponse:
        """
        生成公司研报
        
        Args:
            request: 生成请求
            
        Returns:
            CompanyResearchReportResponse: 生成的研报
        """
        try:
            # 1. 构造 company_info（如果用户未提供）
            company_info = request.company_info
            if not company_info:
                company_info = self._build_company_info(request.company_name, request.stock_code)
                logger.info(f"自动构造 company_info: {company_info}")
            
            # 2. 计算 content_hash
            content_hash = CompanyResearchReport.compute_content_hash(
                company_name=request.company_name,
                stock_code=request.stock_code,
                rating=request.rating,
                report_type=request.report_type,
                company_info=company_info,
                include_risks=request.include_risks,
                tags=request.tags or [],
            )
            
            # 3. 去重检查（如果 force=False）
            if not request.force:
                existing = self.db.query(CompanyResearchReport).filter(
                    CompanyResearchReport.content_hash == content_hash
                ).first()
                
                if existing:
                    logger.info(f"命中已存在研报（ID={existing.id}），直接返回")
                    return CompanyResearchReportResponse.from_orm(existing)
            
            # 4. 构建 Prompt
            prompt = self._build_research_prompt(
                company_name=request.company_name,
                stock_code=request.stock_code,
                rating=request.rating,
                report_type=request.report_type,
                company_info=company_info,
                include_risks=request.include_risks,
                tags=request.tags,
            )
            logger.info(f"生成 Prompt 长度: {len(prompt)}")
            
            # 5. 调用 AI Hub 生成研报
            ai_response = await self._call_ai_hub(prompt)
            logger.info(f"AI 生成完成，内容长度: {len(ai_response['content'])}")
            
            # 6. 提取章节（从 markdown 中解析 ## 标题）
            sections = self._extract_sections(ai_response['content'])
            
            # 7. 写入数据库
            report = CompanyResearchReport(
                company_name=request.company_name,
                stock_code=request.stock_code,
                rating=request.rating,
                report_type=request.report_type,
                company_info=company_info,
                report_content=ai_response['content'],
                tags=request.tags,
                include_risks=request.include_risks,
                model=ai_response.get('model'),
                tokens_used=ai_response.get('tokens_used'),
                sections=sections,
                content_hash=content_hash,
            )
            
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            
            logger.info(f"公司研报入库成功（ID={report.id}）")
            return CompanyResearchReportResponse.from_orm(report)
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"生成公司研报失败: {e}", exc_info=True)
            raise
    
    async def _call_ai_hub(self, prompt: str) -> dict:
        """
        调用 AI Hub 生成内容
        
        Args:
            prompt: Prompt 文本
            
        Returns:
            dict: AI 响应（content, model, tokens_used）
        """
        import httpx
        
        try:
            async with httpx.AsyncClient(timeout=240.0) as client:
                response = await client.post(
                    f"{self.ai_client.base_url}/ai/chat",
                    json={
                        "message": prompt,
                        "model": "deepseek",
                        "temperature": 0.7,
                        "max_tokens": 8000,
                        "system_prompt": "你是专业证券分析师。请用 Markdown 格式输出结构化研报。",
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # 处理统一响应格式（兼容 data.data 和 data）
                if isinstance(result, dict):
                    if "data" in result and isinstance(result["data"], dict):
                        ai_data = result["data"]
                    else:
                        ai_data = result
                else:
                    raise ValueError("AI 响应格式异常")
                
                return {
                    "content": ai_data.get("content", ""),
                    "model": ai_data.get("model", "deepseek"),
                    "tokens_used": ai_data.get("usage", {}),
                }
        
        except httpx.HTTPError as e:
            logger.error(f"调用 AI Hub 失败: {e}")
            raise Exception(f"AI 生成失败: {str(e)}")
    
    def _extract_sections(self, content: str) -> List[str]:
        """
        从 Markdown 内容中提取章节标题（## 开头）
        
        Args:
            content: Markdown 内容
            
        Returns:
            List[str]: 章节标题列表
        """
        import re
        
        sections = []
        for line in content.split('\n'):
            # 匹配 ## 标题（不匹配 ### 及以下）
            match = re.match(r'^##\s+(.+)$', line.strip())
            if match:
                sections.append(match.group(1))
        
        return sections
    
    def get_reports(self, request: CompanyResearchQueryRequest) -> CompanyResearchListResponse:
        """
        查询公司研报列表
        
        Args:
            request: 查询请求
            
        Returns:
            CompanyResearchListResponse: 研报列表
        """
        try:
            # 构建查询
            query = self.db.query(CompanyResearchReport)
            
            # 评级筛选
            if request.rating:
                query = query.filter(CompanyResearchReport.rating == request.rating)
            
            # 关键词搜索（company_name/stock_code/tags）
            if request.keyword:
                keyword_filter = or_(
                    CompanyResearchReport.company_name.contains(request.keyword),
                    CompanyResearchReport.stock_code.contains(request.keyword),
                    func.json_array_length(CompanyResearchReport.tags) > 0  # 简化：实际应搜索 JSON 内容
                )
                query = query.filter(keyword_filter)
            
            # 获取总数
            total = query.count()
            
            # 分页
            items = query.order_by(CompanyResearchReport.created_at.desc()).offset(request.offset).limit(request.limit).all()
            
            return CompanyResearchListResponse(
                total=total,
                items=[CompanyResearchReportResponse.from_orm(item) for item in items]
            )
        
        except Exception as e:
            logger.error(f"查询公司研报列表失败: {e}", exc_info=True)
            raise
    
    def get_report_by_id(self, report_id: str) -> Optional[CompanyResearchReportResponse]:
        """
        根据 ID 获取公司研报详情
        
        Args:
            report_id: 研报 ID
            
        Returns:
            Optional[CompanyResearchReportResponse]: 研报详情
        """
        try:
            report = self.db.query(CompanyResearchReport).filter(
                CompanyResearchReport.id == report_id
            ).first()
            
            if not report:
                return None
            
            return CompanyResearchReportResponse.from_orm(report)
        
        except Exception as e:
            logger.error(f"获取公司研报详情失败: {e}", exc_info=True)
            raise
