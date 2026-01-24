"""龙虎榜数据定时预热调度器"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from core.database import get_async_session
from services.eastmoney_lhb_service import EastmoneyLhbService

logger = logging.getLogger(__name__)


class LhbScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._running = False

    async def preheat_lhb(self):
        start_time = datetime.now()
        try:
            async for db_session in get_async_session():
                service = EastmoneyLhbService(db_session=db_session)
                trade_date = await service.find_latest_trade_date(refresh=True)
                if not trade_date:
                    logger.warning("未找到可用交易日，跳过龙虎榜预热")
                    return

                tasks = []
                for page in (1, 2):
                    tasks.append(service.fetch_stocks(trade_date=trade_date, page=page, page_size=50, refresh=True))
                for days in (1, 5, 20):
                    tasks.append(service.fetch_summary(window_days=days, end_trade_date=trade_date, page=1, page_size=50, refresh=True))

                results = await asyncio.gather(*tasks, return_exceptions=True)
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                failed = [r for r in results if isinstance(r, Exception)]

                duration = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"龙虎榜预热完成 trade_date={trade_date}，耗时 {duration:.2f}s，成功 {success_count}，失败 {len(failed)}"
                )
                for err in failed:
                    logger.warning(f"龙虎榜预热失败: {err}")
                break
        except Exception as exc:
            logger.error(f"龙虎榜预热异常: {exc}", exc_info=True)

    def start(self, cron_hour: int = 18, cron_minute: int = 10):
        if self._running:
            logger.warning("龙虎榜定时任务已在运行")
            return

        self.scheduler.add_job(
            self.preheat_lhb,
            trigger=CronTrigger(hour=cron_hour, minute=cron_minute),
            id="lhb_preheat",
            name="龙虎榜预热任务",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.start()
        self._running = True
        logger.info("龙虎榜定时任务已启动")
        asyncio.create_task(self.preheat_lhb())

    def stop(self):
        if not self._running:
            return
        self.scheduler.shutdown(wait=False)
        self._running = False
        logger.info("龙虎榜定时任务已停止")


_scheduler: Optional[LhbScheduler] = None


def get_lhb_scheduler() -> LhbScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = LhbScheduler()
    return _scheduler
