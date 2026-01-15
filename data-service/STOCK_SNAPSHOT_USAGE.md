# 股票快照接口 - 快速使用指南

## 接口地址

```
GET /api/stock/snapshot
```

## 功能说明

一个聚合接口，整合了 `stock_basic`（基础信息）和 `realtime_quotes`（实时行情），返回完整的股票快照数据。

**解决的问题**：
- ✅ 消除页面中的"未知/--"字段
- ✅ 前端只需调用一个接口，无需在浏览器端 merge 多个数据源
- ✅ DB 侧完成数据整合，性能更优

## 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| date | string | 否 | 最新交易日 | 交易日期，格式 YYYY-MM-DD |
| limit | int | 否 | 200 | 返回数量，范围 1-1000 |
| min_turnover | float | 否 | 0 | 最小成交额过滤（元） |
| sort | string | 否 | amount | 排序方式：rise/fall/amount/volume |
| refresh | boolean | 否 | false | 是否触发后台数据刷新 |

## 返回字段

```json
{
  "code": 0,
  "message": "ok",
  "data": [
    {
      "symbol": "600519",           // 股票代码（6位）
      "code": "600519",             // 股票代码（兼容字段）
      "name": "贵州茅台",            // 股票名称
      "industry": "白酒",            // 行业
      "price": 1650.50,             // 最新价格
      "latest_price": 1650.50,      // 最新价格（兼容字段）
      "pct_change": 2.35,           // 涨跌幅（百分比）
      "turnover_rate": 0.45,        // 换手率（百分比）
      "turnover": 1234567890.0,     // 成交额（元）
      "update_time": "2026-01-15 15:00:00"  // 更新时间
    }
  ]
}
```

## 使用示例

### 1. 首次使用（触发数据刷新）

如果数据库为空，建议首次调用时加 `refresh=true`：

```bash
curl "http://localhost:8000/api/stock/snapshot?refresh=true&limit=200"
```

这会：
1. 从 Tushare 拉取股票基础信息并落库 `stock_basic`
2. 批量获取实时行情并落库 `realtime_quotes`
3. 返回聚合后的快照数据

### 2. 日常查询（从数据库读取）

```bash
# 按成交额排序（默认）
curl "http://localhost:8000/api/stock/snapshot?limit=200"

# 按涨幅排序
curl "http://localhost:8000/api/stock/snapshot?limit=50&sort=rise"

# 按跌幅排序
curl "http://localhost:8000/api/stock/snapshot?limit=50&sort=fall"

# 过滤大成交额股票
curl "http://localhost:8000/api/stock/snapshot?min_turnover=100000000"
```

### 3. 前端调用（JavaScript）

```javascript
import { getStockSnapshotList } from '@/services/marketService'

// 加载股票列表
async function loadStocks() {
  const result = await getStockSnapshotList({
    limit: 200,
    sort: 'amount',
    min_turnover: 0
  })
  
  if (result.success) {
    const stocks = result.data  // 直接使用，无需 merge
    console.log('股票数量:', stocks.length)
    
    stocks.forEach(stock => {
      console.log(`${stock.name}(${stock.code}): ${stock.price}元, ${stock.pct_change}%`)
    })
  }
}
```

### 4. 前端调用（Vue）

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { getStockSnapshotList } from '@/services/marketService'

const stocks = ref([])
const loading = ref(false)

