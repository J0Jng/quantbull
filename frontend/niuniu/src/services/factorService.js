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

// 获取因子列表
export const getFactors = async (params = {}) => {
  return handleRequest(() => 
    axiosInstance.get('/factor', {
      params: {
        category: params.category,
        search: params.search,
        limit: params.limit,
        offset: params.offset
      }
    })
  )
}

// 获取因子详情
export const getFactor = async (id) => {
  return handleRequest(() => 
    axiosInstance.get(`/factor/${id}`)
  )
}

// 创建因子
export const createFactor = async (factorData) => {
  return handleRequest(() =>
    axiosInstance.post('/factor', factorData)
  )
}

// 更新因子
export const updateFactor = async (id, updateData) => {
  return handleRequest(() =>
    axiosInstance.put(`/factor/${id}`, updateData)
  )
}

// 删除因子
export const deleteFactor = async (id) => {
  return handleRequest(() =>
    axiosInstance.delete(`/factor/${id}`)
  )
}

// 计算因子值
export const calculateFactor = async (factorId, calculationParams = {}) => {
  return handleRequest(() =>
    axiosInstance.post('/factor/calculate', {
      factorId,
      ...calculationParams
    })
  )
}

// 验证因子表达式
export const validateFactorExpression = async (expression) => {
  return handleRequest(() =>
    axiosInstance.post('/factor/validate', { expression })
  )
}