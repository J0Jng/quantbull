# 🚀 量化牛牛（QuantBull）

### —— AI 驱动的全链路量化投资智能体平台

本项目旨在构建一个集 **数据采集、AI 内容生成、量化策略、数字人视频、投资方案生成、前后端交互** 于一体的全自动金融智能平台。

## 📁 项目结构

```
量化第一次尝试/
├── gateway/              # API网关服务
├── data-service/         # 数据中台服务
├── ai-service/           # AI中台服务
├── quant-engine/         # 量化引擎服务
├── content-service/      # 内容服务
├── frontend-web/         # Web前端
├── miniapp/              # 微信小程序
├── docs/                 # 项目文档
├── ai-prompts/           # AI提示词模板库
├── ai-generated-code/    # AI生成的代码仓库
├── docker-compose.yml    # Docker编排配置
└── README.md            # 项目说明

```

## 🏗️ 微服务架构

```
┌──────────────────────────────────────────────┐
│                 前端层（用户端）              │
│  Web(H5) | 微信小程序 | 微信公众号内容中心      │
└──────────────────────────────────────────────┘
                         │
┌──────────────────────────────────────────────┐
│                 API 网关（鉴权、路由）         │
└──────────────────────────────────────────────┘
                         │
┌──────────────────────────────────────────────┐
│                 后端微服务层                  │
│  数据服务 | AI服务 | 量化引擎 | 内容服务        │
└──────────────────────────────────────────────┘
                         │
┌──────────────────────────────────────────────┐
│                    AI 能力层                 │
│ LLM网关(DeepSeek/Qwen) | 数字人 | 内部FinGPT 模型 │
└──────────────────────────────────────────────┘
                         │
┌──────────────────────────────────────────────┐
│            数据与基础设施层                   │
│ PostgreSQL | TDengine | Redis | OSS | MQ       │
└──────────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 启动服务

```bash
# 启动所有微服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f gateway
```

### 开发环境

```bash
# 后端服务开发
cd gateway
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端开发
cd frontend-web
npm install
npm run dev
```

## 📖 文档

- [架构总览](./docs/architecture/overview.md)
- [API文档](./docs/api/)
- [开发指南](./docs/development/)

## 🛠️ 技术栈

### 后端
- Python / FastAPI
- Celery
- Scrapy / Playwright
- Backtrader / Qlib

### AI
- DeepSeek API
- Qwen API
- QLoRA 微调模型
- 数字人 API

### 数据库
- PostgreSQL（结构化数据）
- TDengine（行情时间序列）
- Redis（缓存与消息队列）
- Milvus（向量数据库）

### 前端
- Vue3 + Element Plus（Web）
- Uni-app（小程序）

## 📝 开发规范

请参考 [编码规范](./docs/development/coding-standards.md)

## 📄 许可证

MIT License

