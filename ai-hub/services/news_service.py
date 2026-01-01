import httpx
from typing import Optional
from datetime import datetime, timedelta

from schemas.ai import NewsGenerationRequest, NewsGenerationResponse, TaskType
from services.llm_service import LLMService
from services.model_router import ModelRouter

from core.logger import get_logger
from core.config import settings

logger = get_logger(__name__)


class NewsService:
    """新闻生成服务"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.model_router = ModelRouter()
    
    async def _fetch_quote_data(self, stock_code: str) -> Optional[dict]:
        """
        从 data-service 拉取实时行情数据
        
        Args:
            stock_code: 股票代码（会自动规范化）
        
        Returns:
            行情数据字典，失败时返回 None
        """
        try:
            # 规范化股票代码：去空格、去后缀、补零到6位
            normalized_code = stock_code.strip()
            # 去掉 .SZ/.SH 后缀
            if '.' in normalized_code:
                normalized_code = normalized_code.split('.')[0]
            # 左侧补零到6位
            normalized_code = normalized_code.zfill(6)

            # 计算查询区间：从“询问日”往前 1 个月
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            start_date_str = start_date.strftime("%Y%m%d")
            end_date_str = end_date.strftime("%Y%m%d")
            
            logger.info(f"正在从 data-service 拉取行情: {normalized_code}")
            
            async with httpx.AsyncClient(timeout=settings.request_timeout) as client:
                response = await client.post(
                    f"{settings.data_service_url}/api/tushare/daily",
                    json={
                        "codes": [normalized_code],
                        "start_date": start_date_str,
                        "end_date": end_date_str,
                        }
                )
                response.raise_for_status()
                
                result = response.json()
                
                # data-service 使用信封格式: {"code": 0, "data": {"data": [...], ...}}
                envelope_data = result.get("data", {})
                if isinstance(envelope_data, dict):
                    items = envelope_data.get("data", [])
                else:
                    # 兼容直接格式
                    items = result.get("data", [])
                
                if items and len(items) > 0:
                    # 取最新一条日线数据
                    quote = items[0]
                    # 转换为普通 dict
                    quote_dict = dict(quote)
                    
                    logger.info(f"成功获取行情: {quote_dict.get('code')} 日期:{quote_dict.get('trade_date')}")
                    return quote_dict
                else:
                    logger.warning(f"data-service 未返回 {normalized_code} 的行情数据")
                    return None
                    
        except httpx.TimeoutException:
            logger.warning(f"调用 data-service 超时: {stock_code}")
            return None
        except httpx.HTTPStatusError as e:
            logger.warning(f"data-service 返回错误: {e.response.status_code}")
            return None
        except Exception as e:
            logger.warning(f"拉取行情失败: {stock_code}, 错误: {str(e)}")
            return None
    
    async def generate_news(self, request: NewsGenerationRequest) -> NewsGenerationResponse:
        """
        生成新闻内容
        
        根据 README.md 中的 Prompt 模板生成新闻
        默认使用 DeepSeek R1（文本生成能力强）
        
        如果提供了 stock_code 但未提供 quote_data，会自动从 data-service 拉取行情
        """
        # 路由到最适合的模型
        model, reason = self.model_router.route(
            task_type=TaskType.NEWS,
            explicit_model=request.model
        )
        logger.info(f"新闻生成路由: {reason}")
        
        # 记录请求参数（用于判断是否触发自动拉取）
        logger.info(f"新闻生成请求参数: stock_code={request.stock_code}, has_quote_data={request.quote_data is not None}")
        
        # 自动拉取行情数据（如果需要）
        quote_data = request.quote_data
        if not quote_data and request.stock_code:
            logger.info(f"触发自动拉取行情: stock_code={request.stock_code}")
            quote_data = await self._fetch_quote_data(request.stock_code)
        elif quote_data:
            logger.info("使用用户提供的 quote_data，不调用 data-service")
        else:
            logger.info("未提供 stock_code，跳过行情拉取")
        
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
        
        if quote_data:
            user_message += f"\n今日行情：{quote_data}"
        
        # 调用 LLM 生成
        response = await self.llm_service.generate_with_system_prompt(
            user_message=user_message,
            system_prompt=system_prompt,
            model=model,
            task_type=TaskType.NEWS,
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
            tokens_used=response.total_tokens,
        )
