/**
 * AI 服务
 * 对接后端 /api/ai/* 接口
 */
import http, { handleRequest } from './http'

/**
 * 生成回测模型代码
 * POST /api/ai/generate/strategy
 * @param {Object} data - 请求数据
 * @param {string} data.user_description - 用户回测模型描述
 * @param {string} data.framework - 框架类型 (backtrader)
 * @param {string} model - AI 模型（可选）
 */
export const generateStrategy = async (data, model = null) => {
  const params = model ? { model } : {}
  return handleRequest(() => 
    http.post('/ai/generate/strategy', data, { params })
  )
}

/**
 * 生成新闻解读
 * POST /api/ai/generate/news
 * @param {Object} data - 请求数据
 * @param {string} data.content - 新闻内容
 * @param {string} model - AI 模型（可选）
 */
export const generateNewsAnalysis = async (data, model = null) => {
  const params = model ? { model } : {}
  return handleRequest(() => 
    http.post('/ai/generate/news', data, { params })
  )
}

/**
 * 生成文本生成摘要
 * POST /api/ai/generate/summary
 * @param {Object} data - 请求数据
 * @param {string} model - AI 模型（可选）
 */
export const generateSummary = async (data, model = null) => {
  const params = model ? { model } : {}
  return handleRequest(() => 
    http.post('/ai/generate/summary', data, { params })
  )
}

/**
 * 生成研报
 * POST /api/ai/report/generate
 * @param {Object} data - 请求数据
 * @param {string} model - AI 模型（可选）
 */
export const generateReport = async (data, model = null) => {
  const params = model ? { model } : {}
  return handleRequest(() => 
    http.post('/ai/report/generate', data, { params })
  )
}

/**
 * 通用聊天接口
 * POST /api/ai/chat
 * @param {Object} data - 请求数据
 * @param {string} data.message - 用户消息
 * @param {Array} data.history - 对话历史（可选）
 * @param {string} model - AI 模型（可选）
 */
export const chat = async (data, model = null) => {
  const params = model ? { model } : {}
  return handleRequest(() => 
    http.post('/ai/chat', data, { params })
  )
}

/**
 * 模型路由推荐
 * POST /api/ai/model/route
 * @param {Object} data - 请求数据
 * @param {string} data.task_type - 任务类型
 */
export const getModelRoute = async (taskType) => {
  return handleRequest(() => 
    http.post('/ai/model/route', { task_type: taskType })
  )
}
