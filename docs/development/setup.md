# 开发环境搭建

## 环境要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+（或使用Docker）
- Redis 7+（或使用Docker）

## 本地开发设置

### 1. 克隆项目

```bash
git clone <repository-url>
cd 量化第一次尝试
```

### 2. 后端服务设置

#### Gateway服务

```bash
cd gateway
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件，填入配置
uvicorn app.main:app --reload --port 8000
```

#### Data Service

```bash
cd data-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件，填入配置
uvicorn app.main:app --reload --port 8001
```

#### AI Service

```bash
cd ai-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 文件，填入API密钥
uvicorn app.main:app --reload --port 8002
```

#### Quant Engine

```bash
cd quant-engine
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8003
```

#### Content Service

```bash
cd content-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8004
```

### 3. 前端项目设置

#### Web前端

```bash
cd frontend-web
npm install
cp .env.example .env.development
npm run dev
```

#### 小程序

```bash
cd miniapp
npm install
cp .env.example .env
npm run dev:mp-weixin
```

### 4. Docker方式启动

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f gateway
```

## 数据库初始化

```bash
# 使用Docker启动数据库
docker-compose up -d postgres redis

# 或手动启动PostgreSQL，然后运行迁移脚本
# （迁移脚本待实现）
```

## 常见问题

### 端口占用

如果端口被占用，可以修改各服务的端口配置：
- Gateway: 8000
- Data Service: 8001
- AI Service: 8002
- Quant Engine: 8003
- Content Service: 8004

### Python依赖安装失败

某些依赖（如TA-Lib）可能需要系统库支持，建议使用Docker环境。

