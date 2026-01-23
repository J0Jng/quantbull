<script setup>
import { onMounted, onUnmounted } from 'vue'
import ChatWidget from './components/ChatWidget.vue'
import LoginModal from './components/LoginModal.vue'
import { useChatStore } from './stores/chat'
import { useAuth } from './composables/useAuth'
import { isAuthenticated } from './services/authService'

// 初始化聊天状态管理
const chatStore = useChatStore()

// 初始化认证状态
const { initAuth, openLoginModal, logged } = useAuth()

// 监听 401 事件，自动弹出登录框
const handleAuthRequired = () => {
  openLoginModal()
}

// 页面加载时设置默认位置
onMounted(async () => {
  // 初始化认证状态
  const authed = await initAuth()
  
  // 如果未登录，自动弹出登录框
  if (!authed && !isAuthenticated()) {
    openLoginModal()
  }
  
  // 监听 401 触发的重新登录事件
  window.addEventListener('auth:required', handleAuthRequired)
  
  // 设置聊天窗口默认位置（右下角）
  if (window.innerWidth > 768) {
    chatStore.setChatPosition(window.innerWidth - 420, window.innerHeight - 620)
  }
})

onUnmounted(() => {
  window.removeEventListener('auth:required', handleAuthRequired)
})
</script>

<template>
  <div id="app">
    <!-- 主应用内容 -->
    <router-view />
    
    <!-- 全局登录弹窗 -->
    <LoginModal />
    
    <!-- 悬浮聊天窗口 -->
    <ChatWidget 
      :system-prompt="chatStore.systemPrompt"
    />
  </div>
</template>

<style>
@import './assets/css/index.css';

/* 全局聊天组件样式增强 */
#app {
  position: relative;
  min-height: 100vh;
}

/* 确保聊天窗口层级最高 */
.chat-widget-container {
  z-index: 9999 !important;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .chat-widget-container {
    z-index: 99999 !important;
  }
}
</style>
