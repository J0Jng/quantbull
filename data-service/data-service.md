<!--
自动生成：data-service 微服务技术说明文档
基于项目实际实现（FastAPI、SQLModel、Tushare、东方财富爬虫）
-->

# data-service 微服务技术说明文档

版本：0.1.0  
日期：2025-12-19

## **1. 服务定位与职责**

- **总体定位**：`data-service` 为量化牛牛平台的数据中台，负责采集、标准化、清洗、存储和对外提供行情/历史/基础数据与舆情数据的能力。它是平台其他服务（`api-gateway`、`ai-hub`、`quant-engine`、`daily-report`）可信赖的数据源。

- **职责边界与协作**：
  - `api-gateway`：统一入口与路由转发，`data-service` 以 HTTP API 形式对外提供数据能力；`api-gateway` 将 `/data/*` 转发到本服务。
  - `ai-hub`：调用 `data-service` 的接口获取标准化历史/实时数据作为 AI 训练或推理的输入（异步/批量数据导出或按需 HTTP 调用）。
  - `quant-engine`：在策略回测和实时交易中通过 API 拉取历史、日线或实时行情；也可直接读取共享数据库视图（权限受控）。
  - `daily-report`：消费 `data-service` 的历史、舆情或聚合数据生成报告（可通过定时导出或 API 拉取）。

- **为什么抽象为独立数据中台**：
  - 解耦：采集与业务计算分离，降低相互影响；
  - 复用：集中提供统一的数据标准与接入，避免不同服务重复实现数据清洗/转换逻辑；
  - 可扩展性：集中管理数据接入（新增数据源、增加缓存/流式能力）更易演进；
  - 运维隔离：数据密集型任务（爬虫、批量导入）不会直接影响业务网关或计算节点的稳定性。

## **2. 目录结构设计与职责**

（基于代码仓库 `data-service/`）

- `main.py`：应用入口，负责应用初始化（日志、数据库、路由、CORS）、事件（startup）中的初始化逻辑。
- `core/`：核心基础设施组件
  - `config.py`：配置管理（采用 `pydantic-settings`），从 `.env` 加载 `DATABASE_URL`、`TUSHARE_TOKEN`、`ENV` 等。
  - `database.py`：数据库连接与会话管理；提供同步 `Session`（用于 SQLModel 的建表与简单事务）和异步 `AsyncSession`（如果需要异步 DB 操作）；实现 `init_db()` 初始化表结构。
  - `logger.py`：集中化日志配置，按环境设置日志级别与格式。
- `routers/`：HTTP 路由层（FastAPI `APIRouter`）
  - 按功能分路由（`quotes.py`、`tushare.py`、`data.py`），每个路由负责参数验证、依赖注入（DB session）和输入/输出模型绑定。
- `services/`：业务服务层，封装数据采集与处理逻辑
  - `eastmoney_spider.py`：东方财富实时行情爬虫实现，负责调用外部 API、解析并映射为内部 `QuoteItem`。
  - `tushare_service.py`：Tushare 接入封装，提供日线、基础信息等批量数据获取及 upsert 逻辑。
  - `data_service.py`：通用的数据清洗/转换工具（如存在）。
- `models/`：数据库模型（使用 `SQLModel`）
  - `realtime_quote.py`：实时行情表 `realtime_quotes`（含唯一约束与索引）。
  - `daily_quote.py`：日线行情表 `daily_quotes`（含唯一约束 `code+trade_date` 与索引）。
  - `data_record.py`：通用数据记录模型（如舆情/采集原始记录）。
- `schemas/`：Pydantic/Response 请求与响应数据模型（接口契约）
  - 定义输入校验、响应模型与示例。

设计原则：分层清晰（router → service → models/database）、职责单一（爬虫/采集只做抓取与标准化，路由只做参数验证与事务控制）、易扩展（新增数据源或模型只需新增 `services` 与 `models`）。

## **3. 核心功能模块（输入 / 处理 / 输出）**

### 3.1 行情数据服务

- 实时行情数据
  - 输入：外部请求（POST `/api/quotes/realtime`，body：codes 列表）或未来可支持内部定时任务触发。
  - 处理：`EastMoneySpider.fetch_quotes()` 调用东方财富 push2 接口获取原始字段；进行字段解析、单位换算（示例：价格 API 返回以分为单位 → 除以 100；成交额返回以“万元”为单位 → 乘以 10000），构建 `QuoteItem`。
  - 输出：返回 `RealtimeQuoteResponse`（包含 `data`, `success_codes`, `failed_codes`），同时将成功记录写入 `realtime_quotes` 表（每次请求插入历史记录；表中有 `UniqueConstraint(code, update_time)` 与 `idx_update_time` 索引）。

