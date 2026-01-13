/**
 * 策略服务
 * 对接后端 /api/strategy/* 接口
 */
import http, { handleRequest } from './http'

/**
 * 获取策略列表
 * GET /api/strategy
 * @param {Object} params - 查询参数
 * @param {string} params.status - 状态筛选
 * @param {string} params.search - 搜索关键词
 * @param {number} params.limit - 每页数量
 * @param {number} params.offset - 偏移量
 */
export const getStrategies = async (params = {}) => {
  return handleRequest(() => 
    http.get('/strategy', {
      params: {
        status: params.status,
        search: params.search,
        limit: params.limit,
        offset: params.offset
      }
    })
  )
}

/**
 * 获取策略详情
 * GET /api/strategy/{id}
 * @param {number} id - 策略 ID
 */
export const getStrategy = async (id) => {
  return handleRequest(() => http.get(`/strategy/${id}`))
}

/**
 * 创建策略
 * POST /api/strategy
 * @param {Object} strategyData - 策略数据
 */
export const createStrategy = async (strategyData) => {
  return handleRequest(() => http.post('/strategy', strategyData))
}

/**
 * 更新策略
 * PUT /api/strategy/{id}
 * @param {number} id - 策略 ID
 * @param {Object} updateData - 更新数据
 */
export const updateStrategy = async (id, updateData) => {
  return handleRequest(() => http.put(`/strategy/${id}`, updateData))
}

/**
 * 删除策略
 * DELETE /api/strategy/{id}
 * @param {number} id - 策略 ID
 */
export const deleteStrategy = async (id) => {
  return handleRequest(() => http.delete(`/strategy/${id}`))
}

/**
 * 验证策略代码
 * POST /api/strategy/validate
 * @param {string} code - 策略代码
 */
export const validateStrategyCode = async (code) => {
  return handleRequest(() => http.post('/strategy/validate', { code }))
}

/**
 * 获取策略回测历史
 * GET /api/backtest
 * @param {number} strategyId - 策略 ID
 */
export const getStrategyBacktests = async (strategyId) => {
  return handleRequest(() => 
    http.get('/backtest', { params: { strategy_id: strategyId } })
  )
}

/**
 * 运行策略回测
 * POST /api/backtest/run
 * @param {number} strategyId - 策略 ID
 * @param {Object} backtestParams - 回测参数
 */
export const runBacktest = async (strategyId, backtestParams) => {
  return handleRequest(() => 
    http.post('/backtest/run', {
      ...backtestParams,
      strategy_id: strategyId
    })
  )
}

/**
 * 生成策略模板（AI 生成）
 * POST /api/ai/generate/strategy
 * @param {string} templateType - 模板类型描述
 */
export const generateStrategyTemplate = async (templateType) => {
  return handleRequest(() => 
    http.post('/ai/generate/strategy', {
      user_description: `Generate a ${templateType} strategy template`,
      framework: 'backtrader'
    })
  )
}

/**
 * 获取内置策略列表
 * GET /api/strategy/builtin
 */
export const getBuiltinStrategies = async () => {
  return handleRequest(() => http.get('/strategy/builtin'))
}

/**
 * 获取策略示例代码
 * GET /api/strategy/examples
 */
export const getStrategyExamples = async () => {
  return handleRequest(() => http.get('/strategy/examples'))
}

/**
 * AI 生成策略代码
 * POST /api/ai/generate/strategy
 * @param {Object} data - 请求数据
 * @param {string} data.user_description - 策略描述
 * @param {string} data.framework - 框架类型
 */
export const generateStrategyCode = async (data) => {
  return handleRequest(() => http.post('/ai/generate/strategy', data))
}