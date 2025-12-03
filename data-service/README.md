# Data Service

数据中台服务，负责行情数据采集、新闻快讯抓取、数据清洗、存储等。

## 快速开始

### 使用 Docker（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f data-service

# 访问 API 文档
open http://localhost:8001/docs
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动服务
make dev  # 或 uvicorn app.main:app --reload --port 8001

# 启动 Celery Worker（新终端）
make worker

# 启动 Celery Beat（新终端）
make beat
```

详细开发指南请参考 [README_DEVELOPMENT.md](./README_DEVELOPMENT.md)

## 目录结构

```
data-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口（含/health和/status端点）
│   ├── config.py            # 配置管理（Pydantic Settings）
│   ├── crawler/             # 数据采集模块 ⭐
│   │   ├── __init__.py
│   │   ├── base.py          # 采集器基类
│   │   ├── market.py        # 行情数据采集器
│   │   └── news.py          # 新闻采集器
│   ├── cleaner/             # 数据清洗模块 ⭐
│   │   ├── __init__.py
│   │   ├── base.py          # 清洗器基类
│   │   ├── market.py        # 行情数据清洗器
│   │   └── news.py          # 新闻清洗器
│   ├── scheduler/           # 任务调度模块 ⭐
│   │   ├── __init__.py
│   │   ├── celery_app.py    # Celery配置
│   │   └── tasks/           # Celery任务
│   │       ├── __init__.py
│   │       ├── market_tasks.py  # 市场数据任务
│   │       └── news_tasks.py    # 新闻任务
│   └── utils/               # 工具模块
│       ├── __init__.py
│       └── logger.py        # 日志配置
├── requirements.txt         # Python依赖
├── Dockerfile              # Docker镜像构建
├── docker-compose.yml      # Docker Compose配置（含Celery Workers）
├── Makefile                # 便捷命令
├── pyproject.toml          # 代码格式化配置
├── .env.example            # 环境变量示例
└── README_DEVELOPMENT.md   # 开发指南
```

⭐ 表示新创建的核心模块

## 核心功能

### 1. 数据采集 (Crawler)

- **BaseCrawler**: 抽象基类，定义采集器接口
- **MarketDataCrawler**: 行情数据采集器
- **NewsCrawler**: 新闻采集器

### 2. 数据清洗 (Cleaner)

- **BaseCleaner**: 抽象基类，定义清洗器接口
- **MarketDataCleaner**: 行情数据清洗器
- **NewsCleaner**: 新闻清洗器

### 3. 任务调度 (Scheduler)

- **Celery集成**: 使用 Redis 作为消息队列
- **定时任务**: 使用 Celery Beat 调度
- **异步任务**: 支持市场数据和新闻的异步采集

## API 端点

### 健康检查

- `GET /` - 根路径，返回服务信息
- `GET /health` - 基本健康检查
- `GET /status` - 详细状态检查（包含 Redis、PostgreSQL 健康状态）

### 示例请求

```bash
# 健康检查
curl http://localhost:8001/health

# 状态检查
curl http://localhost:8001/status
```

## Celery 任务

### 市场数据任务

- `collect_realtime_quotes` - 采集实时行情（每分钟执行）
- `collect_kline_data` - 采集K线数据
- `clean_market_data` - 清洗市场数据

### 新闻任务

- `collect_latest_news` - 采集最新新闻（每5分钟执行）
- `clean_news_data` - 清洗新闻数据
- `process_flash_news` - 处理快讯

## 技术栈

- **Web框架**: FastAPI 0.104+
- **任务队列**: Celery 5.3+ with Redis
- **数据库**: PostgreSQL 15+ (SQLAlchemy)
- **缓存**: Redis 7+
- **配置管理**: Pydantic Settings
- **日志**: Python logging

## 环境变量

参见 `.env.example` 文件，主要配置项：

- `POSTGRES_URL` - PostgreSQL 连接字符串
- `REDIS_URL` - Redis 连接字符串
- `CELERY_BROKER_URL` - Celery Broker URL
- `TUSHARE_TOKEN` - Tushare API Token
- `CLS_API_KEY` - 财联社 API Key

## 开发规范

- 遵循 Python 最佳实践（PEP 8）
- 使用类型提示（Type Hints）
- 完整的文档字符串（Docstrings）
- 代码格式化：Black + isort
- 类型检查：mypy

## Docker 服务

docker-compose.yml 包含以下服务：

- `data-service` - FastAPI 应用
- `celery-worker-market` - 市场数据 Worker
- `celery-worker-news` - 新闻数据 Worker
- `celery-beat` - 任务调度器
- `postgres` - PostgreSQL 数据库
- `redis` - Redis 缓存和消息队列

