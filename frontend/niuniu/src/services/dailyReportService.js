/**
 * 每日内参服务
 * 对接后端 /api/daily-report/* 接口
 */
import http, { handleRequest } from './http'

/**
 * 获取最新的每日报告
 * GET /api/daily-report/latest
 */
export const getLatestDailyReport = async () => {
  return handleRequest(() => http.get('/daily-report/latest'))
}

/**
 * 根据日期获取每日报告
 * GET /api/daily-report/date/{report_date}
 * @param {string} reportDate - 报告日期，格式 YYYY-MM-DD
 */
export const getDailyReportByDate = async (reportDate) => {
  return handleRequest(() => http.get(`/daily-report/date/${reportDate}`))
}

/**
 * 根据 ID 获取每日报告详情
 * GET /api/daily-report/{report_id}
 * @param {number} reportId - 报告 ID
 */
export const getDailyReportById = async (reportId) => {
  return handleRequest(() => http.get(`/daily-report/${reportId}`))
}

/**
 * 获取每日报告列表
 * GET /api/daily-report
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 每页数量
 * @param {number} params.offset - 偏移量
 * @param {string} params.start_date - 开始日期
 * @param {string} params.end_date - 结束日期
 */
export const getDailyReportList = async (params = {}) => {
  return handleRequest(() => http.get('/daily-report', { params }))
}

/**
 * 手动触发生成每日报告
 * POST /api/daily-report/generate
 * @param {Object} data - 生成参数
 * @param {string} data.report_date - 报告日期
 */
export const generateDailyReport = async (data) => {
  return handleRequest(() => http.post('/daily-report/generate', data))
}
