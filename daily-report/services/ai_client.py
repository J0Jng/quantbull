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
        # 假设 ai-hub 运行在 8002 端口
        self.base_url = f"http://localhost:8002/api"
        self.timeout = 120.0  # AI 生成可能需要较长时间
    
    def _build_prompt(self, market_data: MarketDataInput) -> str:
        """
        构建 AI Prompt（与业务逻辑解耦）
        
        Args:
            market_data: 市场数据
            
        Returns:
            str: 完整的 Prompt
        """
        prompt = f"""你是投资组合经理。
基于今日全市场数据与新闻，输出每日投资方案。

要求：
1. 不得涉及承诺收益或投资建议
2. 所有分析必须基于提供的数据，不能捏造
3. 必须包含风险提示

输入数据：
- 报告日期：{market_data.report_date}
- 市场概览：
  * 总成交额：{market_data.market_overview.total_turnover:,.0f} 元
  * 上涨：{market_data.market_overview.rising_count} 只
  * 下跌：{market_data.market_overview.falling_count} 只
  * 平盘：{market_data.market_overview.flat_count} 只
  * 指数数据：{market_data.market_overview.indices}

- ETF 数据（前10只）：
{self._format_etf_data(market_data.etf_list[:10])}

- 股票数据（前50只）：
{self._format_stock_data(market_data.stock_list[:50])}

请生成以下结构化内容（JSON 格式）：

1. ETF 推荐（3个）：
   - ETF 代码 + 名称
   - 所属主题/行业
   - 推荐逻辑（结合市场风格、行业轮动、情绪）

2. 股票推荐（10只）：
   - 股票代码 + 名称
   - 多因子评分（动量/成交活跃度/情绪，每个因子0-10分）
   - 简要 AI 解读（不超过80字/只）

3. 市场情绪总结：
   - 用1-2段话概括当日市场状态（风险偏好、主线）

4. 风险提示 & 合规免责声明：
   - 系统性风险
   - 模型局限性
   - 明确"非投资建议"

5. 公众号文章结构：
   - 标题
   - 小标题大纲（3-5个小标题）

请以 JSON 格式返回，格式如下：
{{
  "etf_recommendations": [
    {{"code": "...", "name": "...", "category": "...", "reasoning": "..."}}
  ],
  "stock_recommendations": [
    {{"code": "...", "name": "...", "factor_scores": {{"momentum": 8.5, "liquidity": 7.2, "sentiment": 6.8}}, "ai_analysis": "..."}}
  ],
  "market_sentiment": "...",
  "risk_warning": "...",
  "article_outline": {{
    "title": "...",
    "sections": ["...", "..."]
  }}
}}
"""
        return prompt
    
    def _format_etf_data(self, etf_list: list) -> str:
        """格式化 ETF 数据用于 Prompt"""
        lines = []
        for etf in etf_list[:10]:
            lines.append(
                f"  - {etf.code} {etf.name}: "
                f"涨跌幅 {etf.change_pct:.2f}%, "
                f"成交额 {etf.turnover:,.0f}, "
                f"分类 {etf.category or '未知'}"
            )
        return "\n".join(lines)
    
    def _format_stock_data(self, stock_list: list) -> str:
        """格式化股票数据用于 Prompt"""
        lines = []
        for stock in stock_list[:50]:
            lines.append(
                f"  - {stock.code} {stock.name}: "
                f"涨跌幅 {stock.change_pct:.2f}%, "
                f"成交额 {stock.turnover:,.0f}, "
                f"换手率 {stock.turnover_rate:.2f}%, "
                f"行业 {stock.industry or '未知'}"
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
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # 假设 ai-hub 提供此接口
                response = await client.post(
                    f"{self.base_url}/llm/generate",
                    json={
                        "prompt": prompt,
                        "model": "deepseek",  # 或 "qwen"
                        "temperature": 0.7,
                        "max_tokens": 4000,
                        "response_format": "json",
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                # 解析 AI 返回的 JSON
                ai_data = result.get("content", {})
                if isinstance(ai_data, str):
                    import json
                    ai_data = json.loads(ai_data)
                
                # 转换为 Pydantic 模型
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
                    article_outline=ArticleOutline(**ai_data.get("article_outline", {})),
                )
        except httpx.HTTPError as e:
            logger.error(f"调用 AI Hub 失败: {e}")
            # 开发环境返回模拟数据
            if settings.env == "local":
                logger.warning("使用模拟 AI 生成数据")
                return self._get_mock_ai_content()
            raise
        except Exception as e:
            logger.error(f"解析 AI 响应失败: {e}", exc_info=True)
            raise
    
    def _get_mock_ai_content(self) -> AIGeneratedContent:
        """获取模拟 AI 内容（开发环境）"""
        return AIGeneratedContent(
            etf_recommendations=[
                ETFRecommendation(
                    code="510300",
                    name="沪深300ETF",
                    category="宽基",
                    reasoning="市场风格偏向大盘蓝筹，沪深300ETF 流动性好，适合稳健配置。",
                ),
                ETFRecommendation(
                    code="159919",
                    name="300ETF",
                    category="宽基",
                    reasoning="创业板表现活跃，300ETF 覆盖成长股，符合当前市场情绪。",
                ),
                ETFRecommendation(
                    code="512880",
                    name="银行ETF",
                    category="行业",
                    reasoning="银行板块估值较低，防御性强，适合当前市场环境。",
                ),
            ],
            stock_recommendations=[
                StockRecommendation(
                    code="000001",
                    name="平安银行",
                    factor_scores={"momentum": 8.5, "liquidity": 7.2, "sentiment": 6.8},
                    ai_analysis="银行板块估值修复，平安银行基本面稳健，成交活跃。",
                ),
                StockRecommendation(
                    code="000002",
                    name="万科A",
                    factor_scores={"momentum": 6.2, "liquidity": 5.8, "sentiment": 5.5},
                    ai_analysis="房地产政策边际改善，万科A 作为龙头有望受益。",
                ),
            ] + [
                StockRecommendation(
                    code=f"60000{i}",
                    name=f"模拟股票{i}",
                    factor_scores={"momentum": 7.0, "liquidity": 6.5, "sentiment": 6.0},
                    ai_analysis=f"模拟股票 {i} 的分析内容，仅供参考。",
                )
                for i in range(3, 11)
            ],
            market_sentiment=(
                "今日市场整体呈现震荡上行态势，主要指数小幅收涨。"
                "市场情绪较为乐观，成交额较前日有所放大。"
                "板块轮动明显，科技、消费板块表现活跃。"
            ),
            risk_warning=(
                "风险提示：本报告仅供参考，不构成投资建议。"
                "投资有风险，入市需谨慎。"
                "市场存在系统性风险，模型分析存在局限性，"
                "投资者应根据自身情况做出独立判断。"
            ),
            article_outline=ArticleOutline(
                title=f"{datetime.now().strftime('%Y年%m月%d日')} 投资方案",
                sections=[
                    "市场概览",
                    "ETF 推荐",
                    "股票推荐",
                    "风险提示",
                ],
            ),
        )
