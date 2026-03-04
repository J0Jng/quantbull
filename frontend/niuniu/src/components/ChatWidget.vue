<script setup>
import { ref, reactive, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '../stores/chat'
import chatService from '../services/chatService'

const props = defineProps({
  systemPrompt: {
    type: String,
    default: ''
  },
  initialHint: {
    type: String,
    default: ''
  }
})

const chatStore = useChatStore()

const isOpen = computed(() => chatStore.isChatOpen)
const isLoading = computed(() => chatStore.isLoading)
const chatHistory = computed(() => chatStore.chatHistory)
const currentMessage = ref('')
const isDragging = ref(false)
const chatWindowRef = ref(null)
const messagesEndRef = ref(null)

const windowState = reactive({
  x: window.innerWidth - 400 - 20,
  y: window.innerHeight - 600 - 20,
  width: 400,
  height: 600,
  isMinimized: computed(() => chatStore.isChatMinimized)
})

const dragOffset = reactive({ x: 0, y: 0 })

const scrollToBottom = () => {
  nextTick(() => {
    messagesEndRef.value?.scrollIntoView({ behavior: 'smooth' })
  })
}

const sendMessage = async () => {
  const message = currentMessage.value.trim()
  if (!message || isLoading.value) return

  chatStore.addMessage(message, true)
  currentMessage.value = ''
  chatStore.setLoading(true)
  scrollToBottom()

  try {
    const response = await chatService.sendChat(
      message,
      props.systemPrompt || chatStore.currentSystemPrompt,
      null,
      0.7,
      1000
    )

    if (response.success) {
      chatStore.addMessage(response.content, false)
    } else {
      throw new Error(response.error || 'AI服务暂时无法响应')
    }
  } catch (error) {
    console.error('聊天错误:', error)
    chatStore.addMessage(`抱歉，服务暂时无法响应: ${error.message}`, false)
  } finally {
    chatStore.setLoading(false)
    scrollToBottom()
  }
}

const handleKeydown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

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

  windowState.x = Math.max(0, Math.min(windowState.x, window.innerWidth - windowState.width))
  windowState.y = Math.max(0, Math.min(windowState.y, window.innerHeight - windowState.height))

  chatStore.setChatPosition(windowState.x, windowState.y)
}

const stopDrag = () => {
  isDragging.value = false
}

const toggleWindow = () => {
  chatStore.toggleChat()
  if (chatStore.isChatOpen) {
    chatStore.markMessagesAsRead()
    scrollToBottom()
  }
}

const minimizeWindow = () => {
  chatStore.minimizeChat()
}

const clearChat = () => {
  chatStore.clearChat()
}

const windowStyles = computed(() => ({
  left: `${chatStore.chatPosition.x}px`,
  top: `${chatStore.chatPosition.y}px`,
  width: `${windowState.width}px`,
  height: windowState.isMinimized ? 'auto' : `${windowState.height}px`,
  transform: windowState.isMinimized ? 'scale(0.8)' : 'scale(1)',
  opacity: windowState.isMinimized ? 0.7 : 1
}))

onMounted(() => {
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)

  if (!chatStore.chatPosition.x && !chatStore.chatPosition.y) {
    chatStore.setChatPosition(window.innerWidth - 450 - 20, window.innerHeight - 600 - 20)
  }
})

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
      <div class="hint-bubble" v-if="chatHistory.length === 0 && props.initialHint">
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
          <span class="ai-icon">💬</span>
          数据分析系统
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
        <div class="chat-toolbar">
          <button class="tool-btn" @click="clearChat" title="清空对话">
            🗑️ 清空
          </button>
        </div>

        <div class="input-container">
          <textarea
            v-model="currentMessage"
            class="message-input"
            placeholder="请输入问题，按 Enter 发送，Shift+Enter 换行"
            rows="3"
            @keydown="handleKeydown"
          ></textarea>
          <button
            @click="sendMessage"
            :disabled="!currentMessage.trim() || isLoading"
            class="send-btn"
          >
            {{ isLoading ? '发送中...' : '发送' }}
          </button>
        </div>
        <div class="input-hint">仅支持文本对话</div>
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

.chat-icon.video-mode {
  background: linear-gradient(45deg, #ff7f00, #ff6b6b);
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
  gap: 8px;
}

.ai-icon {
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

.chat-toolbar {
  margin-bottom: 8px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
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
  flex-direction: column;
  gap: 8px;
}

.message-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
  min-height: 84px;
  max-height: 180px;
}

.message-input:focus {
  outline: none;
  border-color: #ff7f00;
}

.send-btn {
  align-self: flex-end;
  background: #ff7f00;
  color: #fff;
  border: none;
  padding: 8px 18px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  background: #e06f00;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.input-hint {
  margin-top: 6px;
  text-align: center;
  font-size: 11px;
  color: #999;
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
  
  .message-input {
    min-height: 72px;
  }
}

@media (max-width: 480px) {
  .send-btn {
    width: 100%;
  }
}
</style>