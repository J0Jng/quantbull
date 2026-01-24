"""东方财富财报抓取测试脚本（轻量）"""
import asyncio

from core.database import AsyncSessionLocal
from services.eastmoney_bbsj_service import EastmoneyBbsjService


async def main():
    async with AsyncSessionLocal() as session:
        service = EastmoneyBbsjService(db_session=session)
        data = await service.fetch_yjbb(period=None, page=1, page_size=20, refresh=True)
        print(f"yjbb rows: {len(data.get('data', []))}")
        data2 = await service.fetch_yjyg(period=None, page=1, page_size=20, refresh=True)
        print(f"yjyg rows: {len(data2.get('data', []))}")


if __name__ == '__main__':
    asyncio.run(main())
