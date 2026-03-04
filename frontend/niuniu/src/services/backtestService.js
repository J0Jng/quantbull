/**
 * 回测服务
 * 对接后端 /api/backtest/* 接口
 */
import http, { handleRequest } from './http'

/**
 * 运行回测（自动选择同步/异步模式）
 * POST /api/backtest/run
 * @param {Object} data - 回测参数
 */
export const runBacktest = async (data) => {
  return handleRequest(() => http.post('/backtest/run', data))
}

/**
 * 同步运行回测（实时等待结果）
 * POST /api/backtest/run_sync
 * @param {Object} data - 回测参数
 */
export const runBacktestSync = async (data) => {
  return handleRequest(() => 
    http.post('/backtest/run_sync', data, { timeout: 120000 }) // 2分钟超时
  )
}

/**
 * 异步运行回测（返回任务ID）
 * POST /api/backtest/run_async
 * @param {Object} data - 回测参数
 */
export const runBacktestAsync = async (data) => {
  return handleRequest(() => http.post('/backtest/run_async', data))
}

/**
 * 获取回测结果
 * GET /api/backtest/{backtest_id}
 * @param {number} backtestId - 回测 ID
 */
export const getBacktestResult = async (backtestId) => {
  return handleRequest(() => http.get(`/backtest/${backtestId}`))
}

/**
 * 获取回测历史列表
 * GET /api/backtest
 * @param {Object} params - 查询参数
 * @param {number} params.strategy_id - 回测模型 ID
 * @param {number} params.limit - 每页数量
 * @param {number} params.offset - 偏移量
 */
export const getBacktestList = async (params = {}) => {
  return handleRequest(() => http.get('/backtest', { params }))
}
