# Quant Engine - 量化引擎服务

量化牛牛（QuantBull）的量化引擎微服务，提供回测、因子库和策略执行功能。

## 🚀 功能特性

- **策略管理**: 创建、更新、删除和验证量化策略
- **回测引擎**: 执行策略回测，生成详细的回测报告
- **因子库**: 管理技术指标、基本面因子和宏观因子
- **因子计算**: 计算因子值，生成时间序列数据

## 📁 项目结构

```
quant-engine/
├── main.py                 # FastAPI 应用入口
├── run.py                  # 启动脚本
├── requirements.txt        # Python 依赖
├── Dockerfile             # Docker 配置
├── .gitignore             # Git 忽略文件
├── core/                   # 核心模块
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   └── logger.py          # 日志配置
├── routers/               # API 路由
│   ├── __init__.py
│   ├── backtest.py        # 回测路由
│   ├── strategy.py        # 策略路由
│   └── factor.py          # 因子路由
├── services/              # 业务逻辑层
│   ├── __init__.py
│   ├── backtest_service.py    # 回测服务
│   ├── strategy_service.py    # 策略服务
│   └── factor_service.py      # 因子服务
├── models/                # 数据模型
│   ├── __init__.py
│   ├── strategy.py        # 策略模型
│   └── factor.py          # 因子模型
└── schemas/               # Pydantic 模式（API 请求/响应）
    ├── __init__.py
    ├── backtest.py        # 回测模式
    ├── strategy.py        # 策略模式
    └── factor.py          # 因子模式
```

## 🛠️ 技术栈

- **Python 3.12+**
- **FastAPI** - 现代、快速的 Web 框架
- **Pydantic v2** - 数据验证和设置管理
- **Uvicorn** - ASGI 服务器

## 📦 安装和运行

### 本地开发

1. 安装依赖：
```bash
pip install -r requirements.txt
```

**注意**：如果 `data-service` 服务不可用，需要配置 Tushare token：
- 安装 tushare：`pip install tushare`（已在 requirements.txt 中）
- 在 `.env` 文件中设置 `TUSHARE_TOKEN=your_token`

2. 配置环境变量（可选）：
创建 `.env` 文件：
```env
ENV=local
LOG_LEVEL=INFO
PORT=8003
HOST=0.0.0.0
```

3. 启动服务：
```bash
python run.py
```

或使用 uvicorn：
```bash
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

### Docker 运行

```bash
docker build -t quant-engine .
docker run -p 8003:8003 quant-engine
```

## 📚 API 文档

启动服务后，访问：
- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

## 🔌 API 端点

### 策略管理
- `POST /api/strategy` - 创建策略
- `GET /api/strategy/{strategy_id}` - 获取策略
- `PUT /api/strategy/{strategy_id}` - 更新策略
- `DELETE /api/strategy/{strategy_id}` - 删除策略
- `GET /api/strategy` - 列出策略
- `POST /api/strategy/validate` - 验证策略代码

### 回测
- `POST /api/backtest/run` - 执行回测
- `GET /api/backtest/{backtest_id}` - 获取回测结果
- `GET /api/backtest` - 列出回测记录

### 因子管理
- `POST /api/factor` - 创建因子
- `GET /api/factor/{factor_id}` - 获取因子
- `PUT /api/factor/{factor_id}` - 更新因子
- `DELETE /api/factor/{factor_id}` - 删除因子
- `GET /api/factor` - 列出因子
- `POST /api/factor/calculate` - 计算因子值

## 📝 示例

### 创建策略
```bash
curl -X POST "http://localhost:8003/api/strategy" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "双均线策略",
    "description": "基于5日和20日均线的简单策略",
    "code": "class MyStrategy(bt.Strategy):\n    def next(self):\n        ...",
    "parameters": {"fast_period": 5, "slow_period": 20}
  }'
