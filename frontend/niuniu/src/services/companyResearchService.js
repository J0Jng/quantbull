/**
 * 公司研报服务
 * 对接后端 /api/company-research/* 接口
 */
import http, { handleRequest } from './http'

/**
 * 生成公司研报并入库
 * POST /api/company-research/reports/generate
 * @param {Object} data - 生成请求数据
 * @param {string} data.company_name - 公司名称（必填）
 * @param {string} data.stock_code - 股票代码（可选）
 * @param {string} data.rating - 评级（buy/add/hold/reduce/sell，默认 hold）
 * @param {string} data.company_info - 公司基本信息（可空，为空时自动构造）
 * @param {string} data.report_type - 报告类型（summary/analysis，默认 summary）
 * @param {boolean} data.include_risks - 是否包含风险提示（默认 true）
 * @param {string[]} data.tags - 标签列表（可选）
 * @param {boolean} data.force - 是否强制重新生成（默认 false）
 */
export const generateCompanyResearch = async (data) => {
  return handleRequest(() => http.post('/company-research/reports/generate', data))
}

/**
 * 查询公司研报列表
 * GET /api/company-research/reports
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 每页数量（默认 20）
 * @param {number} params.offset - 偏移量（默认 0）
 * @param {string} params.rating - 评级筛选（可选）
 * @param {string} params.keyword - 关键词搜索（可选）
 */
export const getCompanyResearchList = async (params = {}) => {
  return handleRequest(() => http.get('/company-research/reports', { params }))
}

/**
 * 根据 ID 获取公司研报详情
 * GET /api/company-research/reports/{report_id}
 * @param {string} reportId - 研报 ID
 */
export const getCompanyResearchById = async (reportId) => {
  return handleRequest(() => http.get(`/company-research/reports/${reportId}`))
}
