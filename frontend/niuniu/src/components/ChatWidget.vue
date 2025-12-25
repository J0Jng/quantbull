<script setup>
import { ref, reactive, computed, nextTick, onMounted, onUnmounted } from 'vue'

// 定义组件属性
const props = defineProps({
  systemPrompt: {
    type: String,
    default: "你是一个专业的投资顾问和量化分析助手，专注于为用户提供投资策略、市场分析和量化交易相关的帮助。你的职责包括分析用户的投资问题和需求，提供基于市场数据的投资建议，解释量化策略的基本原理，提供风险控制和资产配置建议，回答关于股票、基金、期货等金融产品的相关问题，解释技术指标和基本面分析方法，提供投资组合优化建议。在回答时，请保持专业性和准确性，提示投资风险，强调投资有风险，入市需谨慎，提供实用、可操作的建议，对复杂问题提供分步骤的解决方案，在适当时候推荐平台上的其他专业服务或工具，避免给出过于具体的投资操作建议，鼓励用户进一步咨询专业顾问，始终提醒用户根据自身风险承受能力做出投资决策。"
  },
  initialHint: {
    type: String,
    default: "点击咨询投资问题-"
  }
})

// 状态管理
const isOpen = ref(false)
const isLoading = ref(false)
const currentMessage = ref('')
const chatHistory = ref([])
const isDragging = ref(false)
const chatWindowRef = ref(null)
const messagesEndRef = ref(null)

// 窗口位置状态
const windowState = reactive({
  x: window.innerWidth - 400 - 20, // 距离右侧20px
  y: window.innerHeight - 600 - 20, // 距离底部20px
  width: 400,
  height: 600,
  isMinimized: false
})

// 拖拽相关变量
const dragOffset = reactive({ x: 0, y: 0 })

// 最大历史记录数
const MAX_HISTORY = 50

// 消息滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesEndRef.value) {
      messagesEndRef.value.scrollIntoView({ behavior: 'smooth' })
    }
  })
}

