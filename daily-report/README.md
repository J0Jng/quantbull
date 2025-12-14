# Daily Report Service

每日 AI 投资方案生成服务

## 功能特性

- 📊 日报、周报、月报管理
- 🤖 AI 自动生成投资方案
- 📝 报告状态管理（草稿/已发布/已归档）
- 🔍 报告查询与过滤
- 📋 报告摘要列表

## 技术栈

- Python 3.12
- FastAPI 0.110.3
- Pydantic v2
- Uvicorn

## 项目结构

```
daily-report/
├── main.py                 # FastAPI 入口
├── routers/               # 路由层
│   ├── __init__.py
│   └── report.py          # 报告路由
├── services/              # 业务逻辑层
│   ├── __init__.py
│   └── report_service.py  # 报告服务
├── models/                # 数据模型
│   ├── __init__.py
│   └── report.py          # 报告模型
├── schemas/               # Pydantic 模式
│   ├── __init__.py
│   └── report.py          # 报告模式
├── core/                  # 核心配置
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   └── logger.py          # 日志配置
├── requirements.txt       # 依赖文件
├── Dockerfile            # Docker 配置
└── README.md            # 项目说明
```

## 快速开始

### 本地开发

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行服务：
```bash
python main.py
```

或使用 uvicorn：
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8004
```

3. 访问 API 文档：
- Swagger UI: http://localhost:8004/docs
- ReDoc: http://localhost:8004/redoc

### Docker 运行

1. 构建镜像：
```bash
docker build -t daily-report:latest .
```

2. 运行容器：
```bash
docker run -d -p 8004:8004 --name daily-report daily-report:latest
```

## API 示例

### 创建日报

```bash
curl -X POST "http://localhost:8004/api/report" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "2024年1月1日市场日报",
    "content": "今日市场表现...",
    "report_date": "2024-01-01",
    "report_type": "daily",
    "author": "系统",
    "tags": ["市场分析", "技术指标"]
  }'
```

### 获取日报列表

```bash
curl "http://localhost:8004/api/report?limit=10&offset=0"
```

### 获取日报详情

```bash
curl "http://localhost:8004/api/report/{report_id}"
```

### 发布日报

```bash
curl -X POST "http://localhost:8004/api/report/{report_id}/publish"
```

## 环境变量

创建 `.env` 文件配置环境变量：

```env
ENV=local
LOG_LEVEL=INFO
PORT=8004
HOST=0.0.0.0

# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=quantbull

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

## 健康检查

```bash
curl http://localhost:8004/health
```

响应：
```json
{
  "status": "ok",
  "service": "daily-report",
  "version": "1.0.0",
  "env": "local"
}
```

## 开发说明

- 当前使用内存存储，生产环境应接入数据库（PostgreSQL）
- 所有 API 使用 Pydantic v2 进行数据验证
- 日志配置在 `core/logger.py` 中
- 配置管理在 `core/config.py` 中，支持环境变量

## 注意事项

⚠️ **合规提示**：本服务生成的报告内容仅供投研参考，不构成投资建议。所有内容必须包含风险提示。
