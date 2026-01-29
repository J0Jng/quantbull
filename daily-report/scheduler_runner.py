import asyncio
import signal

from core.config import settings
from core.logger import configure_logging, get_logger
from db.session import init_db
from scheduler import create_scheduler, start_scheduler, shutdown_scheduler


def _setup_logging():
    configure_logging(settings)
    return get_logger("scheduler_runner")


async def _wait_forever():
    stop_event = asyncio.Event()

    def _stop():
        stop_event.set()

    try:
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGTERM, _stop)
        loop.add_signal_handler(signal.SIGINT, _stop)
    except (NotImplementedError, RuntimeError):
        pass

    await stop_event.wait()


async def main():
    logger = _setup_logging()

    logger.info("=" * 50)
    logger.info("Daily Report Scheduler 启动中...")
    logger.info("=" * 50)

    try:
        init_db()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}", exc_info=True)
        if settings.db_type == "postgresql" and settings.env != "local":
            raise
        logger.warning("数据库初始化失败，但允许继续运行（可能使用内存数据库）")

    try:
        create_scheduler()
        start_scheduler()
        logger.info("定时任务调度器已启动")
    except Exception as e:
        logger.error(f"调度器启动失败: {e}", exc_info=True)
        if settings.env != "local":
            raise

    logger.info("Scheduler 已就绪，等待信号...")
    await _wait_forever()

    logger.info("Scheduler 关闭中...")
    shutdown_scheduler()
    logger.info("Scheduler 已关闭")


if __name__ == "__main__":
    asyncio.run(main())
