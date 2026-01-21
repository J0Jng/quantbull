"""
政策法规聚合服务
从证监会、央行等官方网站聚合金融政策法规信息
"""
import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.finance_channel_cache import FinanceChannelCache

logger = logging.getLogger(__name__)


class PolicyAggregator:
    """政策法规聚合器"""
    
    # 缓存 TTL（秒）
    CACHE_TTL = 3600  # 1 小时
    
    def __init__(
        self,
        cache_ttl: int = CACHE_TTL,
        timeout: int = 10,
        db_session: Optional[AsyncSession] = None
    ):
        """
        初始化政策法规聚合器
        
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
        }
    
    async def fetch_policies(self, limit: int = 10, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        抓取政策法规
        
        Args:
            limit: 返回条数
            keyword: 关键词过滤
            
        Returns:
            政策列表
        """
        try:
            # 这里提供模拟数据，真实场景需要爬取官方网站
            policies = [
                {
                    "id": f"policy_{datetime.now().timestamp()}_1",
                    "title": "关于进一步优化资本市场融资环境的通知",
                    "summary": "为进一步提升资本市场服务实体经济能力，优化企业融资环境，证监会发布通知，从简化审批流程、降低融资成本、支持科技创新等多个方面提出具体措施。",
                    "source": "中国证监会",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "url": "http://www.csrc.gov.cn/example1"
                },
                {
                    "id": f"policy_{datetime.now().timestamp()}_2",
                    "title": "关于加强金融科技监管的指导意见",
                    "summary": "为规范金融科技创新发展，防范金融风险，央行联合多部门发布指导意见，明确金融科技创新的边界和监管要求，强化对金融科技平台的持牌经营和合规监管。",
                    "source": "中国人民银行",
                    "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                    "url": "http://www.pbc.gov.cn/example1"
                },
                {
                    "id": f"policy_{datetime.now().timestamp()}_3",
                    "title": "关于推进绿色金融发展的实施方案",
                    "summary": "为贯彻落实碳达峰碳中和战略目标，推动绿色金融发展，相关部门联合制定实施方案，明确绿色金融发展路径，支持绿色产业和项目融资。",
                    "source": "发展改革委、央行",
                    "date": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    "url": "http://www.ndrc.gov.cn/example1"
                },
                {
                    "id": f"policy_{datetime.now().timestamp()}_4",
                    "title": "关于加强投资者保护工作的若干措施",
                    "summary": "为切实保护投资者合法权益，证监会出台多项措施，包括完善投资者权益保护机制、加强信息披露监管、建立投资者赔偿制度等，全面提升投资者保护水平。",
                    "source": "中国证监会",
                    "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                    "url": "http://www.csrc.gov.cn/example2"
                },
                {
                    "id": f"policy_{datetime.now().timestamp()}_5",
                    "title": "关于规范私募基金管理人登记的通知",
                    "summary": "为规范私募基金行业发展，基金业协会发布通知，进一步明确私募基金管理人登记要求，加强事中事后监管，打击违规展业行为。",
                    "source": "中国证券投资基金业协会",
                    "date": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d"),
                    "url": "http://www.amac.org.cn/example1"
                },
            ]
            
            # 关键词过滤
            if keyword:
                keyword_lower = keyword.lower()
                policies = [
                    policy for policy in policies
                    if keyword_lower in policy["title"].lower() or keyword_lower in policy["summary"].lower()
                ]
            
            # 限制数量
            policies = policies[:limit]
            
            logger.info(f"成功构造 {len(policies)} 条政策法规")
            return policies
            
        except Exception as e:
            logger.error(f"抓取政策法规失败：{e}")
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
            cache_key = f"policies:{keyword or 'all'}"
            
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
            logger.error(f"从缓存读取政策数据失败：{e}")
            return None
    
    async def save_to_cache(self, items: List[Dict[str, Any]], keyword: Optional[str] = None, source: str = "official") -> None:
        """
        保存数据到数据库缓存
        
        Args:
            items: 政策列表
            keyword: 关键词
            source: 数据源
        """
        if not self.db_session:
            return
        
        try:
            cache_key = f"policies:{keyword or 'all'}"
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
                    module="policies",
                    payload_json={"items": items},
                    source=source,
                    fetched_at=now,
                    expires_at=expires_at
                )
                self.db_session.add(cache_record)
            
            await self.db_session.commit()
            logger.info(f"政策数据已保存到缓存（{cache_key}）")
            
        except Exception as e:
            logger.error(f"保存政策数据到缓存失败：{e}")
            await self.db_session.rollback()
    
    async def aggregate_policies(self, limit: int = 10, keyword: Optional[str] = None) -> Dict[str, Any]:
        """
        聚合政策法规数据（缓存优先，失败降级）
        
        Args:
            limit: 返回条数
            keyword: 关键词过滤
            
        Returns:
            政策数据响应字典
        """
        try:
            # 1. 尝试从缓存读取
            cached_data = await self.get_from_cache(keyword)
            
            if cached_data and not cached_data["stale"]:
                # 缓存有效，直接返回
                logger.info(f"使用有效缓存的政策数据（keyword={keyword}）")
                return cached_data
            
            # 2. 缓存过期或不存在，重新抓取
            logger.info(f"缓存过期或不存在，重新抓取政策数据（keyword={keyword}）")
            items = await self.fetch_policies(limit=limit, keyword=keyword)
            
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
            logger.error(f"聚合政策数据失败：{e}", exc_info=True)
            
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
_policy_aggregator: Optional[PolicyAggregator] = None


def get_policy_aggregator(db_session: Optional[AsyncSession] = None) -> PolicyAggregator:
    """获取政策法规聚合器单例"""
    global _policy_aggregator
    if _policy_aggregator is None or db_session is not None:
        _policy_aggregator = PolicyAggregator(db_session=db_session)
    return _policy_aggregator
