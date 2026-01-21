"""
AI 生成财经头条服务
"""
import json
import re
import logging
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

AI_HUB_URL = "http://ai-hub:8005"


async def generate_headlines_from_news(news_items: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """
    调用 AI 生成财经头条
    
    Args:
        news_items: 源新闻列表（来自数据库）
        limit: 生成数量
        
    Returns:
        生成的头条列表，每个元素包含 title/summary/tags/content/is_hot
        
    Raises:
        ValueError: 当 AI 输出无法解析或不符合要求
        httpx.HTTPError: 当调用 AI 失败
    """
    if len(news_items) < limit:
        raise ValueError(f"源新闻数量不足：需要 {limit} 条，实际 {len(news_items)} 条")
    
    # 构建提示词
    system_prompt = """你是一位专业的财经编辑。请基于提供的最新财经新闻，生成精炼的财经头条。

严格要求：
1. 只能输出 JSON 数组，不要输出任何解释、markdown 代码块或其他文本
2. 数组长度必须为 10
3. 每条头条必须基于输入的新闻内容，不得编造事实，不得出现投资建议
4. title 必须简洁有力，不超过 200 字符
5. summary 必须客观准确，不超过 500 字符
6. tags 为中文短标签（如"A股"、"货币政策"、"科技"），1-6 个
7. content 可为 null 或简短补充说明
8. is_hot 统一设为 false

输出格式示例：
[
  {
    "title": "央行降准释放流动性 A股迎来反弹",
    "summary": "中国人民银行宣布下调存款准备金率0.5个百分点，预计释放资金约1万亿元。市场对此反应积极，上证指数收涨2.3%。",
    "tags": ["货币政策", "降准", "A股"],
    "content": null,
    "is_hot": false
  }
]"""

    # 构建源新闻摘要
    news_summary = []
    for idx, item in enumerate(news_items[:limit], 1):
        news_summary.append(f"{idx}. 【{item.get('source', '未知')}】{item.get('title', '')}")
        if item.get('summary'):
            news_summary.append(f"   摘要：{item.get('summary')}")
        if item.get('time'):
            news_summary.append(f"   时间：{item.get('time')}")
        news_summary.append("")
    
    user_message = f"请基于以下 {limit} 条最新财经新闻，生成 {limit} 条精炼的财经头条：\n\n" + "\n".join(news_summary)
    
    # 调用 AI Hub
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{AI_HUB_URL}/api/ai/chat",
                json={
                    "message": user_message,
                    "system_prompt": system_prompt,
                    "model": "qwen",
                    "temperature": 0.2,
                    "max_tokens": 4000
                }
            )
            response.raise_for_status()
            ai_result = response.json()
        except httpx.HTTPError as e:
            logger.error(f"调用 AI Hub 失败：{e}")
            raise ValueError(f"AI 服务调用失败：{str(e)}")
    
    # 解析 AI 返回
    content = ai_result.get("content", "")
    if not content:
        raise ValueError("AI 返回内容为空")
    
    # 尝试解析 JSON
    headlines = _parse_json_content(content)
    
    # 验证和清洗
    if not isinstance(headlines, list):
        raise ValueError("AI 输出不是数组")
    
    if len(headlines) != limit:
        logger.warning(f"AI 生成数量不符：期望 {limit}，实际 {len(headlines)}")
        if len(headlines) < limit:
            raise ValueError(f"AI 生成数量不足：期望 {limit}，实际 {len(headlines)}")
        headlines = headlines[:limit]
    
    # 清洗和验证每条数据
    cleaned = []
    for idx, item in enumerate(headlines, 1):
        try:
            cleaned_item = _validate_and_clean_headline(item, idx)
            cleaned.append(cleaned_item)
        except ValueError as e:
            logger.error(f"第 {idx} 条头条验证失败：{e}")
            raise ValueError(f"第 {idx} 条头条不符合要求：{str(e)}")
    
    return cleaned


def _parse_json_content(content: str) -> Any:
    """
    解析 AI 返回的 JSON 内容，处理可能的 markdown 包裹
    
    Args:
        content: AI 返回的原始文本
        
    Returns:
        解析后的 Python 对象
    """
    # 去除前后空白
    content = content.strip()
    
    # 尝试提取 JSON（处理可能的 markdown 代码块）
    json_match = re.search(r'```(?:json)?\s*(\[[\s\S]*?\])\s*```', content)
    if json_match:
        content = json_match.group(1)
    
    # 如果没有代码块，尝试提取第一个 [ 到最后一个 ]
    if not content.startswith('['):
        start = content.find('[')
        end = content.rfind(']')
        if start != -1 and end != -1:
            content = content[start:end+1]
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析失败：{e}\n内容：{content[:500]}")
        raise ValueError(f"AI 输出无法解析为 JSON：{str(e)}")


def _validate_and_clean_headline(item: Dict[str, Any], index: int) -> Dict[str, Any]:
    """
    验证并清洗单条头条数据
    
    Args:
        item: 原始数据
        index: 索引（用于错误提示）
        
    Returns:
        清洗后的数据
    """
    if not isinstance(item, dict):
        raise ValueError(f"不是对象类型")
    
    # 提取和验证字段
    title = str(item.get("title", "")).strip()
    summary = str(item.get("summary", "")).strip()
    tags = item.get("tags", [])
    content = item.get("content")
    is_hot = item.get("is_hot", False)
    
    # 验证必填字段
    if not title:
        raise ValueError("title 不能为空")
    if not summary:
        raise ValueError("summary 不能为空")
    
    # 截断超长字段
    if len(title) > 200:
        logger.warning(f"第 {index} 条 title 超长，截断到 200 字符")
        title = title[:197] + "..."
    
    if len(summary) > 500:
        logger.warning(f"第 {index} 条 summary 超长，截断到 500 字符")
        summary = summary[:497] + "..."
    
    # 清洗 tags
    if not isinstance(tags, list):
        tags = []
    tags = [str(t).strip() for t in tags if str(t).strip()]
    tags = list(dict.fromkeys(tags))[:6]  # 去重并限制数量
    
    # 清洗 content
    if content is not None:
        content = str(content).strip() or None
    
    # 强制 is_hot 为 false
    is_hot = False
    
    return {
        "title": title,
        "summary": summary,
        "tags": tags,
        "content": content,
        "is_hot": is_hot
    }
