# API Gateway 使用指南

## 🚀 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
python run.py
# 或
uvicorn main:app --host 0.0.0.0 --port 8001
```

## 📡 路由转发规则

API Gateway 会自动将请求转发到对应的微服务：

| 路径前缀 | 转发到 | 示例 |
|---------|--------|------|
| `/news/*` | `http://ai-hub:8002` | `/news/generate` → `http://ai-hub:8002/generate` |
| `/data/*` | `http://data-service:8003` | `/data/clean` → `http://data-service:8003/clean` |
| `/quant/*` | `http://quant-engine:8004` | `/quant/backtest` → `http://quant-engine:8004/backtest` |
| `/report/*` | `http://daily-report:8005` | `/report/daily` → `http://daily-report:8005/daily` |

## 🔐 认证说明

### 1. 获取 Token（需要先有认证服务）

```bash
# 假设有认证服务提供登录接口
curl -X POST "http://localhost:8001/api/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. 使用 Token 访问接口

所有接口（除白名单外）都需要在请求头中携带 Token：

```bash
curl -X GET "http://localhost:8001/news/list" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. 白名单路径（不需要鉴权）

- `/health` - 健康检查
- `/docs` - Swagger 文档
- `/openapi.json` - OpenAPI 规范
- `/redoc` - ReDoc 文档
- `/` - 根路径

## 📝 使用示例

### 示例 1: 转发到 data-service

```bash
# GET 请求
curl -X GET "http://localhost:8001/data/records?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# POST 请求
curl -X POST "http://localhost:8001/data/clean" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": "example"}'
```

### 示例 2: 转发到 ai-hub

```bash
curl -X POST "http://localhost:8001/news/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "生成新闻"}'
```

### 示例 3: 转发到 quant-engine

```bash
curl -X POST "http://localhost:8001/quant/backtest" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"strategy": "ma_cross", "start_date": "2024-01-01"}'
```

## ⚙️ 配置说明

在 `.env` 文件中配置：

```env
# 环境配置
ENV=local
LOG_LEVEL=INFO

# 服务端口
PORT=8001
HOST=0.0.0.0

# 微服务地址（Docker 环境）
AI_HUB_URL=http://ai-hub:8002
DATA_SERVICE_URL=http://data-service:8003
QUANT_ENGINE_URL=http://quant-engine:8004
DAILY_REPORT_URL=http://daily-report:8005

# 本地开发环境（可选）
# AI_HUB_URL=http://localhost:8002
# DATA_SERVICE_URL=http://localhost:8003
# QUANT_ENGINE_URL=http://localhost:8004
# DAILY_REPORT_URL=http://localhost:8005

# JWT 配置
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=30

# 限流配置
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# 代理配置
PROXY_TIMEOUT=5.0
PROXY_MAX_RETRIES=2
```

## 🐳 Docker 部署

### 构建镜像

```bash
docker build -t api-gateway:latest .
```

### 运行容器

```bash
docker run -d \
  -p 8001:8001 \
  --name api-gateway \
  --env-file .env \
  api-gateway:latest
```

## 🔍 功能特性

### 1. 统一鉴权（JWT）
- 所有接口默认启用 JWT 鉴权
- 支持白名单路径跳过鉴权
- 自动验证 token 有效性和过期时间

### 2. 日志中间件
- JSON 结构化日志
- 记录请求方法、路径、状态码、耗时
- 支持 ELK / Loki 接入

### 3. 超时控制
- 下游请求超时时间：5 秒（可配置）
- 超时自动返回 502 错误

### 4. 重试机制
- 网络错误或 5xx 时自动重试
- 最大重试次数：2 次
- 指数退避策略

### 5. 限流保护
- IP 级别限流
- 每分钟限制：60 次（可配置）
- 每小时限制：1000 次（可配置）

### 6. CORS 支持
- 允许前端 Web / 小程序跨域访问
- 生产环境建议限制具体域名

## 📊 监控与日志

### 查看日志

日志以 JSON 格式输出，包含：
- `timestamp`: 时间戳
- `method`: HTTP 方法
- `path`: 请求路径
- `client_ip`: 客户端 IP
- `status_code`: 响应状态码
- `process_time_ms`: 处理耗时（毫秒）

### 健康检查

```bash
curl http://localhost:8001/health
```

响应：
```json
{
  "status": "ok",
  "service": "api-gateway",
  "env": "local",
  "port": 8001
}
```

## ⚠️ 注意事项

1. **生产环境配置**：
   - 必须修改 `JWT_SECRET`
   - 限制 CORS 允许的域名
   - 调整限流参数

2. **服务发现**：
   - Docker 环境使用服务名（如 `ai-hub:8002`）
   - 本地开发使用 `localhost`

3. **性能优化**：
   - 限流使用内存实现，多实例部署时需使用 Redis
   - 日志量大时建议接入日志系统（ELK/Loki）

4. **错误处理**：
   - 下游服务不可用时返回 502
   - 超时时自动重试
   - 限流时返回 429
