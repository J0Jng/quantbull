# Docker 测试指南（无需 PostgreSQL）

## 🚀 快速开始

### 方式一：使用 docker-compose（推荐）

```bash
# 启动服务（使用 SQLite）
docker-compose -f docker-compose.test.yml up -d

# 查看日志
docker-compose -f docker-compose.test.yml logs -f

# 停止服务
docker-compose -f docker-compose.test.yml down
```

服务将在 `http://localhost:8004` 启动。

### 方式二：直接使用 Docker

```bash
# 构建镜像
docker build -t daily-report:latest .

# 运行（使用 SQLite，数据持久化）
docker run -d \
  -p 8004:8004 \
  -e DB_TYPE=sqlite \
  -e SQLITE_PATH=/app/data/daily_report.db \
  -v $(pwd)/data:/app/data \
  --name daily-report \
  daily-report:latest

# 查看日志
docker logs -f daily-report

# 停止
docker stop daily-report
docker rm daily-report
```

### 方式三：使用内存数据库（数据不持久化）

```bash
docker run -d \
  -p 8004:8004 \
  -e DB_TYPE=memory \
  --name daily-report \
  daily-report:latest
```

## 📝 环境变量说明

### SQLite 配置（推荐用于测试）

```env
DB_TYPE=sqlite
SQLITE_PATH=/app/data/daily_report.db
```

### 内存数据库配置（数据不持久化）

```env
DB_TYPE=memory
```

### PostgreSQL 配置（生产环境）

```env
DB_TYPE=postgresql
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=quantbull
```

## 🧪 测试 API

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

### 查看 API 文档

访问：http://localhost:8004/docs

## 📊 数据持久化

### SQLite 模式

- 数据文件保存在 `./data/daily_report.db`
- 容器重启后数据仍然存在
- 适合测试和开发环境

### 内存模式

- 数据存储在内存中
- 容器重启后数据丢失
- 适合快速测试

## 🔍 常见问题

### 1. 数据库文件权限问题

如果遇到权限问题，可以：

```bash
# 创建数据目录
mkdir -p data

# 设置权限
chmod 777 data
```

### 2. 查看数据库文件

```bash
# 进入容器
docker exec -it daily-report bash

# 查看数据库文件
ls -lh /app/data/daily_report.db

# 使用 sqlite3 查看数据
sqlite3 /app/data/daily_report.db
.tables
SELECT * FROM daily_investment_reports;
```

### 3. 清理数据

```bash
# 停止容器
docker-compose -f docker-compose.test.yml down

# 删除数据库文件
rm -f data/daily_report.db

# 重新启动
docker-compose -f docker-compose.test.yml up -d
```

## 🎯 优势

使用 SQLite 进行 Docker 测试的优势：

- ✅ **无需额外服务**：不需要启动 PostgreSQL 容器
- ✅ **快速启动**：启动速度快，资源占用少
- ✅ **数据持久化**：通过 volume 挂载，数据可以持久化
- ✅ **易于测试**：适合本地开发和测试
- ✅ **兼容性好**：SQLAlchemy 完全支持 SQLite

## 📚 相关文档

- [QUICK_START.md](./QUICK_START.md) - 快速启动指南
- [MODULE_DESIGN.md](./MODULE_DESIGN.md) - 模块设计文档
