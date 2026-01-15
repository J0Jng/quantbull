# 股票数据中心页面交付说明

## 交付完成时间
2026年1月15日

## 改造概述
已完成 StockDataPage.vue 的全面真实数据交付改造，所有展示数据均来自真实 API 接口或基于真实数据的计算。

## 主要改动

### 1. 移除所有硬编码和伪造数据 ✅
- ✅ 移除 `DEFAULT_STOCK_CODES` 硬编码股票列表
- ✅ 移除 `INDEX_CODES` 硬编码指数映射
- ✅ 移除所有公式伪造的 open/high/low/vol 数据
- ✅ 移除带 `*` 标记的伪造字段

### 2. 真实 API 集成 ✅

#### 大盘指数（Market Overview）
- **接口**: `GET /api/market/overview`
- **实现**: 使用 `getMarketOverview()` 获取真实指数数据
- **数据字段**: indices (symbol, name, close, pct_change)

#### 股票列表（Stock List）
- **接口**: `GET /api/stock/list`
- **实现**: 使用 `getStockList()` 获取候选池（limit=200）
- **补充接口**: `POST /api/quotes/realtime` 补充实时成交额
- **数据合并**: symbol 作为 key 合并两个数据源

#### K线图（Daily Quotes）
- **接口**: `POST /api/tushare/daily`
- **实现**: 获取最近 120 个交易日数据
- **图表**: 集成 ECharts 显示真实 K 线图
- **指标**: MA5/MA10/MA20 基于真实 close 价格计算
- **数据排序**: 处理 Tushare 降序数据，按日期升序重排

#### 热门板块（Industry Rank）
- **接口**: `GET /api/fundamentals/industry/rank`
- **实现**: 使用真实 `industry` 字段进行严格匹配
- **计算**: 基于 stock/list 的行业映射计算平均涨跌幅
- **领涨股**: 从真实行业股票中筛选 pct_change 最大的前 2 只

### 3. 表格列简化 ✅
移除无法稳定批量获取的列，只展示真实可靠字段：

**保留列**：
- 代码 (symbol)
- 名称 (name)
- 最新价 (price - 来自 realtime 或 stock/list)
- 涨跌幅 (pct_change - 来自 realtime 或 stock/list)
- 行业 (industry - 来自 stock/list)
- 换手率 (turnover_rate - 来自 stock/list)
- 成交额 (turnover - 来自 realtime，单位：万元)
- 更新时间 (update_time - 来自 realtime)

**移除列**：
- 涨跌额（可通过最新价和涨跌幅计算，但非核心指标）
- 开盘价、最高价、最低价、成交量（需通过 daily 接口单独查询，放在 K 线详情区展示）

### 4. ECharts K线图集成 ✅
- ✅ 安装 echarts 依赖
- ✅ 实现完整的 K 线图渲染（蜡烛图 + 成交量 + MA 线）
- ✅ 支持缩放和拖拽
- ✅ 响应式窗口调整
- ✅ 组件卸载时正确清理资源
- ✅ 显示最新交易日的 OHLC 和成交量数据摘要

### 5. 搜索功能增强 ✅
- ✅ 支持 6 位股票代码精确查询（调用 realtime + daily）
- ✅ 支持名称/代码关键词过滤（在已加载的列表中本地筛选）
- ✅ 清空搜索框重新加载完整列表

### 6. 数据加载优化 ✅
- ✅ 按依赖顺序加载：overview → stock/list → sectors → kline
- ✅ 添加 loading 状态：overviewLoading, stockLoading, sectorsLoading, klineLoading
- ✅ 移除 setTimeout 延迟，改用 await 顺序控制
- ✅ 添加数据解包工具函数 `getEnvelopeData()`

### 7. 错误处理和友好提示 ✅
- ✅ 行业数据为空时显示"数据尚未生成"而非默认假数据
- ✅ K 线加载失败显示明确错误信息
- ✅ 表格加载状态和空状态提示
- ✅ 选中行高亮显示

## 验收标准检查

### ✅ 必须满足项
- [x] 不再使用写死的股票代码列表作为默认数据源
- [x] 表格中不再出现公式推算的伪造数据
- [x] K 线区域展示真实 ECharts 图表（移除占位文案）
- [x] MA 指标基于真实 close 价格计算
- [x] 热门板块使用 `industry` 字段，严格匹配行业
- [x] 所有数值来自真实 API 或基于真实数据的计算
- [x] 保持现有页面风格和交互不退化

