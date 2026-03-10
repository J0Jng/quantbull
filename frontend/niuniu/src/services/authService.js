import http, { handleRequest } from './http'

export const ACCESS_TOKEN_KEY = 'quantbull_access_token'
export const CURRENT_USER_KEY = 'quantbull_current_user'

const parsePayload = (resp) => resp?.data || resp

const setAuthState = (token, user) => {
  localStorage.setItem(ACCESS_TOKEN_KEY, token)
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user || {}))
}

export const clearAuthState = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(CURRENT_USER_KEY)
}

export const getToken = () => {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export const getStoredUser = () => {
  const raw = localStorage.getItem(CURRENT_USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export const login = async (credentials) => {
  const result = await handleRequest(() => http.post('/auth/login/json', credentials))
  if (!result.success) {
    return result
  }

  const payload = parsePayload(result.data)
  const token = payload?.access_token
  const user = payload?.user
  if (!token || !user) {
    clearAuthState()
    return { success: false, message: '登录响应格式错误' }
  }

  setAuthState(token, user)
  return { success: true, data: result.data }
}

export const getCurrentUser = async () => {
  const result = await handleRequest(() => http.get('/auth/me'))
  if (!result.success) {
    return result
  }
  const payload = parsePayload(result.data)
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(payload || {}))
  return { success: true, data: result.data }
}

export const verifyToken = async () => {
  return handleRequest(() => http.get('/auth/verify'))
}

export const logout = async () => {
  clearAuthState()
}

export const isAuthenticated = () => {
  return Boolean(getToken())
}

export const getTokenBalance = async () => {
  return handleRequest(() => http.get('/tokens/balance'))
}