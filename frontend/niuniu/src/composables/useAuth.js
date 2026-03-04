/**
 * 匿名模式 Composable
 * 为兼容历史调用点保留同名字段/方法，但不再维护登录态/鉴权流程。
 */
import { ref, computed } from 'vue'

// 全局状态（跨组件共享）
const logged = ref(true)
const currentUser = ref('匿名用户')
const currentUserId = ref(null)
const currentUserRole = ref('guest')
const currentUserEmail = ref('')
const currentUserPhone = ref('')
const currentUserCreatedAt = ref('')
const showLoginModal = ref(false)
const showRiskTip = ref(false)
const isQualifiedInvestor = ref(false)

// 表单状态（保留字段以兼容历史模板/调用点）
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
 * 初始化状态（页面加载时调用）
 */
const initAuth = async () => {
  // 匿名模式：不读取/写入任何持久化登录态，不触发弹窗。
  logged.value = true
  currentUser.value = '匿名用户'
  currentUserRole.value = 'guest'
  currentUserId.value = null
  currentUserEmail.value = ''
  currentUserPhone.value = ''
  currentUserCreatedAt.value = ''
  isQualifiedInvestor.value = false
  return true
}

/**
 * 兼容方法：匿名模式下不做任何事
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
  // 匿名模式：不支持登录流程，保持当前匿名状态
  logged.value = true
  showLoginModal.value = false
}

/**
 * 提交注册
 */
const submitRegister = async () => {
  // 匿名模式：不支持注册流程，保持当前匿名状态
  logged.value = true
  showLoginModal.value = false
}

/**
 * 确认风险提示（登录成功后）
 */
const confirmRiskTip = async () => {
  showRiskTip.value = false
  logged.value = true
}

/**
 * 兼容方法：匿名模式下仅清理局部 UI 状态
 */
const logout = async () => {
  logged.value = true
  showLoginModal.value = false
  resetLoginForm()
}

/**
 * 是否为管理员
 */
const isAdmin = computed(() => {
  return false
})

/**
 * 用户显示文本
 */
const userText = computed(() => {
  return '访客模式'
})

/**
 * 兼容方法：匿名模式下始终允许继续
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
