import { ref } from 'vue'

// 模拟策略数据
const strategies = ref([
  {
    id: 'STR001',
    name: '均线交叉策略',
    description: '基于5日均线和20日均线交叉的简单交易策略',
    status: 'active',
    code: `import backtrader as bt

class SimpleMovingAverage(bt.Strategy):
    params = (
        ('window', 20),
    )
    
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.window
        )
    
    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell()
    
    def stop(self):
        self.log(f'最终资产: {self.broker.getvalue():.2f}')`,
    parameters: {
      window: 20,
      threshold: 0.01,
      commission: 0.001
    },
    created_at: '2025-12-15T10:30:00Z',
    updated_at: '2025-12-20T14:25:00Z',
    creator: 'quant_user',
    operations: [
      {
        type: 'create',
        timestamp: '2025-12-15T10:30:00Z',
        user: 'quant_user',
        description: '创建策略'
      },
      {
        type: 'update',
        timestamp: '2025-12-20T14:25:00Z',
        user: 'quant_user',
        description: '优化交易逻辑'
      }
    ]
  }
])

// 模拟回测历史数据
const backtestHistory = ref({
  STR001: [
    {
      id: 'BT001',
      stock_code: '000001',
      start_date: '2025-01-01',
      end_date: '2025-12-01',
      status: 'completed',
      annual_return: 0.1543,
      sharpe_ratio: 1.23,
      max_drawdown: 0.1234
    }
  ]
})

// 获取策略列表
export const getStrategies = async (params = {}) => {
  try {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // 模拟筛选逻辑
    let result = [...strategies.value]
    
    if (params.status) {
      result = result.filter(strategy => strategy.status === params.status)
    }
    
    if (params.search) {
      const searchTerm = params.search.toLowerCase()
      result = result.filter(strategy => 
        strategy.name.toLowerCase().includes(searchTerm) ||
        strategy.description.toLowerCase().includes(searchTerm)
      )
    }
    
    return {
      success: true,
      data: result
    }
  } catch (error) {
    return {
      success: false,
      message: '获取策略列表失败: ' + error.message
    }
  }
}

// 获取策略详情
export const getStrategy = async (id) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 300))
    
    const strategy = strategies.value.find(s => s.id === id)
    if (!strategy) {
      throw new Error('策略不存在')
    }
    
    return {
      success: true,
      data: { ...strategy }
    }
  } catch (error) {
    return {
      success: false,
      message: '获取策略详情失败: ' + error.message
    }
  }
}

// 创建策略
export const createStrategy = async (strategyData) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 验证必填字段
    if (!strategyData.name || !strategyData.code) {
      throw new Error('策略名称和代码不能为空')
    }
    
    // 生成新ID
    const newId = 'STR' + (strategies.value.length + 1).toString().padStart(3, '0')
    
    const newStrategy = {
      id: newId,
      name: strategyData.name,
      description: strategyData.description || '',
      code: strategyData.code,
      parameters: strategyData.parameters || {},
      status: 'active',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      creator: 'current_user',
      operations: [
        {
          type: 'create',
          timestamp: new Date().toISOString(),
          user: 'current_user',
          description: '创建策略'
        }
      ]
    }
    
    strategies.value.push(newStrategy)
    
    return {
      success: true,
      data: newStrategy
    }
  } catch (error) {
    return {
      success: false,
      message: '创建策略失败: ' + error.message
    }
  }
}

// 更新策略
export const updateStrategy = async (id, updateData) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 700))
    
    const index = strategies.value.findIndex(s => s.id === id)
    if (index === -1) {
      throw new Error('策略不存在')
    }
    
    const updatedStrategy = {
      ...strategies.value[index],
      ...updateData,
      updated_at: new Date().toISOString()
    }
    
    // 添加操作记录
    updatedStrategy.operations.push({
      type: 'update',
      timestamp: new Date().toISOString(),
      user: 'current_user',
      description: '更新策略'
    })
    
    strategies.value[index] = updatedStrategy
    
    return {
      success: true,
      data: updatedStrategy
    }
  } catch (error) {
    return {
      success: false,
      message: '更新策略失败: ' + error.message
    }
  }
}

