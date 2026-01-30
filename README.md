## 量化牛牛（QuantBull）后端

面向量化投研的多服务 FastAPI 后端，目前包含网关、AI 能力中台、数据服务、量化引擎、每日投资方案服务和轻量任务服务。以下内容基于现有代码实现整理，避免与未落地的设想混淆。

### 1. 项目简介
- 已实现：多语言 FastAPI 微服务集（AI 生成、行情采集、回测骨架、每日报告编排、统一网关、轻量异步任务）。
- 技术栈：FastAPI + Pydantic v2/SQLModel + Backtrader + APScheduler + httpx；外部接口包含 Tushare、东方财富、DeepSeek/Qwen（OpenAI 兼容）。
- 定位：后端微服务，网关统一对外；AI Hub 作为 LLM 网关；data-service 负责行情采集与持久化；quant-engine 提供回测与因子/策略管理骨架；daily-report 负责编排生成投资方案。

### 2. 技术栈说明
- 后端框架：FastAPI（各服务），APScheduler（daily-report 定时任务），Backtrader（quant-engine 回测）、SQLModel/SQLAlchemy（data-service 持久化），Pydantic v2。
- 数据库：PostgreSQL（data-service 默认，quant-engine 预留）、SQLite/可切换 PostgreSQL（daily-report）。TDengine 配置存在但暂未接入实现。
- 缓存/队列：Redis 仅在配置中出现，当前代码未实际使用；task-service 为内存级简易任务队列。
- AI/第三方：DeepSeek、Qwen 通过 OpenAI 兼容接口（ai-hub/services/llm_*），Tushare（日线/基础信息），东方财富实时行情爬虫（data-service/services/eastmoney_spider.py）。数字人生成接口为占位实现。

### 3. 项目结构与职责
- api-gateway：FastAPI 网关，聚合 OpenAPI（core/openapi_aggregator.py），反向代理到下游服务（routers/proxy.py），简单 JWT 登录（用户名/密码固定 admin/admin123），健康检查。
- ai-hub：LLM 网关与 Prompt 封装（routers/ai.py）。提供新闻/摘要/策略/报告生成、通用 chat、数字人占位、模型路由。模型适配与路由配置在 services.llm_* 与 services/model_router.py。
- data-service：行情采集与清洗。实时行情（routers/quotes.py，经东方财富爬虫）、日线/ETF/stock_basic（routers/tushare.py，经 Tushare）、简单文本清洗示例（routers/data.py）。持久化到 PostgreSQL（core/database.py）。
- quant-engine：回测与因子/策略管理骨架。回测接口目前将任务提交给 task-service；Backtrader 执行逻辑在 services/backtest_service.py，但未与 API 直连。因子/策略 CRUD 为内存实现（services/factor_service.py, services/strategy_service.py）。
- daily-report：每日投资方案编排与调度（scheduler.py 每日 15:10）。通过 data-service/ai-hub 客户端拉取数据并生成报告，存储到数据库（models/daily_report.py）。缺失的 data-service 聚合接口在本地模式会返回模拟数据。
- task-service：内存任务管理（task_store.py），默认 handler 仅模拟 backtest/quick 任务（handlers.py），提供任务提交与状态查询 API。
- docker-compose.yml：提供 postgres/redis/tdengine 及各服务容器编排。

