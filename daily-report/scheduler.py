"""APScheduler 定时任务配置"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from core.config import settings
from core.logger import get_logger
from services.report_service import ReportService
from services.data_client import DataServiceClient
from core.access_control import get_china_today

logger = get_logger(__name__)

# 上海时区
SHANGHAI_TZ = timezone("Asia/Shanghai")

# 全局调度器实例
scheduler = AsyncIOScheduler(timezone=SHANGHAI_TZ)


def create_scheduler() -> AsyncIOScheduler:
    """创建并配置调度器"""
    # 添加每日投资方案生成任务
    # 每个交易日 15:30 执行（收盘后30分钟）
    scheduler.add_job(
        func=generate_daily_report_job,
        trigger=CronTrigger(
            day_of_week="mon-fri",
            hour=15,
            minute=30,
            timezone=SHANGHAI_TZ,
        ),
        id="generate_daily_report",
        name="每日投资方案生成",
        replace_existing=True,
        max_instances=1,  # 确保同一时间只有一个实例运行
    )
    
    logger.info("定时任务已配置: 交易日 15:30 生成投资方案")
    return scheduler


async def generate_daily_report_job():
    """
    定时任务：生成每日投资方案
    
    注意：此函数会在每个交易日 15:30 自动执行
    """
    logger.info("=" * 50)
    logger.info("开始执行定时任务: 生成每日投资方案")
    logger.info("=" * 50)
    
    try:
        today = get_china_today()
        data_client = DataServiceClient()
        is_trading_day = await data_client.is_trading_day(today)
        if not is_trading_day:
            logger.info(f"今日非交易日({today})，跳过生成")
            logger.info("=" * 50)
            return

        service = ReportService()
        
        # 使用今日日期生成报告
        report = await service.generate_daily_report(report_date=today, force=False)
        
        logger.info(f"定时任务完成: 成功生成报告 {report.id} ({report.report_date})")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"定时任务执行失败: {e}", exc_info=True)
        logger.error("=" * 50)
        # 不抛出异常，避免影响调度器


def start_scheduler():
    """启动调度器"""
    if not scheduler.running:
        scheduler.start()
        logger.info("调度器已启动")
    else:
        logger.warning("调度器已在运行中")


def shutdown_scheduler():
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("调度器已关闭")
