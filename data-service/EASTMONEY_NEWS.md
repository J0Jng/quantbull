# 东方财富网财经新闻聚合功能

## 功能概述

从东方财富网抓取财经新闻信息，提供 7×24 小时快讯和财经文章列表两种数据源，聚合成新闻流为前端财经频道页提供动态数据。

## 功能特性

✅ **合规优先**
- 不模拟登录、不使用 Cookie、不绕过验证码/风控、不做高并发
- 只采集公开可访问内容的"摘要级信息"（标题、摘要、时间、链接、缩略图）
- 严禁抓取/存储文章全文到数据库
- 图片优先使用缩略图/公开图链
- 使用东方财富网公开 API 和 HTML 页面

✅ **多策略回退**
- 优先：7×24 快讯接口（更新快、天然摘要级）
- 兜底：财经频道文章列表（有图片、内容丰富）
- 两者都失败时：返回缓存旧数据或空列表

✅ **缓存与降级**
- 内存缓存，TTL 默认 300 秒（5 分钟）
- 抓取失败时返回缓存旧数据（stale=true）
- 无缓存时返回空列表并带 error 字段
- 前端可降级到备用模拟数据

✅ **定时刷新**
- 使用 APScheduler 定时预加载缓存
- 默认每 5 分钟自动刷新
- 减少用户请求时的延迟
- 自动保存到数据库

✅ **数据库存储**
- 新闻数据自动保存到 PostgreSQL（eastmoney_news 表）
- 支持历史新闻查询（最近 1-168 小时）
- 支持关键词搜索（大小写不敏感）
- 自动去重和更新（按 news_id 唯一约束）

✅ **礼貌爬虫策略**
- 使用 httpx.AsyncClient 异步请求
- 并发限流（Semaphore 3~5）
- 轻量 retry（最多 2 次）与超时（10s）
- 文章页抓取加入 100~300ms 随机延迟

## 架构设计

```
前端 (FinanceChannelPage.vue / newsService.js)
    ↓ HTTP GET /api/news/eastmoney/latest 或 /eastmoney/history
API Gateway (api-gateway:8000)
    ↓ 路由转发 /news/* → data-service
Data Service (data-service:8001)
    ↓ /api/news/eastmoney/latest 或 /api/news/eastmoney/history
EastmoneyNewsAggregator
    ├─ 策略 A：7×24 快讯 JSON 接口 (np-listapi.eastmoney.com)
    ├─ 策略 B：财经频道文章列表 HTML 解析 (finance.eastmoney.com)
    ├─ 内存缓存 (TTL 300s)
    └─ 数据库存储 → PostgreSQL (eastmoney_news 表)
    
定时任务调度器 (APScheduler)
    ↓ 每 5 分钟自动刷新
EastmoneyNewsAggregator
    └─ 预加载缓存 + 保存到数据库
```

## API 接口

### GET /api/news/eastmoney/latest（推荐）

获取东方财富网最新财经新闻（实时抓取 + 缓存）。

**请求参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| limit | int | 否 | 20 | 返回的最大条数（1-100） |
| keyword | string | 否 | null | 关键词过滤（在标题/摘要中搜索，大小写不敏感） |

**响应示例**

```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "eastmoney_202601213625140518",
        "title": "央行宣布下调金融机构存款准备金率",
        "summary": "中国人民银行决定于2026年1月25日下调金融机构存款准备金率0.5个百分点...",
        "source": "东方财富网",
        "time": "2小时前",
        "url": "https://finance.eastmoney.com/a/202601213625140518.html",
        "img": "https://np-newspic.dfcfw.com/download/202601213625140518_w210h154.jpg",
        "author": "要闻"
      }
    ],
    "cached": false,
    "stale": false,
    "timestamp": 1737459600
  }
}
```

### GET /api/news/eastmoney/history

查询历史东方财富网新闻（从数据库）。

**请求参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| limit | int | 否 | 20 | 返回的最大条数（1-100） |
| keyword | string | 否 | null | 关键词过滤（在标题/摘要中搜索，大小写不敏感） |
| hours | int | 否 | 24 | 查询最近多少小时的数据（1-168 小时） |

**响应示例**

```json
{
  "code": 200,
  "data": {
    "items": [
      {
        "id": "eastmoney_202601203624987456",
        "title": "A股三大指数全线上涨，北向资金净流入超百亿",
        "summary": "1月20日，A股三大指数集体收涨，沪指涨0.85%收于3250.68点...",
        "source": "东方财富网",
        "time": "2026-01-20 15:30",
        "url": "https://finance.eastmoney.com/a/202601203624987456.html",
        "img": "https://np-newspic.dfcfw.com/download/202601203624987456_w210h154.jpg",
        "author": "股票"
      }
    ],
    "cached": false,
    "stale": false,
    "timestamp": 1737459600
  }
}
```

### 旧接口（已弃用，保持兼容）

以下接口已弃用，但仍可用。内部已转发到东方财富网实现：

- `GET /api/news/weibo/media` → 转发到 `/api/news/eastmoney/latest`
- `GET /api/news/weibo/history` → 转发到 `/api/news/eastmoney/history`

## 数据模型

### eastmoney_news 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 自增主键 |
| news_id | varchar(64) | 新闻唯一标识（eastmoney_前缀 + 文章ID/URL哈希） |
| title | varchar(200) | 新闻标题 |
| summary | text | 新闻摘要（来自快讯内容或文章首段截断） |
| source | varchar(50) | 新闻来源（默认"东方财富网"） |
| author | varchar(100) | 作者/栏目名 |
| url | varchar(500) | 原文链接 |
| img_url | varchar(500) | 配图链接（缩略图） |
| publish_time | varchar(50) | 发布时间（人类可读格式） |
| publish_timestamp | int | 发布时间戳（Unix秒，用于排序） |
| created_at | datetime | 数据入库时间 |
| updated_at | datetime | 数据更新时间 |

