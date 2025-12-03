# Quant Engine Service

量化引擎服务，负责策略回测、因子计算、股票筛选、ETF轮动等。

## 快速开始

### 使用 Docker（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f quant-engine

# 访问 API 文档
open http://localhost:8003/docs
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动服务
make dev  # 或 uvicorn app.main:app --reload --port 8003

# 启动 Celery Worker（新终端）
make worker

# 启动 Celery Beat（新终端）
make beat
```

## 目录结构

```
quant-engine/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口（含/health和/status端点）
│   ├── config.py            # 配置管理（Pydantic Settings）
│   ├── crawler/             # 数据采集模块 ⭐
│   │   ├── __init__.py
│   │   ├── base.py          # 采集器基类
│   │   ├── market.py        # 市场数据采集
│   │   └── factor.py        # 因子数据采集
│   ├── cleaner/             # 数据清洗模块 ⭐
│   │   ├── __init__.py
│   │   ├── base.py          # 清洗器基类
│   │   ├── market.py        # 市场数据清洗器
│   │   └── factor.py        # 因子数据清洗器
│   ├── scheduler/           # 任务调度模块 ⭐
│   │   ├── __init__.py
│   │   ├── celery_app.py    # Celery配置
│   │   └── tasks/           # Celery任务
│   │       ├── __init__.py
│   │       └── quant_tasks.py # 量化相关任务
│   └── utils/               # 工具模块
│       ├── __init__.py
│       └── logger.py        # 日志配置
├── requirements.txt         # Python依赖
├── Dockerfile              # Docker镜像构建
├── docker-compose.yml      # Docker Compose配置（含Celery Workers）
├── Makefile                # 便捷命令
├── pyproject.toml          # 代码格式化配置
└── .env.example            # 环境变量示例
```

⭐ 表示核心模块

## 核心功能

### 1. 数据采集 (Crawler)

- **BaseCrawler**: 抽象基类，定义采集器接口
- **MarketDataCrawler**: 市场数据采集（从data-service获取）
- **FactorDataCrawler**: 因子数据采集

### 2. 数据清洗 (Cleaner)

- **BaseCleaner**: 抽象基类，定义清洗器接口
- **MarketDataCleaner**: 市场数据清洗器（价格一致性验证、数据标准化）
- **FactorDataCleaner**: 因子数据清洗器（NaN/Inf处理、数据验证）

### 3. 任务调度 (Scheduler)

- **Celery集成**: 使用 Redis 作为消息队列
- **定时任务**: 使用 Celery Beat 调度
- **异步任务**: 支持回测、因子计算、股票筛选等

## API 端点

### 健康检查

- `GET /` - 根路径，返回服务信息
- `GET /health` - 基本健康检查
- `GET /status` - 详细状态检查（包含 Redis、PostgreSQL、Data Service 健康状态）

### 示例请求

```bash
# 健康检查
curl http://localhost:8003/health

# 状态检查
curl http://localhost:8003/status
```

## Celery 任务

### 回测任务

- `run_backtest` - 运行策略回测
- `run_scheduled_backtests` - 运行定时回测（每日执行）

### 因子计算任务

- `calculate_factors_daily` - 每日因子计算（16:30执行）

### 选股任务

- `update_stock_scores` - 更新股票评分（16:00执行）
- `select_stocks` - 根据条件选股

### 数据清洗任务

- `clean_market_data` - 清洗市场数据

## 技术栈

- **Web框架**: FastAPI 0.104+
- **任务队列**: Celery 5.3+ with Redis
- **数据库**: PostgreSQL 15+ (SQLAlchemy)
- **缓存**: Redis 7+
- **回测框架**: Backtrader
- **数据处理**: pandas, numpy, scipy
- **技术分析**: TA-Lib
- **机器学习**: scikit-learn
- **配置管理**: Pydantic Settings
- **日志**: Python logging

## 环境变量

参见 `.env.example` 文件，主要配置项：

- `POSTGRES_URL` - PostgreSQL 连接字符串
- `REDIS_URL` - Redis 连接字符串
- `CELERY_BROKER_URL` - Celery Broker URL
- `DATA_SERVICE_URL` - 数据服务地址
- `INITIAL_CAPITAL` - 回测初始资金
- `COMMISSION_RATE` - 手续费率

## 开发规范

- 遵循 Python 最佳实践（PEP 8）
- 使用类型提示（Type Hints）
- 完整的文档字符串（Docstrings）
- 代码格式化：Black + isort
- 类型检查：mypy

## Docker 服务

docker-compose.yml 包含以下服务：

- `quant-engine` - FastAPI 应用
- `celery-worker-quant` - 量化任务 Worker
- `celery-beat` - 任务调度器
- `postgres` - PostgreSQL 数据库
- `redis` - Redis 缓存和消息队列

## 注意事项

### TA-Lib 安装

TA-Lib 需要系统库支持，Dockerfile 中已包含安装步骤。本地开发时可能需要：

```bash
# Ubuntu/Debian
sudo apt-get install ta-lib

# macOS
brew install ta-lib
```

### 回测性能

回测计算可能耗时较长，建议：
- 使用并行计算（配置 `enable_parallel_backtest`）
- 合理设置 Worker 并发数
- 对大量数据进行回测时使用异步任务
