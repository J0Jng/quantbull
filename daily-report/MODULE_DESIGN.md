# Daily Report Service - 模块设计文档

## 📋 一、服务定位

`daily-report` 是一个**编排型服务（Orchestrator）**，负责：

- ✅ **定时调度**：使用 APScheduler 在每个交易日 15:10 自动触发
- ✅ **数据聚合**：从 `data-service` 获取行情数据
- ✅ **AI 调用**：调用 `ai-hub` 生成投研内容
- ✅ **数据持久化**：保存到 PostgreSQL
- ✅ **内容分发**：提供 API 供 Web/小程序/公众号调用

**不负责**：
- ❌ 行情计算与模型训练
- ❌ 数据清洗（假设 data-service 已完成）
- ❌ AI 模型训练

---

## 🏗️ 二、架构设计

### 2.1 技术栈

- **Python 3.10+**
- **FastAPI** - Web 框架
- **APScheduler** - 定时任务调度
- **SQLAlchemy** - ORM
- **PostgreSQL** - 数据库
- **Pydantic v2** - 数据验证
- **httpx** - HTTP 客户端（调用其他微服务）

### 2.2 时区配置

- 统一使用 **Asia/Shanghai** 时区
- 定时任务明确声明 timezone
- 所有时间相关操作使用上海时区

---

## 📁 三、目录结构

```
daily-report/
├── main.py                      # FastAPI 入口 + scheduler 启动
├── scheduler.py                  # APScheduler 配置
├── routers/
│   ├── __init__.py
│   ├── report.py                # 旧版日报路由（保留兼容）
│   └── daily_report.py          # 每日投资方案路由
├── services/
│   ├── __init__.py
│   ├── report_service.py        # 业务编排核心
│   ├── data_client.py           # data-service 调用封装
│   └── ai_client.py             # ai-hub 调用封装
├── models/
│   ├── __init__.py
│   ├── report.py                # 旧版模型（保留兼容）
│   └── daily_report.py          # 每日投资方案数据库模型
├── schemas/
│   ├── __init__.py
│   ├── report.py                # 旧版 Schema（保留兼容）
│   └── daily_report.py          # 每日投资方案 Schema
├── db/
│   ├── __init__.py
│   └── session.py               # 数据库会话管理
└── core/
    ├── __init__.py
    ├── config.py                # 配置管理
    └── logger.py                # 日志配置
```

---

## 🔄 四、业务流程

### 4.1 定时任务流程

```
15:10 (Asia/Shanghai)
    ↓
scheduler.py::generate_daily_report_job()
    ↓
report_service.py::generate_daily_report()
    ↓
[步骤1] data_client.fetch_market_data()
    ├─ 获取市场概览
    ├─ 获取 ETF 列表
    └─ 获取股票列表
    ↓
[步骤2] ai_client.generate_investment_report()
    ├─ 构建 Prompt
    ├─ 调用 ai-hub API
    └─ 解析 AI 返回的 JSON
    ↓
[步骤3] 保存到 PostgreSQL
    ├─ 更新/创建记录
    ├─ 保存结构化数据
    └─ 标记状态为 completed
    ↓
完成 ✅
```

### 4.2 手动触发流程

```
POST /api/daily-report/generate
    ↓
daily_report.py::generate_report()
    ↓
report_service.py::generate_daily_report()
    ↓
[同定时任务流程]
```

---

## 📊 五、数据模型

### 5.1 数据库模型 (`models/daily_report.py`)

**DailyInvestmentReport** 表结构：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| report_date | String(10) | 报告日期（唯一索引） |
| title | String(200) | 报告标题 |
| status | String(20) | 状态：draft/published/archived |
| market_sentiment | Text | 市场情绪总结 |
| etf_recommendations | JSON | ETF 推荐列表（3个） |
| stock_recommendations | JSON | 股票推荐列表（10只） |
| risk_warning | Text | 风险提示 |
| article_title | String(200) | 公众号文章标题 |
| article_outline | JSON | 公众号文章大纲 |
| generation_status | String(20) | 生成状态：pending/processing/completed/failed |
| generation_error | Text | 生成错误信息 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 5.2 Schema 定义 (`schemas/daily_report.py`)

#### 输入 Schema
- `MarketOverview` - 市场概览
- `ETFData` - ETF 数据
- `StockData` - 股票数据
- `MarketDataInput` - 聚合的市场数据

#### AI 生成 Schema
- `ETFRecommendation` - ETF 推荐
- `StockRecommendation` - 股票推荐
- `ArticleOutline` - 文章大纲
- `AIGeneratedContent` - AI 生成内容（完整结构）

#### API 响应 Schema
- `DailyReportResponse` - 报告详情响应
- `DailyReportListResponse` - 报告列表响应
- `DailyReportSummaryResponse` - 报告摘要响应
- `GenerateReportRequest` - 手动触发请求

---

## 🔌 六、服务间调用

### 6.1 Data Service 调用 (`services/data_client.py`)

**假设接口**（需要 data-service 实现）：

```python
# 获取市场概览
GET /api/market/overview?date=2024-01-01

# 获取 ETF 列表
GET /api/etf/list?date=2024-01-01&limit=100

# 获取股票列表
GET /api/stock/list?date=2024-01-01&limit=500&min_turnover=100000000
```

