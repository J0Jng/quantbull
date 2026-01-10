<script setup>
import { ref, reactive, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '../stores/chat'
import digitalHumanService from '../services/digitalHumanService'
import chatService from '../services/chatService'

// 定义组件属性
const props = defineProps({
  systemPrompt: {
    type: String,
    default: ""
  },
  initialHint: {
    type: String,
    default: "点击咨询投资问题-"
  }
})

// 使用状态管理
const chatStore = useChatStore()

// 组件状态
const isOpen = computed(() => chatStore.isChatOpen)
const isLoading = computed(() => chatStore.isLoading)
const currentMessage = ref('')
const chatHistory = computed(() => chatStore.chatHistory)
const isDragging = ref(false)
const chatWindowRef = ref(null)
const messagesEndRef = ref(null)
const videoPlayerRef = ref(null)
const maxTokens = ref(500)

// 窗口位置状态
const windowState = reactive({
  x: window.innerWidth - 400 - 20, // 距离右侧20px
  y: window.innerHeight - 600 - 20, // 距离底部20px
  width: 400,
  height: 600,
  isMinimized: computed(() => chatStore.isChatMinimized)
})

// 拖拽相关变量
const dragOffset = reactive({ x: 0, y: 0 })

// 消息滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesEndRef.value) {
      messagesEndRef.value.scrollIntoView({ behavior: 'smooth' })
    }
  })
}

// 发送消息到AI
const sendMessage = async () => {
  const message = currentMessage.value.trim()
  if (!message || isLoading.value) return

  // 添加用户消息
  chatStore.addMessage(message, true)
  currentMessage.value = ''
  chatStore.setLoading(true)

  try {
    if (chatStore.chatMode === 'video') {
      // 数字人视频模式
      chatStore.setGeneratingVideo(true)
      
      // 生成适合视频的金融内容
      const videoPrompt = digitalHumanService.generateFinancialContent(message)
      
      // 先获取AI生成的文本内容
      const aiResponse = await chatService.sendChat(
        videoPrompt,
        chatStore.currentSystemPrompt,
        null,
        0.7,
        maxTokens.value
      )
      
      if (aiResponse.success) {
        // 验证内容合规性
        const validation = digitalHumanService.validateFinancialContent(aiResponse.content)
        if (!validation.isValid) {
          throw new Error(`内容不符合金融监管要求: ${validation.issues.join(', ')}`)
        }
        
        // 生成数字人视频
        const videoResult = await digitalHumanService.generateVideo(
          aiResponse.content,
          40, // 40秒视频
          'professional' // 专业语音风格
        )
        
        if (videoResult.success) {
          // 添加AI文字回复
          chatStore.addMessage(aiResponse.content, false)
          // 如果已生成视频URL，添加视频消息
          if (videoResult.videoUrl) {
            chatStore.addMessage('数字人视频解读', false, videoResult.videoUrl)
          } else {
            // 添加任务信息
            chatStore.setCurrentVideoTask(videoResult)
          }
        } else {
          throw new Error(videoResult.error || '视频生成失败')
        }
      } else {
        throw new Error(aiResponse.error || 'AI生成失败')
      }
    } else {
      // 普通聊天模式
      const response = await chatService.sendChat(
        message, 
        chatStore.currentSystemPrompt,
        null,
        0.7,
        maxTokens.value
      )
      
      if (response.success) {
        chatStore.addMessage(response.content, false)
      } else {
        throw new Error(response.error || 'AI服务暂时无法响应')
      }
    }
  } catch (error) {
    console.error('聊天错误:', error)
    chatStore.addMessage(`抱歉，服务暂时无法响应: ${error.message}`, false)
  } finally {
    chatStore.setLoading(false)
    chatStore.setGeneratingVideo(false)
  }

  scrollToBottom()
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
  
  // 更新存储中的位置
  chatStore.setChatPosition(windowState.x, windowState.y)
}

const stopDrag = () => {
  isDragging.value = false
}

// 切换窗口状态
const toggleWindow = () => {
  chatStore.toggleChat()
}

// 最小化窗口
const minimizeWindow = () => {
  chatStore.minimizeChat()
}

// 切换聊天模式
const switchMode = (mode) => {
  chatStore.switchMode(mode)
}

// 清除聊天记录
const clearChat = () => {
  chatStore.clearChat()
}

