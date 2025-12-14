# Tushare 数据接入服务 API 文档

## 概述

Tushare 数据接入服务提供标准化的历史行情与基本面数据，作为量化平台的数据来源。

**定位：**
- 标准化历史数据与基本面数据
- 不承担实时行情与舆情任务
- 可被量化引擎、AI 选股、回测服务调用

## 配置

### 环境变量

在 `.env` 文件中配置 Tushare Token：

```env
TUSHARE_TOKEN=your_tushare_token_here
```

获取 Token：
1. 访问 https://tushare.pro/
2. 注册账号并获取 Token

## API 接口

### 1. POST /api/tushare/daily

获取日线行情数据（支持批量查询）

**请求体：**
```json
{
  "codes": ["000001", "600000"],
  "start_date": "20250101",
  "end_date": "20251231"
}
```

**响应：**
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
  "success_codes": ["000001", "600000"],
  "failed_codes": []
}
```

**字段说明：**
- `code`: 股票代码（6位，不带 .SZ/.SH）
- `trade_date`: 交易日期（YYYYMMDD）
- `open/high/low/close`: 开盘/最高/最低/收盘价（元）
- `vol`: 成交量（手）
- `amount`: 成交额（元）

**特性：**
- 自动保存到数据库（upsert）
- 单个股票失败不影响整体
- 支持批量查询

### 2. GET /api/tushare/stock_basic

获取股票基础信息

**请求：**
```
GET /api/tushare/stock_basic?exchange=
```

**响应：**
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

### 3. POST /api/tushare/fund_daily

获取 ETF 日线行情

**请求体：**（与 daily 接口相同）
```json
{
  "codes": ["159919", "510300"],
  "start_date": "20250101",
  "end_date": "20251231"
}
```

## 数据库

### 表结构：daily_quotes

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 主键（自增） |
| code | str | 股票代码（索引） |
| trade_date | date | 交易日期（索引） |
| open | float | 开盘价 |
| high | float | 最高价 |
| low | float | 最低价 |
| close | float | 收盘价 |
| vol | int | 成交量（手） |
| amount | float | 成交额（元） |

**约束：**
- 唯一约束：`(code, trade_date)`
- 使用 upsert（存在即更新）

## 使用示例

### PowerShell

```powershell
# 测试日线行情
$body = @{
    codes = @("000001", "600000")
    start_date = "20250101"
    end_date = "20251213"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/tushare/daily" `
    -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

### Python

```python
import requests

# 获取日线行情
response = requests.post(
    "http://localhost:8000/api/tushare/daily",
    json={
        "codes": ["000001", "600000"],
        "start_date": "20250101",
        "end_date": "20251231"
    }
)
print(response.json())
```

### curl

```bash
curl -X POST http://localhost:8000/api/tushare/daily \
  -H "Content-Type: application/json" \
  -d '{
    "codes": ["000001", "600000"],
    "start_date": "20250101",
    "end_date": "20251231"
  }'
```

## 错误处理

- 单个股票接口失败不影响整体
- 捕获 Tushare 接口异常并记录日志
- 对空数据返回空数组而非报错
- 失败的股票代码会出现在 `failed_codes` 列表中

## 注意事项

1. **Token 配置**：必须配置 `TUSHARE_TOKEN` 环境变量
2. **日期格式**：必须为 YYYYMMDD 格式（8位数字）
3. **股票代码**：支持 6 位代码，会自动添加市场后缀
4. **数据保存**：数据会自动保存到数据库，使用 upsert 避免重复
5. **限流**：注意 Tushare 的 API 调用频率限制

## 支持的接口

- ✅ 股票基础信息（stock_basic）
- ✅ 日线行情（daily）
- ✅ ETF 日线行情（fund_daily）
- ✅ 指数日线行情（index_daily）- 服务已实现，路由可扩展
- ✅ 主要财务指标（fina_indicator）- 服务已实现，路由可扩展

## 测试

使用测试脚本：

```powershell
cd data-service
.\test-tushare-api.ps1
```

或访问 Swagger UI：
http://localhost:8000/docs

