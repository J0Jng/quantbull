import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useChatStore = defineStore('chat', () => {
  // 聊天窗口状态
  const isChatOpen = ref(false)
  const isChatMinimized = ref(false)
  const chatPosition = ref({ x: 0, y: 0 })
  
  // 聊天模式
  const chatMode = ref('text') // 'text' | 'video'
  
  // 聊天历史记录
  const chatHistory = ref([])
  const isLoading = ref(false)
  
  // 数字人视频生成状态
  const isGeneratingVideo = ref(false)
  const currentVideoTask = ref(null)
  
  // 默认系统提示词
  const systemPrompt = ref("你是一个专业的投资顾问和量化分析助手，专注于为用户提供投资策略、市场分析和量化交易相关的帮助。你的职责包括分析用户的投资问题和需求，提供基于市场数据的投资建议，解释量化策略的基本原理，提供风险控制和资产配置建议，回答关于股票、基金、期货等金融产品的相关问题，解释技术指标和基本面分析方法，提供投资组合优化建议。在回答时，请保持专业性和准确性，提示投资风险，强调投资有风险，入市需谨慎，提供实用、可操作的建议，对复杂问题提供分步骤的解决方案，在适当时候推荐平台上的其他专业服务或工具，避免给出过于具体的投资操作建议，鼓励用户进一步咨询专业顾问，始终提醒用户根据自身风险承受能力做出投资决策。输出要求：1) 必须分行输出；2) 使用短句，每句不超过20字；3) 不使用“略/后续/省略号”来截断回答；4) 需要分段时用空行分隔。")

  // 数字人专用提示词
  const digitalHumanPrompt = ref("你是一个专业的金融主播，需要对当前金融市场进行分析解读。请生成适合视频口播的专业金融内容，要求：1) 语言生动、适合口语表达；2) 专业准确，包含市场分析；3) 强调投资风险，不推荐具体股票；4) 内容要简洁明了，控制在200字以内；5) 必须分行输出，短句表达，每句不超过20字。")

  // 最大历史记录数
  const MAX_HISTORY = 50

  // 计算属性
  const unreadMessageCount = computed(() => 
    chatHistory.value.filter(msg => !msg.isRead).length
  )

  const hasUnreadMessages = computed(() => unreadMessageCount.value > 0)

  const currentSystemPrompt = computed(() => 
    chatMode.value === 'video' ? digitalHumanPrompt.value : systemPrompt.value
  )

  const modeIcon = computed(() => 
    chatMode.value === 'video' ? '🎥' : '💬'
  )

  const modeTitle = computed(() => 
    chatMode.value === 'video' ? '数字人投资顾问' : '智能投资顾问'
  )

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

  const addMessage = (content, isUser = true, videoUrl = null) => {
    const message = {
      id: Date.now() + Math.random(),
      content,
      isUser,
      timestamp: new Date().toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      isRead: !isUser, // AI消息默认未读
      videoUrl,
      type: videoUrl ? 'video' : 'text'
    }
    
    chatHistory.value.push(message)
    
    // 限制历史记录数量
    if (chatHistory.value.length > MAX_HISTORY) {
      chatHistory.value = chatHistory.value.slice(-MAX_HISTORY)
    }
  }

  const clearChat = () => {
    chatHistory.value = []
    currentVideoTask.value = null
  }

  const markMessagesAsRead = () => {
    chatHistory.value.forEach(msg => {
      msg.isRead = true
    })
  }

  const setLoading = (loading) => {
    isLoading.value = loading
  }

  const setGeneratingVideo = (generating) => {
    isGeneratingVideo.value = generating
  }

  const setCurrentVideoTask = (task) => {
    currentVideoTask.value = task
  }

  const setSystemPrompt = (prompt) => {
    systemPrompt.value = prompt
  }

  const setDigitalHumanPrompt = (prompt) => {
    digitalHumanPrompt.value = prompt
  }

  const switchMode = (mode) => {
    chatMode.value = mode
    // 切换模式时清空当前视频任务
    if (mode === 'text') {
      currentVideoTask.value = null
      isGeneratingVideo.value = false
    }
  }

  return {
    // 状态
    isChatOpen,
    isChatMinimized,
    chatPosition,
    chatHistory,
    isLoading,
    systemPrompt,
    chatMode,
    isGeneratingVideo,
    currentVideoTask,
    
    // 计算属性
    unreadMessageCount,
    hasUnreadMessages,
    currentSystemPrompt,
    modeIcon,
    modeTitle,
    
    // 方法
    toggleChat,
    minimizeChat,
    setChatPosition,
    addMessage,
    clearChat,
    markMessagesAsRead,
    setLoading,
    setSystemPrompt,
    setGeneratingVideo,
    setCurrentVideoTask,
    setDigitalHumanPrompt,
    switchMode
  }
})