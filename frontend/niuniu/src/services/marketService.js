/**
 * 市场数据服务
 * 对接后端 /api/quotes/*, /api/tushare/*, /api/market/* 接口
 */
import http, { handleRequest } from './http'

/**
 * 获取实时行情
 * POST /api/quotes/realtime
 * @param {Object} data - 请求数据
 * @param {string[]} data.codes - 股票代码列表
 */
export const getRealtimeQuotes = async (codes) => {
  return handleRequest(() => 
    http.post('/quotes/realtime', { codes })
  )
}

/**
 * 获取日线行情
 * POST /api/tushare/daily
 * @param {Object} data - 请求数据
 * @param {string[]} data.codes - 股票代码列表（6位格式）
 * @param {string} data.start_date - 开始日期 YYYYMMDD
 * @param {string} data.end_date - 结束日期 YYYYMMDD
 */
export const getDailyQuotes = async (data) => {
  return handleRequest(() => http.post('/tushare/daily', data))
}

/**
 * 获取股票基础信息
 * GET /api/tushare/stock_basic
 * @param {string} tsCode - 股票代码（可选）
 */
export const getStockBasic = async (tsCode) => {
  const params = tsCode ? { ts_code: tsCode } : {}
  return handleRequest(() => http.get('/tushare/stock_basic', { params }))
}

/**
 * 获取 ETF 日线行情
 * POST /api/tushare/fund_daily
 * @param {Object} data - 请求数据
 */
export const getFundDaily = async (data) => {
  return handleRequest(() => http.post('/tushare/fund_daily', data))
}

/**
 * 获取市场概览
 * GET /api/market/overview
 * @param {string} date - 日期（可选）
 */
export const getMarketOverview = async (date) => {
  const params = date ? { date } : {}
  return handleRequest(() => http.get('/market/overview', { params }))
}

/**
 * 获取 ETF 列表
 * GET /api/etf/list
 * @param {Object} params - 查询参数
 */
export const getETFList = async (params = {}) => {
  return handleRequest(() => http.get('/etf/list', { params }))
}

/**
 * 获取股票列表
 * GET /api/stock/list
 * @param {Object} params - 查询参数
 */
export const getStockList = async (params = {}) => {
  return handleRequest(() => http.get('/stock/list', { params }))
}

/**
 * 获取股票快照列表（聚合接口，DB 侧整合）
 * GET /api/stock/snapshot
 * @param {Object} params - 查询参数
 * @param {string} params.date - 交易日期 YYYY-MM-DD（可选）
 * @param {number} params.limit - 返回数量（默认 200）
 * @param {number} params.min_turnover - 最小成交额（元）
 * @param {string} params.sort - 排序方式：rise/fall/amount/volume
 * @param {boolean} params.refresh - 是否触发数据刷新
 */
export const getStockSnapshotList = async (params = {}) => {
  return handleRequest(() => http.get('/stock/snapshot', { params }))
}

/**
 * 批量获取股票基本面数据
 * POST /api/fundamentals/batch
 * @param {Object} data - 请求数据
 * @param {string[]} data.codes - 股票代码列表（6位格式）
 */
export const getFundamentalsBatch = async (codes) => {
  return handleRequest(() => 
    http.post('/fundamentals/batch', { codes })
  )
}

/**
 * 获取行业排名
 * GET /api/fundamentals/industry/rank
 * @param {Object} params - 查询参数
 */
export const getIndustryRank = async (params = {}) => {
  return handleRequest(() => http.get('/fundamentals/industry/rank', { params }))
}

/**
 * 股票代码转换工具
 * 将6位数字代码转换为 Tushare 格式
 * @param {string} code - 6位股票代码
 * @returns {string} Tushare 格式代码
 */
export const convertToTsCode = (code) => {
  if (!code || code.length !== 6) return code
  // 根据股票代码判断交易所
  const prefix = code.substring(0, 1)
  if (['6'].includes(prefix)) {
    return `${code}.SH` // 上海
  } else if (['0', '3', '2'].includes(prefix)) {
    return `${code}.SZ` // 深圳
  } else if (['4', '8'].includes(prefix)) {
    return `${code}.BJ` // 北京
  }
  return code
}

/**
 * 批量转换股票代码
 * @param {string[]} codes - 6位股票代码列表
 * @returns {string[]} Tushare 格式代码列表
 */
export const convertToTsCodes = (codes) => {
  return codes.map(convertToTsCode)
}

/**
 * 获取龙虎榜数据
 * GET /api/tushare/top_list
 * @param {string} tradeDate - 交易日期 YYYYMMDD
 */
export const getTopList = async (tradeDate) => {
  return handleRequest(() => 
    http.get('/tushare/top_list', { params: { trade_date: tradeDate } })
  )
}

/**
 * 获取龙虎榜机构交易明细
 * GET /api/tushare/top_inst
 * @param {string} tradeDate - 交易日期 YYYYMMDD
 */
export const getTopInst = async (tradeDate) => {
  return handleRequest(() => 
    http.get('/tushare/top_inst', { params: { trade_date: tradeDate } })
  )
}

/**
 * 获取最近N个交易日的龙虎榜汇总
 * GET /api/tushare/top_list_summary
 * @param {number} days - 天数（1, 5, 20）
 * @returns {Promise} 龙虎榜汇总数据
 */
export const getTopListSummary = async (days = 1) => {
  return handleRequest(() => 
    http.get('/tushare/top_list_summary', { params: { days } })
  )
}
