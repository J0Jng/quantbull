"""财经头条定时生成调度器"""
import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from sqlalchemy import text

from core.database import get_async_session
from models.headline_news import HeadlineNews
from services.eastmoney_news_service import EastmoneyNewsAggregator
from services.headlines_ai_service import generate_headlines_from_news

logger = logging.getLogger(__name__)

# 上海时区
SHANGHAI_TZ = timezone("Asia/Shanghai")


class DailyHeadlinesScheduler:
    """每日财经头条自动生成"""

    def __init__(self, hour: int = 3, minute: int = 0, limit: int = 10, hours: int = 24):
        self.hour = hour
        self.minute = minute
        self.limit = limit
        self.hours = hours
        self.scheduler = AsyncIOScheduler(timezone=SHANGHAI_TZ)
        self._running = False

    async def generate_daily_headlines(self):
        """定时任务：AI 生成每日财经头条"""
        logger.info("=" * 50)
        logger.info("开始执行定时任务: 生成每日财经头条")
        logger.info("=" * 50)

        try:
            async for db_session in get_async_session():
                try:
                    aggregator = EastmoneyNewsAggregator(db_session=db_session)
                    source_news = await aggregator.get_news_from_database(
                        limit=self.limit,
                        hours=self.hours,
                    )

                    if len(source_news) < self.limit:
                        logger.warning(
                            "源新闻数量不足，跳过生成: 需要 %s 条，实际 %s 条",
                            self.limit,
                            len(source_news),
                        )
                        return

                    generated = await generate_headlines_from_news(source_news, limit=self.limit)

                    now = datetime.now()

                    await db_session.execute(
                        text(
                            "SELECT setval(pg_get_serial_sequence('headline_news','id'), "
                            "COALESCE((SELECT MAX(id) FROM headline_news), 1), true)"
                        )
                    )

                    created_items = []
                    for item in generated:
                        headline = HeadlineNews(
                            title=item["title"],
                            date_text=now.strftime("%Y-%m-%d %H:%M"),
                            summary=item["summary"],
                            tags=item["tags"],
                            content=item.get("content"),
                            source="AI生成",
                            url="",
                            is_hot=False,
                            publish_time=now,
                        )
                        db_session.add(headline)
                        created_items.append(headline)

                    await db_session.commit()

                    logger.info("定时任务完成: 成功生成 %s 条财经头条", len(created_items))
                    logger.info("=" * 50)
                finally:
                    await db_session.close()
                    break
        except Exception as e:
            logger.error(f"定时任务执行失败: {e}", exc_info=True)
            logger.info("=" * 50)

    def start(self):
        if self._running:
            logger.warning("每日财经头条定时任务已在运行")
            return

        self.scheduler.add_job(
            self.generate_daily_headlines,
            trigger=CronTrigger(hour=self.hour, minute=self.minute, timezone=SHANGHAI_TZ),
            id="daily_headlines_generate",
            name="每日财经头条生成",
            replace_existing=True,
            max_instances=1,
        )

        self.scheduler.start()
        self._running = True
        logger.info("每日财经头条定时任务已启动：每日 %02d:%02d", self.hour, self.minute)

    def stop(self):
        if not self._running:
            return

        self.scheduler.shutdown(wait=False)
        self._running = False
        logger.info("每日财经头条定时任务已停止")


_scheduler: Optional[DailyHeadlinesScheduler] = None


def get_daily_headlines_scheduler(
    hour: int = 3,
    minute: int = 0,
    limit: int = 10,
    hours: int = 24,
) -> DailyHeadlinesScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = DailyHeadlinesScheduler(
            hour=hour,
            minute=minute,
            limit=limit,
            hours=hours,
        )
    return _scheduler