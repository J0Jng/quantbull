"""
批量添加更多财经头条新闻数据
运行方式：docker exec -it data-service python scripts/add_more_headlines.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models.headline_news import HeadlineNews
from datetime import datetime, timedelta
import random

# 数据库连接
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://quantbull:quantbull123@quantbull_postgres:5432/quantbull")

# 更多新闻数据
MORE_HEADLINES = [
    {
        "title": "美联储维持利率不变 市场预期年内降息两次",
        "date": "2025-12-22 08:00",
        "summary": "美联储在最新议息会议上决定维持联邦基金利率目标区间不变，但暗示今年可能降息两次。市场对此反应积极，美股三大指数集体上涨。",
        "tags": ["美联储", "利率", "货币政策"],
        "source": "华尔街见闻",
        "url": "https://example.com/news/7"
    },
    {
        "title": "特斯拉Q4交付量超预期 股价盘后大涨6%",
        "date": "2025-12-22 07:30",
        "summary": "特斯拉公布第四季度交付量达48.5万辆，超过市场预期的47万辆。全年交付量突破180万辆，同比增长38%。",
        "tags": ["特斯拉", "汽车", "财报"],
        "source": "第一财经",
        "url": "https://example.com/news/8"
    },
    {
        "title": "ChatGPT推出订阅制 月费20美元引发争议",
        "date": "2025-12-21 18:00",
        "summary": "OpenAI宣布推出ChatGPT Plus订阅服务，月费20美元，提供更快的响应速度和优先访问新功能。分析师认为这标志着AI商业化进入新阶段。",
        "tags": ["人工智能", "ChatGPT", "订阅"],
        "source": "科技日报",
        "url": "https://example.com/news/9"
    },
    {
        "title": "中国11月CPI同比下降0.5% 通缩压力显现",
        "date": "2025-12-21 16:30",
        "summary": "国家统计局公布11月CPI数据同比下降0.5%，连续第二个月负增长。食品价格是主要拖累因素，猪肉价格同比下降31.8%。",
        "tags": ["CPI", "通缩", "宏观经济"],
        "source": "财新网",
        "url": "https://example.com/news/10"
    },
    {
        "title": "贵州茅台市值突破3万亿 成A股市值第一股",
        "date": "2025-12-21 15:00",
        "summary": "贵州茅台股价今日收盘报2368元，市值突破3万亿元，超越工商银行成为A股市值最高的上市公司。",
        "tags": ["贵州茅台", "白酒", "市值"],
        "source": "证券时报",
        "url": "https://example.com/news/11"
    },
    {
        "title": "比亚迪新能源车销量连续8个月超特斯拉",
        "date": "2025-12-21 14:00",
        "summary": "比亚迪公布11月新能源汽车销量达30.16万辆，连续8个月超过特斯拉全球销量，巩固全球新能源车销量冠军地位。",
        "tags": ["比亚迪", "新能源车", "销量"],
        "source": "经济观察报",
        "url": "https://example.com/news/12"
    },
    {
        "title": "黄金价格突破2100美元 创历史新高",
        "date": "2025-12-21 13:00",
        "summary": "受地缘政治紧张局势和美元走弱影响，国际黄金价格突破2100美元/盎司，刷新历史新高。分析师预计金价仍有上涨空间。",
        "tags": ["黄金", "贵金属", "价格"],
        "source": "东方财富网",
        "url": "https://example.com/news/13"
    },
    {
        "title": "腾讯推出AI编程助手Copilot 挑战GitHub",
        "date": "2025-12-21 12:00",
        "summary": "腾讯云宣布推出AI编程助手Copilot，支持多种编程语言，价格比GitHub Copilot低30%。业内认为这将加剧AI编程工具市场竞争。",
        "tags": ["腾讯", "AI编程", "Copilot"],
        "source": "36氪",
        "url": "https://example.com/news/14"
    },
    {
        "title": "欧盟通过《人工智能法案》 全球首部AI监管法律",
        "date": "2025-12-21 11:00",
        "summary": "欧盟议会正式通过《人工智能法案》，对高风险AI系统实施严格监管。违规企业最高可被罚款3000万欧元或全球营收的6%。",
        "tags": ["欧盟", "AI监管", "法案"],
        "source": "新华社",
        "url": "https://example.com/news/15"
    },
    {
        "title": "阿里巴巴回归港股主板 首日涨幅达8%",
        "date": "2025-12-21 10:00",
        "summary": "阿里巴巴完成港股双重主要上市，首日开盘大涨8%，成交额突破200亿港元。分析师看好回归后的资金流入效应。",
        "tags": ["阿里巴巴", "港股", "回归"],
        "source": "彭博社",
        "url": "https://example.com/news/16"
    },
    {
        "title": "韩国央行降息25个基点 应对经济下行压力",
        "date": "2025-12-20 18:00",
        "summary": "韩国央行宣布降息25个基点至3.25%，为连续第二次降息。央行表示将继续关注经济下行风险和通胀走势。",
        "tags": ["韩国", "降息", "货币政策"],
        "source": "路透社",
        "url": "https://example.com/news/17"
    },
    {
        "title": "蔚来汽车推出手机NIO Phone 进军消费电子",
        "date": "2025-12-20 16:00",
        "summary": "蔚来正式发布首款智能手机NIO Phone，售价6499元起。李斌表示手机将与汽车深度融合，打造完整的用户生态。",
        "tags": ["蔚来", "手机", "消费电子"],
        "source": "虎嗅网",
        "url": "https://example.com/news/18"
    },
    {
        "title": "全球半导体销售额连续4个月增长 复苏迹象明显",
        "date": "2025-12-20 14:00",
        "summary": "世界半导体贸易统计协会数据显示，10月全球半导体销售额同比增长11.6%，连续4个月保持增长，行业复苏趋势明显。",
        "tags": ["半导体", "芯片", "行业"],
        "source": "集微网",
        "url": "https://example.com/news/19"
    },
    {
        "title": "字节跳动估值达2250亿美元 超越阿里成中国第一",
        "date": "2025-12-20 13:00",
        "summary": "据知情人士透露，字节跳动最新一轮内部股票回购估值达2250亿美元，超越阿里巴巴成为中国估值最高的互联网公司。",
        "tags": ["字节跳动", "估值", "互联网"],
        "source": "晚点LatePost",
        "url": "https://example.com/news/20"
    },
    {
        "title": "中国11月外贸数据超预期 出口增长8.5%",
        "date": "2025-12-20 10:00",
        "summary": "海关总署公布11月外贸数据，出口同比增长8.5%，进口增长6.7%，均超市场预期。前11个月贸易顺差达8234亿美元。",
        "tags": ["外贸", "出口", "进口"],
        "source": "央视财经",
        "url": "https://example.com/news/21"
    },
]


async def add_headlines():
    """添加更多头条新闻"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        async with session.begin():
            # 获取当前最大ID
            from sqlalchemy import select
            result = await session.execute(select(func.max(HeadlineNews.id)))
            max_id = result.scalar() or 0
            
            print(f"当前最大ID: {max_id}")
            
            # 添加新数据
            for idx, item in enumerate(MORE_HEADLINES, start=1):
                headline = HeadlineNews(
                    id=max_id + idx,
                    title=item["title"],
                    date=item["date"],
                    summary=item["summary"],
                    tags=item["tags"],
                    source=item["source"],
                    url=item["url"],
                    is_hot=idx <= 5  # 前5条设为热点
                )
                session.add(headline)
                print(f"添加: {headline.title}")
            
            await session.commit()
            print(f"\n成功添加 {len(MORE_HEADLINES)} 条新闻！")


if __name__ == "__main__":
    asyncio.run(add_headlines())
