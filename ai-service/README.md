# AI Service

AI中台服务，负责LLM网关、Prompt管理、AI内容生成、策略代码生成等。

## 快速开始

### 使用 Docker（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f ai-service

# 访问 API 文档
open http://localhost:8002/docs
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 API 密钥

# 启动服务
make dev  # 或 uvicorn app.main:app --reload --port 8002

# 启动 Celery Worker（新终端）
make worker

# 启动 Celery Beat（新终端）
make beat
```

## 目录结构

```
ai-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口（含/health和/status端点）
│   ├── config.py            # 配置管理（Pydantic Settings）
│   ├── crawler/             # 数据采集模块 ⭐
│   │   ├── __init__.py
│   │   ├── base.py          # 采集器基类
│   │   ├── prompt.py        # Prompt模板采集
│   │   └── vector.py        # 向量数据采集
│   ├── cleaner/             # 内容清洗模块 ⭐
│   │   ├── __init__.py
│   │   ├── base.py          # 清洗器基类
│   │   └── content.py       # AI生成内容清洗器
│   ├── scheduler/           # 任务调度模块 ⭐
│   │   ├── __init__.py
│   │   ├── celery_app.py    # Celery配置
│   │   └── tasks/           # Celery任务
│   │       ├── __init__.py
│   │       └── ai_tasks.py  # AI相关任务
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
- **PromptTemplateCrawler**: Prompt模板采集
- **VectorDataCrawler**: 向量数据采集

### 2. 内容清洗 (Cleaner)

- **BaseCleaner**: 抽象基类，定义清洗器接口
- **ContentCleaner**: AI生成内容清洗器（HTML清理、Markdown处理、风险提示）

### 3. 任务调度 (Scheduler)

- **Celery集成**: 使用 Redis 作为消息队列
- **定时任务**: 使用 Celery Beat 调度
- **异步任务**: 支持AI内容生成、报告生成等

## API 端点

### 健康检查

- `GET /` - 根路径，返回服务信息
- `GET /health` - 基本健康检查
- `GET /status` - 详细状态检查（包含 Redis、PostgreSQL、Milvus、LLM 提供商状态）

### 示例请求

```bash
# 健康检查
curl http://localhost:8002/health

# 状态检查
curl http://localhost:8002/status
```

## Celery 任务

### AI生成任务

- `generate_daily_report` - 生成投资日刊（每日16:00执行）
- `generate_news_article` - 生成新闻文章
- `generate_strategy_code` - 生成策略代码

### 维护任务

- `sync_prompt_templates` - 同步Prompt模板（每小时执行）
- `clean_old_generations` - 清理旧生成内容（每日执行）
- `clean_content` - 清洗生成内容

## 技术栈

- **Web框架**: FastAPI 0.104+
- **任务队列**: Celery 5.3+ with Redis
- **数据库**: PostgreSQL 15+ (SQLAlchemy)
- **向量数据库**: Milvus 2.3+
- **LLM SDKs**: OpenAI (兼容DeepSeek), DashScope (Qwen)
- **NLP**: LangChain, Sentence Transformers
- **配置管理**: Pydantic Settings
- **日志**: Python logging

## 环境变量

参见 `.env.example` 文件，主要配置项：

- `POSTGRES_URL` - PostgreSQL 连接字符串
- `REDIS_URL` - Redis 连接字符串
- `CELERY_BROKER_URL` - Celery Broker URL
- `DEEPSEEK_API_KEY` - DeepSeek API 密钥
- `QWEN_API_KEY` - 通义千问 API 密钥
- `MILVUS_HOST` - Milvus 主机地址
- `MILVUS_PORT` - Milvus 端口

## 开发规范

- 遵循 Python 最佳实践（PEP 8）
- 使用类型提示（Type Hints）
- 完整的文档字符串（Docstrings）
- 代码格式化：Black + isort
- 类型检查：mypy

## Docker 服务

docker-compose.yml 包含以下服务：

- `ai-service` - FastAPI 应用
- `celery-worker-ai` - AI任务 Worker
- `celery-beat` - 任务调度器
- `postgres` - PostgreSQL 数据库
- `redis` - Redis 缓存和消息队列
- `milvus` - Milvus 向量数据库
