# API 测试指南

## 前提条件
确保服务已启动：
```powershell
# 方式1: 本地运行
cd data-service
uvicorn main:app --reload

# 方式2: Docker 运行
docker run -p 8000:8000 data-service
```

## 测试方法

### 方法 1: 使用 PowerShell 脚本（推荐）
```powershell
cd data-service
.\test-api.ps1
```

### 方法 2: 使用 PowerShell 命令

#### 测试 GET /health
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET | Select-Object -ExpandProperty Content
```

#### 测试 POST /api/data/clean
```powershell
$body = @{
    source = "ec"
    content = "Sample text"
    tags = @("NEWS", "STOCK")
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/data/clean" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

### 方法 3: 使用 curl（如果已安装）
```bash
# GET /health
curl http://localhost:8000/health

# POST /api/data/clean
curl -X POST http://localhost:8000/api/data/clean \
  -H "Content-Type: application/json" \
  -d '{"source":"ec","content":"Sample text","tags":["NEWS","STOCK"]}'
```

### 方法 4: 使用 FastAPI 自动文档（最简单）

1. 启动服务后，在浏览器访问：
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

2. 在 Swagger UI 中可以直接测试 API：
   - 点击 `/health` → Try it out → Execute
   - 点击 `/api/data/clean` → Try it out → 输入 JSON → Execute

## 预期响应

### GET /health
```json
{
  "status": "ok",
  "service": "data-service",
  "env": "local"
}
```

### POST /api/data/clean
```json
{
  "source": "ec",
  "content": "Sample text",
  "tags": ["news", "stock"],
  "summary": "ec payload accepted with 2 words and 2 tags."
}
```

