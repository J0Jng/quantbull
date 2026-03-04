/**
 * 模拟参数服务
 * 对接后端 /api/factor/* 接口
 */
import http, { handleRequest } from './http'

/**
 * 获取模拟参数列表
 * GET /api/factor
 * @param {Object} params - 查询参数
 * @param {string} params.category - 类别筛选
 * @param {string} params.search - 搜索关键词
 * @param {number} params.limit - 每页数量
 * @param {number} params.offset - 偏移量
 */
export const getFactors = async (params = {}) => {
  return handleRequest(() => 
    http.get('/factor', {
      params: {
        category: params.category,
        search: params.search,
        limit: params.limit,
        offset: params.offset
      }
    })
  )
}

/**
 * 获取模拟参数详情
 * GET /api/factor/{id}
 * @param {number} id - 模拟参数 ID
 */
export const getFactor = async (id) => {
  return handleRequest(() => http.get(`/factor/${id}`))
}

/**
 * 创建模拟参数
 * POST /api/factor
 * @param {Object} factorData - 模拟参数数据
 */
export const createFactor = async (factorData) => {
  return handleRequest(() => http.post('/factor', factorData))
}

/**
 * 更新模拟参数
 * PUT /api/factor/{id}
 * @param {number} id - 模拟参数 ID
 * @param {Object} updateData - 更新数据
 */
export const updateFactor = async (id, updateData) => {
  return handleRequest(() => http.put(`/factor/${id}`, updateData))
}

/**
 * 删除模拟参数
 * DELETE /api/factor/{id}
 * @param {number} id - 模拟参数 ID
 */
export const deleteFactor = async (id) => {
  return handleRequest(() => http.delete(`/factor/${id}`))
}

/**
 * 计算模拟参数值
 * POST /api/factor/calculate
 * @param {Object} calculationParams - 计算参数
 * @param {string} calculationParams.factor_id - 模拟参数 ID
 * @param {string} calculationParams.symbol - 股票代码
 * @param {string} calculationParams.start_date - 开始日期 YYYY-MM-DD
 * @param {string} calculationParams.end_date - 结束日期 YYYY-MM-DD
 */
export const calculateFactor = async (calculationParams) => {
  return handleRequest(() => http.post('/factor/calculate', calculationParams))
}

/**
 * 验证模拟参数表达式（如果后端支持）
 * @param {string} expression - 模拟参数表达式
 */
export const validateFactorExpression = async (expression) => {
  // 前端本地验证或调用后端接口
  return handleRequest(() => 
    http.post('/factor/validate', { expression })
  )
}