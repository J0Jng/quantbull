/**
 * 统一 HTTP 客户端配置
 * 所有 API 请求的基础配置
 */
import axios from 'axios'

// API 网关基础 URL
// 开发环境使用 Vite 代理，生产环境使用实际网关地址
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

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

const csrfCookieNames = [
  import.meta.env.VITE_CSRF_COOKIE_NAME,
  'quantbull_csrf',
  'qb_csrf'
].filter(Boolean)

const getCookie = (name) => {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`))
  return match ? decodeURIComponent(match[1]) : null
}

const getCsrfToken = () => {
  for (const name of csrfCookieNames) {
    const token = getCookie(name)
    if (token) return token
  }
  return null
}

// 请求拦截器 - 添加 CSRF token（仅对非幂等请求）
http.interceptors.request.use(
  (config) => {
    const method = (config.method || 'get').toLowerCase()
    if (['post', 'put', 'patch', 'delete'].includes(method)) {
      const csrfToken = getCsrfToken()
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 统一错误处理
http.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      let message = '请求失败'
      
      if (data && data.message) {
        message = data.message
      } else if (data && data.detail) {
        message = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
      } else if (status === 401 || status === 403) {
        message = '暂无数据'
      } else if (status === 404) {
        message = '资源不存在'
      } else if (status === 422) {
        message = '请求参数错误'
      } else if (status >= 500) {
        message = '服务器错误，请稍后重试'
      }
      
      return Promise.reject({ message, status, data })
    } else if (error.request) {
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
    return {
      success: true,
      data: response
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
