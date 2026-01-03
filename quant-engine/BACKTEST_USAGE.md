# 回测服务使用指南

## 概述

`quant-engine` 的回测服务使用 Backtrader 执行量化策略回测，支持自定义策略（AI 生成）和内置策略。

## API 端点

### POST /api/backtest/run

执行回测

## 请求参数

```json
{
  "stock_code": "000001",           // 股票代码（6位，如：000001）
  "start_date": "2022-01-01",       // 开始日期（YYYY-MM-DD）
  "end_date": "2023-01-01",         // 结束日期（YYYY-MM-DD）
  
  "strategy_mode": "builtin",       // 策略模式：custom 或 builtin
  "strategy_name": "ma_cross",      // 内置策略名称（builtin 模式）
  "strategy_code": "",              // 策略代码（custom 模式）
  
  "data_source": "tushare",         // 数据源：tushare 或 tdengine
  
  "enable_ai_review": true,         // 是否启用 AI 评价数据
  
  // 可选参数
  "initial_cash": 1000000.0,        // 初始资金（默认：1,000,000）
  "commission": 0.001,              // 手续费率（默认：0.001）
  "slippage": 0.0,                  // 滑点（默认：0.0）
  "parameters": {}                  // 策略参数
}
```

## 响应格式

### 基础回测输出（始终返回）

```json
{
  "success": true,
  "backtest_id": "backtest_xxx",
  "metrics": {
    "initial_cash": 1000000.0,
    "final_value": 1180000.0,
    "total_return": 18.0,
    "annual_return": 18.0,
    "sharpe_ratio": 1.42,
    "max_drawdown": 5.5,
    "trading_days": 252
  },
  "daily_nav": [
    {"date": "2022-01-01", "nav": 1.0},
    {"date": "2022-01-02", "nav": 1.01},
    ...
  ],
  "ai_review": { ... }  // 如果 enable_ai_review=true
}
```

### AI 评价数据（enable_ai_review=true 时返回）

```json
{
  "ai_review": {
    "strategy_type": "trend_following",
    "holding_period_days_avg": 12.4,
    "trade_count": 86,
    "win_rate": 0.54,
    "profit_loss_ratio": 1.37,
    "volatility": 0.22,
    "max_consecutive_loss": 5,
    "drawdown_duration_days": 78,
    "return_over_drawdown": 0.86
  }
}
```

## 使用示例

### 1. 使用内置策略（双均线交叉）

```bash
curl -X POST "http://localhost:8003/api/backtest/run" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "000001",
    "start_date": "2022-01-01",
    "end_date": "2023-01-01",
    "strategy_mode": "builtin",
    "strategy_name": "ma_cross",
    "data_source": "tushare",
    "enable_ai_review": true,
    "parameters": {
      "fast_period": 5,
      "slow_period": 20
    }
  }'
```

### 2. 使用自定义策略（AI 生成）

```bash
curl -X POST "http://localhost:8003/api/backtest/run" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "000001",
    "start_date": "2022-01-01",
    "end_date": "2023-01-01",
    "strategy_mode": "custom",
    "strategy_code": "import backtrader as bt\n\nclass MyStrategy(bt.Strategy):\n    def next(self):\n        if not self.position:\n            if self.data.close[0] > self.data.close[-1]:\n                self.buy()\n        else:\n            if self.data.close[0] < self.data.close[-1]:\n                self.sell()",
    "data_source": "tushare",
    "enable_ai_review": true
  }'
```

### 3. 使用 RSI 策略

```bash
curl -X POST "http://localhost:8003/api/backtest/run" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_code": "000001",
    "start_date": "2022-01-01",
    "end_date": "2023-01-01",
    "strategy_mode": "builtin",
    "strategy_name": "rsi",
    "data_source": "tushare",
    "enable_ai_review": true,
    "parameters": {
      "rsi_period": 14,
      "rsi_low": 30,
      "rsi_high": 70
    }
  }'
```

## 内置策略

### ma_cross - 双均线交叉策略

参数：
- `fast_period`: 短期均线周期（默认：5）
- `slow_period`: 长期均线周期（默认：20）

策略逻辑：
- 短期均线上穿长期均线时买入
- 短期均线下穿长期均线时卖出

### rsi - RSI 策略

参数：
- `rsi_period`: RSI 周期（默认：14）
- `rsi_low`: RSI 低位阈值（默认：30）
- `rsi_high`: RSI 高位阈值（默认：70）

策略逻辑：
- RSI < 30 时买入（超卖）
- RSI > 70 时卖出（超买）

### legacy_turtle_trade - 海龟交易策略

参数：
- `threshold`: 回看周期（默认：60）
- `hold_bars`: 持仓周期（默认：10）
- `stop_loss`: 止损比例（可选）
- `take_profit`: 止盈比例（可选）

策略逻辑：
- 当日收盘价 >= 最近 N 日最高收盘价时买入
- 持有 hold_bars 根 K 线后卖出

### legacy_enter - 放量上涨策略

参数：
- `threshold`: 回看周期（默认：60）
- `hold_bars`: 持仓周期（默认：10）

策略逻辑：
- 当日涨幅 > 2% 且收盘价 > 开盘价
- 成交量 >= 5日均量的 2 倍
- 成交额 >= 2 亿

### legacy_keep_increasing - 持续上涨策略

参数：
- `threshold`: 回看周期（默认：30）
- `hold_bars`: 持仓周期（默认：10）

策略逻辑：
- 30日均线持续向上
- 当日 MA30 / 30日前 MA30 > 1.2

### legacy_backtrace_ma250 - 回踩年线策略

