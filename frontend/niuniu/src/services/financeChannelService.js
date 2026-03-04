/**
 * 宏微观数据数据服务
 * 
 * 对接后端宏微观数据 API
 */
import http from './http'

/**
 * 获取市场数据（指数行情）
 * @returns {Promise<Object>} 市场数据响应
 */
export async function getMarketData() {
  return http.get('/finance-channel/market')
}


/**
 * 获取投资观点
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回条数，默认 10
 * @param {string} params.keyword - 关键词过滤（可选）
 * @param {number} params.page - 页码，默认 1
 * @returns {Promise<Object>} 观点数据响应
 */
export async function getIdeas(params = {}) {
  const { limit = 10, keyword, page = 1 } = params
  const queryParams = new URLSearchParams()
  
  queryParams.append('limit', limit)
  queryParams.append('page', page)
  if (keyword) queryParams.append('keyword', keyword)
  
  return http.get(`/finance-channel/ideas?${queryParams.toString()}`)
}

/**
 * 获取政策法规
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回条数，默认 10
 * @param {string} params.keyword - 关键词过滤（可选）
 * @param {number} params.page - 页码，默认 1
 * @returns {Promise<Object>} 政策数据响应
 */
export async function getPolicies(params = {}) {
  const { limit = 10, keyword, page = 1 } = params
  const queryParams = new URLSearchParams()
  
  queryParams.append('limit', limit)
  queryParams.append('page', page)
  if (keyword) queryParams.append('keyword', keyword)
  
  return http.get(`/finance-channel/policies?${queryParams.toString()}`)
}

/**
 * 获取宏微观数据综合数据（一次性获取所有模块）
 * @param {Object} params - 查询参数
 * @param {string} params.keyword - 新闻/观点/政策的关键词过滤（可选）
 * @param {number} params.limit - 各模块返回条数，默认 10
 * @returns {Promise<Object>} 综合数据响应
 */
export async function getFinanceChannelOverview(params = {}) {
  const { keyword, limit = 10 } = params
  const queryParams = new URLSearchParams()
  
  queryParams.append('limit', limit)
  if (keyword) queryParams.append('keyword', keyword)
  
  return http.get(`/finance-channel/overview?${queryParams.toString()}`)
}

export default {
  getMarketData,
  getIdeas,
  getPolicies,
  getFinanceChannelOverview
}
