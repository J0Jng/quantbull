# 策略管理功能交付说明

## 改动文件清单

### 后端文件
1. **quant-engine/services/strategy_examples.py** (新建)
   - 提供离线可用的策略示例代码
   - 包含 4 个常用策略示例

2. **quant-engine/services/strategy_service.py** (修改)
   - 增强 `validate_strategy()` 方法，使用 AST 静态分析
   - 添加 `get_strategy_examples()` 方法
   - 修改 `list_strategies()` 支持 search 参数

3. **quant-engine/routers/strategy.py** (修改)
   - 新增 `GET /api/strategy/examples` 接口
   - 修改 `GET /api/strategy` 接口支持 search 参数

### 前端文件
4. **frontend/niuniu/src/services/strategyService.js** (修改)
   - 新增 `getStrategyExamples()` API

5. **frontend/niuniu/src/views/StrategyListPage.vue** (修改)
   - 改为服务端分页
   - 支持实时搜索（debounce 300ms）
   - 改进状态筛选和错误处理

6. **frontend/niuniu/src/views/StrategyCreatePage.vue** (修改)
   - 新增示例代码下拉选择
   - 增强验证功能，调用实际 API
   - 新增 AI 生成策略对话框
   - 改进错误/警告展示

### 测试脚本
7. **test_strategy_backtest.py** (修改)
   - 新增策略代码验证步骤
   - 修正因子创建逻辑

8. **test_strategy_workflow.py** (修改)
   - 修正 `bt.CrossOver` 为 `bt.indicators.CrossOver`
   - 新增验证步骤

---

## 新增/更新的接口说明

### 1. GET /api/strategy/examples
**功能**: 获取策略示例代码（离线可用）

**请求**: 无参数

**响应**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "ma_crossover",
        "name": "双均线交叉策略",
        "description": "经典的双均线交叉策略...",
        "code": "import backtrader as bt\n\nclass...",
        "default_parameters": {
          "fast_period": 10,
          "slow_period": 30
        }
      }
    ],
    "total": 4
  }
}
```

### 2. POST /api/strategy/validate (增强)
**功能**: 验证策略代码（AST 静态分析）

**请求**:
```json
{
  "code": "import backtrader as bt\n..."
}
```

**响应**:
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["建议在策略类中定义 __init__ 方法来初始化指标"],
  "message": "策略代码验证通过"
}
```

**验证规则**:
- ❌ 语法错误 → `valid=false` + errors（含行号）
- ❌ 缺少 `next()` 方法 → `valid=false` + errors
- ❌ 导入危险模块（os/sys/subprocess等） → `valid=false` + errors
- ❌ 调用危险函数（eval/exec/open等） → `valid=false` + errors
- ⚠️ 缺少 `__init__` → `valid=true` + warnings

### 3. GET /api/strategy (增强)
**功能**: 列出策略（支持搜索）

**请求参数**:
- `status`: 状态筛选（draft/active/archived）
- `search`: 搜索关键词（在 name/description 中搜索，不区分大小写）
- `limit`: 每页数量（默认 20）
- `offset`: 偏移量（默认 0）

**响应**:
```json
{
  "total": 50,
  "strategies": [...]
}
```

---

## 手动验收 UI 步骤

### 验收策略列表页

1. **启动服务并访问列表页**
   - 确保后端服务运行：`http://localhost:8000`
   - 前端访问：`http://localhost:5173/strategies`
   - ✅ 页面正常加载，显示策略列表或空状态

2. **测试搜索功能**
   - 在搜索框输入关键词（例如："均线"）
   - ✅ 输入后 300ms 自动触发搜索
   - ✅ 显示匹配的策略
   - ✅ 搜索框清空后显示全部

3. **测试筛选和分页**
   - 切换状态筛选（全部/活跃/非活跃）
   - ✅ 列表立即更新
   - ✅ 分页控件显示总页数和总条数
   - ✅ 点击"下一页"/"上一页"正常切换

4. **测试删除功能**
   - 点击某个策略的"删除"按钮
   - ✅ 弹出确认对话框
   - ✅ 确认后删除成功，列表自动刷新
   - ✅ 如果当前页为空，自动回退到上一页

5. **测试其他操作**
   - 点击"刷新"按钮 → ✅ 重新加载当前页
   - 点击"创建新策略" → ✅ 跳转到创建页
   - 点击策略名称 → ✅ 跳转到详情页

### 验收策略创建页

6. **测试示例代码插入**
   - 访问 `http://localhost:5173/strategies/create`
   - 点击"插入示例代码"下拉框
   - ✅ 显示 4 个示例（双均线/RSI/风控/仓位控制）
   - 选择一个示例 → ✅ 代码和参数自动填充
   - ✅ 自动触发验证，显示验证结果