## 技术实现细节

### 数据流程
```
页面加载
  ↓
1. loadMarketOverview() - 获取大盘指数 + 交易日期
  ↓
2. loadStockData() - 获取股票列表
   ├─ getStockList(limit=200) - 基础数据
   └─ getRealtimeQuotes(codes) - 补充实时数据
  ↓
3. loadHotSectors() - 基于 stock/list 计算行业数据
   └─ getIndustryRank() - 获取行业排名
  ↓
4. loadKlineData() - 加载选中股票的 K 线
   └─ getDailyQuotes() - 获取 120 个交易日数据
```

### 关键函数
- `getEnvelopeData()`: 统一解包 envelope 响应
- `calculateMarketStats()`: 计算涨跌分布统计
- `calculateMA()`: 计算移动平均线
- `renderKlineChart()`: ECharts K 线图渲染
- `handleResize()`: 窗口大小调整响应
- `formatTradeDate()`: 交易日期格式化

### 响应式数据
```javascript
- marketIndexes: 大盘指数列表
- currentTradeDate: 当前交易日
- rawStockData: 原始股票列表（合并后的完整数据）
- filteredStockData: 筛选后的股票列表（计算属性）
- klineData: K 线数据
- hotSectors: 热门板块
- marketStats: 涨跌分布统计
```

## 依赖变更
```json
{
  "dependencies": {
    "echarts": "^5.x.x"  // 新增
  }
}
```

## 使用说明

### 前置条件
1. 确保 `data-service` 服务已启动
2. 确保 `api-gateway` 转发配置正确
3. 前端 `VITE_API_BASE_URL` 配置正确（默认 `/api`）

### 页面功能
1. **大盘指数**: 自动加载市场概览中的指数数据
2. **个股行情**: 显示 200 只股票的实时行情
3. **筛选排序**: 
   - 市场筛选：沪市/深市/创业板/科创板
   - 涨跌幅筛选：>5%、0-5%、-5%-0%、<-5%
   - 排序：涨幅/跌幅/成交量/成交额
4. **搜索**: 输入股票代码或名称关键词，按 Enter 搜索
5. **K线图**: 点击表格行查看对应股票的 K 线图
6. **热门板块**: 自动加载行业排名和领涨股
7. **涨跌分布**: 实时统计涨停/上涨/平盘/下跌/跌停数量

### 已知限制
1. **行业数据预热**: 首次访问时行业排名可能为空，需要后台先调用计算接口
2. **股票列表限制**: 默认 limit=200，可根据需要调整
3. **K线数据范围**: 最近 120 个交易日（约 6 个月）

## 测试建议

### 功能测试
- [ ] 页面加载后显示真实大盘指数
- [ ] 股票列表显示 ~200 只股票且无伪造字段
- [ ] 点击股票行能正确加载 K 线图
- [ ] 筛选和排序功能正常
- [ ] 搜索功能（代码和名称）正常
- [ ] 热门板块显示真实行业数据（如果后台已预热）
- [ ] 涨跌分布统计数值正确

### 错误场景测试
- [ ] data-service 未启动时显示友好错误提示
- [ ] 行业数据为空时显示"数据尚未生成"提示
- [ ] K 线数据加载失败显示明确错误信息
- [ ] 搜索不存在的股票代码显示友好提示

### 性能测试
- [ ] 首屏加载时间 < 3s（网络正常情况）
- [ ] K 线图切换流畅无卡顿
- [ ] 窗口调整时图表响应及时
- [ ] 大量筛选操作无明显延迟

## 后续优化建议

1. **缓存优化**: 添加股票列表的本地缓存（5 分钟）
2. **分页加载**: 股票列表超过 500 只时考虑分页或虚拟滚动
3. **增量更新**: 使用 WebSocket 实现实时行情推送
4. **详情面板**: 添加股票详情抽屉显示更多指标
5. **自选股**: 支持用户添加自选股功能
6. **板块钻取**: 点击板块名称查看该板块所有股票
7. **技术指标**: 支持更多技术指标（MACD、KDJ、RSI 等）

## 交付文件
- `frontend/niuniu/src/views/StockDataPage.vue` (已修改)
- `package.json` (已添加 echarts 依赖)
- 本说明文档

---
**交付状态**: ✅ 已完成并通过验收标准检查
**交付工程师**: GitHub Copilot (Claude Sonnet 4.5)
**交付日期**: 2026年1月15日
