"""行业排名定时任务 - 每日预热缓存"""
import logging
import sys
from pathlib import Path

# 添加项目路径到 sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from services.fundamentals_service import FundamentalsService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('industry_rank_scheduler.log')
    ]
)

logger = logging.getLogger(__name__)


def preheat_industry_rank():
    """预热行业排名缓存 - 计算当前月份的数据并保存到数据库"""
    try:
        current_month = datetime.now().strftime("%Y-%m")
        logger.info(f"开始预热行业排名缓存 - 月份: {current_month}")
        
        service = FundamentalsService()
        # force_recalculate=True 强制重新计算并更新数据库
        result = service.calculate_industry_rank(month=current_month, force_recalculate=True)
        
        if result:
            logger.info(f"预热完成！共计算了 {len(result)} 个行业的排名")
            logger.info(f"Top 5 行业: {[f'{item.industry}({item.score})' for item in result[:5]]}")
        else:
            logger.warning("预热失败：未返回任何数据")
            
    except Exception as e:
        logger.error(f"预热行业排名失败: {e}", exc_info=True)


def main():
    """启动定时任务调度器"""
    scheduler = BlockingScheduler()
    
    # 每天下午 15:30 执行预热任务（收盘后）
    scheduler.add_job(
        preheat_industry_rank,
        trigger=CronTrigger(hour=2, minute=00),
        id='preheat_industry_rank',
        name='预热行业排名缓存',
        replace_existing=True
    )
    
    logger.info("行业排名定时任务已启动")
    logger.info("调度计划: 每天 2:00 执行预热（收盘后）")
    
    # 可选：启动时立即执行一次
    # logger.info("启动时立即执行一次预热...")
    # preheat_industry_rank()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("定时任务已停止")


if __name__ == "__main__":
    main()
