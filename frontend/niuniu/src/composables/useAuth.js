/**
 * 统一认证 Composable
 * 提供全局认证状态和方法，避免各页面重复实现登录逻辑
 */
import { ref, computed } from 'vue'
import { login as authLogin, register as authRegister, logout as authLogout, isAuthenticated } from '@/services/authService'

// 全局状态（跨组件共享）
const logged = ref(false)
const currentUser = ref('')
const showLoginModal = ref(false)
const showRiskTip = ref(false)
const isQualifiedInvestor = ref(false)

// 登录表单状态
const loginForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  email: ''
})
const isRegisterMode = ref(false)
const loginLoading = ref(false)
const errorMessage = ref('')
const errorVisible = ref(false)
const successMessage = ref('')
const successVisible = ref(false)

/**
 * 初始化认证状态（页面加载时调用）
 */
const initAuth = () => {
  if (isAuthenticated()) {
    logged.value = true
    currentUser.value = localStorage.getItem('quantLoginUser') || '用户'
    isQualifiedInvestor.value = localStorage.getItem('qualifiedInvestor') === 'certified'
  } else {
    logged.value = false
    currentUser.value = ''
    isQualifiedInvestor.value = false
  }
}

/**
 * 显示登录弹窗
 */
const openLoginModal = () => {
  resetLoginForm()
  isRegisterMode.value = false
  showLoginModal.value = true
}

/**
 * 关闭登录弹窗
 */
const closeLoginModal = () => {
  showLoginModal.value = false
  resetLoginForm()
}

/**
 * 重置登录表单
 */
const resetLoginForm = () => {
  loginForm.value = {
    username: '',
    password: '',
    confirmPassword: '',
    email: ''
  }
  errorVisible.value = false
  successVisible.value = false
  errorMessage.value = ''
  successMessage.value = ''
}

/**
 * 切换到注册模式
 */
const switchToRegister = () => {
  isRegisterMode.value = true
  resetLoginForm()
}

/**
 * 切换到登录模式
 */
const switchToLogin = () => {
  isRegisterMode.value = false
  resetLoginForm()
}

/**
 * 显示错误信息
 */
const showError = (message) => {
  errorMessage.value = message
  errorVisible.value = true
  setTimeout(() => {
    errorVisible.value = false
  }, 3000)
}

/**
 * 显示成功信息
 */
const showSuccess = (message) => {
  successMessage.value = message
  successVisible.value = true
  setTimeout(() => {
    successVisible.value = false
  }, 2000)
}

/**
 * 提交登录
 */
const submitLogin = async () => {
  const { username, password } = loginForm.value
  
  if (!username.trim() || !password.trim()) {
    showError('请输入账号和密码')
    return
  }
  
  loginLoading.value = true
  errorVisible.value = false
  
  try {
    const result = await authLogin({
      username: username.trim(),
      password: password.trim()
    })
    
    if (result.success) {
      // 登录成功，显示动态风险提示
      showRiskTip.value = true
      showLoginModal.value = false
      localStorage.setItem('quantLoginUser', username.trim())
      resetLoginForm()
    } else {
      showError(result.error || result.message || '账号或密码错误，请重试！')
    }
  } catch (error) {
    console.error('Login error:', error)
    showError('登录失败，请稍后重试')
  } finally {
    loginLoading.value = false
  }
}

/**
 * 提交注册
 */
const submitRegister = async () => {
  const { username, password, confirmPassword, email } = loginForm.value
  
  if (!username.trim() || !password.trim()) {
    showError('请输入账号和密码')
    return
  }
  
  if (password !== confirmPassword) {
    showError('两次密码输入不一致')
    return
  }
  
  if (password.length < 6) {
    showError('密码长度不能少于6位')
    return
  }
  
  loginLoading.value = true
  errorVisible.value = false
  
  try {
    const result = await authRegister({
      username: username.trim(),
      password: password.trim(),
      email: email.trim() || undefined
    })
    
    if (result.success) {
      showSuccess('注册成功！请登录')
      setTimeout(() => {
        switchToLogin()
      }, 2000)
    } else {
      showError(result.error || result.message || '注册失败，请稍后重试')
    }
  } catch (error) {
    console.error('Register error:', error)
    showError('注册失败，请稍后重试')
  } finally {
    loginLoading.value = false
  }
}

/**
 * 确认风险提示（登录成功后）
 */
const confirmRiskTip = () => {
  showRiskTip.value = false
  logged.value = true
  currentUser.value = localStorage.getItem('quantLoginUser') || '用户'
  isQualifiedInvestor.value = localStorage.getItem('qualifiedInvestor') === 'certified'
}

/**
 * 退出登录
 */
const logout = () => {
  authLogout()
  logged.value = false
  currentUser.value = ''
  isQualifiedInvestor.value = false
  localStorage.removeItem('quantLoginUser')
}

/**
 * 用户显示文本
 */
const userText = computed(() => {
  return logged.value ? `已登录（${currentUser.value}）` : '登录/注册'
})

/**
 * 检查是否需要显示登录弹窗（用于需要登录的操作）
 * @returns {boolean} 如果已登录返回 true，否则显示登录弹窗并返回 false
 */
const requireAuth = () => {
  if (logged.value) {
    return true
  }
  openLoginModal()
  return false
}

export function useAuth() {
  return {
    // 状态
    logged,
    currentUser,
    showLoginModal,
    showRiskTip,
    isQualifiedInvestor,
    loginForm,
    isRegisterMode,
    loginLoading,
    errorMessage,
    errorVisible,
    successMessage,
    successVisible,
    userText,
    
    // 方法
    initAuth,
    openLoginModal,
    closeLoginModal,
    resetLoginForm,
    switchToRegister,
    switchToLogin,
    submitLogin,
    submitRegister,
    confirmRiskTip,
    logout,
    requireAuth
  }
}
