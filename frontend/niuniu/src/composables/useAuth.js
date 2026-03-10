import { ref, computed } from 'vue'
import {
  login,
  getCurrentUser,
  verifyToken,
  logout as serviceLogout,
  isAuthenticated,
  getStoredUser,
  clearAuthState
} from '@/services/authService'

const logged = ref(false)
const currentUser = ref('')
const currentUserId = ref(null)
const currentUserRole = ref('guest')
const currentUserEmail = ref('')
const currentUserPhone = ref('')
const currentUserCreatedAt = ref('')
const showLoginModal = ref(false)
const showRiskTip = ref(false)
const isQualifiedInvestor = ref(false)

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

const applyUserState = (user) => {
  currentUser.value = user?.username || ''
  currentUserId.value = user?.id ?? user?.user_id ?? null
  currentUserRole.value = user?.role || 'user'
  currentUserEmail.value = user?.email || ''
  currentUserPhone.value = user?.phone || ''
  currentUserCreatedAt.value = user?.created_at || ''
  isQualifiedInvestor.value = !!user?.qualified_investor
  logged.value = true
}

const resetAuthState = () => {
  logged.value = false
  currentUser.value = ''
  currentUserId.value = null
  currentUserRole.value = 'guest'
  currentUserEmail.value = ''
  currentUserPhone.value = ''
  currentUserCreatedAt.value = ''
  isQualifiedInvestor.value = false
}

const showError = (message) => {
  errorMessage.value = message
  errorVisible.value = true
  setTimeout(() => {
    errorVisible.value = false
  }, 3000)
}

const showSuccess = (message) => {
  successMessage.value = message
  successVisible.value = true
  setTimeout(() => {
    successVisible.value = false
  }, 2000)
}

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

const initAuth = async () => {
  if (!isAuthenticated()) {
    resetAuthState()
    return false
  }

  const stored = getStoredUser()
  if (stored?.username) {
    applyUserState(stored)
  }

  const verified = await verifyToken()
  if (!verified.success) {
    clearAuthState()
    resetAuthState()
    return false
  }

  const meResult = await getCurrentUser()
  if (!meResult.success) {
    clearAuthState()
    resetAuthState()
    return false
  }

  const userData = meResult.data?.data || meResult.data || {}
  applyUserState(userData)
  return true
}

const openLoginModal = () => {
  isRegisterMode.value = false
  showLoginModal.value = true
}

const closeLoginModal = () => {
  showLoginModal.value = false
  resetLoginForm()
}

const switchToRegister = () => {
  showError('当前仅支持管理员创建普通用户，不开放公开注册')
}

const switchToLogin = () => {
  isRegisterMode.value = false
}

const submitLogin = async () => {
  const username = (loginForm.value.username || '').trim()
  const password = (loginForm.value.password || '').trim()
  if (!username || !password) {
    showError('请输入用户名和密码')
    return { success: false }
  }

  loginLoading.value = true
  try {
    const result = await login({ username, password })
    if (!result.success) {
      showError(result.message || '登录失败')
      return result
    }

    const user = result.data?.data?.user || result.data?.user
    applyUserState(user || {})
    showSuccess('登录成功')
    showLoginModal.value = false
    resetLoginForm()
    return { success: true }
  } finally {
    loginLoading.value = false
  }
}

const submitRegister = async () => {
  showError('当前仅支持管理员创建普通用户，不开放公开注册')
  return { success: false }
}

const confirmRiskTip = async () => {
  showRiskTip.value = false
}

const logout = async () => {
  await serviceLogout()
  resetAuthState()
  showLoginModal.value = false
  resetLoginForm()
}

const isAdmin = computed(() => currentUserRole.value === 'admin')

const userText = computed(() => {
  if (!logged.value) {
    return '请登录'
  }
  return currentUser.value || '用户'
})

const requireAuth = () => {
  if (logged.value) {
    return true
  }
  openLoginModal()
  return false
}

export function useAuth() {
  return {
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