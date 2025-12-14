# API Gateway 服务

量化牛牛统一 API 网关服务，负责路由所有微服务请求、处理鉴权、日志与限流。

## 📁 目录结构

```
api-gateway/
├── main.py                 # FastAPI 入口
├── requirements.txt        # 依赖包
├── Dockerfile             # Docker 镜像
├── .env.example           # 环境变量示例
├── .gitignore            # Git 忽略文件
├── core/                  # 核心模块
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   └── logger.py         # 日志配置
├── routers/              # 路由模块
│   ├── __init__.py
│   ├── auth.py          # 认证路由
│   ├── gateway.py       # 网关路由
│   └── proxy.py         # 代理路由
├── services/            # 服务层
│   ├── __init__.py
│   ├── auth_service.py  # 认证服务
│   └── proxy_service.py # 代理服务
├── models/              # 数据模型
│   ├── __init__.py
│   └── user.py         # 用户模型
└── schemas/            # Pydantic 模式
    ├── __init__.py
    ├── auth.py         # 认证模式
    └── gateway.py      # 网关模式
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 3. 运行服务

```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 或使用 Python
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. 访问文档

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 📡 API 端点

### 认证相关

- `POST /api/auth/login` - 用户登录（OAuth2 格式）
- `POST /api/auth/login/json` - 用户登录（JSON 格式）
- `GET /api/auth/me` - 获取当前用户信息

### 网关相关

- `GET /health` - 网关健康检查
- `GET /api/gateway/health` - 网关健康检查（详细）
- `GET /api/gateway/services/health` - 检查所有微服务健康状态

### 代理相关

- `GET/POST/PUT/DELETE /api/proxy/{service_name}/{path}` - 代理请求到指定微服务
- `POST /api/proxy/data/clean` - 代理数据清洗请求（示例）

## 🔐 认证说明

### 登录获取 Token

```bash
curl -X POST "http://localhost:8000/api/auth/login/json" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

响应：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 使用 Token 访问受保护接口

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🔄 代理请求示例

### 代理到 data-service

```bash
curl -X GET "http://localhost:8000/api/proxy/data-service/api/clean" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 代理到其他服务

```bash
# ai-hub
curl -X POST "http://localhost:8000/api/proxy/ai-hub/api/generate" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "生成新闻"}'

# quant-engine
curl -X GET "http://localhost:8000/api/proxy/quant-engine/api/strategies" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🐳 Docker 部署

### 构建镜像

```bash
docker build -t api-gateway:latest .
```

### 运行容器

```bash
docker run -d \
  -p 8000:8000 \
  --name api-gateway \
  --env-file .env \
  api-gateway:latest
```

## ⚙️ 配置说明

主要配置项（在 `.env` 文件中设置）：

- `ENV`: 环境（local/prod）
- `LOG_LEVEL`: 日志级别（DEBUG/INFO/WARNING/ERROR）
- `JWT_SECRET`: JWT 密钥（生产环境必须修改）
- `DATA_SERVICE_URL`: data-service 地址
- `AI_HUB_URL`: ai-hub 地址
- `QUANT_ENGINE_URL`: quant-engine 地址
- `DAILY_REPORT_URL`: daily-report 地址
- `USER_SERVICE_URL`: user-service 地址

## 📝 技术栈

- **FastAPI**: 现代、快速的 Web 框架
- **Pydantic v2**: 数据验证和设置管理
- **python-jose**: JWT 令牌处理
- **httpx**: 异步 HTTP 客户端（用于代理请求）
- **Uvicorn**: ASGI 服务器

## 🔧 开发说明

1. **认证服务**: `AuthService` 目前使用示例实现，实际应连接 `user-service` 进行用户验证
2. **代理服务**: `ProxyService` 负责将请求转发到各个微服务
3. **限流**: 配置中已预留限流参数，可集成 `slowapi` 等限流库
4. **日志**: 使用标准 Python logging，可集成 ELK 等日志系统

## 📌 注意事项

- 生产环境必须修改 `JWT_SECRET`
- CORS 配置应根据实际前端域名调整
- 建议添加限流中间件防止 API 滥用
- 代理请求超时时间可根据实际需求调整
