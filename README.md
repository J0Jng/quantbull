# QuantBull

QuantBull 是一个面向 A 股市场的开源量化研究与行情分析平台。项目采用前后端分离和微服务架构，整合行情与市场数据、指标分析、量化策略回测、AI 辅助分析及每日市场报告等能力。

> **声明：** QuantBull 仅用于技术研究、学习和信息展示，不构成投资建议、证券交易建议或收益承诺。市场数据可能存在延迟、缺失或误差，请在使用前自行核实，并自行承担投资决策风险。

## 功能概览

- **市场数据：** 股票行情、市场概况、资金流向、龙虎榜、基金与 ETF、财务数据、业绩预告及财经资讯等数据接口。
- **量化研究：** 指标与策略相关服务，支持策略工作流和量化引擎。
- **AI 辅助分析：** 通过 AI Hub 接入兼容 OpenAI 风格 API 的模型服务，提供新闻、摘要和策略相关生成能力。
- **账户与任务：** 用户认证、管理接口、后台任务和每日市场报告服务。
- **Web 应用：** Vue/Vite 前端位于 `frontend/niuniu`，通过 API Gateway 访问后端服务。
- **容器化部署：** Docker Compose 编排网关、业务服务及 PostgreSQL、Redis、TDengine 等依赖。

具体接口可在服务启动后访问 API Gateway 的 `/docs` 和 `/openapi.json`。

## 项目结构

```text
.
├── ai-hub/             # AI 模型接入与生成服务
├── api-gateway/        # API 网关与统一入口
├── daily-report/       # 每日市场报告
├── data-service/       # 行情与金融数据服务
├── frontend/niuniu/    # Web 前端
├── indicator/          # 指标相关模块
├── quant-engine/       # 量化引擎
├── task_service/       # 后台任务服务
├── user-service/       # 用户与认证服务
├── docker/             # 数据库初始化等部署文件
├── docs/               # 部署和运维文档
├── docker-compose.yml  # 多服务部署编排
└── .env.example        # 环境变量模板
```

## 快速开始

### 前置条件

- Docker Engine 和 Docker Compose v2
- Git

如需单独开发前端，还需要 Node.js 与 npm。后端容器使用 Dockerfile 中指定的 Python 运行环境。

### 1. 获取代码并配置环境

```bash
git clone https://github.com/J0Jng/quantbull.git
cd quantbull
cp .env.example .env
```

编辑 `.env`，至少设置数据库密码、每日报告数据库角色密码、JWT 密钥、管理员密码和 CORS 来源。生产环境请使用强随机密钥和密码；不要将 `.env` 或真实 API 密钥提交到 Git。

使用 AI 功能时，按需配置 `DEEPSEEK_API_KEY`、`QWEN_API_KEY` 或 `OPENAI_API_KEY`。使用 Tushare 数据时配置 `TUSHARE_TOKEN`。具体变量说明见 [.env.example](.env.example) 及各服务配置。

### 2. 启动后端服务

```bash
docker compose up -d --build
```

查看服务状态和日志：

```bash
docker compose ps
docker compose logs -f api-gateway
```

API Gateway 默认映射到本机 `8000` 端口。启动后可访问：

- API 文档：<http://localhost:8000/docs>
- OpenAPI 描述：<http://localhost:8000/openapi.json>

### 3. 开发或构建前端

```bash
cd frontend/niuniu
npm ci
npm run dev
```

生产构建：

```bash
npm run build
```

前端部署和 Nginx 反向代理示例见 [docs/deploy-frontend-nginx.md](docs/deploy-frontend-nginx.md)。

## 配置与部署说明

- Compose 使用具名卷保存 PostgreSQL、Redis 和 TDengine 等数据。停止容器可运行 `docker compose down`；该命令默认保留具名卷。
- 修改 `.env` 后，如需让配置变更生效，请按需重建相关服务：`docker compose up -d --build`。
- 线上部署请配置 HTTPS、正确的 CORS 来源及安全 Cookie 参数，并限制管理接口和数据库的网络访问。
- 数据服务可能依赖第三方数据源及其服务条款、访问限制和 API 凭据；请遵守相应规则。
- 更多部署资料见 [`docs/`](docs/)。

## 参与贡献

欢迎提交 Issue 和 Pull Request。提交前请说明变更目的、影响范围和复现步骤；涉及配置时请使用示例值，不要包含密码、令牌或个人数据。

## 许可证

本项目以 [MIT License](LICENSE) 开源。使用、修改和分发时请保留版权声明及许可声明。第三方依赖、数据源和外部服务各自遵循其适用的条款。

## 致谢

感谢所有开源依赖、数据服务及为项目提供建议和反馈的贡献者。
