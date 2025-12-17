# 数据库设置指南

## 问题说明

如果遇到以下错误：
```
psycopg2.OperationalError: connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

这表示 PostgreSQL 服务未运行或无法连接。 
## 解决方案

### 方案 1：启动 PostgreSQL 服务（推荐用于生产环境）

#### Windows

1. **使用 PostgreSQL 安装包**
   - 下载并安装 PostgreSQL: https://www.postgresql.org/download/windows/
   - 安装后，PostgreSQL 服务会自动启动

2. **使用服务管理器启动**
   ```powershell
   # 启动 PostgreSQL 服务
   net start postgresql-x64-14  # 版本号可能不同
   
   # 或使用服务管理器
   services.msc  # 找到 PostgreSQL 服务并启动
   ```

3. **创建数据库**
   ```sql
   -- 使用 psql 命令行工具
   psql -U postgres
   CREATE DATABASE quantbull;
   ```

#### Docker（推荐用于开发环境）

```powershell
# 启动 PostgreSQL 容器
docker run -d --name postgres-quantbull -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=quantbull -p 8000:8000 postgres:15

# 或者使用 docker-compose（如果项目中有）
docker-compose up -d postgres
```

### 方案 2：使用 SQLite（仅用于开发测试）

如果暂时不想安装 PostgreSQL，可以修改配置使用 SQLite：

1. **修改 `.env` 文件**
   ```env
   DATABASE_URL=sqlite:///./quantbull.db
   ```

2. **修改 `core/database.py`**
   ```python
   # 将 PostgreSQL 连接改为 SQLite
   sync_database_url = settings.database_url
   if sync_database_url.startswith("sqlite"):
       engine = create_engine(sync_database_url, echo=False, connect_args={"check_same_thread": False})
   else:
       sync_database_url = settings.database_url.replace("postgresql+psycopg2://", "postgresql://")
       engine = create_engine(sync_database_url, echo=False)
   ```

### 方案 3：跳过数据库初始化（仅测试 API）

应用已经修改为：**即使数据库不可用，应用也能正常启动**。

- API 接口可以正常访问
- 但保存数据到数据库的功能会失败
- 爬虫功能仍然可以正常工作

## 配置数据库连接

创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=postgresql+psycopg2://用户名:密码@主机:端口/数据库名

# 示例
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/quantbull
```

## 验证连接

```powershell
# 测试 PostgreSQL 连接
psql -U postgres -h localhost -d quantbull

# 或在 Python 中测试
python -c "from core.database import engine; engine.connect(); print('连接成功')"
```

## 注意事项

- 生产环境必须使用 PostgreSQL
- 开发环境可以使用 SQLite 或 PostgreSQL
- 应用启动时如果数据库不可用，会记录警告但不会阻止启动
- 首次使用需要手动创建数据库

