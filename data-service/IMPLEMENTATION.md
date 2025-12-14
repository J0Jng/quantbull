# 东方财富实时行情爬虫微服务 - 实现总结

## ✅ 已实现功能

### 1. 核心功能
- ✅ FastAPI 异步接口
- ✅ 东方财富实时行情爬虫（使用 requests + lxml）
- ✅ PostgreSQL + SQLModel ORM
- ✅ FastAPI 依赖注入管理 DB Session
- ✅ 自动根据股票代码判断市场（深圳/上海）
- ✅ 支持沪深 A 股（000/002/300/600/601/603 等）

### 2. 接口设计
- ✅ POST `/api/quotes/realtime` - 获取实时行情
- ✅ 请求体：`{"codes": ["000001", "600000"]}`
- ✅ 返回成功和失败的代码列表

### 3. 数据库设计
- ✅ 表名：`realtime_quotes`
- ✅ 主键：`id`（自增）
- ✅ 唯一约束：`(code, update_time)`
- ✅ 索引：`code`, `update_time`
- ✅ 自动创建表

### 4. 健壮性
- ✅ 单个股票失败不影响整体
- ✅ 捕获请求/解析异常
- ✅ 返回成功与失败的 code 列表
- ✅ 完整的错误日志

## 📁 文件结构

```
data-service/
├── core/
│   ├── config.py          # 配置（含数据库连接）
│   ├── database.py        # 数据库连接和依赖注入
│   └── logger.py          # 日志配置
├── models/
│   └── realtime_quote.py  # SQLModel 模型
├── schemas/
│   └── quote.py           # Pydantic 请求/响应模型
├── services/
│   └── eastmoney_spider.py # 东方财富爬虫服务
├── routers/
│   └── quotes.py           # 行情路由
├── main.py                 # FastAPI 应用入口
├── requirements.txt        # 依赖列表
└── test-quotes-api.ps1     # 测试脚本
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd data-service
pip install -r requirements.txt
```

### 2. 配置数据库

创建 `.env` 文件：

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/quantbull
ENV=local
LOG_LEVEL=INFO
```

### 3. 启动服务

```bash
uvicorn main:app --reload
```

### 4. 测试 API

```powershell
# 使用测试脚本
.\test-quotes-api.ps1

# 或使用浏览器
# 访问 http://localhost:8000/docs
```

## 📊 数据流程

1. **接收请求** → `POST /api/quotes/realtime`
2. **爬取数据** → `EastMoneySpider.fetch_quotes()`
3. **解析数据** → 提取 price, pct_change, turnover 等
4. **保存数据库** → `RealtimeQuote` 模型
5. **返回响应** → 包含成功和失败的代码列表

## 🔧 技术细节

### 股票代码判断逻辑

```python
MARKET_MAP = {
    "000": "0",  # 深圳主板
    "002": "0",  # 深圳中小板
    "300": "0",  # 深圳创业板
    "600": "1",  # 上海主板
    "601": "1",  # 上海主板
    "603": "1",  # 上海主板
}
```

### API 字段映射

- `f58`: 股票名称
- `f43`: 最新价
- `f170`: 涨跌幅（百分比）
- `f47`: 成交额（元）

### 数据库字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键（自增） |
| code | str | 股票代码（索引） |
| name | str | 股票名称 |
| price | float | 最新价 |
| pct_change | float | 涨跌幅（百分比） |
| turnover | float | 成交额（元） |
| update_time | datetime | 更新时间（索引） |

## ⚠️ 注意事项

1. **数据库连接**：确保 PostgreSQL 已启动并创建数据库
2. **网络访问**：需要能够访问东方财富 API
3. **股票代码格式**：必须是 6 位数字
4. **数据更新**：每次请求都会插入新记录（保留历史）

## 🐛 故障排查

### 问题：数据库连接失败

**解决**：检查 `.env` 文件中的 `DATABASE_URL` 配置

### 问题：爬虫返回空数据

**解决**：
1. 检查网络连接
2. 验证股票代码格式
3. 查看日志输出

### 问题：导入错误

**解决**：确保已安装所有依赖
```bash
pip install -r requirements.txt
```

## 📝 后续优化建议

1. 添加缓存机制（Redis）
2. 支持批量查询优化
3. 添加限流保护
4. 支持更多数据源
5. 添加数据验证和清洗

