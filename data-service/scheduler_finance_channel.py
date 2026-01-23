"""
财经频道数据定时刷新调度器

功能：每小时自动刷新财经频道所有模块的数据（市场数据、观点、政策）
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from core.database import get_async_session
from services.market_data_service import get_market_data_aggregator
from services.ideas_service import get_ideas_aggregator
from services.policy_service import get_policy_aggregator

logger = logging.getLogger(__name__)


class FinanceChannelScheduler:
    """财经频道数据定时刷新器"""
    
    def __init__(self, interval_minutes: int = 60):
        """
        初始化调度器
        
        Args:
            interval_minutes: 刷新间隔（分钟），默认60分钟
        """
        self.interval_minutes = interval_minutes
        self.scheduler = AsyncIOScheduler()
        self._running = False
    
    async def refresh_all_data(self):
        """刷新所有财经频道数据"""
        start_time = datetime.now()
        logger.info(f"开始刷新财经频道数据 - {start_time.isoformat()}")
        
        try:
            # 获取数据库会话
            async for db_session in get_async_session():
                try:
                    # 并发刷新所有模块
                    tasks = [
                        self._refresh_market_data(db_session),
                        self._refresh_ideas(db_session),
                        self._refresh_policies(db_session),
                    ]
                    
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # 统计结果
                    success_count = sum(1 for r in results if not isinstance(r, Exception))
                    failed_count = len(results) - success_count
                    
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    logger.info(
                        f"财经频道数据刷新完成 - 耗时: {duration:.2f}秒, "
                        f"成功: {success_count}, 失败: {failed_count}"
                    )
                    
                    # 记录失败的模块
                    module_names = ["市场数据", "投资观点", "政策法规"]
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            logger.error(f"{module_names[i]}刷新失败: {result}")
                    
                finally:
                    await db_session.close()
                    break  # 只使用第一个会话
                    
        except Exception as e:
            logger.error(f"财经频道数据刷新异常: {e}", exc_info=True)
    
    async def _refresh_market_data(self, db_session):
        """刷新市场数据"""
        try:
            aggregator = get_market_data_aggregator(db_session)
            result = await aggregator.aggregate_market_data()
            logger.info(f"市场数据刷新成功，共 {len(result.get('items', []))} 条")
            return result
        except Exception as e:
            logger.error(f"市场数据刷新失败: {e}")
            raise
    
    async def _refresh_ideas(self, db_session):
        """刷新投资观点"""
        try:
            aggregator = get_ideas_aggregator(db_session)
            result = await aggregator.aggregate_ideas(limit=20)
            logger.info(f"投资观点刷新成功，共 {len(result.get('items', []))} 条")
            return result
        except Exception as e:
            logger.error(f"投资观点刷新失败: {e}")
            raise
    
    async def _refresh_policies(self, db_session):
        """刷新政策法规"""
        try:
            aggregator = get_policy_aggregator(db_session)
            result = await aggregator.aggregate_policies(limit=20)
            logger.info(f"政策法规刷新成功，共 {len(result.get('items', []))} 条")
            return result
        except Exception as e:
            logger.error(f"政策法规刷新失败: {e}")
            raise
    
    def start(self, interval_minutes: Optional[int] = None):
        """
        启动定时任务
        
        Args:
            interval_minutes: 刷新间隔（分钟），不传则使用初始化时的值
        """
        if self._running:
            logger.warning("财经频道定时刷新任务已在运行")
            return
        
        interval = interval_minutes or self.interval_minutes
        
        # 添加定时任务
        self.scheduler.add_job(
            self.refresh_all_data,
            trigger=IntervalTrigger(minutes=interval),
            id="finance_channel_refresh",
            name="财经频道数据刷新",
            replace_existing=True,
            max_instances=1,  # 同一时间只允许一个实例运行
        )
        
        # 启动调度器
        self.scheduler.start()
        self._running = True
        
        logger.info(f"财经频道定时刷新任务已启动，间隔: {interval} 分钟")
    
    def stop(self):
        """停止定时任务"""
        if not self._running:
            return
        
        self.scheduler.shutdown(wait=False)
        self._running = False
        logger.info("财经频道定时刷新任务已停止")
    
    def run_now(self):
        """立即执行一次刷新"""
        if not self._running:
            logger.warning("调度器未运行，无法立即执行")
            return
        
        self.scheduler.add_job(
            self.refresh_all_data,
            id="finance_channel_refresh_manual",
            name="财经频道数据刷新（手动触发）",
            replace_existing=True,
        )
        logger.info("已触发财经频道数据刷新（手动）")


# 全局单例
_scheduler: Optional[FinanceChannelScheduler] = None


def get_finance_channel_scheduler(interval_minutes: int = 60) -> FinanceChannelScheduler:
    """获取财经频道调度器单例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = FinanceChannelScheduler(interval_minutes=interval_minutes)
    return _scheduler
