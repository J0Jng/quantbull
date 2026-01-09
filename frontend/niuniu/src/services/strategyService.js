import { ref } from 'vue'
import axios from 'axios'

// API基础配置
const API_BASE_URL = '/api/quant/api'
const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加认证token
axiosInstance.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器 - 统一错误处理
axiosInstance.interceptors.response.use(response => {
  return response.data
}, error => {
  if (error.response) {
    const { status, data } = error.response
    let message = '请求失败'
    if (data && data.message) {
      message = data.message
    } else if (status === 401) {
      message = '认证失败，请重新登录'
    } else if (status === 403) {
      message = '无权限访问该资源'
    } else if (status === 404) {
      message = '资源不存在'
    } else if (status >= 500) {
      message = '服务器错误'
    }
    return Promise.reject({ message, status })
  } else if (error.request) {
    return Promise.reject({ message: '网络错误，请检查网络连接' })
  } else {
    return Promise.reject({ message: error.message || '请求失败' })
  }
})

// 请求工具函数
const handleRequest = async (request) => {
  try {
    const response = await request()
    return {
      success: true,
      data: response
    }
  } catch (error) {
    return {
      success: false,
      message: error.message || '请求失败'
    }
  }
}

// 获取策略列表
export const getStrategies = async (params = {}) => {
  return handleRequest(() => 
    axiosInstance.get('/strategy', {
      params: {
        status: params.status,
        search: params.search,
        limit: params.limit,
        offset: params.offset
      }
    })
  )
}

// 获取策略详情
export const getStrategy = async (id) => {
  return handleRequest(() => 
    axiosInstance.get(`/strategy/${id}`)
  )
}

// 创建策略
export const createStrategy = async (strategyData) => {
  return handleRequest(() =>
    axiosInstance.post('/strategy', strategyData)
  )
}

// 更新策略
export const updateStrategy = async (id, updateData) => {
  return handleRequest(() =>
    axiosInstance.put(`/strategy/${id}`, updateData)
  )
}

// 删除策略
export const deleteStrategy = async (id) => {
  return handleRequest(() =>
    axiosInstance.delete(`/strategy/${id}`)
  )
}

// 验证策略代码
export const validateStrategyCode = async (code) => {
  return handleRequest(() =>
    axiosInstance.post('/strategy/validate', { code })
  )
}

// 获取策略回测历史
export const getStrategyBacktests = async (strategyId) => {
  return handleRequest(() =>
    axiosInstance.get(`/backtest?strategy_id=${strategyId}`)
  )
}

// 运行策略回测
export const runBacktest = async (strategyId, backtestParams) => {
  return handleRequest(() =>
    axiosInstance.post('/backtest/run', {
      ...backtestParams,
      strategy_id: strategyId
    })
  )
}

// 生成策略模板
export const generateStrategyTemplate = async (templateType) => {
  return handleRequest(() =>
    axiosInstance.post('/ai/api/ai/generate/strategy', {
      user_description: `Generate a ${templateType} strategy template`,
      framework: 'backtrader'
    })
  )
}