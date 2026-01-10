/**
 * 研报服务
 * 对接后端 /api/report/* 接口
 */
import http, { handleRequest } from './http'

/**
 * 获取研报列表
 * GET /api/report
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 每页数量
 * @param {number} params.offset - 偏移量
 * @param {string} params.status - 状态筛选
 * @param {string} params.stock_code - 股票代码
 * @param {string} params.keyword - 关键词搜索
 */
export const getReportList = async (params = {}) => {
  return handleRequest(() => http.get('/report', { params }))
}

/**
 * 获取研报摘要列表
 * GET /api/report/summaries/list
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 每页数量
 * @param {number} params.offset - 偏移量
 * @param {string} params.status - 状态筛选
 * @param {string} params.rating - 评级筛选 (buy/add/hold/reduce/sell)
 */
export const getReportSummaries = async (params = {}) => {
  return handleRequest(() => http.get('/report/summaries/list', { params }))
}

/**
 * 根据 ID 获取研报详情
 * GET /api/report/{report_id}
 * @param {number} reportId - 研报 ID
 */
export const getReportById = async (reportId) => {
  return handleRequest(() => http.get(`/report/${reportId}`))
}

/**
 * 创建研报
 * POST /api/report
 * @param {Object} data - 研报数据
 */
export const createReport = async (data) => {
  return handleRequest(() => http.post('/report', data))
}

/**
 * 更新研报
 * PUT /api/report/{report_id}
 * @param {number} reportId - 研报 ID
 * @param {Object} data - 更新数据
 */
export const updateReport = async (reportId, data) => {
  return handleRequest(() => http.put(`/report/${reportId}`, data))
}

/**
 * 删除研报
 * DELETE /api/report/{report_id}
 * @param {number} reportId - 研报 ID
 */
export const deleteReport = async (reportId) => {
  return handleRequest(() => http.delete(`/report/${reportId}`))
}

/**
 * 发布研报
 * POST /api/report/{report_id}/publish
 * @param {number} reportId - 研报 ID
 */
export const publishReport = async (reportId) => {
  return handleRequest(() => http.post(`/report/${reportId}/publish`))
}

/**
 * 归档研报
 * POST /api/report/{report_id}/archive
 * @param {number} reportId - 研报 ID
 */
export const archiveReport = async (reportId) => {
  return handleRequest(() => http.post(`/report/${reportId}/archive`))
}
