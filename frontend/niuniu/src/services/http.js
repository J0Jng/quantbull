/**
 * 统一 HTTP 客户端配置
 * 所有 API 请求的基础配置
 */
import axios from 'axios'

const ACCESS_TOKEN_KEY = 'quantbull_access_token'
const CURRENT_USER_KEY = 'quantbull_current_user'

const clearAuthState = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(CURRENT_USER_KEY)
}

// API 网关基础 URL
// 开发环境使用 Vite 代理，生产环境使用实际网关地址
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'
const API_FALLBACK_BASE_URL = import.meta.env.VITE_API_FALLBACK_BASE_URL || ''

const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value)

const looksLikeHtml = (value) => {
  if (typeof value !== 'string') return false
  const s = value.trim().toLowerCase()
  return s.startsWith('<!doctype html') || s.startsWith('<html')
}

const findBusinessError = (payload, maxDepth = 5) => {
  let current = payload
  let depth = 0
  while (isObject(current) && depth < maxDepth) {
    if ('code' in current) {
      const businessCode = Number(current.code)
      if (!Number.isNaN(businessCode) && businessCode !== 0) {
        return {
          code: businessCode,
          message: current.message || '请求失败',
          data: current.data
        }
      }
    }

    if ('data' in current) {
      current = current.data
      depth += 1
      continue
    }
    break
  }
  return null
}

const unwrapEnvelopeData = (payload, maxDepth = 5) => {
  let current = payload
  let depth = 0
  while (isObject(current) && 'code' in current && 'data' in current && depth < maxDepth) {
    current = current.data
    depth += 1
  }
  return current
}

const getGatewayFallbackBaseUrl = () => {
  if (API_FALLBACK_BASE_URL) return API_FALLBACK_BASE_URL
  if (typeof window === 'undefined') return ''
  if (!import.meta.env.PROD) return ''
  if (!String(API_BASE_URL).startsWith('/')) return ''
  const { protocol, hostname } = window.location
  return `${protocol}//${hostname}:8000${API_BASE_URL}`
}

// 创建 axios 实例
const http = axios.create({
  baseURL: API_BASE_URL,
  // 延长超时时间以支持后端模型降级重试
  timeout: 600000,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json'
  }
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(ACCESS_TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 统一错误处理
http.interceptors.response.use(
  (response) => {
    return response.data
  },
  async (error) => {
    if (error.response) {
      // 线上常见问题：Nginx 未正确反代 /api，先尝试直连网关端口兜底一次。
      const originalConfig = error.config || {}
      const retryStatusCode = error.response.status
      const fallbackBaseUrl = getGatewayFallbackBaseUrl()
      if ((retryStatusCode === 404 || retryStatusCode === 500 || retryStatusCode === 502 || retryStatusCode === 503 || retryStatusCode === 504) && fallbackBaseUrl && !originalConfig.__gatewayFallbackRetried) {
        return http.request({
          ...originalConfig,
          baseURL: fallbackBaseUrl,
          __gatewayFallbackRetried: true
        })
      }

      const { status, data } = error.response
      let message = '请求失败'
      
      if (data && data.message) {
        message = data.message
      } else if (data && data.detail) {
        message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
      } else if (status === 401 || status === 403) {
        message = status === 401 ? '登录已失效，请重新登录' : '无权限访问'
      } else if (status === 404) {
        message = '资源不存在'
      } else if (status === 422) {
        message = '请求参数错误'
      } else if (status >= 500) {
        message = '服务器错误，请稍后重试'
      }
      
      if (status === 401) {
        clearAuthState()
        window.dispatchEvent(new CustomEvent('auth:unauthorized'))
      }

      return Promise.reject({ message, status, data })
    } else if (error.request) {
      const originalConfig = error.config || {}
      const fallbackBaseUrl = getGatewayFallbackBaseUrl()
      if (fallbackBaseUrl && !originalConfig.__gatewayFallbackRetried) {
        try {
          return await http.request({
            ...originalConfig,
            baseURL: fallbackBaseUrl,
            __gatewayFallbackRetried: true
          })
        } catch (retryError) {
          if (retryError?.response) {
            const retryStatus = retryError.response.status
            const retryData = retryError.response.data
            const retryMessage = (retryData && (retryData.message || retryData.detail)) || '服务器错误，请稍后重试'
            return Promise.reject({ message: retryMessage, status: retryStatus, data: retryData })
          }
        }
      }
      return Promise.reject({ message: '网络错误，请检查网络连接', status: 0 })
    } else {
      return Promise.reject({ message: error.message || '请求失败', status: -1 })
    }
  }
)

/**
 * 统一请求处理函数
 * @param {Function} request - 请求函数
 * @returns {Promise<{success: boolean, data?: any, message?: string}>}
 */
export const handleRequest = async (request) => {
  try {
    const response = await request()

    if (looksLikeHtml(response)) {
      return {
        success: false,
        message: '接口返回了 HTML 页面，服务器 API 代理可能未配置正确',
        status: 502,
        data: null
      }
    }

    const businessError = findBusinessError(response)
    if (businessError) {
      return {
        success: false,
        message: businessError.message,
        code: businessError.code,
        data: businessError.data
      }
    }

    return {
      success: true,
      data: response,
      payload: unwrapEnvelopeData(response)
    }
  } catch (error) {
    return {
      success: false,
      message: error.message || '请求失败',
      status: error.status
    }
  }
}

export default http
