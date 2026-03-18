"""AI Hub 客户端（调用 ai-hub 生成投研内容）"""
import httpx
from datetime import datetime
from typing import Optional

from core.config import settings
from core.logger import get_logger
from schemas.daily_report import (
    MarketDataInput,
    AIGeneratedContent,
    ETFRecommendation,
    StockRecommendation,
    ArticleOutline,
)

logger = get_logger(__name__)


class AIHubClient:
    """AI Hub 客户端"""
    
    def __init__(self):
        """初始化客户端"""
        # 从配置读取服务地址，默认使用 Docker 网络内的服务名
        ai_hub_host = getattr(settings, 'ai_hub_host', 'ai-hub')
        ai_hub_port = getattr(settings, 'ai_hub_port', 8002)
        self.base_url = f"http://{ai_hub_host}:{ai_hub_port}/api"
        self.timeout = 240.0  # AI 生成需要较长时间（增加到 240 秒）
        logger.info(f"AI Hub 客户端初始化: {self.base_url}")
    
    def _build_prompt(self, market_data: MarketDataInput) -> str:
        """
        构建 AI Prompt（与业务逻辑解耦）
        
        Args:
            market_data: 市场数据
            
        Returns:
            str: 完整的 Prompt
        """
        prompt = f"""你是专业市场分析助手。基于今日全市场数据，输出每日数据模拟分析。

要求：
1. 不得承诺收益或提供投资建议
2. 分析必须基于提供数据
3. 必须包含风险提示
    4. 不要输出 ETF 推荐或个股推荐

输入数据：
- 报告日期：{market_data.report_date}
- 市场概览：
  总成交额 {market_data.market_overview.total_turnover/1e8:.2f}亿元
  上涨 {market_data.market_overview.rising_count} / 下跌 {market_data.market_overview.falling_count}
  指数：{', '.join([f'{k}({v:.2f})' for k, v in market_data.market_overview.indices.items()])}

- ETF 数据（前20只，仅用于市场风格判断）：
{self._format_etf_data(market_data.etf_list[:20])}

- 股票数据（前30只，仅用于市场情绪判断）：
{self._format_stock_data(market_data.stock_list[:30])}

请以 JSON 格式输出（不要 markdown 代码块）：
{{
  "market_sentiment": "市场情绪总结（1-2段话）",
  "risk_warning": "风险提示 & 免责声明",
  "article_outline": {{
    "title": "文章标题",
    "sections": ["小标题1", "小标题2", "小标题3"]
  }}
}}
"""
        return prompt
    
    def _format_etf_data(self, etf_list: list) -> str:
        """格式化 ETF 数据用于 Prompt"""
        lines = []
        for etf in etf_list:
            lines.append(
                f"  {etf.code} {etf.name}: "
                f"涨 {etf.change_pct:.2f}%, "
                f"{etf.category or '其他'}"
            )
        return "\n".join(lines)
    
    def _format_stock_data(self, stock_list: list) -> str:
        """格式化股票数据用于 Prompt"""
        lines = []
        for stock in stock_list:
            lines.append(
                f"  {stock.code} {stock.name}: "
                f"涨 {stock.change_pct:.2f}%, "
                f"{stock.industry or '未知'}"
            )
        return "\n".join(lines)
    
    async def generate_investment_report(
        self, 
        market_data: MarketDataInput
    ) -> AIGeneratedContent:
        """
        调用 AI Hub 生成投资方案
        
        Args:
            market_data: 市场数据
            
        Returns:
            AIGeneratedContent: AI 生成的内容
        """
        try:
            prompt = self._build_prompt(market_data)
            logger.info(f"调用 AI Hub 生成投资方案，Prompt 长度: {len(prompt)}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 调用 ai-hub 的聊天接口（路径为 /api/ai/chat）
                response = await client.post(
                    f"{self.base_url}/ai/chat",
                    headers={
                        "X-Internal-Service": "daily-report",
                    },
                    json={
                        "message": prompt,
                        "model": "deepseek",
                        "temperature": 0.5,  # 降低温度以获得更稳定输出
                        "max_tokens": 8000,  # 增加 token 限制
                        "system_prompt": "你是专业投资分析师。请严格按照 JSON 格式返回结果，不要使用 markdown 代码块。",
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # 处理统一响应格式
                if isinstance(result, dict) and "data" in result:
                    ai_response = result["data"]
                else:
                    ai_response = result
                
                # 解析 AI 返回的内容
                content = ai_response.get("content", "")
                logger.info(f"AI 响应长度: {len(content)}")
                
                # 尝试从 Markdown 代码块中提取 JSON
                ai_data = self._extract_json_from_response(content)
                
                # 转换为 Pydantic 模型
                logger.info(f"解析 AI 数据: ETF={len(ai_data.get('etf_recommendations', []))}, 股票={len(ai_data.get('stock_recommendations', []))}")
                
                # 数据清洗：截断过长字段
                for stock in ai_data.get("stock_recommendations", []):
                    if "ai_analysis" in stock and len(stock["ai_analysis"]) > 80:
                        stock["ai_analysis"] = stock["ai_analysis"][:77] + "..."
                
                for etf in ai_data.get("etf_recommendations", []):
                    if "reasoning" in etf and len(etf["reasoning"]) > 500:
                        etf["reasoning"] = etf["reasoning"][:497] + "..."
                
                return AIGeneratedContent(
                    etf_recommendations=[
                        ETFRecommendation(**item)
                        for item in ai_data.get("etf_recommendations", [])
                    ],
                    stock_recommendations=[
                        StockRecommendation(**item)
                        for item in ai_data.get("stock_recommendations", [])
                    ],
                    market_sentiment=ai_data.get("market_sentiment", ""),
                    risk_warning=ai_data.get("risk_warning", ""),
                    article_outline=ArticleOutline(**ai_data.get("article_outline", {"title": "投资方案", "sections": []})),
                )
        except httpx.HTTPError as e:
            logger.error(f"调用 AI Hub 失败: {e}")
            raise Exception(f"无法生成 AI 投资分析：{str(e)}。请确保 ai-hub 服务正常运行。")
        except Exception as e:
            logger.error(f"解析 AI 响应失败: {e}", exc_info=True)
            raise Exception(f"生成投资报告失败：{str(e)}")
    
    def _extract_json_from_response(self, content: str) -> dict:
        """从 AI 响应中提取 JSON 数据"""
        import json
        import re
        
        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # 尝试从 Markdown 代码块中提取
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试查找第一个 JSON 对象
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        logger.warning(f"无法从响应中提取 JSON，原始内容: {content[:200]}...")
        return {}
    