// 删除策略
export const deleteStrategy = async (id) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const index = strategies.value.findIndex(s => s.id === id)
    if (index === -1) {
      throw new Error('策略不存在')
    }
    
    strategies.value.splice(index, 1)
    
    return {
      success: true,
      message: '策略已删除'
    }
  } catch (error) {
    return {
      success: false,
      message: '删除策略失败: ' + error.message
    }
  }
}

// 验证策略代码
export const validateStrategyCode = async (code) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 简单验证逻辑
    const errors = []
    const lines = code.split('\n')
    
    if (lines.length < 10) {
      errors.push('代码行数不足10行')
    }
    
    if (!code.includes('class') || !code.includes('def')) {
      errors.push('代码中缺少必要的类和函数定义')
    }
    
    if (errors.length > 0) {
      return {
        success: false,
        message: '代码验证失败',
        errors
      }
    }
    
    return {
      success: true,
      message: '代码验证通过'
    }
  } catch (error) {
    return {
      success: false,
      message: '验证服务暂时不可用'
    }
  }
}

// 获取策略回测历史
export const getStrategyBacktests = async (strategyId) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const history = backtestHistory.value[strategyId] || []
    
    return {
      success: true,
      data: history
    }
  } catch (error) {
    return {
      success: false,
      message: '获取回测历史失败: ' + error.message
    }
  }
}

// 运行策略回测
export const runBacktest = async (strategyId, backtestParams) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    // 模拟回测结果
    const backtestId = 'BT' + (Object.values(backtestHistory.value).flat().length + 1).toString().padStart(3, '0')
    
    const newBacktest = {
      id: backtestId,
      strategy_id: strategyId,
      stock_code: backtestParams.stock_code || '000001',
      start_date: backtestParams.start_date || '2025-01-01',
      end_date: backtestParams.end_date || '2025-12-01',
      status: 'completed',
      annual_return: Math.random() * 0.3 - 0.1, // -10% 到 20%
      sharpe_ratio: Math.random() * 2,
      max_drawdown: Math.random() * 0.2,
      created_at: new Date().toISOString()
    }
    
    if (!backtestHistory.value[strategyId]) {
      backtestHistory.value[strategyId] = []
    }
    
    backtestHistory.value[strategyId].unshift(newBacktest)
    
    return {
      success: true,
      data: newBacktest
    }
  } catch (error) {
    return {
      success: false,
      message: '回测失败: ' + error.message
    }
  }
}

// 生成策略模板
export const generateStrategyTemplate = async (templateType) => {
  try {
    await new Promise(resolve => setTimeout(resolve, 600))
    
    let template = ''
    
    if (templateType === 'moving_average') {
      template = `import backtrader as bt

class SimpleMovingAverage(bt.Strategy):
    params = (
        ('window', 20),
    )
    
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.window
        )
    
    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell()
    
    def stop(self):
        self.log(f'最终资产: {self.broker.getvalue():.2f}')`
    } else if (templateType === 'rsi') {
      template = `import backtrader as bt

class RSIStrategy(bt.Strategy):
    params = (
        ('period', 14),
        ('upper', 70),
        ('lower', 30),
    )
    
    def __init__(self):
        self.rsi = bt.indicators.RSI(
            self.datas[0], period=self.params.period
        )
    
    def next(self):
        if not self.position:
            if self.rsi[0] < self.params.lower:
                self.buy()
        else:
            if self.rsi[0] > self.params.upper:
                self.sell()`
    }
    
    return {
      success: true,
      data: {
        code: template,
        parameters: templateType === 'moving_average' 
          ? { window: 20 } 
          : { period: 14, upper: 70, lower: 30 }
      }
    }
  } catch (error) {
    return {
      success: false,
      message: '生成模板失败: ' + error.message
    }
  }
}