* ⭐ 全栈项目开发流程（Vue3 + Python + FastAPI + 微服务）
* ⭐ AI 使用指令（Prompt 套件）
* ⭐ 模块结构设计
* ⭐ 项目目录结构
* ⭐ 部署流程
---

# 📌 README.md — 量化牛牛（QuantBull）

**Vue3 + Python + FastAPI + AI + 微服务量化平台**

---

## 🐂 项目简介

**量化牛牛（QuantBull）** 是一个证券私募量化投研 AI 平台，集 **数据采集 → AI内容生成 → 量化引擎 → 投资方案生成 → 可视化展示** 于一体。
平台包含：

* Web 前端（Vue3）
* 后端微服务（FastAPI）
* 数据中台（PostgreSQL + TDengine + Redis）
* AI 中枢（DeepSeek、通义千问 + 自有微调模型）
* 自动内容生成系统（新闻、报告、视频、数字人）
* 量化策略与每日投资方案推荐

最终形态包括：
📌 Web 主站
📌 微信小程序
📌 公众号内容自动更新

---

# 🏗️ 一、系统架构

```
frontend (Vue3)
     │
 API Gateway (FastAPI)
     │
 ├─ data-service       数据采集 & 清洗
 ├─ ai-hub             LLM 网关 / 文本生成 / 视频合成
 ├─ quant-engine       回测 / 因子库 / 策略执行
 ├─ daily-report       每日 AI 投资方案
 └─ user-service       用户系统

数据库：
- PostgreSQL（结构化数据）
- TDengine（行情时间序列）
- Redis（缓存 + 队列）
```

---

# 🧩 二、项目目录结构

```
quantbull/
│
├─ frontend/                 # Vue3 前端
│   ├─ src/
│   ├─ vite.config.js
│   └─ package.json
│
├─ backend/
│   ├─ api-gateway/          # FastAPI 统一入口
│   ├─ data-service/         # 爬虫、数据清洗
│   ├─ ai-hub/               # AI 多模型路由层
│   ├─ quant-engine/         # 回测与策略
│   ├─ daily-report/         # AI自动生成投资方案
│   └─ user-service/
│
├─ scripts/                  # 运维脚本、定时任务
│
├─ docs/                     # 文档（部署、设计稿）
│
└─ docker-compose.yml
```

---

# 🚀 三、开发流程（全栈）

## 1. 前端开发流程（Vue3 + Element Plus）

1. 设计 UI（推荐墨刀）

2. 创建工程：

   ```
   npm create vue@latest quantbull-frontend
   npm install element-plus axios pinia vue-router
   ```

3. 实现页面：

   * 首页仪表盘（ETF/股票推荐、新闻、行情）
   * AI 新闻中心
   * 量化实验室（策略编辑器 + 回测图表）
   * 数字人内容播放

4. 接入后端统一 API 网关

---

## 2. 后端开发流程（FastAPI 微服务）

### 分 5 个服务开发：

### 🟦 (1) data-service（数据中台）

* Scrapy/Playwright 爬虫
* 东方财富、财联社、聚宽、Tushare api
* 数据清洗、标准化
* 存入 PostgreSQL & TDengine

### 🟪 (2) ai-hub（AI能力中台）

* DeepSeek、通义千问 API 封装
* 智能模型路由（代码/新闻/总结/策略）
* AIGC（新闻/报告）
* 数字人短视频生成（第三方）

### 🟧 (3) quant-engine（量化引擎）

* Backtrader
* 回测（分钟/日线）
* 因子库
* 策略接口

### 🟨 (4) daily-report（每日 AI 投资方案）

* 每天 15:10 自动触发
* 生成：

  * 3 个 ETF
  * 10 个股票
  * 止损/仓位
  * 风险提示
* 同步至：Web、小程序、公众号

### 🟥 (5) api-gateway（统一 API 网关）

* 路由所有服务
* 处理鉴权
* 日志与限流

---

# 🧠 四、AI Prompt 指令套件（可直接使用）

以下是实际项目中最核心的 Prompt 套件（已经优化好）。

---

## 📌 1. 新闻生成 Prompt（从快讯 → 300字新闻）

```
你是专业金融编辑。请根据以下快讯和最新行情数据，
生成一篇约300字的财经新闻，包含：
- 客观描述
- 行业背景
- 逻辑分析
- 风险提示

快讯：{news}
股票：{code}
今日行情：{quote}

要求：不能虚构信息，不要给推荐性意见。
```

---

## 📌 2. 公司研究报告摘要 Prompt

```
你是资深证券分析师。
请基于以下企业公开信息，生成一篇公司介绍与投研摘要：

内容必须包含：
- 公司主营业务
- 行业地位
- 最近动态
- 风险因素

资料如下：
{company_info}
```

---

## 📌 3. 量化策略生成 Prompt（自然语言 → 可运行 Python）

```
你是量化研究员。
请根据我的描述，生成适用于 Backtrader 的策略代码，
包含：买卖逻辑、风险控制、参数解释。

策略描述：
{user_text}

要求：输出完整可运行策略代码。
```

---

## 📌 4. 每日投资方案（ETF + 股票）

```
你是投资组合经理。
基于今日全市场数据与新闻，输出：

- 3个ETF（含选择理由）
- 10只股票（含因子解释）
- 市场情绪简述
- 风险提示（必须有）

输入数据：
{market_data}
{news_summary}

要求：不得涉及承诺收益或投资建议。
```

---

## 📌 5. 数字人视频生成（文本 → 口播文案）

```
请将以下文本改写为数字人使用的口播稿，
风格专业但口语化，时长控制在 20–40 秒：

内容：
{text}
```

---

# 🛠️ 五、部署流程（Docker）

### 1. 本地开发

```
docker-compose up -d
```

### 2. 部署到服务器

支持：

* 阿里云 / 腾讯云
* K8s / Docker Swarm

### 3. CI/CD（推荐）

* GitHub Actions 自动部署
* 前端打包 → OSS/CDN
* 后端容器镜像 → 服务器

---

# 📲 六、小程序与公众号接入

### 小程序（Uni-app）

* 复用 Web 的 API
* 展示每日投资方案
* 播放数字人视频
* 推送提醒

### 公众号

* 自动推送每日内容
* 自动回复（接入 ai-hub）

---

# 📘 七、二次开发须知

* 本平台属于辅助投研产品，需加强合规提示
* 投资类内容必须添加“风险提示，非投资建议”
* 所有自动爬取数据需遵守网站 Robots 协议
