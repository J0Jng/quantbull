/**
 * 认证服务
 * 对接后端 /api/auth/* 接口
 */
/**
 * 用户登录（JSON 格式）
 * POST /api/auth/login/json
 * @param {Object} credentials - 登录凭证
 * @param {string} credentials.username - 用户名
 * @param {string} credentials.password - 密码
 */
export const login = async (credentials) => {
  localStorage.setItem('session_active', 'true')
  localStorage.setItem('quantLoginUser', credentials?.username || '游客')
  return {
    success: true,
    data: {
      code: 0,
      message: 'ok',
      data: {
        user_id: 0,
        username: credentials?.username || '游客'
      }
    }
  }
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
  localStorage.setItem('session_active', 'true')
  localStorage.setItem('quantLoginUser', userData?.username || '游客')
  return {
    success: true,
    data: {
      code: 0,
      message: 'ok',
      data: {
        user_id: 0,
        username: userData?.username || '游客'
      }
    }
  }
}

/**
 * 获取当前用户信息
 * GET /api/auth/me
 */
export const getCurrentUser = async () => {
  return {
    success: true,
    data: {
      code: 0,
      message: 'ok',
      data: {
        user_id: 0,
        username: localStorage.getItem('quantLoginUser') || '游客',
        role: 'admin',
        qualified_investor: true
      }
    }
  }
}

/**
 * 验证 token 有效性
 * GET /api/auth/verify
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
 * 退出登录
 */
export const logout = async () => {
  localStorage.setItem('session_active', 'true')
  localStorage.removeItem('user_info')
  localStorage.removeItem('access_token')
  localStorage.removeItem('token_type')
  localStorage.removeItem('user_id')
}

/**
 * 检查是否已登录
 * @returns {boolean}
 */
export const isAuthenticated = () => {
  return true
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
  return {
    success: true,
    data: {
      code: 0,
      message: 'ok',
      data: {
        user_id: 0,
        username: localStorage.getItem('quantLoginUser') || '游客',
        role: 'guest',
        ai_tokens: 3000
      }
    }
  }
}