// 添加消息到历史记录
const addMessage = (content, isUser = true) => {
  const message = {
    id: Date.now(),
    content,
    isUser,
    timestamp: new Date().toLocaleTimeString('zh-CN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }
  
  chatHistory.value.push(message)
  
  // 限制历史记录数量
  if (chatHistory.value.length > MAX_HISTORY) {
    chatHistory.value = chatHistory.value.slice(-MAX_HISTORY)
  }
  
  scrollToBottom()
}

// 发送消息到AI
const sendMessage = async () => {
  const message = currentMessage.value.trim()
  if (!message || isLoading.value) return

  // 添加用户消息
  addMessage(message, true)
  currentMessage.value = ''
  isLoading.value = true

  try {
    // 调用API接口
    const response = await fetch('/api/ai/api/ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: message,
        system_prompt: props.systemPrompt,
        model: null, // 让API自动路由
        temperature: 0.7,
        max_tokens: 1000
      })
    })

    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`)
    }

    const data = await response.json()
    
    // 添加AI回复
    addMessage(data.content, false)
    
  } catch (error) {
    console.error('聊天错误:', error)
    addMessage('抱歉，AI助手暂时无法响应，请稍后再试。', false)
  } finally {
    isLoading.value = false
  }
}

// 处理输入框键盘事件
const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 拖拽相关函数
const startDrag = (e) => {
  if (windowState.isMinimized) return
  
  isDragging.value = true
  dragOffset.x = e.clientX - windowState.x
  dragOffset.y = e.clientY - windowState.y
  
  e.preventDefault()
}

const onDrag = (e) => {
  if (!isDragging.value) return
  
  windowState.x = e.clientX - dragOffset.x
  windowState.y = e.clientY - dragOffset.y
  
  // 边界检查
  windowState.x = Math.max(0, Math.min(windowState.x, window.innerWidth - windowState.width))
  windowState.y = Math.max(0, Math.min(windowState.y, window.innerHeight - windowState.height))
}

const stopDrag = () => {
  isDragging.value = false
}

// 切换窗口状态
const toggleWindow = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value && windowState.isMinimized) {
    windowState.isMinimized = false
  }
}

// 最小化窗口
const minimizeWindow = () => {
  windowState.isMinimized = !windowState.isMinimized
}

// 清除聊天记录
const clearChat = () => {
  chatHistory.value = []
}

// 窗口样式计算
const windowStyles = computed(() => ({
  left: `${windowState.x}px`,
  top: `${windowState.y}px`,
  width: `${windowState.width}px`,
  height: windowState.isMinimized ? 'auto' : `${windowState.height}px`,
  transform: windowState.isMinimized ? 'scale(0.8)' : 'scale(1)',
  opacity: windowState.isMinimized ? 0.7 : 1
}))

// 挂载时绑定全局事件
onMounted(() => {
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
})

// 卸载时清理事件
onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
})
</script>

<template>
  <div class="chat-widget-container" v-if="!windowState.isMinimized || !isOpen">
    <!-- 最小化图标按钮 -->
    <div 
      v-if="!isOpen || windowState.isMinimized"
      class="chat-icon"
      :style="{ 
        right: windowState.isMinimized ? `${windowState.x}px` : '20px',
        bottom: windowState.isMinimized ? `${windowState.y}px` : '20px'
      }"
      @click="toggleWindow"
    >
      💬
      <div class="chat-badge" v-if="chatHistory.length > 0">
        {{ Math.min(chatHistory.length, 99) }}
      </div>
      <div class="hint-bubble" v-if="chatHistory.length === 0">
        {{ props.initialHint }}
      </div>
    </div>

    <!-- 聊天窗口 -->
    <div
      v-if="isOpen && !windowState.isMinimized"
      ref="chatWindowRef"
      class="chat-window"
      :style="windowStyles"
    >
      <!-- 标题栏 -->
      <div class="chat-header" @mousedown="startDrag">
        <div class="chat-title">
          <span class="ai-icon">🤖</span>
          智能投资顾问
        </div>
        <div class="chat-actions">
          <button class="action-btn" @click="minimizeWindow" title="最小化">
            −
          </button>
          <button class="action-btn" @click="toggleWindow" title="关闭">
            ×
          </button>
        </div>
      </div>

      <!-- 消息区域 -->
      <div class="chat-messages">
        <div 
          v-for="message in chatHistory"
          :key="message.id"
          :class="['message', message.isUser ? 'user-message' : 'ai-message']"
        >
          <div class="message-content">
            {{ message.content }}
          </div>
          <div class="message-meta">
            <span class="message-time">{{ message.timestamp }}</span>
            <span class="message-sender">{{ message.isUser ? '您' : 'AI助手' }}</span>
          </div>
        </div>
        <div v-if="isLoading" class="message ai-message">
          <div class="message-content loading">
            <span class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </span>
            正在思考中...
          </div>
        </div>
        <div ref="messagesEndRef"></div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-toolbar">
          <button class="tool-btn" @click="clearChat" title="清空对话">
            🗑️
          </button>
        </div>
        <div class="input-container">
          <textarea
            v-model="currentMessage"
            @keydown="handleKeydown"
            placeholder="请输入投资相关问题..."
            rows="2"
            class="message-input"
          ></textarea>
          <button 
            @click="sendMessage" 
            :disabled="!currentMessage.trim() || isLoading"
            class="send-btn"
          >
            {{ isLoading ? '发送中...' : '发送' }}
          </button>
        </div>
        <div class="input-hint">
          按 Enter 发送，Shift+Enter 换行
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-widget-container {
  position: fixed;
  z-index: 10000;
  pointer-events: none;
}

.chat-icon {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: 60px;
  height: 60px;
  background: linear-gradient(45deg, #ff7f00, #ffa500);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(255, 127, 0, 0.3);
  transition: all 0.3s ease;
  pointer-events: auto;
  z-index: 10001;
}

.chat-icon:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(255, 127, 0, 0.4);
}

.chat-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4444;
  color: white;
  border-radius: 10px;
  min-width: 18px;
  height: 18px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.hint-bubble {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  color: #ff7f00;
  padding: 8px 12px;
  border-radius: 18px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #ff7f00;
  margin-bottom: 10px;
  animation: hintPulse 2s infinite;
}

.hint-bubble::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border-width: 6px;
  border-style: solid;
  border-color: white transparent transparent transparent;
}

@keyframes hintPulse {
  0% { transform: translateX(-50%) scale(1); }
  50% { transform: translateX(-50%) scale(1.05); }
  100% { transform: translateX(-50%) scale(1); }
}

.chat-window {
  position: fixed;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  pointer-events: auto;
  transition: all 0.3s ease;
  border: 1px solid #ff7f00;
}

.chat-header {
  background: linear-gradient(45deg, #ff7f00, #ffa500);
  color: white;
  padding: 15px 20px;
  cursor: move;
  display: flex;
  justify-content: space-between;
  align-items: center;
  user-select: none;
}

.chat-title {
  display: flex;
  align-items: center;
  font-weight: 600;
  font-size: 14px;
}

.ai-icon {
  margin-right: 8px;
  font-size: 16px;
}

.chat-actions {
  display: flex;
  gap: 5px;
}

.action-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 3px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  transition: background 0.2s ease;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.chat-messages {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  background: #f8f9fa;
  max-height: 400px;
}

.message {
  margin-bottom: 15px;
  opacity: 0;
  animation: fadeIn 0.3s ease forwards;
}

@keyframes fadeIn {
  to {
    opacity: 1;
  }
}

.message-content {
  padding: 10px 15px;
  border-radius: 18px;
  max-width: 80%;
  word-wrap: break-word;
  line-height: 1.4;
  position: relative;
}

.user-message {
  display: flex;
  justify-content: flex-end;
}

.user-message .message-content {
  background: #ff7f00;
  color: white;
  border-bottom-right-radius: 4px;
}

.ai-message {
  display: flex;
  justify-content: flex-start;
}

.ai-message .message-content {
  background: white;
  color: #333;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 4px;
}

.message-meta {
  font-size: 10px;
  color: #999;
  margin-top: 4px;
  display: flex;
  justify-content: space-between;
  padding: 0 5px;
}

.loading .typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}

.typing-indicator span {
  width: 4px;
  height: 4px;
  background: #999;
  border-radius: 50%;
  animation: typing 1s infinite ease-in-out;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-5px);
  }
}

.chat-input-area {
  border-top: 1px solid #e0e0e0;
  background: white;
  padding: 15px;
}

.input-toolbar {
  margin-bottom: 10px;
}

.tool-btn {
  background: none;
  border: none;
  padding: 5px;
  cursor: pointer;
  border-radius: 3px;
  transition: background 0.2s ease;
}

.tool-btn:hover {
  background: #f0f0f0;
}

.input-container {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: none;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.4;
  min-height: 40px;
  max-height: 120px;
}

.message-input:focus {
  outline: none;
  border-color: #ff7f00;
}

.send-btn {
  background: #ff7f00;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s ease;
  min-width: 70px;
}

.send-btn:hover:not(:disabled) {
  background: #e06f00;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.input-hint {
  font-size: 11px;
  color: #999;
  margin-top: 5px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-window {
    width: 90vw !important;
    height: 70vh !important;
    left: 5vw !important;
    top: 15vh !important;
    right: auto;
    bottom: auto;
  }
}
</style>