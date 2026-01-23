/**
 * 管理员服务
 * 对接后端 /api/admin/* 接口
 */
import http, { handleRequest } from './http'

/**
 * 获取用户列表（分页）
 * GET /api/admin/users
 */
export const listUsers = async ({ limit = 100, offset = 0 } = {}) => {
  return handleRequest(() => http.get(`/admin/users?limit=${limit}&offset=${offset}`))
}

/**
 * 获取用户详情
 * GET /api/admin/users/{user_id}
 */
export const getUser = async (userId) => {
  return handleRequest(() => http.get(`/admin/users/${userId}`))
}

/**
 * 更新用户信息（角色/密码/ai_tokens）
 * PATCH /api/admin/users/{user_id}
 */
export const updateUser = async (userId, payload = {}) => {
  return handleRequest(() => http.patch(`/admin/users/${userId}`, payload))
}

/**
 * 删除用户
 * DELETE /api/admin/users/{user_id}
 */
export const deleteUser = async (userId) => {
  return handleRequest(() => http.delete(`/admin/users/${userId}`))
}

/**
 * 更新用户 AI Token 余额
 * PATCH /api/admin/users/{user_id}/ai-tokens
 */
export const updateUserAiTokens = async (userId, aiTokens) => {
  return handleRequest(() => http.patch(`/admin/users/${userId}/ai-tokens`, { ai_tokens: aiTokens }))
}
