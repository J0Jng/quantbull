"""
财经头条种子数据初始化
"""
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from models.headline_news import HeadlineNews
import logging

logger = logging.getLogger(__name__)


async def seed_headline_news_if_empty(db: AsyncSession) -> None:
    """如果 headline_news 表为空，则插入种子数据"""
    try:
        count_query = select(func.count()).select_from(HeadlineNews)
        result = await db.execute(count_query)
        count = result.scalar_one()
        
        if count > 0:
            logger.info(f"财经头条表已存在 {count} 条数据，跳过种子数据初始化")
            await _sync_headline_news_sequence(db)
            return
        
        logger.info("开始初始化财经头条种子数据...")
        
        # 创建种子数据
        seed_data = []
        
        # 头条新闻 (id 1-6)
        seed_data.append(HeadlineNews(
            id=1, title="央行：将再降准0.5个百分点 释放资金约1万亿元",
            date_text="2025-12-22 09:30",
            summary="本次降准旨在优化流动性结构，降低实体经济融资成本，预计将带动市场融资成本进一步下行，利好中小企业和实体经济发展。",
            tags=["货币政策", "降准", "流动性"],
            publish_time=datetime(2025, 12, 22, 9, 30),
            is_hot=False
        ))
        seed_data.append(HeadlineNews(
            id=2, title="A股三大指数集体高开 宁德时代涨5.1%",
            date_text="2025-12-22 09:25",
            summary="今日开盘，A股三大指数集体高开，创业板指涨幅居前。宁德时代发布公告称其新一代电池技术取得突破，股价应声大涨。",
            tags=["股市", "宁德时代", "创业板"],
            publish_time=datetime(2025, 12, 22, 9, 25),
            is_hot=False
        ))
        seed_data.append(HeadlineNews(
            id=3, title="国际油价涨超1% 报103美元/桶 WTI升4%",
            date_text="2025-12-22 09:15",
            summary="受中东地缘政治紧张局势影响，国际油价持续走高，布伦特原油价格上涨至103美元/桶，WTI原油期货价格上涨4%。",
            tags=["国际油价", "能源", "地缘政治"],
            publish_time=datetime(2025, 12, 22, 9, 15),
            is_hot=False
        ))
        seed_data.append(HeadlineNews(
            id=4, title='房地产"超预期政策"密集发布 多家房企发公告',
            date_text="2025-12-22 09:05",
            summary="近期多地政府陆续出台房地产支持政策，包括放宽限购、下调首付比例等措施，多家房地产企业积极响应并发布相关公告。",
            tags=["房地产", "政策", "限购"],
            publish_time=datetime(2025, 12, 22, 9, 5),
            is_hot=False
        ))
        seed_data.append(HeadlineNews(
            id=5, title="人民币汇率企稳回升 离岸人民币兑美元涨破7.10关口",
            date_text="2025-12-22 08:50",
            summary="随着国内经济复苏信号增强及美元指数走弱，离岸人民币兑美元汇率持续回升，已突破7.10重要关口。",
            tags=["人民币", "汇率", "外汇"],
            publish_time=datetime(2025, 12, 22, 8, 50),
            is_hot=False
        ))
        seed_data.append(HeadlineNews(
            id=6, title="工信部：加快推进新能源汽车充电桩建设 年内新增超20万个",
            date_text="2025-12-22 08:30",
            summary="工信部表示将进一步完善新能源汽车充电基础设施网络，计划年内新增充电桩超过20万个，覆盖更多城市和乡村地区。",
            tags=["新能源汽车", "充电桩", "基建"],
            publish_time=datetime(2025, 12, 22, 8, 30),
            is_hot=False
        ))
        
        # 热点新闻 (id 7-14)
        seed_data.append(HeadlineNews(
            id=7, title="美联储议息会议即将召开 市场密切关注政策动向",
            date_text="2025-12-22 08:00",
            summary="美联储议息会议即将召开，市场密切关注政策动向。",
            tags=["美联储", "货币政策"],
            publish_time=datetime(2025, 12, 22, 8, 0),
            is_hot=True, hot_rank=1
        ))
        seed_data.append(HeadlineNews(
            id=8, title="黄金价格突破每盎司2200美元 创历史新高",
            date_text="2025-12-22 07:50",
            summary="黄金价格突破每盎司2200美元，创历史新高。",
            tags=["黄金", "价格"],
            publish_time=datetime(2025, 12, 22, 7, 50),
            is_hot=True, hot_rank=2
        ))
        seed_data.append(HeadlineNews(
            id=9, title="人工智能芯片需求激增 相关企业订单排至明年",
            date_text="2025-12-22 07:40",
            summary="人工智能芯片需求激增，相关企业订单排至明年。",
            tags=["人工智能", "芯片"],
            publish_time=datetime(2025, 12, 22, 7, 40),
            is_hot=True, hot_rank=3
        ))
        seed_data.append(HeadlineNews(
            id=10, title="全球供应链逐步恢复 但通胀压力依然存在",
            date_text="2025-12-22 07:30",
            summary="全球供应链逐步恢复，但通胀压力依然存在。",
            tags=["供应链", "通胀"],
            publish_time=datetime(2025, 12, 22, 7, 30),
            is_hot=True, hot_rank=4
        ))
        seed_data.append(HeadlineNews(
            id=11, title="绿色能源投资持续增长 碳中和目标推动产业发展",
            date_text="2025-12-22 07:20",
            summary="绿色能源投资持续增长，碳中和目标推动产业发展。",
            tags=["绿色能源", "碳中和"],
            publish_time=datetime(2025, 12, 22, 7, 20),
            is_hot=True, hot_rank=5
        ))
        seed_data.append(HeadlineNews(
            id=12, title="数字货币发展加速 多国央行推进CBDC试点",
            date_text="2025-12-22 07:10",
            summary="数字货币发展加速，多国央行推进CBDC试点。",
            tags=["数字货币", "CBDC"],
            publish_time=datetime(2025, 12, 22, 7, 10),
            is_hot=True, hot_rank=6
        ))
        seed_data.append(HeadlineNews(
            id=13, title="生物医药行业迎来新机遇 创新药研发持续推进",
            date_text="2025-12-22 07:00",
            summary="生物医药行业迎来新机遇，创新药研发持续推进。",
            tags=["生物医药", "创新药"],
            publish_time=datetime(2025, 12, 22, 7, 0),
            is_hot=True, hot_rank=7
        ))
        seed_data.append(HeadlineNews(
            id=14, title="跨境电商蓬勃发展 海外消费市场不断拓展",
            date_text="2025-12-22 06:50",
            summary="跨境电商蓬勃发展，海外消费市场不断拓展。",
            tags=["跨境电商", "电商"],
            publish_time=datetime(2025, 12, 22, 6, 50),
            is_hot=True, hot_rank=8
        ))
        
        # 批量插入
        for item in seed_data:
            db.add(item)
        
        await db.commit()
        logger.info(f"成功初始化 {len(seed_data)} 条财经头条种子数据")
        await _sync_headline_news_sequence(db)
        
    except Exception as e:
        await db.rollback()
        logger.error(f"初始化财经头条种子数据失败：{e}", exc_info=True)


async def _sync_headline_news_sequence(db: AsyncSession) -> None:
    """同步 headline_news 主键序列，避免自增值落后于现有数据"""
    try:
        await db.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('headline_news','id'), "
                "COALESCE((SELECT MAX(id) FROM headline_news), 1), true)"
            )
        )
        await db.commit()
        logger.info("headline_news 主键序列已同步")
    except Exception as e:
        await db.rollback()
        logger.warning(f"headline_news 主键序列同步失败: {e}")
