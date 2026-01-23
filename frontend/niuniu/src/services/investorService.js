/**
 * 合格投资者认证服务
 */
import http, { handleRequest } from './http'

/**
 * 提交合格投资者认证
 * POST /api/investor/certification
 */
export const submitInvestorCertification = async (payload) => {
  return handleRequest(() => http.post('/investor/certification', payload))
}

/**
 * 获取合格投资者认证状态
 * GET /api/investor/status
 */
export const getInvestorStatus = async () => {
  return handleRequest(() => http.get('/investor/status'))
}

/**
 * 撤销合格投资者认证
 * DELETE /api/investor/certification
 */
export const revokeInvestorCertification = async () => {
  return handleRequest(() => http.delete('/investor/certification'))
}
