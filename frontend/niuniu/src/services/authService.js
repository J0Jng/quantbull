/**
 * 认证服务
 * 对接后端 /api/auth/* 接口
 */
import http, { handleRequest } from './http'

/**
 * 用户登录（JSON 格式）
 * POST /api/auth/login/json
 * @param {Object} credentials - 登录凭证
 * @param {string} credentials.username - 用户名
 * @param {string} credentials.password - 密码
 */
export const login = async (credentials) => {
  const result = await handleRequest(() => 
    http.post('/auth/login/json', credentials)
  )
  
  // 后端返回格式: {code: 0, message: "ok", data: {access_token: ..., user_id: ...}}
  // handleRequest 包装后: {success: true, data: {code: 0, message: "ok", data: {...}}}
  const tokenData = result.data?.data || result.data
  
  if (result.success && tokenData?.access_token) {
    // 保存 token 到本地存储
    localStorage.setItem('access_token', tokenData.access_token)
    if (tokenData.refresh_token) {
      localStorage.setItem('refresh_token', tokenData.refresh_token)
    }
  }
  
  return result
}

/**
 * 用户注册
 * POST /api/auth/register
 * @param {Object} userData - 注册信息
 * @param {string} userData.username - 用户名
 * @param {string} userData.password - 密码
 * @param {string} userData.email - 邮箱（可选）
 */
export const register = async (userData) => {
  return handleRequest(() => http.post('/auth/register', userData))
}

/**
 * 获取当前用户信息
 * GET /api/auth/me
 */
export const getCurrentUser = async () => {
  return handleRequest(() => http.get('/auth/me'))
}

/**
 * 验证 token 有效性
 * GET /api/auth/verify
 */
export const verifyToken = async () => {
  return handleRequest(() => http.get('/auth/verify'))
}

/**
 * 退出登录
 */
export const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user_info')
}

/**
 * 检查是否已登录
 * @returns {boolean}
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem('access_token')
}

/**
 * 获取存储的 token
 * @returns {string|null}
 */
export const getToken = () => {
  return localStorage.getItem('access_token')
}

/**
 * 获取当前用户 AI Token 余额
 * GET /api/tokens/balance
 */
export const getTokenBalance = async () => {
  return handleRequest(() => http.get('/tokens/balance'))
}
