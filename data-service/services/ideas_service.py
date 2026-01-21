"""
投资观点聚合服务
从东方财富网和新浪财经聚合投资观点、研报、分析师评论
"""
import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

import httpx
from lxml import html as lxml_html
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.finance_channel_cache import FinanceChannelCache

logger = logging.getLogger(__name__)


class IdeasAggregator:
    """投资观点聚合器"""
    
    # 缓存 TTL（秒）
    CACHE_TTL = 1800  # 30 分钟
    
    def __init__(
        self,
        cache_ttl: int = CACHE_TTL,
        timeout: int = 10,
        db_session: Optional[AsyncSession] = None
    ):
        """
        初始化投资观点聚合器
        
        Args:
            cache_ttl: 缓存过期时间（秒）
            timeout: HTTP 请求超时时间（秒）
            db_session: 数据库会话
        """
        self.cache_ttl = cache_ttl
        self.timeout = timeout
        self.db_session = db_session
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.eastmoney.com/',
        }
    
    async def fetch_ideas(self, limit: int = 10, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        抓取投资观点
        
        Args:
            limit: 返回条数
            keyword: 关键词过滤
            
        Returns:
            观点列表
        """
        try:
            # 这里提供模拟数据，真实场景需要爬取实际网站
            ideas = [
                {
                    "id": f"idea_{datetime.now().timestamp()}_1",
                    "title": "2025年A股市场展望：科技创新引领新周期",
                    "author": "张首席分析师",
                    "source": "东方财富证券",
                    "content": "预计2025年科技板块将继续领涨，建议关注人工智能、半导体和新能源三大赛道。随着政策支持加码，科技创新将成为推动市场上涨的核心驱动力。",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "url": "https://finance.eastmoney.com/example1"
                },
                {
                    "id": f"idea_{datetime.now().timestamp()}_2",
                    "title": "价值投资策略：关注低估值蓝筹股机会",
                    "author": "李资深顾问",
                    "source": "中信证券",
                    "content": "当前市场结构性分化明显，部分传统蓝筹股估值处于历史低位，具备配置价值。建议投资者关注金融、地产、基建等低估值板块。",
                    "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                    "url": "https://finance.eastmoney.com/example2"
                },
                {
                    "id": f"idea_{datetime.now().timestamp()}_3",
                    "title": "新能源汽车产业链投资机会分析",
                    "author": "王行业研究员",
                    "source": "国泰君安",
                    "content": "新能源汽车渗透率持续提升，产业链上下游均有投资价值。重点关注动力电池、智能驾驶、充电桩等细分领域的龙头企业。",
                    "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                    "url": "https://finance.eastmoney.com/example3"
                },
                {
                    "id": f"idea_{datetime.now().timestamp()}_4",
                    "title": "量化策略在震荡市中的应用",
                    "author": "赵量化团队",
                    "source": "华泰证券",
                    "content": "在当前震荡行情下，量化策略可以有效降低回撤，提高收益稳定性。多因子模型和市场中性策略表现突出，建议投资者适当配置量化产品。",
                    "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                    "url": "https://finance.eastmoney.com/example4"
                },
            ]
            
            # 关键词过滤
            if keyword:
                keyword_lower = keyword.lower()
                ideas = [
                    idea for idea in ideas
                    if keyword_lower in idea["title"].lower() or keyword_lower in idea["content"].lower()
                ]
            
            # 限制数量
            ideas = ideas[:limit]
            
            logger.info(f"成功构造 {len(ideas)} 条投资观点")
            return ideas
            
        except Exception as e:
            logger.error(f"抓取投资观点失败：{e}")
            return []
    
    async def get_from_cache(self, keyword: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        从数据库缓存获取数据
        
        Args:
            keyword: 关键词（用于构造缓存键）
            
        Returns:
            缓存数据或 None
        """
        if not self.db_session:
            return None
        
        try:
            cache_key = f"ideas:{keyword or 'all'}"
            
            stmt = select(FinanceChannelCache).where(
                FinanceChannelCache.cache_key == cache_key
            ).order_by(FinanceChannelCache.fetched_at.desc())
            
            result = await self.db_session.execute(stmt)
            cache_record = result.scalars().first()
            
            if not cache_record:
                return None
            
            now = datetime.now()
            is_stale = now > cache_record.expires_at
            
            return {
                "items": cache_record.payload_json.get("items", []),
                "cached": True,
                "stale": is_stale,
                "source": cache_record.source,
                "updated_at": cache_record.fetched_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"从缓存读取观点数据失败：{e}")
            return None
    
    async def save_to_cache(self, items: List[Dict[str, Any]], keyword: Optional[str] = None, source: str = "eastmoney") -> None:
        """
        保存数据到数据库缓存
        
        Args:
            items: 观点列表
            keyword: 关键词
            source: 数据源
        """
        if not self.db_session:
            return
        
        try:
            cache_key = f"ideas:{keyword or 'all'}"
            now = datetime.now()
            expires_at = now + timedelta(seconds=self.cache_ttl)
            
            # 查找现有记录
            stmt = select(FinanceChannelCache).where(
                FinanceChannelCache.cache_key == cache_key
            )
            result = await self.db_session.execute(stmt)
            cache_record = result.scalars().first()
            
            if cache_record:
                # 更新现有记录
                cache_record.payload_json = {"items": items}
                cache_record.source = source
                cache_record.fetched_at = now
                cache_record.expires_at = expires_at
                cache_record.updated_at = now
            else:
                # 创建新记录
                cache_record = FinanceChannelCache(
                    cache_key=cache_key,
                    module="ideas",
                    payload_json={"items": items},
                    source=source,
                    fetched_at=now,
                    expires_at=expires_at
                )
                self.db_session.add(cache_record)
            
            await self.db_session.commit()
            logger.info(f"观点数据已保存到缓存（{cache_key}）")
            
        except Exception as e:
            logger.error(f"保存观点数据到缓存失败：{e}")
            await self.db_session.rollback()
    
    async def aggregate_ideas(self, limit: int = 10, keyword: Optional[str] = None) -> Dict[str, Any]:
        """
        聚合投资观点数据（缓存优先，失败降级）
        
        Args:
            limit: 返回条数
            keyword: 关键词过滤
            
        Returns:
            观点数据响应字典
        """
        try:
            # 1. 尝试从缓存读取
            cached_data = await self.get_from_cache(keyword)
            
            if cached_data and not cached_data["stale"]:
                # 缓存有效，直接返回
                logger.info(f"使用有效缓存的观点数据（keyword={keyword}）")
                return cached_data
            
            # 2. 缓存过期或不存在，重新抓取
            logger.info(f"缓存过期或不存在，重新抓取观点数据（keyword={keyword}）")
            items = await self.fetch_ideas(limit=limit, keyword=keyword)
            
            if not items:
                # 抓取失败，返回过期缓存（如果有）
                if cached_data:
                    logger.warning("抓取失败，返回过期缓存数据")
                    return cached_data
                else:
                    logger.error("抓取失败且无缓存数据")
                    return {
                        "items": [],
                        "cached": False,
                        "stale": True,
                        "source": "none",
                        "updated_at": datetime.now().isoformat()
                    }
            
            # 3. 保存到缓存
            await self.save_to_cache(items, keyword=keyword, source="simulated")
            
            # 4. 返回新数据
            return {
                "items": items,
                "cached": False,
                "stale": False,
                "source": "simulated",
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"聚合观点数据失败：{e}", exc_info=True)
            
            # 降级：尝试返回缓存
            cached_data = await self.get_from_cache(keyword)
            if cached_data:
                logger.warning("发生异常，返回缓存数据")
                return cached_data
            
            # 无缓存，返回空数据
            return {
                "items": [],
                "cached": False,
                "stale": True,
                "source": "none",
                "updated_at": datetime.now().isoformat()
            }


# 全局单例
_ideas_aggregator: Optional[IdeasAggregator] = None


def get_ideas_aggregator(db_session: Optional[AsyncSession] = None) -> IdeasAggregator:
    """获取投资观点聚合器单例"""
    global _ideas_aggregator
    if _ideas_aggregator is None or db_session is not None:
        _ideas_aggregator = IdeasAggregator(db_session=db_session)
    return _ideas_aggregator
