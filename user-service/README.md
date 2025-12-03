# User Service

用户管理服务，负责用户注册、登录、认证、用户数据同步等。

## 快速开始

### 使用 Docker（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f user-service

# 访问 API 文档
open http://localhost:8005/docs
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动服务
make dev  # 或 uvicorn app.main:app --reload --port 8005

# 启动 Celery Worker（新终端）
make worker

# 启动 Celery Beat（新终端）
make beat
```

## 目录结构

```
user-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口（含/health和/status端点）
│   ├── config.py            # 配置管理（Pydantic Settings）
│   ├── crawler/             # 用户数据同步模块 ⭐
│   │   ├── __init__.py
│   │   ├── base.py          # 采集器基类
│   │   ├── wechat.py        # 微信用户同步
│   │   └── external.py      # 外部系统用户同步
│   ├── cleaner/             # 用户数据清洗模块 ⭐
│   │   ├── __init__.py
│   │   ├── base.py          # 清洗器基类
│   │   └── user.py          # 用户数据清洗器
│   ├── scheduler/           # 任务调度模块 ⭐
│   │   ├── __init__.py
│   │   ├── celery_app.py    # Celery配置
│   │   └── tasks/           # Celery任务
│   │       ├── __init__.py
│   │       └── user_tasks.py # 用户相关任务
│   └── utils/               # 工具模块
│       ├── __init__.py
│       └── logger.py        # 日志配置
├── requirements.txt         # Python依赖
├── Dockerfile              # Docker镜像构建
├── docker-compose.yml      # Docker Compose配置（含Celery Workers）
├── Makefile                # 便捷命令
├── pyproject.toml          # 代码格式化配置
├── .env.example            # 环境变量示例
└── README.md              # 本文档
```

⭐ 表示核心模块

## 核心功能

### 1. 用户数据同步 (Crawler)

- **BaseCrawler**: 抽象基类，定义同步器接口
- **WeChatUserCrawler**: 微信小程序用户同步
- **ExternalUserCrawler**: 外部系统用户同步

### 2. 用户数据清洗 (Cleaner)

- **BaseCleaner**: 抽象基类，定义清洗器接口
- **UserDataCleaner**: 用户数据清洗器（包含验证、格式化）

### 3. 任务调度 (Scheduler)

- **Celery集成**: 使用 Redis 作为消息队列
- **定时任务**: 使用 Celery Beat 调度
- **异步任务**: 支持用户数据同步、令牌清理等

## API 端点

### 健康检查

- `GET /` - 根路径，返回服务信息
- `GET /health` - 基本健康检查
- `GET /status` - 详细状态检查（包含 Redis、PostgreSQL 健康状态）

### 示例请求

```bash
# 健康检查
curl http://localhost:8005/health

# 状态检查
curl http://localhost:8005/status
```

## Celery 任务

### 用户同步任务

- `sync_wechat_users` - 同步微信用户（每小时执行）
- `sync_external_users` - 同步外部系统用户
- `clean_user_data` - 清洗用户数据

### 维护任务

- `clean_expired_tokens` - 清理过期令牌（每小时执行）
- `clean_inactive_users` - 清理非活跃用户（每日执行）

## 技术栈

- **Web框架**: FastAPI 0.104+
- **任务队列**: Celery 5.3+ with Redis
- **数据库**: PostgreSQL 15+ (SQLAlchemy)
- **缓存**: Redis 7+
- **认证**: JWT (python-jose)
- **密码加密**: bcrypt (passlib)
- **配置管理**: Pydantic Settings
- **日志**: Python logging

## 环境变量

参见 `.env.example` 文件，主要配置项：

- `POSTGRES_URL` - PostgreSQL 连接字符串
- `REDIS_URL` - Redis 连接字符串
- `CELERY_BROKER_URL` - Celery Broker URL
- `JWT_SECRET_KEY` - JWT 密钥（生产环境必须修改）
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Access Token 过期时间（分钟）
- `WECHAT_APPID` - 微信小程序 AppID
- `WECHAT_SECRET` - 微信小程序 Secret

## 开发规范

- 遵循 Python 最佳实践（PEP 8）
- 使用类型提示（Type Hints）
- 完整的文档字符串（Docstrings）
- 代码格式化：Black + isort
- 类型检查：mypy

## Docker 服务

docker-compose.yml 包含以下服务：

- `user-service` - FastAPI 应用
- `celery-worker-users` - 用户任务 Worker
- `celery-beat` - 任务调度器
- `postgres` - PostgreSQL 数据库
- `redis` - Redis 缓存和消息队列

## 安全特性

- 密码哈希存储（bcrypt）
- JWT Token 认证
- 密码强度验证
- 敏感数据清理
- SQL 注入防护（SQLAlchemy ORM）

