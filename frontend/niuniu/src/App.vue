<script setup>
import { onMounted } from 'vue'
import ChatWidget from './components/ChatWidget.vue'
import { useChatStore } from './stores/chat'

// 初始化聊天状态管理
const chatStore = useChatStore()

// 页面加载时设置默认位置
onMounted(() => {
  // 设置聊天窗口默认位置（右下角）
  if (window.innerWidth > 768) {
    chatStore.setChatPosition(window.innerWidth - 420, window.innerHeight - 620)
  }
})
</script>

<template>
  <div id="app">
    <!-- 主应用内容 -->
    <router-view />
    
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