7. **测试代码验证功能**
   - 输入错误代码（如 `import os`）
   - 点击"验证代码"
   - ✅ 显示红色错误提示：禁止导入危险模块 'os'
   - 修正代码后再验证 → ✅ 显示绿色通过提示

8. **测试 AI 生成功能**
   - 点击"AI生成"按钮
   - ✅ 弹出对话框
   - 输入策略描述：如"基于MACD的趋势策略"
   - 点击"生成策略"
   - ✅ 代码填充到编辑器
   - ✅ 自动触发验证

9. **测试提交限制**
   - 在代码中写入 `eval("test")`
   - 点击"创建策略"
   - ✅ 提示验证未通过，无法提交
   - 修正后 → ✅ 可以成功创建

10. **测试表单完整性**
    - 不填策略名称直接提交 → ✅ 提示必填
    - 代码少于 10 行 → ✅ 提示行数不足
    - JSON 参数格式错误 → ✅ 提示格式错误

---

## 运行脚本验收

### 前置条件
1. 后端服务运行：
   ```bash
   # 进入 quant-engine 目录
   cd quant-engine
   python -m uvicorn main:app --reload --port 8003
   
   # 或通过网关启动
   cd api-gateway
   python -m uvicorn main:app --reload --port 8000
   ```

2. 确保 PostgreSQL 数据库运行（如果使用数据库）

3. Python 环境已安装依赖：`requests`

### 运行测试脚本

**脚本 1: test_strategy_backtest.py**
```bash
cd f:\code\项目\quantbull
python test_strategy_backtest.py
```

**预期输出**:
```
🚀 开始测试策略创建和回测流程

============================================================
0. 测试登录
============================================================
...
✅ 登录成功！

============================================================
1. 创建因子（ma_10, ma_30）
============================================================
...
✅ 创建成功！因子ID: xxx

============================================================
1.5. 测试策略代码验证
============================================================
✅ 策略代码验证通过！

============================================================
2. 测试创建策略
============================================================
✅ 策略创建成功！策略ID: xxx

============================================================
3. 测试获取策略
============================================================
✅ 策略获取成功

...

============================================================
✅ 测试完成
============================================================
```

**脚本 2: test_strategy_workflow.py**
```bash
python test_strategy_workflow.py
```

**预期行为**:
- 验证步骤通过
- 策略创建成功
- 回测提交成功
- 轮询获取结果

### 失败排查

如果测试失败，检查：

1. **网络连接**: `curl http://localhost:8000/health`
2. **服务状态**: 查看后端日志
3. **数据库连接**: 检查 PostgreSQL 是否运行
4. **认证问题**: 确认 JWT token 正确返回
5. **依赖服务**: 确认 factor 服务可用（或使用 default factor_id）

---

## 验证安全检查

### 测试危险代码拦截

**测试 1: 导入 os 模块**
```python
code = """
import os
import backtrader as bt

class BadStrategy(bt.Strategy):
    def next(self):
        os.system('ls')
"""

# 预期: valid=false, errors=["第2行: 禁止导入危险模块 'os'"]
```

**测试 2: 调用 eval**
```python
code = """
import backtrader as bt

class BadStrategy(bt.Strategy):
    def next(self):
        result = eval("1+1")
"""

# 预期: valid=false, errors=["第5行: 禁止调用危险函数 'eval'"]
```

**测试 3: 缺少 next 方法**
```python
code = """
import backtrader as bt

class IncompleteStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SMA(self.data.close)
"""

# 预期: valid=false, errors=["策略类 IncompleteStrategy 缺少 next() 方法..."]
```

---

## 已知限制与后续优化

1. **因子依赖**: 当前策略创建需要 factor_ids，如果因子服务不可用，使用 `["default"]` 作为占位
2. **AI 生成**: 需要配置 DeepSeek/Qwen API Key，否则 AI 生成功能不可用
3. **编辑页**: StrategyEditPage.vue 未完全更新示例代码功能，但验证功能已增强
4. **数据库**: 策略存储使用 SQLite/PostgreSQL，确保数据库正常运行

---

## 总结

✅ **后端**: AST 静态验证 + 示例代码接口 + 搜索分页  
✅ **前端**: 服务端分页 + 示例插入 + AI 生成 + 增强验证  
✅ **测试**: 脚本增加验证步骤，确保代码通过检查

**核心改进**:
- 代码验证从简单字符串检查升级为 AST 静态分析
- 支持危险代码拦截（os/eval/exec等）
- 提供离线可用示例代码
- 服务端分页 + 实时搜索
- 错误/警告详细展示（含行号）

**可交付标准**:
- ✅ 用户可通过 UI 插入示例代码并一键验证
- ✅ 不能提交包含危险操作的策略代码
- ✅ 列表页支持搜索、筛选、分页
- ✅ 验证结果清晰可读，包含行号定位
