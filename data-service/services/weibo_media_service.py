"""
东方财富网财经新闻聚合服务

功能：从东方财富网抓取财经新闻信息
合规原则：
1. 只采集公开可访问内容的"摘要级信息"
2. 图片优先使用缩略图/公开图链
3. 遵守网站的 robots.txt 和访问频率限制
"""
import asyncio
import hashlib
import logging
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, quote

import httpx
from lxml import html as lxml_html
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.weibo_news import WeiboNews

logger = logging.getLogger(__name__)


class WeiboMediaAggregator:
    """东方财富网财经新闻聚合器"""
    
    # 东方财富网新闻分类
    NEWS_CATEGORIES = [
        {"name": "要闻", "url": "https://finance.eastmoney.com/a/cywjh.html"},
        {"name": "股票", "url": "https://finance.eastmoney.com/a/cgpzx.html"},
        {"name": "基金", "url": "https://finance.eastmoney.com/a/cjjyj.html"},
        {"name": "全球", "url": "https://finance.eastmoney.com/a/cqqzx.html"},
    ]
    
    # 内存缓存
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_ttl: int = 300  # 缓存 TTL（秒），默认 5 分钟
    
    def __init__(
        self,
        news_categories: Optional[List[Dict[str, str]]] = None,
        cache_ttl: int = 300,
        timeout: int = 10,
        max_items_per_category: int = 10,
        db_session: Optional[AsyncSession] = None
    ):
        """
        初始化东方财富网新闻聚合器
        
        Args:
            news_categories: 新闻分类列表，每个分类包含 name, url
            cache_ttl: 缓存过期时间（秒）
            timeout: HTTP 请求超时时间（秒）
            max_items_per_category: 每个分类抓取的最大条数
            db_session: 数据库会话（可选，用于持久化存储）
        """
        self.news_categories = news_categories or self.NEWS_CATEGORIES
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.max_items_per_category = max_items_per_category
        self.db_session = db_session
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://finance.eastmoney.com/',
        }
    
    async def fetch_category_news(self, category: Dict[str, str], client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """
        抓取单个分类的新闻内容
        
        Args:
            category: 分类信息，包含 name, url
            client: httpx 客户端
            
        Returns:
            新闻列表，每条包含 id, title, summary, time, url, img, author
        """
        name = category.get("name", "未知分类")
        url = category.get("url")
        
        if not url:
            logger.warning(f"分类配置不完整，跳过：{category}")
            return []
        
        try:
            # 请求新闻列表页
            response = await client.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout,
                follow_redirects=True
            )
            
            if response.status_code != 200:
                logger.error(f"抓取分类 {name} HTTP 错误：{response.status_code}")
                return []
            
            # 解析 HTML
            tree = lxml_html.fromstring(response.content)
            news_items = []
            
            # 尝试多种选择器以适应不同页面结构
            # 东方财富网新闻列表通常在 ul.newslist 或类似结构中
            selectors = [
                '//div[@class="newslist"]//li',
                '//ul[@class="newslist"]//li',
                '//div[contains(@class, "news")]//li',
                '//div[@id="newsListContent"]//li',
            ]
            
            news_elements = []
            for selector in selectors:
                news_elements = tree.xpath(selector)
                if news_elements:
                    break
            
            for item in news_elements[:self.max_items_per_category]:
                try:
                    # 提取标题和链接
                    title_elem = item.xpath('.//a[@title]')
                    if not title_elem:
                        title_elem = item.xpath('.//a')
                    
                    if not title_elem:
                        continue
                    
                    title = title_elem[0].get('title') or title_elem[0].text_content().strip()
                    link = title_elem[0].get('href', '')
                    
                    # 确保链接是完整的 URL
                    if link and not link.startswith('http'):
                        link = urljoin('https://finance.eastmoney.com', link)
                    
                    # 提取时间
                    time_elem = item.xpath('.//span[contains(@class, "time")]//text() | .//span[@class="date"]//text()')
                    time_str = time_elem[0].strip() if time_elem else ""
                    formatted_time = self._format_time(time_str)
                    
                    # 提取摘要（如果有）
                    summary_elem = item.xpath('.//p[@class="info"]//text() | .//div[@class="info"]//text()')
                    summary = summary_elem[0].strip() if summary_elem else title
                    
                    # 提取图片（如果有）
                    img_elem = item.xpath('.//img/@src')
                    img_url = img_elem[0] if img_elem else None
                    
                    # 生成唯一 ID
                    news_id = f"eastmoney_{hashlib.md5(link.encode()).hexdigest()[:16]}"
                    
                    # 解析时间戳
                    timestamp = self._parse_time_to_timestamp(time_str)
                    
                    news_items.append({
                        "id": news_id,
                        "title": title[:200],  # 限制长度
                        "summary": summary[:500] if summary else title[:500],
                        "source": "东方财富网",
                        "time": formatted_time,
                        "url": link,
                        "img": img_url,
                        "author": name,  # 使用分类名作为作者
                        "created_timestamp": timestamp
                    })
                    
                except Exception as e:
                    logger.warning(f"解析新闻项失败：{e}")
                    continue
            
            logger.info(f"成功抓取分类 {name}，获得 {len(news_items)} 条新闻")
            return news_items
            
        except httpx.TimeoutException:
            logger.error(f"抓取分类 {name} 超时")
            return []
        except httpx.HTTPStatusError as e:
            logger.error(f"抓取分类 {name} HTTP 错误：{e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"抓取分类 {name} 失败：{e}", exc_info=True)
            return []
    
    def _clean_html(self, html_text: str) -> str:
        """清理 HTML 标签，返回纯文本"""
        try:
            tree = lxml_html.fromstring(html_text)
            return tree.text_content().strip()
        except Exception:
            # 降级：使用正则表达式清理
            return re.sub(r'<[^>]+>', '', html_text).strip()
    
    def _extract_title_summary(self, text: str, max_title_len: int = 50, max_summary_len: int = 150) -> tuple:
        """
        从文本中提取标题和摘要
        
        Args:
            text: 原始文本
            max_title_len: 标题最大长度
            max_summary_len: 摘要最大长度
            
        Returns:
            (title, summary)
        """
        if not text:
            return "无标题", "无内容"
        
        # 如果文本足够短，标题和摘要相同
        if len(text) <= max_title_len:
            return text, text
        
        # 标题：前 max_title_len 个字符
        title = text[:max_title_len] + "..." if len(text) > max_title_len else text
        
        # 摘要：前 max_summary_len 个字符
        summary = text[:max_summary_len] + "..." if len(text) > max_summary_len else text
        
        return title, summary
    
    def _extract_image(self, mblog: Dict[str, Any]) -> Optional[str]:
        """
        提取微博图片链接（优先使用缩略图）
        
        Args:
            mblog: 微博数据
            
        Returns:
            图片 URL 或 None
        """
        # 优先使用 pic_infos
        pic_infos = mblog.get("pic_infos", {})
        if pic_infos:
            first_pic = next(iter(pic_infos.values()), None)
            if first_pic:
                # 使用缩略图（thumbnail）
                thumbnail = first_pic.get("thumbnail", {})
                if thumbnail and thumbnail.get("url"):
                    return thumbnail["url"]
                
                # 降级到原图（但优先使用小图）
                if first_pic.get("url"):
                    return first_pic["url"]
        
        # 备选方案：使用 pics 字段
        pics = mblog.get("pics", [])
        if pics and len(pics) > 0:
            return pics[0].get("url")
        
        # 无图
        return None
    
    def _format_time(self, time_str: str) -> str:
        """
        格式化时间为人类可读格式
        
        Args:
            time_str: 时间字符串，如 "2026-01-21 14:30" 或 "01-21 14:30"
            
        Returns:
            格式化后的时间字符串，如 "2小时前"、"1天前"、"2026-01-21"
        """
        if not time_str:
            return "未知时间"
        
        try:
            # 尝试解析东方财富网的时间格式
            now = datetime.now()
            
            # 处理相对时间
            if "分钟前" in time_str or "小时前" in time_str or "天前" in time_str:
                return time_str
            
            # 处理今天/昨天
            if "今天" in time_str:
                time_part = time_str.replace("今天", "").strip()
                return f"今天 {time_part}" if time_part else "今天"
            if "昨天" in time_str:
                return "昨天"
            
            # 尝试解析完整日期时间
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m-%d %H:%M", "%Y-%m-%d"]:
                try:
                    if fmt == "%m-%d %H:%M":
                        dt = datetime.strptime(time_str, fmt)
                        dt = dt.replace(year=now.year)
                    else:
                        dt = datetime.strptime(time_str, fmt)
                    
                    delta = now - dt
                    
                    if delta.total_seconds() < 60:
                        return "刚刚"
                    elif delta.total_seconds() < 3600:
                        return f"{int(delta.total_seconds() / 60)}分钟前"
                    elif delta.total_seconds() < 86400:
                        return f"{int(delta.total_seconds() / 3600)}小时前"
                    elif delta.days < 7:
                        return f"{delta.days}天前"
                    else:
                        return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            # 无法解析，返回原始字符串
            return time_str
        except Exception:
            return time_str
    
    def _parse_time_to_timestamp(self, time_str: str) -> int:
        """将时间字符串转换为时间戳（用于排序）"""
        if not time_str:
            return int(time.time())
        
        try:
            now = datetime.now()
            
            # 处理相对时间
            if "分钟前" in time_str:
                minutes = int(re.search(r'(\d+)', time_str).group(1))
                return int((now - timedelta(minutes=minutes)).timestamp())
            elif "小时前" in time_str:
                hours = int(re.search(r'(\d+)', time_str).group(1))
                return int((now - timedelta(hours=hours)).timestamp())
            elif "天前" in time_str:
                days = int(re.search(r'(\d+)', time_str).group(1))
                return int((now - timedelta(days=days)).timestamp())
            
            # 尝试解析完整日期时间
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m-%d %H:%M", "%Y-%m-%d"]:
                try:
                    if fmt == "%m-%d %H:%M":
                        dt = datetime.strptime(time_str, fmt)
                        dt = dt.replace(year=now.year)
                    else:
                        dt = datetime.strptime(time_str, fmt)
                    return int(dt.timestamp())
                except ValueError:
                    continue
            
            return int(time.time())
        except Exception:
            return int(time.time())
    
    async def aggregate_news(
        self,
        limit: int = 20,
        keyword: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        聚合所有分类的新闻内容
        
        Args:
            limit: 返回的最大条数
            keyword: 关键词过滤（在标题/摘要中搜索）
            use_cache: 是否使用缓存
            
        Returns:
            {
                "items": [...],
                "cached": bool,  # 是否来自缓存
                "stale": bool,   # 缓存是否过期（降级场景）
                "timestamp": int # 数据时间戳
            }
        """
        cache_key = f"eastmoney_news_{limit}_{keyword or 'all'}"
        
        # 检查缓存
        if use_cache and cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            cache_age = time.time() - cache_entry["timestamp"]
            
            if cache_age < self.cache_ttl:
                logger.info(f"命中缓存，cache_key={cache_key}, age={cache_age:.1f}s")
                return {
                    **cache_entry["data"],
                    "cached": True,
                    "stale": False
                }
        
        # 抓取所有分类的新闻
        try:
            all_news = []
            
            async with httpx.AsyncClient() as client:
                # 并发抓取所有分类
                tasks = [
                    self.fetch_category_news(category, client)
                    for category in self.news_categories
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        logger.error(f"抓取分类失败：{result}")
                        continue
                    all_news.extend(result)
            
            # 去重（根据 id）
            unique_news = {news["id"]: news for news in all_news}
            all_news = list(unique_news.values())
            
            # 关键词过滤
            if keyword:
                keyword_lower = keyword.lower()
                all_news = [
                    news for news in all_news
                    if keyword_lower in news["title"].lower() or keyword_lower in news["summary"].lower()
                ]
            
            # 按发布时间倒序排序
            all_news.sort(key=lambda x: x.get("created_timestamp", 0), reverse=True)
            
            # 限制数量
            all_news = all_news[:limit]
            
            # 移除内部字段
            for news in all_news:
                news.pop("created_timestamp", None)
            
            result_data = {
                "items": all_news,
                "cached": False,
                "stale": False,
                "timestamp": int(time.time())
            }
            
            # 更新缓存
            self._cache[cache_key] = {
                "data": result_data,
                "timestamp": time.time()
            }
            
            # 保存到数据库（如果配置了数据库会话）
            if self.db_session:
                await self._save_to_database(all_news)
            
            logger.info(f"成功聚合东方财富网新闻，共 {len(all_news)} 条")
            return result_data
            
        except Exception as e:
            logger.error(f"聚合微博新闻失败：{e}", exc_info=True)
            
            # 降级：返回缓存旧数据（如果有）
            if cache_key in self._cache:
                cache_entry = self._cache[cache_key]
                logger.warning(f"使用过期缓存数据降级，cache_key={cache_key}")
                return {
                    **cache_entry["data"],
                    "cached": True,
                    "stale": True
                }
            
            # 无缓存：返回空列表
            return {
                "items": [],
                "cached": False,
                "stale": False,
                "timestamp": int(time.time()),
                "error": "抓取失败且无缓存数据"
            }
    
    async def _save_to_database(self, posts: List[Dict[str, Any]]) -> None:
        """
        将新闻数据保存到数据库
        
        Args:
            posts: 新闻列表
        """
        if not self.db_session:
            return
        
        try:
            saved_count = 0
            for post in posts:
                # 检查是否已存在
                stmt = select(WeiboNews).where(WeiboNews.weibo_id == post["id"])
                result = await self.db_session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    # 更新已有记录
                    existing.title = post["title"]
                    existing.summary = post["summary"]
                    existing.url = post.get("url")
                    existing.img_url = post.get("img")
                    existing.publish_time = post["time"]
                    existing.updated_at = datetime.now()
                else:
                    # 创建新记录
                    news = WeiboNews(
                        weibo_id=post["id"],
                        title=post["title"],
                        summary=post["summary"],
                        source=post.get("source", "新浪微博"),
                        author=post.get("author"),
                        url=post.get("url"),
                        img_url=post.get("img"),
                        publish_time=post["time"],
                        publish_timestamp=post.get("created_timestamp", 0)
                    )
                    self.db_session.add(news)
                    saved_count += 1
            
            await self.db_session.commit()
            logger.info(f"成功保存 {saved_count} 条新闻到数据库")
        except Exception as e:
            logger.error(f"保存新闻到数据库失败：{e}", exc_info=True)
            await self.db_session.rollback()
    
    async def get_news_from_database(
        self,
        limit: int = 20,
        keyword: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        从数据库查询历史新闻
        
        Args:
            limit: 返回的最大条数
            keyword: 关键词过滤
            hours: 查询最近多少小时的数据
            
        Returns:
            新闻列表
        """
        if not self.db_session:
            return []
        
        try:
            # 计算时间范围
            cutoff_timestamp = int(time.time()) - (hours * 3600)
            
            # 构建查询
            stmt = select(WeiboNews).where(
                WeiboNews.publish_timestamp >= cutoff_timestamp
            )
            
            # 关键词过滤
            if keyword:
                keyword_filter = f"%{keyword}%"
                stmt = stmt.where(
                    (WeiboNews.title.like(keyword_filter)) | 
                    (WeiboNews.summary.like(keyword_filter))
                )
            
            # 排序和限制
            stmt = stmt.order_by(desc(WeiboNews.publish_timestamp)).limit(limit)
            
            result = await self.db_session.execute(stmt)
            news_list = result.scalars().all()
            
            # 转换为字典格式
            return [
                {
                    "id": news.weibo_id,
                    "title": news.title,
                    "summary": news.summary,
                    "source": news.source,
                    "time": news.publish_time,
                    "url": news.url,
                    "img": news.img_url,
                    "author": news.author
                }
                for news in news_list
            ]
        except Exception as e:
            logger.error(f"从数据库查询新闻失败：{e}", exc_info=True)
            return []


# 全局单例
_aggregator_instance: Optional[WeiboMediaAggregator] = None


def get_weibo_media_aggregator(
    cache_ttl: int = 300,
    timeout: int = 10,
    max_items_per_account: int = 10,
    db_session: Optional[AsyncSession] = None
) -> WeiboMediaAggregator:
    """获取全局微博媒体聚合器实例"""
    global _aggregator_instance
    if _aggregator_instance is None:
        _aggregator_instance = WeiboMediaAggregator(
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_items_per_account=max_items_per_account,
            db_session=db_session
        )
    return _aggregator_instance
