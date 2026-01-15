# 因子管理模块交付文档

## 模块概述

因子管理模块是量化交易平台的核心功能之一，用于创建、管理和计算量化因子。因子可被策略引用，用于生成交易信号。

## 功能特性

### 1. 因子列表展示
- **服务端分页**: 支持大规模因子数据的高效加载
- **类别筛选**: 按技术指标、基本面因子、宏观因子分类筛选
- **关键词搜索**: 支持按名称、代码、描述进行模糊搜索（带防抖）
- **快捷操作**: 查看详情、编辑、删除、计算

### 2. 因子创建
- **基本信息**: 名称、代码（自动生成唯一标识）、类别、描述
- **表达式编辑**: 支持 pandas.eval 语法的因子表达式
- **表达式验证**: 实时验证表达式语法和有效性
- **模板应用**: 快速插入常用因子模板
- **参数配置**: JSON 格式的因子参数

### 3. 因子计算
- **时间范围选择**: 自定义开始和结束日期
- **股票代码输入**: 指定计算标的
- **结果可视化**: 图表展示因子时间序列
- **统计数据**: 均值、标准差等统计指标
- **数据导出**: 详细数据表格展示

### 4. 因子与策略关联
- **因子选择器**: 在策略创建时选择关联因子
- **多因子支持**: 策略可关联多个因子
- **类别过滤**: 按类别筛选可用因子

## API 接口

### 因子列表
```
GET /api/factor?category=technical&search=MA&limit=20&offset=0
```

### 创建因子
```
POST /api/factor
{
  "name": "20日均线偏离度",
  "code": "MA20_DEV",
  "category": "technical",
  "description": "收盘价相对20日均线的偏离程度",
  "expression": "(close - MA_20) / MA_20",
  "data_source": "tushare",
  "parameters": {}
}
```

### 验证表达式
```
POST /api/factor/validate
{
  "expression": "(close - MA_20) / MA_20"
}
```

响应:
```json
{
  "valid": true,
  "expression": "(close - MA_20) / MA_20",
  "errors": [],
  "warnings": ["表达式使用了以下列: MA_20, close"],
  "suggested_fix": null
}
```

### 计算因子
```
POST /api/factor/calculate
{
  "factor_id": "uuid",
  "symbol": "000001.SZ",
  "start_date": "2024-01-01",
  "end_date": "2024-06-30"
}
```

## 表达式语法

### 支持的列名
因子表达式支持以下预定义列名：

**价格数据:**
- `open`, `high`, `low`, `close`, `volume`
- `pre_close`, `change`, `pct_chg`, `amount`

**均线指标:**
- `MA_5`, `MA_10`, `MA_20`, `MA_60`, `MA_120`, `MA_250`
- `EMA_12`, `EMA_26`

**技术指标:**
- `RSI_6`, `RSI_12`, `RSI_14`
- `MACD`, `MACD_signal`, `MACD_hist`
- `BOLL_upper`, `BOLL_mid`, `BOLL_lower`
- `KDJ_K`, `KDJ_D`, `KDJ_J`
- `ATR_14`, `CCI_14`
- `OBV`, `VOLUME_MA_5`, `VOLUME_MA_20`

### 表达式示例
```python
# 均线偏离度
(close - MA_20) / MA_20

# RSI 超卖信号
RSI_14

# MACD 金叉判断
MACD - MACD_signal

# 布林带位置
(close - BOLL_lower) / (BOLL_upper - BOLL_lower)

# 多因子组合
(RSI_14 / 100 + (close - MA_20) / MA_20) / 2
```

## 数据模型

### Factor 模型
```python
class Factor:
    id: str          # UUID 主键
    code: str        # 因子代码 (唯一标识，如 "F1A2B3C4")
    name: str        # 因子名称
    description: str # 因子描述
    expression: str  # 因子表达式
    data_source: str # 数据源 (tushare/akshare/custom)
    category: str    # 类别 (technical/fundamental/macro)
    formula: str     # 公式说明
    parameters: dict # 参数配置
    created_at: datetime
    updated_at: datetime
```

## 前端组件

### 页面路由
- `/factors` - 因子列表页
- `/factors/create` - 创建因子页
- `/factors/:id` - 因子详情页
- `/factors/:id/edit` - 编辑因子页

### 状态管理 (Pinia Store)
```javascript
// stores/factor.js
state: {
  factors: [],      // 因子列表
  total: 0,         // 总数
  currentFactor: null,
  loading: false,
  error: null,
  validationResult: null
}

actions: {
  fetchFactors(params),
  fetchFactor(id),
  createNewFactor(data),
  updateExistingFactor(id, data),
  removeFactor(id),
  calculateFactorValue(factorId, params),
  validateExpression(expression)
}
```

## 测试用例

### 后端测试
```bash
# 运行因子模块测试
python -m pytest test_factor.py -v
```

### 测试场景
1. 创建因子 - 验证必填字段、表达式格式
2. 列表查询 - 验证分页、搜索、筛选
3. 表达式验证 - 验证语法检查、危险代码检测
4. 因子计算 - 验证数据加载、计算结果

## 部署说明

### 环境变量
```
DATABASE_URL=postgresql://user:pass@host:5432/quantbull
TUSHARE_TOKEN=your_token
```

### 数据库迁移
```sql
-- 添加 code 和 updated_at 字段
ALTER TABLE factor ADD COLUMN code VARCHAR(20);
ALTER TABLE factor ADD COLUMN updated_at TIMESTAMP;

-- 为现有记录生成 code
UPDATE factor SET code = 'F' || substring(md5(random()::text) from 1 for 6) WHERE code IS NULL;
```

## 已知限制

1. 表达式仅支持 pandas.eval 语法，不支持完整 Python 语法
2. 因子计算需要有效的 Tushare 数据订阅
3. 大规模回测时因子计算可能较慢

## 后续计划

- [ ] 因子回测功能
- [ ] 因子相关性分析
- [ ] 因子 IC/IR 评估
- [ ] 自定义数据源支持
- [ ] 因子版本管理