参数：
- `threshold`: 回看周期（默认：60）
- `hold_bars`: 持仓周期（默认：20）
- `stop_loss`: 止损比例（默认：0.08）
- `take_profit`: 止盈比例（默认：0.2）

策略逻辑：
- 前段由年线(250日)以下向上突破
- 后段在年线以上回踩，伴随缩量
- 需要至少 250+60 日历史数据

### legacy_low_atr - 低ATR成长策略

参数：
- `threshold`: 回看周期（默认：10）
- `hold_bars`: 持仓周期（默认：15）

策略逻辑：
- 最近 N 日的最高收盘价比最低收盘价高 1.1 倍
- ATR（平均波动率）< 10%

### legacy_low_backtrace - 低回撤上涨策略

参数：
- `threshold`: 回看周期（默认：60）
- `hold_bars`: 持仓周期（默认：15）

策略逻辑：
- 期间涨幅 > 50%
- 无单日跌幅超过 7%

### legacy_climax_limitdown - 地量跌停策略

参数：
- `threshold`: 回看周期（默认：60）
- `hold_bars`: 持仓周期（默认：5）

策略逻辑：
- 当日跌停（跌幅 >= 9.5%）
- 成交量萎缩（地量）
- 风险提示：逆势策略，风险较高

## 自定义策略要求

自定义策略代码必须：

1. 继承 `bt.Strategy`
2. 实现 `next()` 方法（每个 bar 执行）
3. 不访问网络、不写文件
4. 使用标准的 Backtrader API

示例：

```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    def __init__(self):
        # 初始化指标
        self.sma = bt.indicators.SMA(self.data.close, period=20)
    
    def next(self):
        # 策略逻辑
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell()
```

## AI 评价数据说明

当 `enable_ai_review=true` 时，返回的结构化数据可用于 LLM 评价。

这些数据将被传递给 `ai-hub` 服务，用于生成策略评价报告。

**注意**：`quant-engine` 只负责计算这些数据，不生成自然语言评价。

## 数据源

### Tushare

- 通过 `data-service` API 获取数据
- 如果 `data-service` 不可用，可配置 `TUSHARE_TOKEN` 直接调用 Tushare API

### TDengine

- 暂未实现，计划中

## 注意事项

1. **数据获取**：确保 `data-service` 服务运行或配置了 Tushare token
2. **策略代码安全**：自定义策略代码在受限环境中执行，但仍需注意安全
3. **回测时间**：长时间回测可能需要较长时间，建议设置合理的超时
4. **内存使用**：大量数据可能占用较多内存

## 错误处理

常见错误：

- `未获取到行情数据`：数据源不可用或股票代码错误
- `策略代码语法错误`：自定义策略代码有语法问题
- `内置策略不存在`：strategy_name 不正确

查看可用内置策略：

```bash
ls strategies/*.py
```

---

## 内设因子

quant-engine 启动时会自动初始化一批内设因子，可直接用于因子计算。

### 内设因子清单

| 因子名称 | expression | 说明 | 类别 |
|---------|-----------|------|------|
| rsi | rsi | 相对强弱指数 (14日) | momentum |
| rsi_6 | rsi_6 | 相对强弱指数 (6日) | momentum |
| rsi_12 | rsi_12 | 相对强弱指数 (12日) | momentum |
| rsi_24 | rsi_24 | 相对强弱指数 (24日) | momentum |
| macd | macd | MACD 线 | trend |
| macds | macds | MACD 信号线 | trend |
| macdh | macdh | MACD 柱状图 | trend |
| atr | atr | 平均真实波幅 (14日) | volatility |
| boll | boll | 布林带中轨 | volatility |
| boll_ub | boll_ub | 布林带上轨 | volatility |
| boll_lb | boll_lb | 布林带下轨 | volatility |
| kdjk | kdjk | KDJ K值 | momentum |
| kdjd | kdjd | KDJ D值 | momentum |
| kdjj | kdjj | KDJ J值 | momentum |
| wr_14 | wr_14 | 威廉指标 (14日) | momentum |
| cci | cci | 商品通道指数 (14日) | momentum |
| adx | adx | 平均趋向指数 | trend |
| vr | vr | 成交量变异率 | volume |
| obv | obv | 能量潮指标 | volume |
| roc | roc | 变动率指标 (12日) | momentum |
| psy | psy | 心理线指标 (12日) | sentiment |
| supertrend | supertrend | 超级趋势指标 | trend |

### 因子计算示例

```bash
# 计算 RSI_6 因子
curl -X POST "http://localhost:8003/api/factors/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "factor_id": "builtin_rsi_6",
    "symbol": "000001",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
  }'
```

### 自定义表达式

因子的 `expression` 支持简单的算术运算：

```json
{
  "name": "rsi_diff",
  "expression": "rsi_6 - rsi_12",
  "description": "RSI_6 与 RSI_12 的差值"
}
```

支持的运算符：`+`, `-`, `*`, `/`, `(`, `)`

---

## TA-Lib 安装说明

内设因子和 legacy 策略依赖 TA-Lib 库。

### Docker 构建（推荐）

Dockerfile 已包含 TA-Lib 安装，直接使用即可：

```bash
cd quant-engine
docker build -t quant-engine .
docker run -p 8003:8003 quant-engine
```

### Windows 本地安装

1. 下载预编译 wheel：
   - 访问 https://github.com/cgohlke/talib-build/releases
   - 下载对应 Python 版本的 wheel（如 `TA_Lib-0.4.28-cp312-cp312-win_amd64.whl`）

2. 安装：
   ```bash
   pip install TA_Lib-0.4.28-cp312-cp312-win_amd64.whl
   ```

### Linux 本地安装

```bash
# 下载并安装 TA-Lib C 库
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# 安装 Python 包
pip install ta-lib
```
