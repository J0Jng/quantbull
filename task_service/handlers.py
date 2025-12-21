import asyncio
from typing import Callable, Dict, Any


async def backtest_handler(payload: Dict[str, Any], update_progress: Callable[[float], None]):
    """Simulated long-running backtest handler for demonstration.

    It periodically calls update_progress and returns a result URL string.
    """
    total_steps = payload.get("steps", 5)
    for i in range(total_steps):
        # simulate work
        await asyncio.sleep(payload.get("step_delay", 1))
        update_progress((i + 1) / total_steps * 0.9)  # leave final 10% for finalizing

    # finalize
    await asyncio.sleep(0.5)
    update_progress(1.0)
    # in real case, upload artifact and return URL
    return f"/results/backtest/{payload.get('name','unknown')}/{int(asyncio.get_event_loop().time())}"


async def quick_task_handler(payload: Dict[str, Any], update_progress: Callable[[float], None]):
    update_progress(0.2)
    await asyncio.sleep(0.2)
    update_progress(1.0)
    return {"result_url": "/results/quick/ok"}


# small helper to register common handlers
def register_default_handlers(manager):
    manager.register_handler("backtest", backtest_handler)
    manager.register_handler("quick", quick_task_handler)
