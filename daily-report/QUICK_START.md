# Daily Report Service - 快速启动指南

## 🚀 快速开始

### 1. 安装依赖

```bash
cd daily-report
pip install -r requirements.txt
```

### 2. 配置数据库

#### 选项 A：使用 SQLite（推荐用于测试，无需 PostgreSQL）

创建 `.env` 文件：

```env
ENV=local
LOG_LEVEL=INFO
PORT=8004
HOST=0.0.0.0

# 使用 SQLite（无需 PostgreSQL）
DB_TYPE=sqlite
SQLITE_PATH=daily_report.db

DEFAULT_TIMEZONE=Asia/Shanghai
```

#### 选项 B：使用内存数据库（数据不持久化）

```env
DB_TYPE=memory
```

#### 选项 C：使用 PostgreSQL（生产环境）

确保 PostgreSQL 已安装并运行：

```bash
# 创建数据库
createdb quantbull
```

`.env` 配置：

```env
DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=quantbull
POSTGRES_SCHEMA=public
```

### 3. 配置环境变量（可选）

如果不创建 `.env` 文件，将使用默认配置（SQLite）。

### 4. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8004` 启动。

---

## 🐳 Docker + PostgreSQL 持久化（推荐）

在 Docker Compose 环境下，`daily-report` 可以与 `data-service` 共用同一个 PostgreSQL 实例。
为了隔离数据，`daily-report` 使用独立的 schema/user（默认 `daily_report` / `daily_report_user`）。

⚠️ **注意**：初始化 SQL 只在 PostgreSQL 数据卷首次创建时执行。如果你的 `pgdata` 已存在，
需要手动创建 schema/user 或谨慎清空卷后重启。

### 验证表与数据

1) 验证表在 `daily_report` schema 下：

```bash
psql -h localhost -U daily_report_user -d quantbull_db \
  -c "\dt daily_report.*"
```

应能看到：

- `daily_report.company_research_reports`
- `daily_report.daily_investment_reports`

2) 生成一份报告后验证数据写入：

```bash
psql -h localhost -U daily_report_user -d quantbull_db \
  -c "SELECT id, report_date, status FROM daily_report.daily_investment_reports ORDER BY created_at DESC LIMIT 5;"
```

---

## 📡 API 使用示例

### 手动触发生成报告

```bash
curl -X POST "http://localhost:8004/api/daily-report/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "report_date": "2024-01-01",
    "force": false
  }'
```

### 获取最新报告

```bash
curl "http://localhost:8004/api/daily-report/latest"
```

### 根据日期获取报告

```bash
curl "http://localhost:8004/api/daily-report/date/2024-01-01"
```

### 列出所有报告

```bash
curl "http://localhost:8004/api/daily-report?limit=10&offset=0"
```

---

## 🔍 查看 API 文档

启动服务后访问：

- **Swagger UI**: http://localhost:8004/docs
- **ReDoc**: http://localhost:8004/redoc

---

## ⏰ 定时任务

定时任务会在**每个交易日 15:10（Asia/Shanghai）**自动执行。

### 查看定时任务状态

服务启动时会输出：

```
定时任务已配置: 每日 15:10 生成投资方案
调度器已启动
```

### 手动触发（测试）

如果不想等待定时任务，可以手动触发：

```bash
curl -X POST "http://localhost:8004/api/daily-report/generate"
```

---

## 🧪 开发环境说明

### 模拟数据

在开发环境（`ENV=local`）下：

- 如果 `data-service` 不可用，会使用模拟的市场数据
- 如果 `ai-hub` 不可用，会使用模拟的 AI 生成内容

### 服务地址配置

当前硬编码的服务地址：

- `data-service`: `http://localhost:8001`
- `ai-hub`: `http://localhost:8002`

**开发时**：确保这两个服务运行，或使用模拟数据。

---

## 🐛 常见问题

### 1. 数据库连接失败

**错误**：`could not connect to server`

**解决**：
- 确保 PostgreSQL 已启动
- 检查 `.env` 中的数据库配置
- 确认数据库 `quantbull` 已创建

### 2. 定时任务不执行

**检查**：
- 查看日志是否有错误
- 确认时区设置正确（Asia/Shanghai）
- 手动触发测试：`POST /api/daily-report/generate`

### 3. 服务调用失败

**错误**：`调用 data-service 失败` 或 `调用 ai-hub 失败`

**解决**：
- 开发环境会自动使用模拟数据
- 生产环境需要确保服务可访问
- 检查服务地址配置

---

## 📊 数据库初始化

首次运行会自动创建表结构。

如果需要手动初始化：

```python
from db.session import init_db
init_db()
```

---

## 🐳 Docker 测试（无需 PostgreSQL）

### 方式一：使用 docker-compose（推荐）

```bash
# 使用 SQLite（数据持久化到 ./data 目录）
docker-compose -f docker-compose.test.yml up -d

# 查看日志
docker-compose -f docker-compose.test.yml logs -f

# 停止
docker-compose -f docker-compose.test.yml down
```

### 方式二：直接使用 Docker

```bash
# 构建
docker build -t daily-report:latest .

# 运行（使用 SQLite，无需 PostgreSQL）
docker run -d \
  -p 8004:8004 \
  -e DB_TYPE=sqlite \
  -e SQLITE_PATH=/app/daily_report.db \
  -v $(pwd)/data:/app/data \
  --name daily-report \
  daily-report:latest

# 或使用内存数据库（数据不持久化）
docker run -d \
  -p 8004:8004 \
  -e DB_TYPE=memory \
  --name daily-report \
  daily-report:latest
```

## 🔧 生产环境部署

### Docker 部署（使用 PostgreSQL）

```bash
# 构建
docker build -t daily-report:latest .

# 运行
docker run -d \
  -p 8004:8004 \
  -e DB_TYPE=postgresql \
  -e POSTGRES_HOST=your_postgres_host \
  -e POSTGRES_PASSWORD=your_password \
  --name daily-report \
  daily-report:latest
```

### 环境变量

生产环境必须配置：

```env
ENV=production
DB_TYPE=postgresql
POSTGRES_HOST=your_postgres_host
POSTGRES_PASSWORD=your_password
DATA_SERVICE_URL=http://data-service:8001
AI_HUB_URL=http://ai-hub:8002
```

### 数据库类型说明

- **`sqlite`**：使用 SQLite 数据库，适合测试和开发，无需额外服务
- **`memory`**：使用内存数据库，数据不持久化，适合快速测试
- **`postgresql`**：使用 PostgreSQL，适合生产环境

---

## 📝 下一步

1. **配置服务地址**：修改 `data_client.py` 和 `ai_client.py` 中的服务地址
2. **实现交易日判断**：添加交易日判断逻辑，避免非交易日执行
3. **接入消息队列**：考虑使用 Celery 或 RabbitMQ 处理异步任务
4. **监控告警**：添加 Prometheus 监控和告警

---

## 📚 相关文档

- [MODULE_DESIGN.md](./MODULE_DESIGN.md) - 模块设计文档
- [README.md](./README.md) - 项目说明
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - 项目结构