```

### 执行回测（使用内置策略）
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

### 执行回测（使用自定义策略）
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

**注意**：在 PowerShell 中，需要使用 `Invoke-RestMethod` 或转义 JSON：
```powershell
# PowerShell 方式 1：使用 Invoke-RestMethod
$body = @{
    stock_code = "000001"
    start_date = "2022-01-01"
    end_date = "2023-01-01"
    strategy_mode = "builtin"
    strategy_name = "ma_cross"
    data_source = "tushare"
    enable_ai_review = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8003/api/backtest/run" -Method Post -Body $body -ContentType "application/json"

# PowerShell 方式 2：使用 curl.exe（Windows 10+）
curl.exe -X POST "http://localhost:8003/api/backtest/run" `
  -H "Content-Type: application/json" `
  -d '{\"stock_code\":\"000001\",\"start_date\":\"2022-01-01\",\"end_date\":\"2023-01-01\",\"strategy_mode\":\"builtin\",\"strategy_name\":\"ma_cross\",\"data_source\":\"tushare\",\"enable_ai_review\":true}'
```

### 计算因子
```bash
curl -X POST "http://localhost:8003/api/factor/calculate" \
  -H "Content-Type: application/json" \
  -d '{
    "factor_id": "factor_xxx",
    "symbol": "000001.SZ",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31"
  }'
```

## ⚠️ 注意事项

1. **回测服务已集成 Backtrader**：支持自定义策略（AI 生成）和内置策略（ma_cross、rsi）

2. **数据源**：
   - Tushare：通过 `data-service` API 或直接调用（需配置 token）
   - TDengine：计划中

3. **数据存储**：当前使用内存存储，生产环境应使用数据库持久化

4. **安全性**：自定义策略代码在受限环境中执行，但仍需注意安全

5. **性能优化**：大量回测任务应考虑使用任务队列（如 Celery）

6. **PowerShell 使用**：在 Windows PowerShell 中，建议使用 `Invoke-RestMethod` 或 `curl.exe`（Windows 10+）

## 🔄 后续开发

- [x] 集成 Backtrader 回测框架
- [ ] 连接 TDengine 获取历史行情数据（已实现接口，待实现具体逻辑）
- [ ] 实现真实的因子计算（RSI、MACD、MA 等）
- [ ] 添加数据库持久化（PostgreSQL）
- [ ] 实现异步任务队列
- [ ] 添加策略回测结果可视化
- [ ] 实现因子分析工具
- [ ] 改进净值曲线提取（使用 Backtrader Observer）

## 🧪 测试

### 快速测试

运行快速测试脚本检查服务是否可用：

```bash
python test_backtest_simple.py
```

### 完整测试

运行完整测试脚本（需要数据源可用）：

```bash
python test_backtest.py
```

测试脚本会：
1. 检查服务健康状态
2. 测试内置策略回测（ma_cross）
3. 测试自定义策略回测
4. 测试列出回测记录

**注意**：完整测试需要：
- `data-service` 服务运行，或
- 配置了 `TUSHARE_TOKEN` 环境变量

## 🔧 故障排除

### 502 Bad Gateway 错误

如果遇到 502 错误，通常是因为服务未正确启动。使用以下脚本修复：

**PowerShell:**
```powershell
# 方法 1：使用修复脚本（推荐）
.\restart_service.ps1

# 方法 2：使用诊断脚本
.\check_service.ps1
```

**手动修复:**
```powershell
# 1. 停止占用端口的进程
$pid = (Get-NetTCPConnection -LocalPort 8003).OwningProcess
Stop-Process -Id $pid -Force

# 2. 重新启动服务
python run.py
```

### 端口被占用

如果端口 8003 被占用：

```powershell
# 查看占用端口的进程
netstat -ano | findstr :8003

# 停止进程（替换 PID 为实际进程ID）
taskkill /F /PID <进程ID>

# 或修改端口（在 .env 文件中）
PORT=8004
```

## 📄 许可证

MIT License
