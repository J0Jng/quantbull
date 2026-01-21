"""
东方财富网新闻定时刷新任务

功能：
1. 定时预加载东方财富网新闻到缓存
2. 定时保存新闻数据到数据库
3. 提高数据时效性，减少用户请求时的抓取延迟
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from services.eastmoney_news_service import EastmoneyNewsAggregator

logger = logging.getLogger(__name__)


class EastmoneyNewsScheduler:
    """东方财富网新闻定时刷新调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.aggregator: Optional[EastmoneyNewsAggregator] = None
        self.is_running = False
    
    async def refresh_news_cache(self):
        """定时刷新新闻缓存"""
        try:
            logger.info("开始定时刷新东方财富网新闻缓存...")
            
            # 获取数据库会话
            async for db_session in get_async_session():
                # 创建带数据库会话的聚合器
                aggregator = EastmoneyNewsAggregator(db_session=db_session)
                
                # 预加载默认新闻（不使用缓存，强制刷新）
                result = await aggregator.aggregate_news(
                    limit=50,  # 预加载更多数据
                    use_cache=False  # 不使用缓存，强制刷新
                )
                
                news_count = len(result.get("items", []))
                has_error = "error" in result
                
                if has_error:
                    logger.warning(f"定时刷新遇到问题，获取 {news_count} 条新闻，错误：{result.get('error')}")
                else:
                    logger.info(f"定时刷新完成，成功获取 {news_count} 条东方财富网新闻")
                
                # 只执行一次，退出循环
                break
                
        except Exception as e:
            logger.error(f"定时刷新东方财富网新闻失败：{e}", exc_info=True)
    
    def start(self, interval_minutes: int = 5):
        """
        启动定时任务
        
        Args:
            interval_minutes: 刷新间隔（分钟），默认 5 分钟
        """
        if self.is_running:
            logger.warning("东方财富网新闻定时任务已在运行")
            return
        
        try:
            # 添加定时任务
            self.scheduler.add_job(
                self.refresh_news_cache,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id="eastmoney_news_refresh",
                name="东方财富网新闻定时刷新",
                replace_existing=True,
                max_instances=1  # 同一时间只允许一个实例运行
            )
            
            # 启动调度器
            self.scheduler.start()
            self.is_running = True
            
            logger.info(f"东方财富网新闻定时刷新任务已启动，间隔 {interval_minutes} 分钟")
            
            # 启动后立即执行一次预热
            asyncio.create_task(self.refresh_news_cache())
            
        except Exception as e:
            logger.error(f"启动东方财富网新闻定时任务失败：{e}", exc_info=True)
    
    def stop(self):
        """停止定时任务"""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("东方财富网新闻定时刷新任务已停止")
        except Exception as e:
            logger.error(f"停止东方财富网新闻定时任务失败：{e}", exc_info=True)
    
    def get_next_run_time(self):
        """获取下次运行时间"""
        job = self.scheduler.get_job("eastmoney_news_refresh")
        if job:
            return job.next_run_time
        return None
    
    def get_status(self) -> dict:
        """获取调度器状态"""
        return {
            "is_running": self.is_running,
            "next_run_time": str(self.get_next_run_time()) if self.get_next_run_time() else None,
            "job_id": "eastmoney_news_refresh"
        }


# 全局调度器实例
_scheduler_instance: Optional[EastmoneyNewsScheduler] = None


def get_eastmoney_news_scheduler() -> EastmoneyNewsScheduler:
    """获取全局调度器实例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = EastmoneyNewsScheduler()
    return _scheduler_instance
