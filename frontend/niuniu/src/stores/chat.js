import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useChatStore = defineStore('chat', () => {
  // 聊天窗口状态
  const isChatOpen = ref(false)
  const isChatMinimized = ref(false)
  const chatPosition = ref({ x: 0, y: 0 })
  
  // 聊天历史记录
  const chatHistory = ref([])
  const isLoading = ref(false)
  
  // 默认系统提示词
  const systemPrompt = ref("你是一个专业的投资顾问和量化分析助手，专注于为用户提供投资策略、市场分析和量化交易相关的帮助。你的职责包括分析用户的投资问题和需求，提供基于市场数据的投资建议，解释量化策略的基本原理，提供风险控制和资产配置建议，回答关于股票、基金、期货等金融产品的相关问题，解释技术指标和基本面分析方法，提供投资组合优化建议。在回答时，请保持专业性和准确性，提示投资风险，强调投资有风险，入市需谨慎，提供实用、可操作的建议，对复杂问题提供分步骤的解决方案，在适当时候推荐平台上的其他专业服务或工具，避免给出过于具体的投资操作建议，鼓励用户进一步咨询专业顾问，始终提醒用户根据自身风险承受能力做出投资决策。")

  // 最大历史记录数
  const MAX_HISTORY = 50

  // 计算属性
  const unreadMessageCount = computed(() => 
    chatHistory.value.filter(msg => !msg.isRead).length
  )

  const hasUnreadMessages = computed(() => unreadMessageCount.value > 0)

  // 操作方法
  const toggleChat = () => {
    isChatOpen.value = !isChatOpen.value
    if (isChatOpen.value) {
      isChatMinimized.value = false
    }
  }

  const minimizeChat = () => {
    isChatMinimized.value = !isChatMinimized.value
  }

  const setChatPosition = (x, y) => {
    chatPosition.value = { x, y }
  }

  const addMessage = (content, isUser = true) => {
    const message = {
      id: Date.now() + Math.random(),
      content,
      isUser,
      timestamp: new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      isRead: !isUser // AI消息默认未读
    }
    
    chatHistory.value.push(message)
    
    // 限制历史记录数量
    if (chatHistory.value.length > MAX_HISTORY) {
      chatHistory.value = chatHistory.value.slice(-MAX_HISTORY)
    }
  }

  const clearChat = () => {
    chatHistory.value = []
  }

  const markMessagesAsRead = () => {
    chatHistory.value.forEach(msg => {
      msg.isRead = true
    })
  }

  const setLoading = (loading) => {
    isLoading.value = loading
  }

  const setSystemPrompt = (prompt) => {
    systemPrompt.value = prompt
  }

  return {
    // 状态
    isChatOpen,
    isChatMinimized,
    chatPosition,
    chatHistory,
    isLoading,
    systemPrompt,
    
    // 计算属性
    unreadMessageCount,
    hasUnreadMessages,
    
    // 方法
    toggleChat,
    minimizeChat,
    setChatPosition,
    addMessage,
    clearChat,
    markMessagesAsRead,
    setLoading,
    setSystemPrompt
  }
})