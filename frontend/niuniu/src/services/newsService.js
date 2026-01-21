/**
 * 财经新闻服务
 * 
 * 数据来源：东方财富网
 * 注意：旧的微博接口方法已保留以保持兼容，但内部已改为调用东方财富网接口
 */
import http from './http'

/**
 * 获取东方财富网最新财经新闻（推荐使用）
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回的最大条数，默认 20
 * @param {string} params.keyword - 关键词过滤（可选）
 * @returns {Promise<Object>} 新闻列表响应
 */
export async function getEastmoneyLatestNews(params = {}) {
  const { limit = 20, keyword } = params
  const queryParams = new URLSearchParams()
  
  queryParams.append('limit', limit)
  if (keyword) {
    queryParams.append('keyword', keyword)
  }
  
  return http.get(`/news/eastmoney/latest?${queryParams.toString()}`)
}

/**
 * 获取东方财富网历史新闻（从数据库）
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回的最大条数，默认 20
 * @param {string} params.keyword - 关键词过滤（可选）
 * @param {number} params.hours - 查询最近多少小时的数据，默认 24
 * @returns {Promise<Object>} 新闻列表响应
 */
export async function getEastmoneyHistoryNews(params = {}) {
  const { limit = 20, keyword, hours = 24 } = params
  const queryParams = new URLSearchParams()
  
  queryParams.append('limit', limit)
  queryParams.append('hours', hours)
  if (keyword) {
    queryParams.append('keyword', keyword)
  }
  
  return http.get(`/news/eastmoney/history?${queryParams.toString()}`)
}

/**
 * 【已弃用】获取微博财经媒体聚合新闻
 * @deprecated 请使用 getEastmoneyLatestNews 替代
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回的最大条数，默认 20
 * @param {string} params.keyword - 关键词过滤（可选）
 * @returns {Promise<Object>} 新闻列表响应
 */
export async function getWeiboMediaNews(params = {}) {
  // 内部转发到东方财富网接口，保持向后兼容
  return getEastmoneyLatestNews(params)
}

/**
 * 【已弃用】获取微博历史新闻
 * @deprecated 请使用 getEastmoneyHistoryNews 替代
 * @param {Object} params - 查询参数
 * @returns {Promise<Object>} 新闻列表响应
 */
export async function getWeiboHistoryNews(params = {}) {
  // 内部转发到东方财富网接口，保持向后兼容
  return getEastmoneyHistoryNews(params)
}

/**
 * 获取财经头条列表（分页）
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码，从 1 开始，默认 1
 * @param {number} params.page_size - 每页条数，默认 10
 * @param {string} params.keyword - 关键词过滤（可选）
 * @returns {Promise<Object>} 头条列表响应
 */
export async function getHeadlines(params = {}) {
  const { page = 1, page_size = 10, keyword } = params
  const queryParams = new URLSearchParams()
  
  queryParams.append('page', page)
  queryParams.append('page_size', page_size)
  if (keyword) {
    queryParams.append('keyword', keyword)
  }
  
  return http.get(`/news/headlines?${queryParams.toString()}`)
}

/**
 * 获取热点聚焦列表
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回的最大条数，默认 8
 * @returns {Promise<Object>} 热点列表响应
 */
export async function getHotHeadlines(params = {}) {
  const { limit = 8 } = params
  const queryParams = new URLSearchParams()
  
  queryParams.append('limit', limit)
  
  return http.get(`/news/headlines/hot?${queryParams.toString()}`)
}

/**
 * 获取财经头条详情
 * @param {number} id - 新闻 ID
 * @returns {Promise<Object>} 头条详情响应
 */
export async function getHeadlineDetail(id) {
  return http.get(`/news/headlines/${id}`)
}

/**
 * 创建财经头条（管理员）
 * @param {Object} payload - 创建请求
 * @param {string} payload.title - 标题（必填，1-200字符）
 * @param {string} payload.summary - 摘要（必填，1-500字符）
 * @param {string[]} payload.tags - 标签数组（可选）
 * @param {string} payload.content - 正文（可选）
 * @param {string} payload.source - 来源（可选，默认"手动添加"）
 * @param {string} payload.url - 原文链接（可选）
 * @param {boolean} payload.is_hot - 是否热点（可选，默认false）
 * @returns {Promise<Object>} 创建的头条详情
 */
export async function createHeadline(payload) {
  return http.post('/news/headlines', payload)
}

/**
 * 更新财经头条（管理员）
 * @param {number} id - 新闻 ID
 * @param {Object} payload - 更新请求
 * @param {string} payload.title - 标题（可选）
 * @param {string} payload.summary - 摘要（可选）
 * @param {string[]} payload.tags - 标签数组（可选）
 * @param {string} payload.content - 正文（可选）
 * @param {boolean} payload.is_hot - 是否热点（可选）
 * @returns {Promise<Object>} 更新后的头条详情
 */
export async function updateHeadline(id, payload) {
  return http.put(`/news/headlines/${id}`, payload)
}

/**
 * 删除财经头条（管理员）
 * @param {number} id - 新闻 ID
 * @returns {Promise<Object>} 删除结果
 */
export async function deleteHeadline(id) {
  return http.delete(`/news/headlines/${id}`)
}

/**
 * AI 生成今日财经头条（管理员）
 * @param {Object} payload - 生成请求
 * @param {number} payload.limit - 生成数量，默认 10
 * @param {number} payload.hours - 源新闻时间范围（小时），默认 24
 * @param {boolean} payload.force - 是否强制重新生成，默认 false
 * @returns {Promise<Object>} 生成结果
 */
export async function generateDailyHeadlines(payload = {}) {
  return http.post('/news/headlines/generate_daily', {
    limit: payload.limit || 10,
    hours: payload.hours || 24,
    force: payload.force || false
  })
}

export default {
  getEastmoneyLatestNews,
  getEastmoneyHistoryNews,
  getWeiboMediaNews,  // 保留旧方法名，兼容现有调用
  getWeiboHistoryNews,
  getHeadlines,
  getHotHeadlines,
  getHeadlineDetail,
  createHeadline,
  updateHeadline,
  deleteHeadline,
  generateDailyHeadlines
}
