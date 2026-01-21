"""
微博财经新闻定时刷新任务

功能：
1. 定时预加载微博新闻到缓存
2. 定时保存新闻数据到数据库
3. 提高数据时效性，减少用户请求时的抓取延迟
"""
import asyncio
import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from services.weibo_media_service import WeiboMediaAggregator

logger = logging.getLogger(__name__)


class WeiboNewsScheduler:
    """微博新闻定时刷新调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.aggregator: WeiboMediaAggregator = None
        self.is_running = False
    
    async def refresh_news_cache(self):
        """定时刷新新闻缓存"""
        try:
            logger.info("开始定时刷新微博新闻缓存...")
            
            # 获取数据库会话
            async for db_session in get_async_session():
                # 创建带数据库会话的聚合器
                aggregator = WeiboMediaAggregator(db_session=db_session)
                
                # 预加载默认新闻（不使用缓存，强制刷新）
                result = await aggregator.aggregate_news(
                    limit=50,  # 预加载更多数据
                    use_cache=False  # 不使用缓存，强制刷新
                )
                
                news_count = len(result.get("items", []))
                logger.info(f"定时刷新完成，获取 {news_count} 条新闻")
                
                # 只执行一次，退出循环
                break
                
        except Exception as e:
            logger.error(f"定时刷新新闻失败：{e}", exc_info=True)
    
    def start(self, interval_minutes: int = 5):
        """
        启动定时任务
        
        Args:
            interval_minutes: 刷新间隔（分钟），默认 5 分钟
        """
        if self.is_running:
            logger.warning("定时任务已在运行")
            return
        
        try:
            # 添加定时任务
            self.scheduler.add_job(
                self.refresh_news_cache,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id="weibo_news_refresh",
                name="微博新闻定时刷新",
                replace_existing=True,
                max_instances=1  # 同一时间只允许一个实例运行
            )
            
            # 启动调度器
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"微博新闻定时刷新任务已启动，间隔 {interval_minutes} 分钟")
            
        except Exception as e:
            logger.error(f"启动定时任务失败：{e}", exc_info=True)
    
    def stop(self):
        """停止定时任务"""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("微博新闻定时刷新任务已停止")
        except Exception as e:
            logger.error(f"停止定时任务失败：{e}", exc_info=True)
    
    def get_next_run_time(self):
        """获取下次运行时间"""
        job = self.scheduler.get_job("weibo_news_refresh")
        if job:
            return job.next_run_time
        return None


# 全局调度器实例
_scheduler_instance: WeiboNewsScheduler = None


def get_weibo_news_scheduler() -> WeiboNewsScheduler:
    """获取全局调度器实例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = WeiboNewsScheduler()
    return _scheduler_instance