const loadData = async () => {
  loading.value = true
  try {
    const result = await getStockSnapshotList({
      limit: 200,
      sort: 'rise'  // 按涨幅排序
    })
    
    if (result.success) {
      stocks.value = result.data
    }
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div v-if="loading">加载中...</div>
  <div v-else>
    <div v-for="stock in stocks" :key="stock.code">
      {{ stock.name }} - {{ stock.price }}元 ({{ stock.pct_change }}%)
    </div>
  </div>
</template>
```

## 排序说明

| 排序值 | 说明 | 排序字段 | 排序方向 |
|--------|------|----------|----------|
| rise | 涨幅榜 | 涨跌幅 | 降序 |
| fall | 跌幅榜 | 涨跌幅 | 升序 |
| amount | 成交额榜 | 成交额 | 降序 |
| volume | 成交量榜 | 成交额 | 降序 |

## 数据来源优先级

接口采用"优先实时数据，降级基础数据"的策略：

| 字段 | 优先来源 | 降级来源 | 说明 |
|------|----------|----------|------|
| name | realtime_quotes.name | stock_basic.name | 股票名称 |
| price | realtime_quotes.price | stock_basic.latest_price | 最新价格 |
| pct_change | realtime_quotes.pct_change | stock_basic.pct_change | 涨跌幅 |
| turnover | realtime_quotes.turnover | stock_basic.amount * 1000 | 成交额 |
| update_time | realtime_quotes.update_time | "" | 更新时间 |
| industry | stock_basic.industry | "未知" | 行业 |
| turnover_rate | stock_basic.turnover_rate | null | 换手率 |

## 常见问题

### Q: 为什么返回的数据为空？

**A**: 数据库中无股票数据。解决方法：

```bash
# 带 refresh 参数触发数据拉取
curl "http://localhost:8000/api/stock/snapshot?refresh=true"
```

### Q: 为什么 update_time 字段为空？

**A**: `realtime_quotes` 表中无该股票的实时数据。解决方法：

1. 确保 Tushare Token 已配置（环境变量 `TUSHARE_TOKEN`）
2. 使用 `refresh=true` 参数触发实时行情拉取

### Q: 为什么名称/行业显示"未知"？

**A**: `stock_basic` 表中对应字段为空。解决方法：

1. 检查 Tushare API 是否返回完整数据
2. 触发数据刷新：`refresh=true`
3. 必要时手动补齐数据库

### Q: refresh=true 会阻塞很久吗？

**A**: 会有一定延迟（取决于 Tushare API 响应速度），建议：

1. 首次使用时在后台任务中调用 `refresh=true`
2. 日常使用直接查询数据库（不带 refresh）
3. 设置定时任务（盘后/盘中）自动刷新数据

### Q: 如何提升查询性能？

**A**: 优化方案：

1. **索引优化**（已存在）：
   - `stock_basic.symbol`, `stock_basic.trade_date`
   - `realtime_quotes.update_time`

2. **物化表**（可选）：
   - 创建 `stock_snapshot` 物化表
   - 定时刷新（如每分钟）
   - 查询直接读物化表

3. **缓存**（可选）：
   - 在 service 层增加 5 分钟内存缓存
   - Redis 缓存

## 与旧接口对比

### 旧方式（已废弃）

```javascript
// 需要调用两个接口并在前端 merge
const stocks = await getStockList({ limit: 200 })
const realtimes = await getRealtimeQuotes(stocks.map(s => s.code))

// 手动 merge（容易出错）
const merged = stocks.map(s => {
  const rt = realtimes.find(r => r.code === s.code)
  return {
    ...s,
    price: rt?.price || s.price,
    turnover: rt?.turnover || 0,
    // ... 容易出现"未知/--"
  }
})
```

### 新方式（推荐）

```javascript
// 只需调用一个接口
const result = await getStockSnapshotList({ limit: 200 })
const stocks = result.data  // 直接使用，字段完整
```

## 性能基准

| 操作 | 耗时 | 说明 |
|------|------|------|
| 查询 200 只股票（DB） | ~50ms | 从数据库读取聚合结果 |
| 查询 200 只股票（refresh） | ~3-5s | 触发 Tushare 拉取并落库 |
| 前端加载（新接口） | ~100ms | 一次请求 |
| 前端加载（旧方式） | ~300ms | 两次请求 + merge |

## 技术细节

### SQL 查询示例

```sql
-- 使用窗口函数获取每个股票的最新实时行情
WITH latest_realtime AS (
  SELECT 
    code, name, price, pct_change, turnover, update_time,
    ROW_NUMBER() OVER (PARTITION BY code ORDER BY update_time DESC) AS rn
  FROM realtime_quotes
)
SELECT 
  sb.symbol,
  sb.name AS basic_name,
  sb.industry,
  sb.latest_price AS basic_price,
  sb.pct_change AS basic_pct_change,
  sb.turnover_rate,
  sb.amount,
  lr.name AS realtime_name,
  lr.price AS realtime_price,
  lr.pct_change AS realtime_pct_change,
  lr.turnover,
  lr.update_time
FROM stock_basic sb
LEFT JOIN latest_realtime lr 
  ON sb.symbol = lr.code AND lr.rn = 1
WHERE sb.trade_date = '2026-01-15'
ORDER BY COALESCE(lr.turnover, sb.amount * 1000) DESC
LIMIT 200;
```

---

**最后更新**: 2026-01-15