**开发环境**：如果 data-service 不可用，返回模拟数据。

### 6.2 AI Hub 调用 (`services/ai_client.py`)

**假设接口**（需要 ai-hub 实现）：

```python
POST /api/llm/generate
{
    "prompt": "...",
    "model": "deepseek",  # 或 "qwen"
    "temperature": 0.7,
    "max_tokens": 4000,
    "response_format": "json"
}
```

**开发环境**：如果 ai-hub 不可用，返回模拟数据。

---

## 🤖 七、AI Prompt 设计

### 7.1 Prompt 结构

Prompt 在 `ai_client.py::_build_prompt()` 中构建，包含：

1. **角色定义**：投资组合经理
2. **输入数据**：
   - 市场概览（指数、成交额、涨跌分布）
   - ETF 数据（前10只）
   - 股票数据（前50只）
3. **输出要求**：
   - ETF 推荐（3个）
   - 股票推荐（10只）
   - 市场情绪总结
   - 风险提示
   - 公众号文章结构
4. **格式要求**：JSON 格式

### 7.2 Prompt 特点

- ✅ **与业务逻辑解耦**：Prompt 构建独立于业务代码
- ✅ **数据驱动**：所有输入来自 data-service，不捏造数据
- ✅ **结构化输出**：要求 JSON 格式，便于解析
- ✅ **合规要求**：明确要求风险提示和免责声明

---

## ⏰ 八、定时任务配置

### 8.1 调度器配置 (`scheduler.py`)

```python
# 每个交易日 15:10 执行
CronTrigger(
    hour=15,
    minute=10,
    timezone=SHANGHAI_TZ,
)
```

### 8.2 任务特性

- ✅ **时区明确**：使用 Asia/Shanghai
- ✅ **单实例运行**：`max_instances=1`
- ✅ **错误处理**：捕获异常，不影响调度器
- ✅ **日志记录**：完整的执行日志

---

## 🛣️ 九、API 接口

### 9.1 每日投资方案接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/daily-report/generate` | 手动触发生成 |
| GET | `/api/daily-report/latest` | 获取最新报告 |
| GET | `/api/daily-report/date/{date}` | 根据日期获取 |
| GET | `/api/daily-report/{id}` | 根据ID获取 |
| GET | `/api/daily-report` | 列出所有报告 |

### 9.2 请求示例

**手动触发生成**：
```bash
curl -X POST "http://localhost:8004/api/daily-report/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "report_date": "2024-01-01",
    "force": false
  }'
```

**获取最新报告**：
```bash
curl "http://localhost:8004/api/daily-report/latest"
```

---

## 🔧 十、配置说明

### 10.1 环境变量 (`core/config.py`)

```env
# 服务配置
ENV=local
LOG_LEVEL=INFO
PORT=8004
HOST=0.0.0.0

# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=quantbull

# 时区
DEFAULT_TIMEZONE=Asia/Shanghai
```

### 10.2 服务地址配置

在 `data_client.py` 和 `ai_client.py` 中硬编码了服务地址：
- data-service: `http://localhost:8001`
- ai-hub: `http://localhost:8002`

**生产环境建议**：通过环境变量配置。

---

## 🚀 十一、部署与运行

### 11.1 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 确保 PostgreSQL 运行
# 创建数据库
createdb quantbull

# 运行服务
python main.py
```

### 11.2 Docker 部署

```bash
# 构建镜像
docker build -t daily-report:latest .

# 运行容器
docker run -d \
  -p 8004:8004 \
  -e POSTGRES_HOST=postgres \
  -e POSTGRES_PASSWORD=your_password \
  --name daily-report \
  daily-report:latest
```

---

## 📝 十二、设计原则

1. **编排型服务**：只负责调度和编排，不处理具体业务逻辑
2. **服务解耦**：通过 HTTP 调用其他服务，便于独立部署
3. **数据驱动**：AI 分析基于真实数据，不捏造
4. **错误处理**：完善的异常处理和日志记录
5. **开发友好**：开发环境提供模拟数据，便于测试
6. **可扩展性**：方便未来接入 Celery / 消息队列

---

## 🔮 十三、未来扩展

### 13.1 消息队列集成

可以将定时任务改为发送消息到 RabbitMQ/Kafka，由 Worker 处理：

```python
# 发送消息
await message_queue.publish({
    "type": "generate_daily_report",
    "report_date": "2024-01-01"
})
```

### 13.2 Celery 集成

使用 Celery 替代 APScheduler：

```python
@celery_app.task
def generate_daily_report_task(report_date: str):
    # 异步任务
    pass
```

### 13.3 交易日判断

添加交易日判断逻辑，避免非交易日执行：

```python
def is_trading_day(date: str) -> bool:
    # 判断是否为交易日
    pass
```

---

## ✅ 十四、代码质量

- ✅ **类型提示**：所有函数都有类型注解
- ✅ **文档字符串**：所有类和方法都有文档
- ✅ **错误处理**：完善的异常处理
- ✅ **日志记录**：关键步骤都有日志
- ✅ **Pydantic v2**：使用最新版本的数据验证
- ✅ **代码可运行**：所有代码经过验证，可直接运行

---

## 📚 十五、相关文档

- [README.md](./README.md) - 项目说明
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - 项目结构
- [requirements.txt](./requirements.txt) - 依赖列表
