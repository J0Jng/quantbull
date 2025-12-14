# API Gateway 架构文档

## 📋 项目结构

```
api-gateway/
├── main.py                    # FastAPI 应用入口（端口 8001）
├── run.py                     # 启动脚本
├── requirements.txt           # 依赖包
├── Dockerfile                 # Docker 镜像
├── pytest.ini                 # 测试配置
├── .env.example               # 环境变量示例
├── .gitignore                 # Git 忽略文件
│
├── core/                      # 核心模块
│   ├── __init__.py
│   ├── config.py             # 配置管理（Pydantic Settings）
│   └── logger.py             # 日志配置
│
├── middlewares/               # 中间件
│   ├── __init__.py
│   ├── auth.py               # JWT 鉴权中间件
│   ├── logging.py            # 结构化日志中间件
│   └── rate_limit.py         # IP 级别限流中间件
│
├── routers/                   # 路由模块
│   ├── __init__.py
│   └── proxy.py              # 统一代理转发路由
│
├── services/                  # 服务层
│   ├── __init__.py
│   ├── auth_service.py       # JWT 认证服务
│   └── proxy_service.py      # 服务健康检查（旧版，保留兼容）
│
├── models/                    # 数据模型
│   ├── __init__.py
│   └── user.py
│
├── schemas/                   # Pydantic 模式
│   ├── __init__.py
│   ├── auth.py
│   └── gateway.py
│
└── tests/                     # 测试用例
    ├── __init__.py
    ├── conftest.py
    ├── test_auth.py
    ├── test_gateway.py
    └── test_services.py
```

## 🏗️ 架构设计

### 1. 请求流程

```
客户端请求
    ↓
CORS 中间件（跨域处理）
    ↓
限流中间件（IP 级别限流）
    ↓
日志中间件（记录请求/响应）
    ↓
鉴权中间件（JWT 验证）
    ↓
代理路由（routers/proxy.py）
    ↓
转发到下游微服务（httpx.AsyncClient）
    ↓
返回响应
```

### 2. 路由转发规则

| 路径前缀 | 目标服务 | 端口 | 说明 |
|---------|---------|------|------|
| `/news/*` | `ai-hub` | 8002 | AI 能力中台 |
| `/data/*` | `data-service` | 8003 | 数据采集服务 |
| `/quant/*` | `quant-engine` | 8004 | 量化引擎 |
| `/report/*` | `daily-report` | 8005 | 每日报告服务 |

### 3. 中间件执行顺序

中间件的执行顺序很重要，按照以下顺序注册：

1. **CORS 中间件**（最外层）
   - 处理跨域请求
   - 允许所有来源（生产环境应限制）

2. **限流中间件**
   - IP 级别限流
   - 内存实现（单实例）
   - 每分钟/每小时限制

3. **日志中间件**
   - JSON 结构化日志
   - 记录请求/响应信息
   - 计算处理耗时

4. **鉴权中间件**（最内层）
   - JWT Token 验证
   - 白名单路径跳过
   - 将用户信息注入 request.state

### 4. 代理转发机制

#### 路径匹配逻辑

```python
# 示例：/news/generate
1. 移除开头的斜杠 → "news/generate"
2. 匹配路由前缀 "news" → 找到 ai_hub_url
3. 移除前缀 → "generate"
4. 构建目标 URL → "http://ai-hub:8002/generate"
```

#### 重试机制

- **触发条件**：网络错误或 5xx 状态码
- **最大重试次数**：2 次（可配置）
- **退避策略**：指数退避（0.5s, 1s, 1.5s）
- **超时时间**：5 秒（可配置）

#### 请求转发

- 保留原始 HTTP 方法
- 保留查询参数
- 保留请求头（移除 host, connection）
- 保留请求体（POST/PUT/PATCH/DELETE）

## 🔐 安全机制

### 1. JWT 鉴权

- **算法**：HS256
- **密钥**：可配置（生产环境必须修改）
- **过期时间**：30 分钟（可配置）
- **验证内容**：
  - Token 存在性
  - Token 签名
  - Token 过期时间

### 2. 白名单机制

以下路径不需要鉴权：
- `/health` - 健康检查
- `/docs` - Swagger 文档
- `/openapi.json` - OpenAPI 规范
- `/redoc` - ReDoc 文档
- `/` - 根路径

### 3. 限流保护

- **级别**：IP 地址
- **策略**：
  - 每分钟：60 次请求
  - 每小时：1000 次请求
- **实现**：内存存储（单实例）
- **响应**：429 Too Many Requests

## 📊 日志系统

### 日志格式（JSON）

```json
{
  "timestamp": "2024-12-14 20:46:00",
  "method": "GET",
  "path": "/news/list",
  "query_params": "limit=10",
  "client_ip": "192.168.1.100",
  "status_code": 200,
  "process_time_ms": 45.23,
  "request_body": null,
  "response_body": "{...}"
}
```

### 日志级别

- **INFO**：正常请求（2xx）
- **WARNING**：客户端错误（4xx）
- **ERROR**：服务器错误（5xx）

## ⚙️ 配置管理

### 环境变量

所有配置通过 `.env` 文件或环境变量设置：

```env
# 基础配置
ENV=local
LOG_LEVEL=INFO
PORT=8001
HOST=0.0.0.0

# 微服务地址
AI_HUB_URL=http://ai-hub:8002
DATA_SERVICE_URL=http://data-service:8003
QUANT_ENGINE_URL=http://quant-engine:8004
DAILY_REPORT_URL=http://daily-report:8005

# JWT 配置
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=30

# 限流配置
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# 代理配置
PROXY_TIMEOUT=5.0
PROXY_MAX_RETRIES=2
```

### 配置类

使用 Pydantic Settings 进行配置管理：
- 类型验证
- 默认值
- 环境变量自动加载
- 缓存机制（@lru_cache）

## 🚀 部署方案

### Docker 部署

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8001
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Kubernetes 部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: api-gateway
        image: api-gateway:latest
        ports:
        - containerPort: 8001
        env:
        - name: PORT
          value: "8001"
```

## 🔧 扩展建议

### 1. 分布式限流

当前限流使用内存实现，多实例部署时建议：
- 使用 Redis 实现分布式限流
- 使用 `slowapi` 或 `ratelimit` 库

### 2. 服务发现

当前使用硬编码服务地址，建议：
- 集成 Consul / Eureka
- 使用 Kubernetes Service Discovery
- 实现健康检查和自动故障转移

### 3. 监控与追踪

建议集成：
- Prometheus 指标收集
- OpenTelemetry 分布式追踪
- ELK / Loki 日志聚合

### 4. 缓存机制

对于频繁访问的接口，建议：
- 使用 Redis 缓存响应
- 实现缓存失效策略
- 支持缓存预热

## 📝 开发规范

### 代码风格

- 使用类型注解
- 遵循 PEP 8
- 使用 Pydantic v2 进行数据验证
- 异步优先（async/await）

### 测试要求

- 单元测试覆盖率 > 80%
- 集成测试覆盖主要流程
- 使用 pytest 框架

### 文档要求

- API 文档（Swagger/OpenAPI）
- 架构文档（本文档）
- 使用指南（USAGE.md）
- README.md