- 历史行情数据
  - 输入：HTTP 请求（POST `/api/tushare/daily` 带 `codes, start_date, end_date`）或离线批量任务。
  - 处理：`TushareService.fetch_daily()` 调用 `tushare.pro_api`，将返回的 DataFrame 行映射为 `DailyQuoteItem`；对单日记录使用 PostgreSQL `ON CONFLICT` 完成 upsert（通过 `sqlalchemy.dialects.postgresql.insert`）。
  - 输出：返回包含日线记录的 `DailyQuoteResponse`，并将数据持久化到 `daily_quotes` 表（复合唯一索引 `uq_code_trade_date`）。

- ETF / 股票统一数据模型
  - 设计思想：使用统一的字段名（`code`, `trade_date/update_time`, `open/high/low/close`, `vol`, `amount`, `price`, `pct_change`）并在 schema 层区分来源（`source: eastmoney|tushare|fund`），以便上层消费方统一解析。

### 3.2 新闻与舆情数据（规划/实现建议）

- 财经快讯采集
  - 输入：第三方 RSS/HTTP API、网页爬虫或第三方推送。
  - 处理：解析原始 HTML/JSON，抽取 `title, content, published_at, source, tickers[]`，文本去噪与分词（可选），并生成结构化 `DataRecord`。
  - 输出：保存到 `data_records` 或专门的 `news` 表，并提供按股票或时间线检索的 API（例如 `/api/data/news?code=000001&start=...`）。

- 新闻标准化结构（建议）
  - 基本字段：`id, source, title, summary, content, published_at(UTC), tickers[], tags[], raw_payload`。
  - 关联方式：通过 `tickers[]`（標準化为 6 位代码 + 市场后缀，如 `000001.SZ`）建立与行情的关联；同时记录事件时间用于时间线聚合。

### 3.3 数据标准化与清洗

- 股票代码规范
  - 统一在系统内部使用：6 位数字（如 `000001`）并在需要外部调用时附加市场后缀（`.SZ` / `.SH`）。
  - 提供 `normalize_code()` 工具（见 `services/tushare_service.py`）：去除后缀、填充零到 6 位。

- 时间字段规范
  - 存储：数据库使用 `timestamp` / `date` 类型；所有对外 API 采用 ISO 8601（UTC）格式：`YYYY-MM-DDTHH:MM:SSZ` 或 `YYYY-MM-DD`（trade_date）。
  - 精度：实时行情保留秒级；如未来需要毫秒级，可扩展字段类型。

- 数值字段处理原则
  - 价格：统一以「元」为单位（浮点）；从上游数据源进行明确换算（例如东方财富分→元、Tushare 通常已为元）。
  - 涨跌幅：使用百分比表示（例如 `1.23` 表示 1.23%）；确保原始小数/基点换算一致。
  - 成交额：以「元」为单位，精度取两位小数；如上游使用“万元”单位需转换。
  - 缺失值：对于关键字段（price/name/update_time）若缺失则视为失败并列入 `failed_codes`，保证入库数据质量。

## **4. API 设计示例**（遵循 RESTful 风格、真实可用）

下面列出 3 个代表性接口（与当前实现一致）：

### 接口 1：获取实时行情
- 请求路径：`POST /api/quotes/realtime`
- 请求方法：`POST`
- 请求参数（JSON body）：

```json
{
  "codes": ["000001", "600000"]
}
```

- 返回结构（JSON 示例）：

```json
{
  "data": [
    {
      "code": "000001",
      "name": "平安银行",
      "price": 12.34,
      "pct_change": 1.23,
      "turnover": 123456789.0,
      "update_time": "2025-12-13T15:00:00"
    }
  ],
  "success_codes": ["000001"],
  "failed_codes": []
}
```

说明：本接口同步触发抓取并返回结果；成功项会写入 `realtime_quotes` 表以保留历史。

### 接口 2：获取日线（Tushare）并入库
- 请求路径：`POST /api/tushare/daily`
- 请求方法：`POST`
- 请求参数（JSON body）：

