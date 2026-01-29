import asyncio
from sqlalchemy import text
from core.database import get_async_session

async def upgrade():
    print("Starting migration...")
    statements = [
        "ALTER TABLE lhb_stock_item ADD COLUMN IF NOT EXISTS net_buy_ratio FLOAT;",
        "ALTER TABLE lhb_stock_item ADD COLUMN IF NOT EXISTS turnover_rate FLOAT;",
        "ALTER TABLE lhb_stock_item ADD COLUMN IF NOT EXISTS circulation_market_value FLOAT;"
    ]

    async for session in get_async_session():
        print("Got session")
        for stmt in statements:
            try:
                print(f"Executing: {stmt}")
                await session.execute(text(stmt))
            except Exception as e:
                print(f"Error executing {stmt}: {e}")
        await session.commit()
    print("Migration finished.")

if __name__ == "__main__":
    import sys
    import os
    # Add data-service to path
    sys.path.append(os.path.join(os.getcwd(), "data-service"))
    asyncio.run(upgrade())
