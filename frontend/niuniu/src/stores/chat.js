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
  const systemPrompt = ref("你是脑科学研究平台的数据分析机器人。仅可围绕学术研究、算法验证、历史公开数据模拟与技术实验进行回答。禁止提供荐股、投资推荐、交易建议、买卖时点、收益承诺。若涉及市场类问题，仅输出数据处理方法、模型假设、模拟步骤与局限性。每次回答必须以“本内容为AI生成的学术研究模拟内容，仅供技术参考”开头，以“本内容不代表任何投资建议，不构成任何操作指引”结尾。")

  // 数字人专用提示词
  const digitalHumanPrompt = ref("你是学术实验播报助手，仅输出公开数据说明、算法验证过程、历史数据模拟结论与误差分析。禁止任何投资咨询或交易引导。每次回答必须以“本内容为AI生成的学术研究模拟内容，仅供技术参考”开头，以“本内容不代表任何投资建议，不构成任何操作指引”结尾。")

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
    chatMode.value === 'video' ? '数字人实验播报助手' : '数据分析机器人'
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