```json
{
  "codes": ["000001", "600000"],
  "start_date": "20250101",
  "end_date": "20251231"
}
```

- 返回结构（JSON 示例）：

```json
{
  "data": [
    {
      "code": "000001",
      "trade_date": "20251213",
      "open": 12.10,
      "high": 12.50,
      "low": 12.00,
      "close": 12.34,
      "vol": 12345678,
      "amount": 123456789.0
    }
  ],
  "success_codes": ["000001"],
  "failed_codes": []
}
```

说明：服务使用 `tushare.pro_api` 获取数据，使用 PostgreSQL 的 `ON CONFLICT` 做 upsert 保持数据幂等性。

### 接口 3：获取股票基础信息
- 请求路径：`GET /api/tushare/stock_basic?exchange=`
- 请求方法：`GET`
- 请求参数：`exchange`（可选，空 表示全部）
- 返回结构（JSON 示例）：

```json
{
  "data": [
    {
      "ts_code": "000001.SZ",
      "symbol": "000001",
      "name": "平安银行",
      "area": "深圳",
      "industry": "银行",
      "list_date": "19910403"
    }
  ]
}
```

说明：此接口为只读查询，返回已标准化的基础信息，适合策略引擎/前端展示使用。

## **5. 数据流转说明（重点）**

1. 数据源
   - 实时行情：东方财富 `push2` 接口（`EastMoneySpider`）
   - 历史/基础：Tushare（`TushareService`）
   - 舆情/新闻：第三方 RSS/API 或自建爬虫（规划）

2. 典型链路：数据源 → data-service → 数据库存储 → 前端 / AI 服务
   - 客户端/上游服务通过 `api-gateway` 发起请求到 `data-service`。
   - `data-service` 调用对应 `services`（e.g., `eastmoney_spider` / `tushare_service`）获取并标准化数据。
   - 成功的数据写入 PostgreSQL（实时行情按时间写入历史记录，日线使用 upsert 保持最新）。
   - 消费者（`api-gateway` 转发、`ai-hub`、`quant-engine`、`daily-report`）通过 HTTP 调用或数据库直接读取（需授权）获取数据。

3. 同步 / 异步 / 定时区分
   - 实时同步：`POST /api/quotes/realtime` 为同步请求，调用方等待返回后获得当次抓取结果；同时写入 DB（同步事务）。
   - 异步写入：对于大批量历史回填，可走后台任务队列（推荐使用 Celery / RQ / APScheduler），避免阻塞 HTTP 请求。当前实现通过 API 调用触发批量写入（同步循环 + upsert）。
   - 定时任务触发：生产环境建议由外部调度（Kubernetes CronJob、systemd timer 或 APScheduler）定期触发日线或舆情抓取任务。

## **6. 异常处理与日志体系**

- 网络异常策略
  - 外部请求设置超时（例如 `requests.get(..., timeout=10)`），捕获 `requests.exceptions` 并重试（建议：幂等短重试策略，3 次以内，指数回退）。
  - 对于短暂网络错误，返回 `failed_codes` 并记录警告日志，避免单点失败影响整个批次。

- 数据源不可用或返回异常
  - 记录完整错误信息（包含请求参数与返回体片段）并返回调用方可识别的失败列表。
  - 在 `startup` 阶段初始化第三方 API（例如 Tushare）失败，应用记录 warning 并继续启动（以保证 API 可访问），但应在监控/告警上报中标注异常。

- 数据库异常
  - 采用事务性写入：捕获异常后 `rollback()` 并记录 ERROR 日志；返回结果不因单次写库失败而中断已获取的数据返回给调用方。
  - 常见错误处理：连接失败（提示检查 `DATABASE_URL`、数据库是否运行），约束冲突（通过 upsert 解决业务冲突）。

- 日志分级设计
  - `INFO`：业务正常行为（请求开始/结束、成功抓取 N 条、upsert 成功）。
  - `WARNING`：外部 API 返回异常、部分代码失败、初始化第三方服务失败（不阻止启动）。
  - `ERROR`：写库失败、解析失败导致关键字段缺失、不可恢复的异常。

日志实现：使用 `core.logger.configure_logging()` 统一配置，输出到 stdout（容器友好），并可在生产中配置结构化输出（JSON）和集中化收集（ELK/Prometheus + Grafana）

## **7. 当前完成度（用于验收）**

