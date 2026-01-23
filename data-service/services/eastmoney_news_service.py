"""
东方财富网财经新闻聚合服务

功能：从东方财富网抓取财经新闻信息（快讯 + 文章列表双策略）
合规原则：
1. 只采集公开可访问内容的"摘要级信息"
2. 不模拟登录、不使用 Cookie、不绕过反爬
3. 控制并发与请求频率，遵守礼貌爬虫原则
4. 图片优先使用缩略图/公开图链
"""
import asyncio
import hashlib
import logging
import random
import re
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin

import httpx
from lxml import html as lxml_html
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.eastmoney_news import EastmoneyNews

logger = logging.getLogger(__name__)


class EastmoneyNewsAggregator:
    """
    东方财富网财经新闻聚合器
    
    支持两种抓取策略：
    1. 7×24 快讯接口（优先，更新频率高，天然摘要级）
    2. 财经频道文章列表（兜底，有图片，需补充摘要）
    """
    
    # 7×24 快讯接口配置（JSONP 格式）
    KUAIXUN_API_URL = "https://np-listapi.eastmoney.com/comm/web/getFastNewsList"
    KUAIXUN_PARAMS = {
        "client": "web",
        "biz": "web_724",  # 7×24小时快讯
        "fastColumn": "",  # 默认全部，可设为：yw(要闻)/ssgs(上市公司)/jjsj(基金数据)等
        "sortEnd": "",
        "pageSize": "20",
        "req_trace": str(int(time.time() * 1000)),
    }
    
    # 财经频道文章列表配置（HTML 解析）
    # 说明：部分老栏目链接会 404，暂保留稳定可用的要闻入口作为兜底来源
    NEWS_CATEGORIES = [
        {"name": "要闻", "url": "https://finance.eastmoney.com/a/cywjh.html"},
    ]
    
    # 内存缓存
    _cache: Dict[str, Dict[str, Any]] = {}
    _cache_ttl: int = 300  # 缓存 TTL（秒），默认 5 分钟
    
    def __init__(
        self,
        cache_ttl: int = 300,
        timeout: int = 10,
        max_items_per_category: int = 10,
        max_concurrent_requests: int = 3,
        db_session: Optional[AsyncSession] = None
    ):
        """
        初始化东方财富网新闻聚合器
        
        Args:
            cache_ttl: 缓存过期时间（秒）
            timeout: HTTP 请求超时时间（秒）
            max_items_per_category: 每个分类抓取的最大条数
            max_concurrent_requests: 最大并发请求数
            db_session: 数据库会话（可选，用于持久化存储）
        """
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.max_items_per_category = max_items_per_category
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.db_session = db_session
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://kuaixun.eastmoney.com/',
        }
    
    # ==================== 策略 A: 7×24 快讯接口 ====================
    
    async def fetch_kuaixun_news(self, client: httpx.AsyncClient, limit: int = 20) -> List[Dict[str, Any]]:
        """
        从 7×24 快讯接口获取新闻（优先策略）
        
        Args:
            client: httpx 客户端
            limit: 获取的最大条数
            
        Returns:
            新闻列表
        """
        try:
            params = {**self.KUAIXUN_PARAMS, "pageSize": str(min(limit, 50))}
            
            response = await client.get(
                self.KUAIXUN_API_URL,
                params=params,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                logger.error(f"快讯接口 HTTP 错误：{response.status_code}")
                return []
            
            data = response.json()
            
            code = data.get("code")
            message = (data.get("message") or "").lower()
            if not (code in (0, "0", 1, "1") or message == "success"):
                logger.error(f"快讯接口返回错误：{data.get('message', '未知错误')}")
                return []
            
            news_list = data.get("data", {}).get("fastNewsList", [])
            items = []
            
            for news in news_list[:limit]:
                try:
                    news_item = self._parse_kuaixun_item(news)
                    if news_item:
                        items.append(news_item)
                except Exception as e:
                    logger.warning(f"解析快讯项失败：{e}")
                    continue
            
            logger.info(f"快讯接口成功获取 {len(items)} 条新闻")
            return items
            
        except httpx.TimeoutException:
            logger.error("快讯接口请求超时")
            return []
        except Exception as e:
            logger.error(f"快讯接口抓取失败：{e}", exc_info=True)
            return []
    
    def _parse_kuaixun_item(self, news: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析快讯接口返回的单条新闻"""
        # 快讯接口字段示例：
        # {"newsId": "xxx", "title": "...", "digest": "...", "showTime": "01-21 10:35", 
        #  "postTime": 1737459600000, "url": "...", "image": "..."}
        
        news_id_raw = news.get("code") or news.get("newsId") or news.get("id") or ""
        title = news.get("title", "").strip()
        digest = news.get("digest", "") or news.get("summary", "") or ""
        
        # 尝试多个时间字段
        show_time = news.get("showTime", "") or news.get("showtime", "")
        post_time_ms = news.get("postTime") or news.get("posttime") or 0
        
        url = news.get("url", "") or news.get("infoUrl", "") or ""
        image = news.get("image", "") or news.get("img", "") or None
        
        # 如果没有标题，跳过
        if not title:
            return None
        
        # 生成 news_id
        if news_id_raw:
            news_id = f"eastmoney_{news_id_raw}"
        elif url:
            # 尝试从 URL 提取 ID
            match = re.search(r'/(\d{15,20})\.html', url)
            if match:
                news_id = f"eastmoney_{match.group(1)}"
            else:
                news_id = f"eastmoney_{hashlib.md5(url.encode()).hexdigest()[:16]}"
        else:
            news_id = f"eastmoney_{hashlib.md5(title.encode()).hexdigest()[:16]}"
        
        # 处理摘要
        summary = digest.strip() if digest else title
        if len(summary) > 200:
            summary = summary[:197] + "..."
        
        # 处理时间：优先使用 showTime，其次 postTime
        if show_time:
            publish_timestamp = self._parse_time_to_timestamp(show_time)
        elif post_time_ms and post_time_ms > 1000000000000:
            # 毫秒级时间戳
            publish_timestamp = int(post_time_ms / 1000)
        elif post_time_ms:
            publish_timestamp = int(post_time_ms)
        else:
            publish_timestamp = int(time.time())
        
        formatted_time = self._format_time_from_timestamp(publish_timestamp)
        
        # 确保 URL 完整
        if url and not url.startswith('http'):
            url = urljoin('https://kuaixun.eastmoney.com', url)
        
        return {
            "id": news_id,
            "title": title[:200],
            "summary": summary,
            "source": "东方财富网",
            "time": formatted_time,
            "url": url,
            "img": image if image else None,
            "author": "快讯",
            "publish_timestamp": publish_timestamp
        }
    
    # ==================== 策略 B: 财经频道文章列表 ====================
    
    async def fetch_category_news(self, category: Dict[str, str], client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """
        抓取单个分类的新闻内容（HTML 解析策略）
        
        Args:
            category: 分类信息，包含 name, url
            client: httpx 客户端
            
        Returns:
            新闻列表
        """
        name = category.get("name", "未知分类")
        url = category.get("url")
        
        if not url:
            logger.warning(f"分类配置不完整，跳过：{category}")
            return []
        
        async with self.semaphore:  # 限流
            try:
                # 添加随机延迟（100~300ms）
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
                response = await client.get(
                    url, 
                    headers={**self.headers, 'Referer': 'https://finance.eastmoney.com/'},
                    timeout=self.timeout,
                    follow_redirects=True
                )
                
                if response.status_code != 200:
                    if response.status_code == 404:
                        logger.warning(f"抓取分类 {name} 404，已跳过：{url}")
                    else:
                        logger.error(f"抓取分类 {name} HTTP 错误：{response.status_code}")
                    return []
                
                return await self._parse_category_html(response.content, name, client)
                
            except httpx.TimeoutException:
                logger.error(f"抓取分类 {name} 超时")
                return []
            except Exception as e:
                logger.error(f"抓取分类 {name} 失败：{e}", exc_info=True)
                return []
    
    async def _parse_category_html(self, content: bytes, category_name: str, client: httpx.AsyncClient) -> List[Dict[str, Any]]:
        """解析分类列表页 HTML"""
        try:
            tree = lxml_html.fromstring(content)
            news_items = []
            
            # 东方财富网新闻列表的多种选择器
            selectors = [
                '//div[@id="newsListContent"]//li',
                '//ul[@class="newlist"]/li',
                '//div[contains(@class, "news")]//li[contains(@class, "item")]',
                '//ul[contains(@class, "list")]/li',
            ]
            
            news_elements = []
            for selector in selectors:
                news_elements = tree.xpath(selector)
                if news_elements:
                    break
            
            for item in news_elements[:self.max_items_per_category]:
                try:
                    news_item = self._parse_list_item(item, category_name)
                    if news_item:
                        news_items.append(news_item)
                except Exception as e:
                    logger.debug(f"解析列表项失败：{e}")
                    continue
            
            logger.info(f"分类 {category_name} 成功解析 {len(news_items)} 条新闻")
            return news_items
            
        except Exception as e:
            logger.error(f"解析分类 HTML 失败：{e}")
            return []
    
    def _parse_list_item(self, item, category_name: str) -> Optional[Dict[str, Any]]:
        """解析列表页中的单个新闻条目"""
        # 提取标题和链接
        title_elem = item.xpath('.//a[@title]')
        if not title_elem:
            title_elem = item.xpath('.//a[contains(@href, "/a/")]')
        if not title_elem:
            title_elem = item.xpath('.//a')
        
        if not title_elem:
            return None
        
        title = title_elem[0].get('title') or title_elem[0].text_content().strip()
        link = title_elem[0].get('href', '')
        
        if not title or not link:
            return None
        
        # 确保链接是完整的 URL
        if link and not link.startswith('http'):
            link = urljoin('https://finance.eastmoney.com', link)
        
        # 从 URL 提取文章 ID
        match = re.search(r'/a/(\d+)\.html', link)
        if match:
            news_id = f"eastmoney_{match.group(1)}"
        else:
            news_id = f"eastmoney_{hashlib.md5(link.encode()).hexdigest()[:16]}"
        
        # 提取时间
        time_elem = item.xpath('.//span[contains(@class, "time")]//text() | .//span[@class="date"]//text() | .//span[@class="sj"]//text()')
        time_str = time_elem[0].strip() if time_elem else ""
        publish_timestamp = self._parse_time_to_timestamp(time_str)
        formatted_time = self._format_time_from_timestamp(publish_timestamp) if not time_str else self._format_time(time_str)
        
        # 提取摘要（列表页可能没有完整摘要）
        summary_elem = item.xpath('.//p[contains(@class, "info")]//text() | .//div[contains(@class, "info")]//text() | .//p//text()')
        summary_texts = [s.strip() for s in summary_elem if s.strip()]
        summary = ' '.join(summary_texts)[:200] if summary_texts else title
        
        # 提取图片
        img_elem = item.xpath('.//img/@src')
        img_url = None
        if img_elem:
            img_url = img_elem[0]
            if img_url and not img_url.startswith('http'):
                img_url = urljoin('https://finance.eastmoney.com', img_url)
        
        return {
            "id": news_id,
            "title": title[:200],
            "summary": summary if summary else title[:200],
            "source": "东方财富网",
            "time": formatted_time,
            "url": link,
            "img": img_url,
            "author": category_name,
            "publish_timestamp": publish_timestamp
        }
    
    # ==================== 聚合与缓存逻辑 ====================
    
    async def aggregate_news(
        self,
        limit: int = 20,
        keyword: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        聚合新闻内容（主入口方法）
        
        采用多策略回退：
        1. 优先使用快讯接口（稳定、更新快）
        2. 快讯接口失败时，回退到文章列表解析
        
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
        
        # 尝试抓取新闻
        try:
            all_news = []
            
            async with httpx.AsyncClient() as client:
                # 策略 A：优先使用快讯接口
                all_news = await self.fetch_kuaixun_news(client, limit=limit * 2)
                
                # 策略 B：如果快讯接口数据不足，补充文章列表
                if len(all_news) < limit:
                    logger.info(f"快讯数据不足（{len(all_news)}条），尝试补充文章列表数据")
                    
                    tasks = [
                        self.fetch_category_news(category, client)
                        for category in self.NEWS_CATEGORIES
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for result in results:
                        if isinstance(result, Exception):
                            logger.warning(f"抓取分类失败：{result}")
                            continue
                        all_news.extend(result)
            
            # 去重（根据 id）
            unique_news = {news["id"]: news for news in all_news}
            all_news = list(unique_news.values())
            
            # 关键词过滤（大小写不敏感）
            if keyword:
                keyword_lower = keyword.lower()
                all_news = [
                    news for news in all_news
                    if keyword_lower in news["title"].lower() or keyword_lower in news.get("summary", "").lower()
                ]
            
            # 按发布时间倒序排序
            all_news.sort(key=lambda x: x.get("publish_timestamp", 0), reverse=True)
            
            # 限制数量
            all_news = all_news[:limit]
            
            # 准备返回数据（移除内部字段）
            result_items = []
            for news in all_news:
                item = {
                    "id": news["id"],
                    "title": news["title"],
                    "summary": news.get("summary", news["title"]),
                    "source": news.get("source", "东方财富网"),
                    "time": news.get("time", ""),
                    "url": news.get("url", ""),
                    "img": news.get("img"),
                    "author": news.get("author")
                }
                result_items.append(item)
            
            result_data = {
                "items": result_items,
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
            
            logger.info(f"成功聚合东方财富网新闻，共 {len(result_items)} 条")
            return result_data
            
        except Exception as e:
            logger.error(f"聚合东方财富新闻失败：{e}", exc_info=True)
            
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
    
    # ==================== 数据库操作 ====================
    
    async def _save_to_database(self, posts: List[Dict[str, Any]]) -> None:
        """
        将新闻数据保存到数据库（upsert 语义：存在则更新，不存在则插入）
        
        Args:
            posts: 新闻列表
        """
        if not self.db_session:
            return
        
        try:
            saved_count = 0
            updated_count = 0
            
            for post in posts:
                news_id = post["id"]
                
                # 检查是否已存在
                stmt = select(EastmoneyNews).where(EastmoneyNews.news_id == news_id)
                result = await self.db_session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    # 更新已有记录
                    existing.title = post["title"]
                    existing.summary = post.get("summary", post["title"])
                    existing.url = post.get("url")
                    existing.img_url = post.get("img")
                    existing.publish_time = post.get("time", "")
                    existing.publish_timestamp = post.get("publish_timestamp", int(time.time()))
                    existing.author = post.get("author")
                    existing.updated_at = datetime.now()
                    updated_count += 1
                else:
                    # 创建新记录
                    news = EastmoneyNews(
                        news_id=news_id,
                        title=post["title"],
                        summary=post.get("summary", post["title"]),
                        source=post.get("source", "东方财富网"),
                        author=post.get("author"),
                        url=post.get("url"),
                        img_url=post.get("img"),
                        publish_time=post.get("time", ""),
                        publish_timestamp=post.get("publish_timestamp", int(time.time()))
                    )
                    self.db_session.add(news)
                    saved_count += 1
            
            await self.db_session.commit()
            logger.info(f"数据库操作完成：新增 {saved_count} 条，更新 {updated_count} 条")
            
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
            keyword: 关键词过滤（大小写不敏感）
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
            stmt = select(EastmoneyNews).where(
                EastmoneyNews.publish_timestamp >= cutoff_timestamp
            )
            
            # 关键词过滤（大小写不敏感）
            if keyword:
                keyword_filter = f"%{keyword}%"
                stmt = stmt.where(
                    (EastmoneyNews.title.ilike(keyword_filter)) | 
                    (EastmoneyNews.summary.ilike(keyword_filter))
                )
            
            # 排序和限制
            stmt = stmt.order_by(desc(EastmoneyNews.publish_timestamp)).limit(limit)
            
            result = await self.db_session.execute(stmt)
            news_list = result.scalars().all()
            
            # 转换为字典格式（符合 NewsItem 契约）
            return [
                {
                    "id": news.news_id,
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
    
    # ==================== 工具方法 ====================
    
    def _format_time(self, time_str: str) -> str:
        """
        格式化时间为人类可读格式
        
        Args:
            time_str: 时间字符串，如 "2026-01-21 14:30" 或 "01-21 14:30"
            
        Returns:
            格式化后的时间字符串，如 "2小时前"、"1天前"、"2026-01-21 14:30"
        """
        if not time_str:
            return "未知时间"
        
        try:
            now = datetime.now()
            
            # 处理相对时间（已经是相对格式）
            if "分钟前" in time_str or "小时前" in time_str or "天前" in time_str or "刚刚" in time_str:
                return time_str
            
            # 处理今天/昨天
            if "今天" in time_str:
                return time_str
            if "昨天" in time_str:
                return time_str
            
            # 尝试解析完整日期时间
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m-%d %H:%M", "%Y-%m-%d", "%m月%d日 %H:%M", "%m月%d日"]:
                try:
                    if fmt in ["%m-%d %H:%M", "%m月%d日 %H:%M", "%m月%d日"]:
                        dt = datetime.strptime(time_str, fmt)
                        # 处理跨年情况
                        dt = dt.replace(year=now.year)
                        if dt > now:
                            dt = dt.replace(year=now.year - 1)
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
                        return dt.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    continue
            
            # 无法解析，返回原始字符串
            return time_str
        except Exception:
            return time_str
    
    def _format_time_from_timestamp(self, timestamp: int) -> str:
        """从时间戳生成人类可读的时间字符串"""
        try:
            now = datetime.now()
            dt = datetime.fromtimestamp(timestamp)
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
                return dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return "未知时间"
    
    def _parse_time_to_timestamp(self, time_str: str) -> int:
        """将时间字符串转换为时间戳（用于排序）"""
        if not time_str:
            return int(time.time())
        
        try:
            now = datetime.now()
            
            # 处理相对时间
            if "刚刚" in time_str:
                return int(time.time())
            elif "分钟前" in time_str:
                match = re.search(r'(\d+)', time_str)
                if match:
                    minutes = int(match.group(1))
                    return int((now - timedelta(minutes=minutes)).timestamp())
            elif "小时前" in time_str:
                match = re.search(r'(\d+)', time_str)
                if match:
                    hours = int(match.group(1))
                    return int((now - timedelta(hours=hours)).timestamp())
            elif "天前" in time_str:
                match = re.search(r'(\d+)', time_str)
                if match:
                    days = int(match.group(1))
                    return int((now - timedelta(days=days)).timestamp())
            
            # 尝试解析完整日期时间
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m-%d %H:%M", "%Y-%m-%d", "%m月%d日 %H:%M", "%m月%d日"]:
                try:
                    if fmt in ["%m-%d %H:%M", "%m月%d日 %H:%M", "%m月%d日"]:
                        dt = datetime.strptime(time_str, fmt)
                        dt = dt.replace(year=now.year)
                        # 处理跨年情况
                        if dt > now:
                            dt = dt.replace(year=now.year - 1)
                    else:
                        dt = datetime.strptime(time_str, fmt)
                    return int(dt.timestamp())
                except ValueError:
                    continue
            
            return int(time.time())
        except Exception:
            return int(time.time())


# 全局单例
_aggregator_instance: Optional[EastmoneyNewsAggregator] = None


def get_eastmoney_news_aggregator(
    cache_ttl: int = 300,
    timeout: int = 10,
    max_items_per_category: int = 10,
    db_session: Optional[AsyncSession] = None
) -> EastmoneyNewsAggregator:
    """获取全局东方财富新闻聚合器实例"""
    global _aggregator_instance
    if _aggregator_instance is None:
        _aggregator_instance = EastmoneyNewsAggregator(
            cache_ttl=cache_ttl,
            timeout=timeout,
            max_items_per_category=max_items_per_category,
            db_session=db_session
        )
    return _aggregator_instance
