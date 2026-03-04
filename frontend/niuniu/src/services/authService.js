/**
 * 匿名模式兼容服务
 * 为兼容历史调用点保留同名方法，但不再维护登录态/Token。
 */

/**
 * 兼容方法：保持签名但不做状态写入
 */
export const login = async (credentials) => {
  return {
    success: true,
    data: {
      code: 0,
      message: 'ok',
      data: {
        user_id: 0,
        username: credentials?.username || '匿名用户'
      }
    }
  }
}

/**
 * 兼容方法：保持签名但不做状态写入
 */
export const register = async (userData) => {
  return {
    success: true,
    data: {
      code: 0,
      message: 'ok',
      data: {
        user_id: 0,
        username: userData?.username || '匿名用户'
      }
    }
  }
}

/**
 * 获取当前用户信息（匿名模式返回固定访客信息）
 */
export const getCurrentUser = async () => {
  return {
    success: true,
    data: {
      code: 0,
      message: 'ok',
      data: {
        user_id: 0,
        username: '匿名用户',
        role: 'guest',
        qualified_investor: false
      }
    }
  }
}

/**
 * 兼容方法：始终返回有效
 */
export const verifyToken = async () => {
  return {
    success: true,
    data: {
      code: 0,
      message: 'ok',
      data: {
        valid: true
      }
    }
  }
}

/**
 * 兼容方法：匿名模式下无状态可清理
 */
export const logout = async () => {
  return
}

/**
 * 匿名模式下始终可用
 */
export const isAuthenticated = () => {
  return true
}

/**
 * 匿名模式下不提供 Token
 */
export const getToken = () => {
  return null
}

/**
 * 获取当前用户 AI 额度（匿名模式返回空值或后端实际返回）
 */
export const getTokenBalance = async () => {
  return {
    success: true,
    data: {
      code: 0,
      message: 'ok',
      data: {
        user_id: 0,
        username: '匿名用户',
        role: 'guest',
        ai_tokens: null
      }
    }
  }
}