### 4. 已实现功能（基于代码）
- ✅ API 网关：健康检查、登录获取 JWT、OpenAPI 聚合、路径代理到 /news|/data|/quant|/report 下游。
- ✅ AI Hub：/api/generate/news、/summary、/strategy、/report、/digital-human、/model/route、/chat 等 LLM 生成接口（需 DeepSeek/Qwen API Key）。数字人返回占位任务。
- ✅ Data Service：
   - /api/quotes/realtime 东方财富实时行情，结果落库。
   - /api/tushare/daily、/fund_daily、/stock_basic 通过 Tushare 获取并 upsert。
   - /api/data/clean 演示文本清洗。
   - /api/lhb/* 龙虎榜数据（上榜个股、个股统计、机构买卖、机构席位追踪、活跃营业部、营业部排行、营业部上榜统计），数据来源东方财富公开数据。
   - /api/videos 视频中心：GET 匿名获取列表；POST/DELETE 仅管理员可用。
- ✅ Daily Report：
   - /api/generate 手动生成报告；/api/latest、/api/date/{date}、/api/{id} 查询；/api 列表。
   - APScheduler 每日 15:10 自动触发生成（需 data/ai 服务可用或使用本地模拟数据）。
- ✅ Task Service：/api/tasks 创建任务并查询状态，内存存储，内置 backtest/quick 演示。
- ✅ Quant Engine：回测/因子/策略 API 框架（路由与 schema），回测请求当前转发到 task-service；Backtrader 逻辑可用于后续接线。

### 5. API 使用示例
- 启动对应服务后访问 Swagger：
   - AI Hub: http://localhost:8002/docs
   - Data Service: http://localhost:8001/docs
   - Quant Engine: http://localhost:8003/docs
   - Daily Report: http://localhost:8004/docs
   - API Gateway: http://localhost:8000/docs

- 生成新闻（AI Hub）：
```bash
curl -X POST http://localhost:8002/api/generate/news \
   -H "Content-Type: application/json" \
   -d '{"news_flash":"苹果发布新品","stock_code":"AAPL","target_length":200}'
```

- 获取日线行情（Data Service）：
```bash
curl -X POST http://localhost:8001/api/tushare/daily \
   -H "Content-Type: application/json" \
   -d '{"codes":["000001"],"start_date":"20240101","end_date":"20240131"}'
```

- 触发每日投资方案生成（Daily Report）：
```bash
curl -X POST http://localhost:8004/api/generate -H "Content-Type: application/json" -d '{}'
```

- 网关代理（示例）：
```bash
curl http://localhost:8000/api/health           # 网关自身健康
curl http://localhost:8000/api/news/generate/news -d '{...}' # 通过网关转发到 ai-hub
```

### 6. 启动与运行
**本地（逐服务）**
1) Python ≥3.10，进入各服务目录安装依赖：`pip install -r requirements.txt`。
2) 配置环境变量或 `.env`：
    - ai-hub：`DEEPSEEK_API_KEY`/`QWEN_API_KEY`，可选数字人 API；`PORT` 默认为 8002。
    - data-service：`TUSHARE_TOKEN` 必填；`DATABASE_URL`/`SYNC_DATABASE_URL` 指向 PostgreSQL。
    - daily-report：`DB_TYPE`=`sqlite|postgresql` 及对应连接；默认使用 `daily_report.db`。
    - api-gateway：`JWT_SECRET`、各下游服务 URL；默认使用容器内服务名。
3) 启动示例：
```bash
uvicorn main:app --reload --port 8002   # ai-hub
uvicorn main:app --reload --port 8001   # data-service
uvicorn main:app --reload --port 8003   # quant-engine
uvicorn main:app --reload --port 8004   # daily-report
uvicorn main:app --reload --port 8000   # api-gateway
python task_service/main.py             # task-service
```

**Docker Compose**
```bash
docker-compose up -d
```
会同时拉起 postgres/redis/tdengine 与各微服务（端口 8000~8004, 9000）。若不需要 TDengine 可在 compose 中移除。

#### 前端（可选：Nginx 静态站点）
项目已在 [docker-compose.yml](docker-compose.yml) 中补充 `frontend-nginx` 服务：
- 容器对外暴露 `80`；
- `/api/` 反代到 `api-gateway:8000`；
- 静态文件从 `frontend/niuniu/dist` 挂载提供。

首次部署前请在服务器（或 CI）先构建前端产物：
```bash
cd frontend/niuniu
npm ci
npm run build
```
然后启动：
```bash
docker compose up -d --build
```
访问：`http://<服务器IP>/`（API 通过同域 `/api/` 走网关）。

### 7. Roadmap / 未实现但在代码中预留
- data-service 尚未提供 data_client 期望的 `/market/overview`、`/etf/list`、`/stock/list` 接口，daily-report 在非 local 环境会因此失败；需补齐实际数据源或统一聚合接口。
- ai-hub 数字人生成、LLM 适配器需要真实三方 API Key；Rate limit/鉴权仅为占位。
- quant-engine 回测 API 目前只把请求转发到 task-service（模拟任务）；未将 services/backtest_service.py 执行结果落库或回传。
- 因子/策略管理为内存实现，无持久化、无校验数据源；TDengine 数据加载 TODO。
- task-service 使用内存 store，缺少持久化与真正的异步执行器/消息队列。
- API 网关认证未接 user-service，登录凭证为固定示例账号。

### 8. 合规与注意事项
- 投研内容需附带风险提示，代码层面的提示与验证逻辑有限，需在产品侧加强。
- Tushare/东方财富爬虫需遵守各自使用条款和频控；生产环境请增加重试与缓存。
