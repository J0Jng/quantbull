Task Service (MVP)
===================

This module implements a simple platform-level async task service (MVP).

Features:
- POST /api/tasks -> create task, returns `task_id`
- GET /api/tasks/{task_id} -> stable status schema
- In-memory `TaskStore` and `TaskManager` with handler registry
- Simple sample handlers (backtest, quick)

Future upgrades: persist to Redis, replace asyncio.create_task with Celery or other worker.
