"""资金流向定时预热调度器"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from core.database import get_async_session
from services.eastmoney_fund_flow_service import EastmoneyFundFlowService

logger = logging.getLogger(__name__)


class FundFlowScheduler:
    """资金流向定时预热"""

    def __init__(self, interval_minutes: int = 30):
        self.interval_minutes = interval_minutes
        self.scheduler = AsyncIOScheduler()
        self._running = False

    async def preheat_fund_flow(self):
        """批量预热资金流向数据"""
        start_time = datetime.now()
        logger.info(f"开始预热资金流向数据 - {start_time.isoformat()}")

        market_list = ["hs", "sh", "sz", "cyb", "kcb"]
        sector_types = ["industry", "concept", "region"]
        stock_markets = ["all", "hsa", "sha", "sza", "kcb", "cyb"]
        stats = [1, 5, 10]
        pages = [1, 2]
        page_size = 50

        try:
            async for db_session in get_async_session():
                try:
                    service = EastmoneyFundFlowService(db_session=db_session)
                    tasks = []

                    for market in market_list:
                        tasks.append(service.get_market_flow(market=market, refresh=True))

                    for sector_type in sector_types:
                        for page in pages:
                            tasks.append(
                                service.get_sector_flow(
                                    sector_type=sector_type,
                                    page=page,
                                    page_size=page_size,
                                    refresh=True,
                                )
                            )

                    for market in stock_markets:
                        for stat in stats:
                            for page in pages:
                                tasks.append(
                                    service.get_stock_flow(
                                        market=market,
                                        stat=stat,
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
                        f"资金流向预热完成 - 耗时: {duration:.2f}秒, 成功: {success_count}, 失败: {failed_count}"
                    )

                    if failed_count:
                        for res in results:
                            if isinstance(res, Exception):
                                logger.warning(f"资金流向预热失败: {res}")
                finally:
                    await db_session.close()
                    break
        except Exception as e:
            logger.error(f"资金流向预热异常: {e}", exc_info=True)

    def start(self, interval_minutes: Optional[int] = None):
        if self._running:
            logger.warning("资金流向定时任务已在运行")
            return

        interval = interval_minutes or self.interval_minutes
        self.scheduler.add_job(
            self.preheat_fund_flow,
            trigger=IntervalTrigger(minutes=interval),
            id="fund_flow_preheat",
            name="资金流向预热",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.start()
        self._running = True
        logger.info(f"资金流向定时任务已启动，预热间隔: {interval} 分钟")

    def stop(self):
        if not self._running:
            return

        self.scheduler.shutdown(wait=False)
        self._running = False
        logger.info("资金流向定时任务已停止")


_scheduler: Optional[FundFlowScheduler] = None


def get_fund_flow_scheduler(interval_minutes: int = 15) -> FundFlowScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = FundFlowScheduler(interval_minutes=interval_minutes)
    return _scheduler