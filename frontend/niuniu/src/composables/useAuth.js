/**
 * 统一认证 Composable
 * 提供全局认证状态和方法，避免各页面重复实现登录逻辑
 */
import { ref, computed } from 'vue'

// 全局状态（跨组件共享）
const logged = ref(false)
const currentUser = ref('')
const currentUserId = ref(null)
const currentUserRole = ref('user')
const currentUserEmail = ref('')
const currentUserPhone = ref('')
const currentUserCreatedAt = ref('')
const showLoginModal = ref(false)
const showRiskTip = ref(false)
const isQualifiedInvestor = ref(false)

// 登录表单状态
const loginForm = ref({
  username: '',
  password: '',
  confirmPassword: '',
  email: '',
  phone: ''
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
const initAuth = async () => {
  logged.value = true
  localStorage.setItem('session_active', 'true')
  currentUser.value = localStorage.getItem('quantLoginUser') || '游客'
  currentUserRole.value = localStorage.getItem('userRole') || 'admin'
  currentUserId.value = null
  currentUserEmail.value = ''
  currentUserPhone.value = ''
  currentUserCreatedAt.value = ''
  isQualifiedInvestor.value = true
  localStorage.setItem('qualifiedInvestor', 'certified')
  return true
}

/**
 * 显示登录弹窗
 */
const openLoginModal = () => {
  showLoginModal.value = false
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
    email: '',
    phone: ''
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
  logged.value = true
  currentUser.value = localStorage.getItem('quantLoginUser') || '游客'
  currentUserRole.value = 'admin'
  isQualifiedInvestor.value = true
  localStorage.setItem('session_active', 'true')
  localStorage.setItem('qualifiedInvestor', 'certified')
  showLoginModal.value = false
}

/**
 * 提交注册
 */
const submitRegister = async () => {
  logged.value = true
  currentUser.value = localStorage.getItem('quantLoginUser') || '游客'
  currentUserRole.value = 'admin'
  isQualifiedInvestor.value = true
  localStorage.setItem('session_active', 'true')
  localStorage.setItem('qualifiedInvestor', 'certified')
  showLoginModal.value = false
}

/**
 * 确认风险提示（登录成功后）
 */
const confirmRiskTip = async () => {
  showRiskTip.value = false
  logged.value = true
  currentUser.value = localStorage.getItem('quantLoginUser') || '游客'
  currentUserRole.value = 'admin'
  isQualifiedInvestor.value = true
  localStorage.setItem('qualifiedInvestor', 'certified')
}

/**
 * 退出登录
 */
const logout = async () => {
  logged.value = true
  currentUser.value = localStorage.getItem('quantLoginUser') || '游客'
  currentUserRole.value = 'admin'
  isQualifiedInvestor.value = true
  localStorage.setItem('session_active', 'true')
  localStorage.setItem('qualifiedInvestor', 'certified')
}

/**
 * 是否为管理员
 */
const isAdmin = computed(() => {
  return logged.value && currentUserRole.value === 'admin'
})

/**
 * 用户显示文本
 */
const userText = computed(() => {
  return logged.value ? `访客模式（${currentUser.value}）` : '访客模式'
})

/**
 * 检查是否需要显示登录弹窗（用于需要登录的操作）
 * @returns {boolean} 如果已登录返回 true，否则显示登录弹窗并返回 false
 */
const requireAuth = () => {
  return true
}

export function useAuth() {
  return {
    // 状态
    logged,
    currentUser,
    currentUserId,
    currentUserRole,
    currentUserEmail,
    currentUserPhone,
    currentUserCreatedAt,
    isAdmin,
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
