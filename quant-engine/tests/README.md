# Quant Engine 测试文档

本目录包含 quant-engine 模块的测试用例。

## 测试结构

```
tests/
├── __init__.py
├── conftest.py          # Pytest 配置和共享 fixtures
├── test_api.py          # API 端点测试
├── test_services.py     # 服务层测试
├── test_utils.py        # 测试工具函数
├── pytest.ini          # Pytest 配置文件
└── README.md           # 本文档
```

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
# 运行 API 测试
pytest tests/test_api.py

# 运行服务层测试
pytest tests/test_services.py
```

### 运行特定测试类或函数

```bash
# 运行特定测试类
pytest tests/test_api.py::TestHealthCheck

# 运行特定测试函数
pytest tests/test_api.py::TestHealthCheck::test_root_endpoint
```

### 显示详细输出

```bash
pytest -v
```

### 显示覆盖率

```bash
# 需要安装 pytest-cov
pip install pytest-cov

# 运行测试并显示覆盖率
pytest --cov=. --cov-report=html
```

## 测试说明

### 1. API 端点测试 (test_api.py)

测试所有 FastAPI 端点：
- 健康检查端点 (`/`, `/health`)
- 策略管理端点 (`/api/strategy/*`)
- 回测端点 (`/api/backtest/*`)

**注意**：回测测试可能需要数据服务，部分测试可能被跳过或需要 mock。

### 2. 服务层测试 (test_services.py)

测试业务逻辑层：
- `StrategyService`: 策略管理服务
- `BacktestService`: 回测服务

**注意**：回测服务测试使用模拟数据，避免依赖外部服务。

### 3. 测试工具 (test_utils.py)

提供测试辅助函数：
- `create_mock_market_data()`: 生成模拟行情数据
- `mock_httpx_response()`: 创建模拟 HTTP 响应

## 测试数据

测试使用模拟数据，不依赖：
- 外部数据服务（data-service）
- Tushare API
- TDengine 数据库

这确保了测试的独立性和可重复性。

## 注意事项

1. **回测测试**：部分回测测试需要 mock 数据加载服务，因为实际执行需要真实的市场数据。

2. **异步测试**：服务层测试使用 `pytest-asyncio`，确保异步函数正确测试。

3. **测试隔离**：每个测试都是独立的，不依赖其他测试的状态。

4. **模拟数据**：使用固定随机种子确保测试结果可重复。

## 持续集成

建议在 CI/CD 流程中运行测试：

```yaml
# 示例 GitHub Actions 配置
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ -v
```

## 扩展测试

添加新测试时：
1. 遵循命名约定：`test_*.py` 文件，`test_*` 函数
2. 使用 fixtures 共享测试数据
3. Mock 外部依赖
4. 保持测试独立和可重复
