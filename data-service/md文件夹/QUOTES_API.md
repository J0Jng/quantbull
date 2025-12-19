# 实时行情 API 文档

## 接口说明

### POST /api/quotes/realtime

获取沪深 A 股实时行情数据，支持批量查询。

**请求体：**
```json
{
  "codes": ["000001", "600000", "000002"]
}
```

**响应：**
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
  "success_codes": ["000001", "600000"],
  "failed_codes": ["000002"]
}
```

## 支持的股票代码

- **深圳市场**：000, 001, 002, 003, 300 开头
- **上海市场**：600, 601, 603, 605, 688 开头

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| code | string | 股票代码（6位） |
| name | string | 股票名称 |
| price | float | 最新价（元） |
| pct_change | float | 涨跌幅（百分比，如 1.23 表示 1.23%） |
| turnover | float | 成交额（元） |
| update_time | datetime | 更新时间（ISO 格式） |

## 数据库

数据会自动保存到 PostgreSQL 数据库的 `realtime_quotes` 表中。

**表结构：**
- `id`: 主键（自增）
- `code`: 股票代码（索引）
- `name`: 股票名称
- `price`: 最新价
- `pct_change`: 涨跌幅
- `turnover`: 成交额
- `update_time`: 更新时间（索引）
- 唯一约束：`(code, update_time)`

## 使用示例

### PowerShell

```powershell
$body = @{
    codes = @("000001", "600000")
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/quotes/realtime" `
    -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

### curl

```bash
curl -X POST http://localhost:8000/api/quotes/realtime \
  -H "Content-Type: application/json" \
  -d '{"codes": ["000001", "600000"]}'
```

### Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/quotes/realtime",
    json={"codes": ["000001", "600000"]}
)
print(response.json())
```

## 错误处理

- 单个股票获取失败不影响其他股票
- 失败的股票代码会出现在 `failed_codes` 列表中
- 成功的股票数据会出现在 `data` 列表中

## 注意事项

1. 确保数据库已配置并连接成功
2. 股票代码必须是 6 位数字
3. 仅支持沪深 A 股，不支持港股、美股等
4. 数据来源：东方财富实时行情接口

