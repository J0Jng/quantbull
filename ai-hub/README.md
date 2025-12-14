# AI Hub 服务

**LLM 网关（AI 中台服务）** - 统一 AI 能力中台，上层服务无需感知具体模型

## 核心特性

### 🎯 模型接入（Adapter 模式）

- ✅ **DeepSeek R1**：偏文本生成、新闻、逻辑推理
- ✅ **通义千问 Qwen2.5**：偏结构化输出、代码生成、投研摘要
- ✅ **可扩展架构**：采用 Adapter 模式，便于后续新增模型

### 🚀 对外 API（FastAPI 异步接口）

- ✅ `POST /api/ai/generate/news` - 生成新闻解读（默认：DeepSeek）
- ✅ `POST /api/ai/generate/summary` - 生成投研摘要（默认：Qwen）
- ✅ `POST /api/ai/generate/strategy` - 生成策略代码（默认：Qwen）

### 🧠 智能模型路由

- ✅ **自动模型选择**：根据任务类型自动路由到最适合的模型
  - 新闻/长文本生成 → DeepSeek
  - 摘要/代码/结构化输出 → Qwen
- ✅ **显式指定**：支持在 request 中显式指定 model（可选）

### 🏗️ 工程架构

- ✅ **全异步调用**：FastAPI + httpx.AsyncClient
- ✅ **Adapter 模式**：模型调用逻辑封装在 `services/llm` 层
- ✅ **统一接口**：上层服务无需感知具体模型
- ✅ **生产级规范**：代码可扩展、可维护

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```env
# 基础配置
ENV=local
LOG_LEVEL=INFO
PORT=8002
HOST=0.0.0.0

# DeepSeek R1 API（偏文本生成、新闻、逻辑推理）
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat  # 或 deepseek-r1

# 通义千问 Qwen2.5 API（偏结构化输出、代码生成、投研摘要）
QWEN_API_KEY=your-qwen-api-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-turbo  # 或 qwen2.5-7b-chat

# OpenAI 兼容接口（可选）
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# 数字人服务（可选）
DIGITAL_HUMAN_API_URL=
DIGITAL_HUMAN_API_KEY=

# 模型配置
DEFAULT_MODEL=deepseek
MAX_TOKENS=4096
TEMPERATURE=0.7
```

### 3. 启动服务

```bash
python run.py
```

或使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### 4. 访问文档

- API 文档：http://localhost:8002/docs
- 健康检查：http://localhost:8002/health

## API 示例

### 1. 生成新闻解读（默认 DeepSeek）

```bash
curl -X POST "http://localhost:8002/api/ai/generate/news" \
  -H "Content-Type: application/json" \
  -d '{
    "news_flash": "某公司发布新产品，预计将推动行业变革",
    "stock_code": "000001",
    "quote_data": {"price": 10.5, "change": 0.5},
    "target_length": 300,
    "model": null
  }'
```

**响应示例：**
```json
{
  "news_content": "根据最新快讯，某公司发布了创新产品...",
  "model": "deepseek",
  "word_count": 298,
  "tokens_used": 450
}
```

### 2. 生成投研摘要（默认 Qwen）

```bash
curl -X POST "http://localhost:8002/api/ai/generate/summary" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "公司2024年Q1财报显示，营收同比增长30%，净利润增长25%...",
    "summary_type": "structured",
    "max_length": 500,
    "model": null
  }'
```

**响应示例：**
```json
{
  "summary": "- 核心要点：营收增长30%，净利润增长25%...",
  "model": "qwen",
  "tokens_used": 320,
  "sections": ["- 核心要点", "- 关键数据", "- 风险因素"]
}
```

### 3. 生成策略代码（默认 Qwen）

```bash
curl -X POST "http://localhost:8002/api/ai/generate/strategy" \
  -H "Content-Type: application/json" \
  -d '{
    "user_description": "基于5日均线和20日均线的金叉死叉策略",
    "framework": "backtrader",
    "include_risk_control": true,
    "model": null
  }'
```

**响应示例：**
```json
{
  "strategy_code": "import backtrader as bt\n\nclass MyStrategy(bt.Strategy):\n...",
  "model": "qwen",
  "explanation": "策略包含可配置参数，请查看代码中的参数定义。",
  "parameters": {
    "framework": "backtrader",
    "include_risk_control": true
  },
  "tokens_used": 1200
}
```

### 4. 显式指定模型

所有接口都支持显式指定模型：

```bash
curl -X POST "http://localhost:8002/api/ai/generate/news" \
  -H "Content-Type: application/json" \
  -d '{
    "news_flash": "快讯内容",
    "model": "qwen"
  }'
```

## 项目结构

```
ai-hub/
├── main.py                          # FastAPI 入口文件
├── run.py                           # 启动脚本
├── requirements.txt                 # Python 依赖（Pydantic v2）
├── Dockerfile                       # Docker 配置
├── .gitignore                      # Git 忽略文件
├── README.md                        # 项目文档
│
├── core/                           # 核心配置模块
│   ├── __init__.py
│   ├── config.py                   # 配置管理（支持 .env）
│   └── logger.py                   # 日志配置
│
├── routers/                        # 路由层
│   ├── __init__.py
│   └── ai.py                       # AI 相关 API 路由
│
├── services/                       # 业务逻辑层
│   ├── __init__.py
│   ├── llm_service.py              # LLM 网关服务（统一接口）
│   ├── model_router.py             # 智能模型路由
│   ├── news_service.py             # 新闻生成服务
│   ├── summary_service.py          # 摘要生成服务
│   ├── strategy_service.py         # 策略生成服务
│   ├── report_service.py           # 报告生成服务（兼容）
│   ├── digital_human_service.py   # 数字人服务（兼容）
│   │
│   └── llm/                        # LLM 适配器层（Adapter 模式）
│       ├── __init__.py
│       ├── base.py                 # LLMAdapter 抽象基类
│       ├── deepseek_adapter.py     # DeepSeek R1 适配器
│       ├── qwen_adapter.py         # Qwen2.5 适配器
│       └── llm_factory.py          # LLM 工厂类
│
├── models/                         # 数据模型
│   ├── __init__.py
│   └── ai_request.py               # AI 请求记录模型
│
└── schemas/                        # Pydantic v2 模式
    ├── __init__.py
    └── ai.py                       # AI 相关 Schema（请求/响应）
```

## Docker 部署

```bash
docker build -t ai-hub:latest .
docker run -d -p 8002:8002 --env-file .env ai-hub:latest
```

## 技术栈

- **Python 3.12+**
- **FastAPI 0.110+** - 异步 Web 框架
- **Pydantic v2** - 数据验证
- **httpx** - 异步 HTTP 客户端
- **Adapter 模式** - 可扩展的模型接入架构

## 设计目标

✅ **统一 AI 中台**：上层服务无需感知具体模型  
✅ **可扩展架构**：采用 Adapter 模式，便于新增模型  
✅ **智能路由**：根据任务类型自动选择最适合的模型  
✅ **生产级规范**：代码可维护、可测试、符合微服务规范

## 注意事项

1. 所有 API Key 请妥善保管，不要提交到代码仓库
2. 生产环境请修改 CORS 配置，限制允许的域名
3. 模型路由规则可在 `services/model_router.py` 中自定义
4. 新增模型只需实现 `LLMAdapter` 接口并在 `LLMFactory` 中注册
5. 所有投资相关内容必须包含风险提示
