# Data Service 开发指南

## 快速开始

### 环境要求

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+ (或使用 Docker)
- Redis 7+ (或使用 Docker)

### 本地开发

1. **克隆代码并进入目录**

```bash
cd data-service
```

2. **创建虚拟环境**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

4. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入配置
```

5. **启动服务**

```bash
# 启动 FastAPI 服务
uvicorn app.main:app --reload --port 8001

# 在另一个终端启动 Celery Worker
celery -A app.scheduler.celery_app worker --loglevel=info

# 在另一个终端启动 Celery Beat
celery -A app.scheduler.celery_app beat --loglevel=info
```

### Docker 开发

```bash
# 启动所有服务（包括数据库）
docker-compose up -d

# 查看日志
docker-compose logs -f data-service

# 停止服务
docker-compose down
```

## 代码结构

```
data-service/
├── app/
│   ├── crawler/          # 数据采集模块
│   │   ├── base.py       # 采集器基类
│   │   ├── market.py     # 行情数据采集器
│   │   └── news.py       # 新闻采集器
│   ├── cleaner/          # 数据清洗模块
│   │   ├── base.py       # 清洗器基类
│   │   ├── market.py     # 行情数据清洗器
│   │   └── news.py       # 新闻清洗器
│   ├── scheduler/        # 任务调度模块
│   │   ├── celery_app.py # Celery 配置
│   │   └── tasks/        # Celery 任务
│   ├── utils/            # 工具模块
│   │   └── logger.py     # 日志配置
│   ├── config.py         # 配置管理
│   └── main.py           # FastAPI 应用入口
├── requirements.txt      # Python 依赖
├── Dockerfile           # Docker 镜像构建
└── docker-compose.yml   # Docker Compose 配置
```

## API 端点

### 健康检查

- `GET /health` - 基本健康检查
- `GET /status` - 详细状态检查（包含依赖健康）

### 示例

```bash
# 健康检查
curl http://localhost:8001/health

# 状态检查
curl http://localhost:8001/status
```

## Celery 任务

### 市场数据任务

- `collect_realtime_quotes` - 采集实时行情
- `collect_kline_data` - 采集K线数据
- `clean_market_data` - 清洗市场数据

### 新闻任务

- `collect_latest_news` - 采集最新新闻
- `clean_news_data` - 清洗新闻数据
- `process_flash_news` - 处理快讯

### 手动触发任务

```python
from app.scheduler.tasks.market_tasks import collect_realtime_quotes

# 异步执行
result = collect_realtime_quotes.delay(codes=["000001", "600000"])

# 获取结果
print(result.get(timeout=10))
```

## 开发规范

### 代码格式化

```bash
# 使用 black 格式化代码
black app/

# 使用 isort 整理导入
isort app/
```

### 类型检查

```bash
# 使用 mypy 进行类型检查
mypy app/
```

### 测试

```bash
# 运行测试（待实现）
pytest tests/
```

## 常见问题

### Redis 连接失败

确保 Redis 服务正在运行：

```bash
docker-compose up -d redis
# 或
redis-cli ping
```

### PostgreSQL 连接失败

检查连接字符串格式：

```
postgresql://user:password@host:port/database
```

### Celery Worker 无法启动

检查 Redis 连接和任务队列配置。

## 下一步

- [ ] 实现具体的数据采集逻辑
- [ ] 添加数据存储到数据库
- [ ] 实现完整的错误处理
- [ ] 添加单元测试
- [ ] 配置 CI/CD

