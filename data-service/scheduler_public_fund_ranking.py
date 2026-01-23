"""公募基金排行榜定时预热与清理调度器"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from core.database import get_async_session
from services.fund_ranking_service import FundRankingService

logger = logging.getLogger(__name__)


class PublicFundRankingScheduler:
    """公募基金排行榜定时预热与清理"""

    def __init__(self, interval_minutes: int = 60, retention_days: int = 30):
        self.interval_minutes = interval_minutes
        self.retention_days = retention_days
        self.scheduler = AsyncIOScheduler()
        self._running = False

    async def preheat_public_ranking(self):
        """批量预热公募基金排行榜数据"""
        start_time = datetime.now()
        logger.info(f"开始预热公募基金排行榜数据 - {start_time.isoformat()}")

        fund_types = ["", "stock", "hybrid", "bond", "monetary"]
        sort_fields = ["default", "return1m", "return1y"]
        pages = [1, 2]
        page_size = 50

        try:
            async for db_session in get_async_session():
                try:
                    service = FundRankingService(db_session=db_session)
                    tasks = []
                    for fund_type in fund_types:
                        for sort_by in sort_fields:
                            for page in pages:
                                tasks.append(
                                    service.get_public_ranking(
                                        fund_type=fund_type,
                                        return_sign="",
                                        sort_by=sort_by,
                                        order="desc",
                                        keyword="",
                                        page=page,
                                        page_size=page_size,
                                        refresh=True,
                                    )
                                )

                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    success_count = sum(1 for r in results if not isinstance(r, Exception))
                    failed_count = len(results) - success_count

                    duration = (datetime.now() - start_time).total_seconds()
                    logger.info(
                        f"公募基金排行榜预热完成 - 耗时: {duration:.2f}秒, 成功: {success_count}, 失败: {failed_count}"
                    )

                    if failed_count:
                        for res in results:
                            if isinstance(res, Exception):
                                logger.warning(f"公募基金排行榜预热失败: {res}")
                finally:
                    await db_session.close()
                    break
        except Exception as e:
            logger.error(f"公募基金排行榜预热异常: {e}", exc_info=True)

    async def cleanup_public_ranking(self):
        """清理过期公募基金排行榜数据"""
        start_time = datetime.now()
        logger.info(f"开始清理公募基金排行榜历史数据 - {start_time.isoformat()}")

        try:
            async for db_session in get_async_session():
                try:
                    service = FundRankingService(db_session=db_session)
                    removed = await service.cleanup_public_funds(retention_days=self.retention_days)
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.info(
                        f"公募基金排行榜清理完成 - 耗时: {duration:.2f}秒, 删除: {removed}"
                    )
                finally:
                    await db_session.close()
                    break
        except Exception as e:
            logger.error(f"公募基金排行榜清理异常: {e}", exc_info=True)

    def start(self, interval_minutes: Optional[int] = None):
        if self._running:
            logger.warning("公募基金排行榜定时任务已在运行")
            return

        interval = interval_minutes or self.interval_minutes

        self.scheduler.add_job(
            self.preheat_public_ranking,
            trigger=IntervalTrigger(minutes=interval),
            id="public_fund_ranking_preheat",
            name="公募基金排行榜预热",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.add_job(
            self.cleanup_public_ranking,
            trigger=CronTrigger(hour=3, minute=30),
            id="public_fund_ranking_cleanup",
            name="公募基金排行榜清理",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.start()
        self._running = True
        logger.info(f"公募基金排行榜定时任务已启动，预热间隔: {interval} 分钟，清理: 每日 03:30")

    def stop(self):
        if not self._running:
            return

        self.scheduler.shutdown(wait=False)
        self._running = False
        logger.info("公募基金排行榜定时任务已停止")


_scheduler: Optional[PublicFundRankingScheduler] = None


def get_public_fund_ranking_scheduler(
    interval_minutes: int = 60,
    retention_days: int = 30,
) -> PublicFundRankingScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = PublicFundRankingScheduler(
            interval_minutes=interval_minutes,
            retention_days=retention_days,
        )
    return _scheduler