- 已完成的核心功能（代码实现依据 `IMPLEMENTATION.md` 与仓库）：
  - FastAPI 异步服务框架与路由注册（`main.py`, `routers/`）。
  - 东方财富实时行情爬虫实现（`services/eastmoney_spider.py`），支持批量查询并解析关键字段。
  - 日线数据通过 Tushare 获取并保存（`services/tushare_service.py`、`routers/tushare.py`）。
  - PostgreSQL + SQLModel 模型实现（`models/realtime_quote.py`, `models/daily_quote.py`），并在 `core/database.py` 中提供表初始化逻辑。
  - API 文档与示例（`QUOTES_API.md`, `TUSHARE_API.md`）和项目 `README` 中的快速启动说明。

- 已验证通过的技术点：
  - PostgreSQL 连接与表创建（`init_db()` 在 startup 中执行，可在容器环境下自动创建表）。
  - 基础行情接口与数据库写入链路：POST `/api/quotes/realtime` 流程已跑通（抓取 → 解析 → 写库 → 返回）。
  - Tushare 日线批量获取与 upsert 流程已验证。

- 当前完整跑通的业务链路：
  - 客户端 → `api-gateway` → `data-service` → 东方财富/Tushare → PostgreSQL → 客户端/前端。

## **8. 调试与运行说明**

以下命令基于项目根目录 `data-service/`：

### 环境准备

复制 `.env` 示例并设置数据库与 Tushare Token：

```bash
cp .env.example .env
# 编辑 .env，设置 DATABASE_URL 与 TUSHARE_TOKEN
```

示例 `.env`（开发）：

```env（要修改）
DATABASE_URL=postgresql+psycopg2://postgres:password@postgres-quantbull:5432/quant
TUSHARE_TOKEN=your_tushare_token
ENV=local
LOG_LEVEL=INFO
```

### 本地启动服务（开发）

```bash
# 安装依赖
pip install -r requirements.txt

# 启动（自动重载）
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 接口测试示例

curl（实时行情）：

```bash
curl -X POST http://localhost:8000/api/quotes/realtime \
  -H "Content-Type: application/json" \
  -d '{"codes":["000001","600000"]}'
```

curl（日线）：

```bash
curl -X POST http://localhost:8000/api/tushare/daily \
  -H "Content-Type: application/json" \
  -d '{"codes":["000001"], "start_date":"20250101", "end_date":"20251231"}'
```

### 数据库连接与检查

在容器 / 本地使用 `psql` 或 GUI 工具连接 PostgreSQL：

```bash
psql -U postgres -h localhost -d quant

-- 查看表结构
\d realtime_quotes
\d daily_quotes
```

### Docker / Docker Compose

项目内提供 `Dockerfile` 与 `docker-compose.yml`（示例）：

```bash
# 构建并启动（包含 Postgres）
docker-compose up -d --build

# 查看日志
docker-compose logs -f app
```

容器环境下请确保 `DATABASE_URL` 环境变量指向 `postgres-quantbull` 服务（`docker-compose.yml` 中示例已配置）。

###
1. 启动服务后，在浏览器访问：
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

2. 在 Swagger UI 中可以直接测试 API：
   - 点击 `/health` → Try it out → Execute
   - 点击 `/api/data/clean` → Try it out → 输入 JSON → Execute

## **9. 运维与扩展建议（简要）**

- 将爬虫/批量任务移出同步 HTTP 路径，接入任务队列（Celery/RQ + Redis）以提高并发与稳定性。
- 为高频实时行情场景引入缓存层（Redis），减少外部抓取频率并提高响应速度。
- 增加指标采集（Prometheus）与结构化日志（ELK/Fluentd），为 SLA / 性能优化提供数据。
- 为舆情/新闻引入去重与文本索引（Elasticsearch）以支持复杂检索与语义分析。

## **附录：关键实现摘录 / 注意点**

- 东方财富字段处理：`f43`（价格，分）→ 除以 100；`f170`（涨跌幅，分）→ 除以 100；`f47`（成交额，单位 万元）→ *10000。
- Tushare 使用：`tushare.pro_api(TUSHARE_TOKEN)`，结果以 DataFrame 返回，需逐行映射并 `ON CONFLICT` upsert。
- 数据库表约束：
  - `realtime_quotes`：`UNIQUE(code, update_time)`，`INDEX(update_time)`。
  - `daily_quotes`：`UNIQUE(code, trade_date)`，`INDEX(trade_date)`。

---
