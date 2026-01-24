"""财报数据定时预热调度器"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from core.database import get_async_session
from services.eastmoney_bbsj_service import EastmoneyBbsjService

logger = logging.getLogger(__name__)


class FinancialReportScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._running = False

    @staticmethod
    def _latest_period() -> str:
        now = datetime.now()
        year = now.year
        month = now.month
        if month >= 12:
            m = 12
        elif month >= 9:
            m = 9
        elif month >= 6:
            m = 6
        elif month >= 3:
            m = 3
        else:
            year -= 1
            m = 12
        return f"{year}{m:02d}"

    async def preheat_financial_reports(self):
        start_time = datetime.now()
        period = self._latest_period()
        logger.info(f"开始预热财报数据 period={period}")

        try:
            async for db_session in get_async_session():
                service = EastmoneyBbsjService(db_session=db_session)
                tasks = []
                for page in (1, 2):
                    tasks.append(service.fetch_yjbb(period=period, page=page, page_size=50, refresh=True))
                    tasks.append(service.fetch_yjkb(period=period, page=page, page_size=50, refresh=True))
                    tasks.append(service.fetch_yjyg(period=period, page=page, page_size=50, refresh=True))
                    tasks.append(service.fetch_yysj(period=period, page=page, page_size=50, refresh=True))

                results = await asyncio.gather(*tasks, return_exceptions=True)
                success_count = sum(1 for r in results if not isinstance(r, Exception))
                failed = [r for r in results if isinstance(r, Exception)]

                duration = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"财报预热完成 period={period}，耗时 {duration:.2f}s，成功 {success_count}，失败 {len(failed)}"
                )
                for err in failed:
                    logger.warning(f"财报预热失败: {err}")
                break
        except Exception as exc:
            logger.error(f"财报预热异常: {exc}", exc_info=True)

    async def refresh_yysj(self):
        period = self._latest_period()
        try:
            async for db_session in get_async_session():
                service = EastmoneyBbsjService(db_session=db_session)
                await service.fetch_yysj(period=period, page=1, page_size=100, refresh=True)
                logger.info(f"预约披露更新完成 period={period}")
                break
        except Exception as exc:
            logger.warning(f"预约披露更新失败: {exc}")

    def start(self, cron_hour: int = 3, cron_minute: int = 20, yysj_interval_hours: int = 6):
        if self._running:
            logger.warning("财报定时任务已在运行")
            return

        self.scheduler.add_job(
            self.preheat_financial_reports,
            trigger=CronTrigger(hour=cron_hour, minute=cron_minute),
            id="financial_report_preheat",
            name="财报预热任务",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.add_job(
            self.refresh_yysj,
            trigger=IntervalTrigger(hours=yysj_interval_hours),
            id="financial_report_yysj_refresh",
            name="预约披露更新",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.start()
        self._running = True
        logger.info("财报定时任务已启动")
        asyncio.create_task(self.preheat_financial_reports())

    def stop(self):
        if not self._running:
            return
        self.scheduler.shutdown(wait=False)
        self._running = False
        logger.info("财报定时任务已停止")


_scheduler: Optional[FinancialReportScheduler] = None


def get_financial_report_scheduler() -> FinancialReportScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = FinancialReportScheduler()
    return _scheduler