// 窗口样式计算
const windowStyles = computed(() => ({
  left: `${chatStore.chatPosition.x}px`,
  top: `${chatStore.chatPosition.y}px`,
  width: `${windowState.width}px`,
  height: windowState.isMinimized ? 'auto' : `${windowState.height}px`,
  transform: windowState.isMinimized ? 'scale(0.8)' : 'scale(1)',
  opacity: windowState.isMinimized ? 0.7 : 1
}))

// 挂载时绑定全局事件
onMounted(() => {
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
  
  // 初始化窗口位置
  if (!chatStore.chatPosition.x && !chatStore.chatPosition.y) {
    chatStore.setChatPosition(window.innerWidth - 450 - 20, window.innerHeight - 600 - 20)
  }
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
          <span class="ai-icon">{{ chatStore.modeIcon }}</span>
          {{ chatStore.modeTitle }}
          <span class="mode-badge" :class="chatStore.chatMode">
            {{ chatStore.chatMode === 'video' ? '视频模式' : '文字模式' }}
          </span>
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
            <template v-if="message.type === 'video' && message.videoUrl">
              <!-- 视频消息 -->
              <div class="video-message">
                <div class="video-text">{{ message.content }}</div>
                <div class="video-player">
                  <video controls width="100%">
                    <source :src="message.videoUrl" type="video/mp4">
                    您的浏览器不支持视频播放。
                  </video>
                  <div class="video-info">
                    <span class="video-duration">{{ Math.ceil(message.content.length / 5) }}秒视频</span>
                  </div>
                </div>
              </div>
            </template>
            <template v-else>
              <!-- 文字消息 -->
              {{ message.content }}
            </template>
          </div>
          <div class="message-meta">
            <span class="message-time">{{ message.timestamp }}</span>
            <span class="message-sender">{{ message.isUser ? '您' : 'AI助手' }}</span>
            <span v-if="message.type === 'video'" class="video-tag">🎥 视频</span>
          </div>
        </div>
        
        <!-- 视频生成状态 -->
        <div v-if="chatStore.isGeneratingVideo" class="message ai-message">
          <div class="message-content loading">
            <span class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </span>
            <div class="video-generating">
              <div>正在生成数字人视频...</div>
              <div class="generating-progress">AI分析 → 内容优化 → 视频渲染</div>
            </div>
          </div>
        </div>
        
        <!-- 视频任务信息 -->
        <div v-if="chatStore.currentVideoTask && chatStore.currentVideoTask.status === 'completed'" class="message ai-message">
          <div class="message-content video-task-info">
            <div class="task-success">✅ 数字人视频生成成功！</div>
            <div class="task-details">
              视频时长: {{ chatStore.currentVideoTask.estimatedDuration || 40 }}秒
              <br>任务ID: {{ chatStore.currentVideoTask.taskId }}
            </div>
          </div>
        </div>
        
        <div v-if="isLoading && chatStore.chatMode === 'text'" class="message ai-message">
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
        <!-- 模式切换工具栏 -->
        <div class="mode-switcher">
          <div class="mode-switch-label">沟通模式：</div>
          <div class="mode-buttons">
            <button 
              class="mode-switch-btn" 
              :class="{ active: chatStore.chatMode === 'text' }"
              @click="switchMode('text')"
            >
              <span class="mode-icon">💬</span>
              <span class="mode-text">文字聊天</span>
            </button>
            <button 
              class="mode-switch-btn" 
              :class="{ active: chatStore.chatMode === 'video' }"
              @click="switchMode('video')"
            >
              <span class="mode-icon">🎥</span>
              <span class="mode-text">数字人视频</span>
            </button>
          </div>
          <button class="tool-btn" @click="clearChat" title="清空对话">
            🗑️ 清空
          </button>
        </div>
        
        <div class="input-container">
          <div class="token-control">
            <label for="maxTokens">max_tokens</label>
            <input
              id="maxTokens"
              type="number"
              v-model.number="maxTokens"
              min="128"
              max="4096"
              step="64"
            />
          </div>
          <textarea
            v-model="currentMessage"
            @keydown="handleKeydown"
            :placeholder="chatStore.chatMode === 'video' ? '输入投资问题，将生成数字人视频解读...' : '请输入投资相关问题...'"
            rows="2"
            class="message-input"
          ></textarea>
          <button 
            @click="sendMessage" 
            :disabled="!currentMessage.trim() || isLoading || chatStore.isGeneratingVideo"
            class="send-btn"
            :class="chatStore.chatMode"
          >
            {{ 
              chatStore.isGeneratingVideo ? '生成中...' : 
              isLoading ? '思考中...' : 
              chatStore.chatMode === 'video' ? '生成视频' : '发送'
            }}
          </button>
        </div>
        <div class="input-hint">
          {{ 
            chatStore.chatMode === 'video' ? 
            '输入问题，AI将生成专业口播视频解读' : 
            '按 Enter 发送，Shift+Enter 换行' 
          }}
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

.mode-badge {
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
}

.mode-badge.text {
  background: rgba(255, 127, 0, 0.1);
  color: #ff7f00;
  border: 1px solid rgba(255, 127, 0, 0.3);
}

.mode-badge.video {
  background: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
  border: 1px solid rgba(255, 107, 107, 0.3);
}

.mode-btn {
  background: rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.mode-btn.active {
  background: rgba(255, 255, 255, 0.4);
  transform: scale(1.1);
}

.mode-btn:hover {
  background: rgba(255, 255, 255, 0.3);
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

/* 视频消息样式 */
.video-message {
  width: 100%;
}

.video-text {
  margin-bottom: 8px;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}

.video-player {
  border-radius: 8px;
  overflow: hidden;
  background: #f0f0f0;
}

.video-player video {
  display: block;
  max-height: 200px;
}

.video-info {
  padding: 8px;
  background: rgba(0, 0, 0, 0.05);
  font-size: 11px;
  color: #666;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.video-tag {
  font-size: 10px;
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  padding: 1px 4px;
  border-radius: 4px;
  margin-left: 8px;
}

/* 视频生成状态 */
.video-generating {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.generating-progress {
  font-size: 10px;
  color: #666;
  font-weight: 500;
}

/* 视频任务信息 */
.video-task-info {
  background: rgba(76, 175, 80, 0.1) !important;
  border-color: rgba(76, 175, 80, 0.3) !important;
}

.task-success {
  color: #4caf50;
  font-weight: 600;
  margin-bottom: 4px;
}

.task-details {
  font-size: 11px;
  color: #666;
  line-height: 1.3;
}

/* 模式指示器 */
.mode-indicator {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.mode-indicator.text {
  background: rgba(255, 127, 0, 0.1);
  color: #ff7f00;
  border: 1px solid rgba(255, 127, 0, 0.2);
}

.mode-indicator.video {
  background: rgba(255, 107, 107, 0.1);
  color: #ff6b6b;
  border: 1px solid rgba(255, 107, 107, 0.2);
}

.chat-input-area {
  border-top: 1px solid #e0e0e0;
  background: white;
  padding: 15px;
}

.input-toolbar {
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
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
  gap: 10px;
  align-items: flex-end;
}

.token-control {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 120px;
}

.token-control label {
  font-size: 12px;
  color: #666;
}

.token-control input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
}

.token-control input:focus {
  outline: none;
  border-color: #ff7f00;
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
  transition: all 0.2s ease;
  min-width: 70px;
}

.send-btn.video {
  background: #ff6b6b;
}

.send-btn.video:hover:not(:disabled) {
  background: #e05b5b;
}

.send-btn:hover:not(:disabled) {
  background: #e06f00;
}

.send-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 模式切换器样式 */
.mode-switcher {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.mode-switch-label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  white-space: nowrap;
}

.mode-buttons {
  display: flex;
  gap: 8px;
}

.mode-switch-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 2px solid #e9ecef;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 12px;
  font-weight: 500;
}

.mode-switch-btn:hover {
  border-color: #ffa500;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(255, 127, 0, 0.15);
}

.mode-switch-btn.active {
  border-color: #ff7f00;
  background: linear-gradient(45deg, #ff7f00, #ffa500);
  color: white;
  box-shadow: 0 2px 12px rgba(255, 127, 0, 0.25);
}

.mode-switch-btn.active:hover {
  border-color: #e06f00;
  background: linear-gradient(45deg, #e06f00, #ff7f00);
}

.mode-switch-btn.video-mode.active {
  border-color: #ff6b6b;
  background: linear-gradient(45deg, #ff6b6b, #ff8e8e);
}

.mode-switch-btn.video-mode.active:hover {
  border-color: #e05b5b;
  background: linear-gradient(45deg, #e05b5b, #ff7b7b);
}

.mode-icon {
  font-size: 14px;
}

.mode-text {
  font-weight: 600;
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
  
  .video-player video {
    max-height: 150px;
  }
  
  .mode-switcher {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .mode-buttons {
    justify-content: center;
  }
  
  .mode-switch-label {
    text-align: center;
  }
}

@media (max-width: 480px) {
  .mode-switch-btn {
    padding: 4px 8px;
    font-size: 11px;
  }
  
  .mode-icon {
    font-size: 12px;
  }
}
</style>