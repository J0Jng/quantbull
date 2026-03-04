<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import ChatWidget from './components/ChatWidget.vue'
import { useChatStore } from './stores/chat'

// 初始化聊天状态管理
const chatStore = useChatStore()

const showComplianceModal = ref(false)

// 页面加载时设置默认位置
onMounted(async () => {
  // 设置聊天窗口默认位置（右下角）
  if (window.innerWidth > 768) {
    chatStore.setChatPosition(window.innerWidth - 420, window.innerHeight - 620)
  }

  const hasShown = localStorage.getItem('compliance_declaration_seen')
  if (!hasShown) {
    showComplianceModal.value = true
    localStorage.setItem('compliance_declaration_seen', '1')
  }
})

const closeComplianceModal = () => {
  showComplianceModal.value = false
}

onUnmounted(() => {
})
</script>

<template>
  <div id="app">
    <div class="global-risk-banner">本模块内容仅基于历史公开数据做技术研究，不做任何交易推荐，不承担任何相关法律风险。</div>

    <div v-if="showComplianceModal" class="compliance-modal-mask" @click.self="closeComplianceModal">
      <div class="compliance-modal">
        <h3>网站合规声明</h3>
        <p>平台主体为深脑纪元·数据模拟实验室，仅用于学术研究与数据模拟，无任何商业金融服务属性。</p>
        <p>平台不具备证券投资咨询资格，不提供任何形式的证券投资咨询服务，不推荐股票、不指导买卖操作、不代客理财。</p>
        <p>所有内容仅为历史公开数据统计与模拟，不代表未来走势，不构成任何操作指引，用户据此操作产生的所有风险自行承担。</p>
        <p>员工不得提供任何投资咨询相关服务，违规行为与平台无关。因数据误差、系统故障等不可抗力导致的问题，平台不承担责任。</p>
        <button class="close-btn" @click="closeComplianceModal">我已知悉</button>
      </div>
    </div>

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

.global-risk-banner {
  position: sticky;
  top: 0;
  z-index: 10000;
  background: #fff7e6;
  color: #8c4b00;
  border-bottom: 1px solid #ffd591;
  padding: 8px 12px;
  font-size: 12px;
  text-align: center;
}

.compliance-modal-mask {
  position: fixed;
  inset: 0;
  z-index: 10001;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.compliance-modal {
  width: min(760px, 100%);
  background: #fff;
  border-radius: 10px;
  padding: 20px;
}

.compliance-modal h3 {
  margin: 0 0 10px;
}

.compliance-modal p {
  margin: 8px 0;
  line-height: 1.6;
}

.close-btn {
  margin-top: 10px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background: #ff7f24;
  color: #fff;
  cursor: pointer;
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