**索引**：
- `news_id`：唯一索引
- `publish_timestamp`：普通索引（用于时间范围查询）
- `author`：普通索引
- `created_at`：普通索引

## 数据源说明

### 策略 A：7×24 快讯接口（优先）

- **接口地址**：`https://np-listapi.eastmoney.com/comm/web/getFastNewsList`
- **数据特点**：更新频率高、天然摘要级、无需解析 HTML
- **字段映射**：
  - `newsId` / `code` → `id`
  - `title` → `title`
  - `digest` → `summary`
  - `showTime` / `postTime` → `time` / `publish_timestamp`
  - `url` → `url`
  - `image` → `img`

### 策略 B：财经频道文章列表（兜底）

- **页面地址**：
  - 要闻：https://finance.eastmoney.com/a/cywjh.html
  - 股票：https://finance.eastmoney.com/a/cgpzx.html
  - 基金：https://finance.eastmoney.com/a/cjjyj.html
  - 全球：https://finance.eastmoney.com/a/cqqzx.html
- **数据特点**：有缩略图、可解析摘要、更稳定
- **解析规则**：
  - 文章 URL 正则：`/a/(\d+)\.html` → 提取文章 ID
  - 图片 CDN：`https://np-newspic.dfcfw.com/download/...`

## ID 生成规则

1. **优先**：从 URL 提取数字 ID
   - 文章页：`/a/(\d{15,20})\.html` → `eastmoney_<id>`
2. **兜底**：URL 的 MD5 哈希
   - `eastmoney_<md5(url)[:16]>`

## 时间处理规则

### 输出格式（time 字段）

- 60 秒内：`刚刚`
- 1 小时内：`x分钟前`
- 24 小时内：`x小时前`
- 7 天内：`x天前`
- 超过 7 天：`YYYY-MM-DD HH:mm`

### 时间戳（publish_timestamp）

- 用于数据库排序和时间范围查询
- 统一为 Unix 秒级时间戳
- 处理跨年/跨日情况

## 前端调用示例

```javascript
import { getEastmoneyLatestNews, getEastmoneyHistoryNews } from '@/services/newsService'

// 获取最新新闻
const latestNews = await getEastmoneyLatestNews({ limit: 10 })

// 带关键词过滤
const filteredNews = await getEastmoneyLatestNews({ limit: 20, keyword: '央行' })

// 查询历史新闻
const historyNews = await getEastmoneyHistoryNews({ hours: 48, limit: 50 })

// 旧方法仍可用（向后兼容）
const oldWayNews = await getWeiboMediaNews({ limit: 10 })  // 内部已转发到东方财富
```

## 错误处理

### 抓取失败降级

1. 如果缓存存在：返回缓存数据，`stale=true`
2. 如果无缓存：返回空列表，附带 `error` 字段

```json
{
  "items": [],
  "cached": false,
  "stale": false,
  "timestamp": 1737459600,
  "error": "抓取失败且无缓存数据"
}
```

### 数据库操作失败

- 不影响接口返回（优先返回抓取数据）
- 记录错误日志
- 自动回滚事务

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| cache_ttl | 300 | 缓存过期时间（秒） |
| timeout | 10 | HTTP 请求超时时间（秒） |
| max_items_per_category | 10 | 每个分类抓取的最大条数 |
| max_concurrent_requests | 3 | 最大并发请求数 |
| interval_minutes | 5 | 定时刷新间隔（分钟） |

## 文件结构

```
data-service/
├── models/
│   └── eastmoney_news.py          # 数据库模型
├── services/
│   └── eastmoney_news_service.py  # 新闻聚合服务
├── routers/
│   └── news.py                    # API 路由（含新旧接口）
├── scheduler_eastmoney_news.py    # 定时任务调度器
└── EASTMONEY_NEWS.md              # 本文档

frontend/niuniu/src/services/
└── newsService.js                 # 前端服务（已更新）
```

## 与旧版微博新闻的对比

| 特性 | 微博新闻（旧） | 东方财富新闻（新） |
|------|---------------|-------------------|
| 数据源 | 微博公开 API | 东方财富网快讯/文章 |
| 更新频率 | 依赖微博账号发布 | 7×24 小时持续更新 |
| 数据稳定性 | 受微博风控影响 | 相对稳定 |
| 图片支持 | 微博缩略图 | 东方财富 CDN 缩略图 |
| 接口路径 | /weibo/* | /eastmoney/*（推荐） |
| 数据库表 | weibo_news | eastmoney_news |

## 迁移指南

### 后端

无需额外操作，启动时会自动：
1. 创建 `eastmoney_news` 表
2. 启动东方财富新闻定时任务
3. 旧接口 `/weibo/*` 自动转发到新实现

### 前端

1. **推荐**：将 `getWeiboMediaNews` 调用改为 `getEastmoneyLatestNews`
2. **兼容**：保持原有调用不变（内部已自动转发）

## 常见问题

### Q: 快讯接口返回空数据？
A: 检查网络连接，或尝试手动访问快讯页面确认是否正常。系统会自动回退到文章列表解析。

### Q: 数据库没有数据？
A: 确认定时任务已启动（查看启动日志），或手动调用一次 `/api/news/eastmoney/latest` 触发入库。

### Q: 图片无法显示？
A: 东方财富图片 CDN 可能有防盗链，前端可配置图片代理或使用默认占位图。

### Q: 如何调整刷新频率？
A: 修改 `main.py` 中的 `scheduler.start(interval_minutes=5)` 参数。

## 更新日志

- **2026-01-21**：初始版本，支持东方财富网快讯和文章列表双策略抓取
