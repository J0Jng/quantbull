<template>
  <div class="daily-insight-page" style="background: #fff8f0; min-height: 100vh;">
    <!-- 头部 -->
    <div class="header">
      <div class="logo" @click="goHome">
        <span class="logo-icon">🧠</span> 
        <span class="logo-text">脑科学研究室 <span class="logo-divider">|</span> 每日数据模拟分析</span>
      </div>
      <div class="date-selector">
        <button class="date-btn" @click="previousDay" title="前一天">←</button>
        <input v-model="selectedDate" type="date" class="date-input" @change="loadDailyData" />
        <button class="date-btn" @click="nextDay" title="后一天">→</button>
      </div>
      <div class="header-opt">
        <router-link to="/" class="nav-btn">
          <span class="btn-icon">🏠</span> 返回首页
        </router-link>
      </div>
    </div>

    <!-- 页面内容 -->
    <div class="content">
      <!-- 页面标题 -->
      <div class="page-title-section">
        <h1>每日数据模拟分析</h1>
        <p class="page-subtitle">{{ formatDate(selectedDate) }} | 专业数据分析</p>
      </div>

      <div class="state-container">
        <!-- 1. 加载状态 -->
        <div v-if="loading" class="status-section loading-section">
          <div class="loading-spinner"></div>
          <p>{{ loadingText }}</p>
        </div>

        <!-- 2. 非交易日提示 -->
        <div v-else-if="nonTradingDay" class="status-section empty-section">
          <div class="empty-icon">📅</div>
          <p>非交易日缺失数据</p>
        </div>

        <!-- 3. 错误提示 -->
        <div v-else-if="error" class="status-section error-section">
          <div class="error-icon">⚠️</div>
          <p>{{ error }}</p>
          <button class="retry-btn" @click="forceRegenerate">重新生成</button>
        </div>

        <!-- 4. 空状态 -->
        <div v-else-if="!hasReportContent" class="status-section empty-section">
          <div class="empty-icon">📭</div>
          <p>该日期暂无内参数据</p>
          <button class="retry-btn" @click="forceRegenerate">重新生成</button>
        </div>

        <!-- 5. 正常展示模块 -->
        <div v-else class="report-content layout-fadeIn">
          <!-- 市场概览模块 -->
          <section class="module market-overview">
            <h2 class="module-title">
              <span class="title-icon">📊</span>
              市场概览
            </h2>
            <!-- 市场情绪分析 -->
            <div class="market-sentiment">
              <h3>市场情绪分析</h3>
              <div class="sentiment-content">
                <p>{{ marketSentiment }}</p>
              </div>
            </div>
          </section>

          <!-- 重点关注模块 -->
          <section class="module key-focus">
            <h2 class="module-title">
              <span class="title-icon">⭐</span>
              重点关注
            </h2>
            <div class="focus-content">
              <div class="focus-item">
                <h3>文章要点</h3>
                <div v-if="articleSections.length > 0">
                  <ul class="article-sections">
                    <li v-for="(section, index) in articleSections" :key="index" class="section-item">
                      <span class="section-index">{{ index + 1 }}.</span>
                      <span class="section-content">{{ section }}</span>
                    </li>
                  </ul>
                </div>
                <div v-else class="no-content">
                  <p>暂无内容要点</p>
                </div>
              </div>
            </div>
          </section>

          <!-- 风险提示模块 -->
          <section class="module risk-alert">
            <h2 class="module-title">
              <span class="title-icon">⚠️</span>
              风险提示
            </h2>
            <div class="risk-content">
              <div class="risk-item">
                <div class="risk-warning-content">
                  <p>{{ riskWarning }}</p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>

    <!-- 统一页脚 -->
    <FooterComponent />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import FooterComponent from '@/components/FooterComponent.vue'
import { getDailyReportByDate } from '@/services/dailyReportService'
import { getTradingDayStatus } from '@/services/marketService'
import { getYesterdayString } from '@/utils/accessControl'

const router = useRouter()

// ─── 响应式状态 ──────────────────────────────────────────────
const loading = ref(true)
const loadingText = ref('正在加载数据...')
const error = ref('')
const selectedDate = ref(getYesterdayString())
const reportData = ref(null)
const nonTradingDay = ref(false)
const requestSeq = ref(0)

// ─── 轮询相关 ─────────────────────────────────────────────────
const POLL_INTERVAL_MS = 3000
const POLL_MAX_MS = 60000
let pollTimer = null

const clearPoll = () => {
  if (pollTimer !== null) {
    clearTimeout(pollTimer)
    pollTimer = null
  }
}

// ─── 计算属性 ─────────────────────────────────────────────────
const marketSentiment = computed(() =>
  reportData.value?.market_sentiment || '暂无市场情绪分析'
)

const articleSections = computed(() => {
  const sections = reportData.value?.article_outline?.sections
  return Array.isArray(sections) ? sections : []
})

const riskWarning = computed(() =>
  reportData.value?.risk_warning ||
  '本模块内容仅基于历史公开数据做技术研究，不做任何交易推荐，不承担任何相关法律风险。请根据自身风险承受能力合理配置资产。'
)

const hasReportContent = computed(() =>
  !!reportData.value && !isReportTextEmpty(reportData.value)
)

// ─── 工具函数 ─────────────────────────────────────────────────
const isReportTextEmpty = (data) => {
  if (!data) return true
  const hasMarket = (data.market_sentiment || '').trim().length > 0
  const hasOutline = Array.isArray(data.article_outline?.sections) && data.article_outline.sections.length > 0
  const hasRisk = (data.risk_warning || '').trim().length > 0
  return !(hasMarket || hasOutline || hasRisk)
}

const normalizeGenerationStatus = (status) =>
  String(status || '').toLowerCase()

const unwrapBackendData = (result) => {
  if (!result || !result.success || !result.data) return null
  let data = result.data
  if (data && data.data && data.code === 0) data = data.data
  return data
}

const goHome = () => router.push('/')

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
}

const isFutureDate = (dateString) => {
  return new Date(dateString).getTime() > new Date(getYesterdayString()).getTime()
}

// ─── 交易日判断（仅使用专用接口，失败时降级为交易日以避免误判）──
const checkTradingDayStatus = async (dateString) => {
  try {
    const tradingResult = await getTradingDayStatus(dateString)
    if (tradingResult.success && tradingResult.data) {
      let payload = tradingResult.data
      if (payload.data && payload.code === 0) payload = payload.data
      if (typeof payload.is_trading_day === 'boolean') {
        return payload.is_trading_day
          ? { isTrading: true }
          : { isTrading: false }
      }
    }
  } catch (e) {
    console.warn('交易日接口判断失败，按交易日处理:', e)
  }

  // 接口不可用或返回结构异常时，不阻断日报加载
  // 非交易日情况由日报接口的 409 响应兜底处理
  return { isTrading: true }
}

// ─── 将生成状态+数据转换为页面状态 ────────────────────────────
const applyReportData = (data, reqId) => {
  if (reqId !== requestSeq.value) return
  if (!data?.id || !data?.report_date) {
    reportData.value = null
    error.value = '暂无该日期数据，可点击重新生成'
    return
  }
  const status = normalizeGenerationStatus(data.generation_status)
  if (status === 'failed') {
    reportData.value = data
    error.value = '日报生成失败，请稍后重试'
    return
  }
  if (status === 'completed' && !isReportTextEmpty(data)) {
    reportData.value = data
    error.value = ''
    return
  }
  if (status === 'completed' && isReportTextEmpty(data)) {
    reportData.value = data
    error.value = '日报生成完成但内容为空，请稍后重试'
    return
  }
  // pending / processing：保持 loading 继续轮询
  // 调用方负责启动轮询，此处不关闭 loading
}

// ─── 轮询（用于普通加载后遇到 pending/processing 的兜底）────────
const startPolling = (dateStr, startTime, reqId) => {
  clearPoll()
  pollTimer = setTimeout(async () => {
    if (reqId !== requestSeq.value) return

    if (Date.now() - startTime > POLL_MAX_MS) {
      if (reqId === requestSeq.value) {
        error.value = '生成时间较长，可稍后手动重新生成'
        loading.value = false
      }
      return
    }

    try {
      const result = await getDailyReportByDate(dateStr, { refresh: false })
      if (reqId !== requestSeq.value) return

      const data = unwrapBackendData(result)
      const status = normalizeGenerationStatus(data?.generation_status)

      if (status === 'completed' || status === 'failed') {
        applyReportData(data, reqId)
        if (reqId === requestSeq.value) loading.value = false
      } else {
        // 仍在生成中，继续轮询
        startPolling(dateStr, startTime, reqId)
      }
    } catch (e) {
      if (reqId === requestSeq.value) {
        error.value = '轮询获取数据失败，可手动重新生成'
        loading.value = false
      }
    }
  }, POLL_INTERVAL_MS)
}

// ─── 主加载函数 ───────────────────────────────────────────────
/**
 * @param {boolean} forceRefresh - true 时调用 ?refresh=true 强制重建
 */
const loadDailyData = async (forceRefresh = false) => {
  clearPoll()
  const reqId = (requestSeq.value += 1)
  loading.value = true
  loadingText.value = forceRefresh ? '正在重新生成...' : '正在加载数据...'
  error.value = ''
  nonTradingDay.value = false
  reportData.value = null

  try {
    if (isFutureDate(selectedDate.value)) {
      error.value = '无法查看未来日期的每日数据模拟分析'
      return
    }

    const tradingStatus = await checkTradingDayStatus(selectedDate.value)
    if (reqId !== requestSeq.value) return

    if (tradingStatus.isTrading === false) {
      nonTradingDay.value = true
      return
    }

    const result = await getDailyReportByDate(selectedDate.value, { refresh: forceRefresh })
    if (reqId !== requestSeq.value) return

    // 处理 HTTP 层错误（handleRequest 捕获后返回 { success: false, status, message }）
    if (!result.success) {
      if (result.status === 409) {
        error.value = result.message || '市场数据日期不匹配，该日期无法生成日报'
      } else {
        error.value = result.message || '加载数据失败，请稍后重试'
      }
      return
    }

    const data = unwrapBackendData(result)
    const status = normalizeGenerationStatus(data?.generation_status)

    if (status === 'pending' || status === 'processing') {
      // 接口同步返回了处理中状态（非 forceRefresh 场景可能遇到）
      // 保持 loading spinner，启动轮询直到 completed/failed
      loadingText.value = '数据生成中，请稍候...'
      startPolling(selectedDate.value, Date.now(), reqId)
      return // loading 由轮询结束时关闭
    }

    applyReportData(data, reqId)
  } catch (e) {
    if (reqId === requestSeq.value) {
      error.value = '加载数据失败，请稍后重试'
      console.error('加载每日数据模拟分析失败:', e)
    }
  } finally {
    // 仅在非轮询路径上关闭 loading（轮询路径已提前 return）
    if (reqId === requestSeq.value && !pollTimer) {
      loading.value = false
    }
  }
}

// 错误态/空态按钮触发强制重新生成
const forceRegenerate = () => loadDailyData(true)

// ─── 日期导航 ─────────────────────────────────────────────────
const previousDay = () => {
  const date = new Date(selectedDate.value)
  date.setDate(date.getDate() - 1)
  selectedDate.value = date.toISOString().split('T')[0]
  loadDailyData()
}

const nextDay = () => {
  const date = new Date(selectedDate.value)
  date.setDate(date.getDate() + 1)
  const nextDateStr = date.toISOString().split('T')[0]
  if (isFutureDate(nextDateStr)) {
    error.value = '无法查看未来日期的每日数据模拟分析'
    return
  }
  selectedDate.value = nextDateStr
  loadDailyData()
}

// ─── 生命周期 ─────────────────────────────────────────────────
onMounted(() => loadDailyData())
onBeforeUnmount(() => {
  clearPoll()
  // 令所有 in-flight 请求结果失效
  requestSeq.value += 1
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "微软雅黑", sans-serif;
}

.daily-insight-page {
  background-color: #fff8f0;
  min-height: 100vh;
}

.header {
  background-color: #ff7f24;
  padding: 12px 20px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 99;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.logo {
  font-size: 22px;
  font-weight: bold;
  color: #ffffff;
  cursor: pointer;
}

.date-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.date-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.date-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.date-input {
  background: white;
  border: 1px solid #ffb380;
  padding: 6px 10px;
  border-radius: 4px;
  color: #333;
}

.header-opt {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-opt a {
  color: white;
  text-decoration: none;
  font-size: 14px;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-icon {
  font-size: 16px;
}

.logo-icon {
  margin-right: 5px;
  font-size: 24px;
  vertical-align: middle;
}

.logo-divider {
  margin: 0 8px;
  opacity: 0.6;
  font-weight: normal;
}

.header-opt a:hover {
  background-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.nav-btn {
  background: rgba(255, 255, 255, 0.15);
}

.share-btn {
  background: rgba(255, 255, 255, 0.2);
}

.admin-generate-btn {
  background: rgba(255, 255, 255, 0.25);
  font-weight: bold;
}

.admin-generate-btn.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
  transform: none;
}

.content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.page-title-section h1 {
  font-size: 32px;
  color: #ff7f00;
  margin-bottom: 10px;
}

.page-subtitle {
  color: #666;
  font-size: 16px;
}

.status-section {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}

.loading-section {
  color: #ff7f00;
}

.error-section, .empty-section {
  color: #666;
}

.error-icon, .empty-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.retry-btn {
  margin-top: 20px;
  background: #ff7f00;
  color: white;
  border: none;
  padding: 8px 24px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.retry-btn:hover {
  background: #e67300;
  box-shadow: 0 4px 12px rgba(255, 127, 0, 0.2);
}

.retry-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.layout-fadeIn {
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ff7f00;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.module {
  background: white;
  border-radius: 8px;
  margin-bottom: 20px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 2px solid #ffb380;
}

.module-title {
  font-size: 22px;
  color: #ff7f00;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 24px;
}

/* 市场情绪样式 */
.market-sentiment {
  margin-bottom: 20px;
}

.market-sentiment h3 {
  color: #ff7f00;
  margin-bottom: 10px;
  font-size: 16px;
}

.sentiment-content {
  background: #fff6ee;
  padding: 15px;
  border-radius: 6px;
  line-height: 1.6;
}

/* 文章要点样式 */
.article-sections {
  list-style: none;
  padding: 0;
}

.section-item {
  display: flex;
  align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.section-item:last-child {
  border-bottom: none;
}

.section-index {
  color: #ff7f00;
  font-weight: bold;
  margin-right: 10px;
  min-width: 20px;
}

.section-content {
  flex: 1;
  color: #333;
  line-height: 1.5;
}

.no-content {
  text-align: center;
  color: #999;
  padding: 20px 0;
}

/* 风险提示样式 */
.risk-warning-content {
  background: #fff5f5;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid #ff4444;
  line-height: 1.6;
}

.risk-warning-content p {
  margin: 0;
  color: #333;
}

/* 市场概览样式 */
.market-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 6px;
  border-left: 4px solid #ff7f00;
}

.stat-icon {
  font-size: 24px;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin: 2px 0;
}

.stat-change {
  font-size: 14px;
  font-weight: bold;
}

.positive { color: #18A44B; }
.negative { color: #C62828; }

.sector-performance h3 {
  margin-bottom: 10px;
  color: #333;
}

.sector-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}

.sector-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #fff6ee;
  border-radius: 4px;
}

/* 重点关注样式 */
.focus-content {
  display: grid;
  gap: 20px;
}

.focus-item h3 {
  color: #ff7f00;
  margin-bottom: 10px;
  font-size: 16px;
}

.focus-item ul li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.event-time {
  color: #ff7f00;
  font-weight: bold;
  min-width: 60px;
}

.policy-analysis {
  background: #fff6ee;
  padding: 15px;
  border-radius: 6px;
}

.policy-impact {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed #ffb380;
}

.institution-views {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.view-card {
  background: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
  border-left: 3px solid #ff7f00;
}

.institution-name {
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.view-content {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.view-rating {
  font-size: 12px;
  color: #ff7f00;
  font-weight: bold;
}

/* 风险提示样式 */
.risk-content {
  display: grid;
  gap: 20px;
}

.risk-item h3 {
  color: #C62828;
  margin-bottom: 10px;
  font-size: 16px;
}

.risk-item ul li {
  padding: 5px 0;
  border-bottom: 1px solid #f0f0f0;
}

.investment-tips p {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.risk-control {
  display: grid;
  gap: 10px;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
}

.control-icon {
  color: #18A44B;
}

.page-footer {
  background: #ff7f24;
  color: white;
  text-align: center;
  padding: 100px 0;
  margin-top: 60px;
  width: 100%;
  max-width: 3000px;
  margin-left: auto;
  margin-right: auto;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(255, 127, 36, 0.3);
  border: 4px solid #ff9933;
  font-size: 18px;
  font-weight: bold;
}

.page-footer p {
  margin: 5px 0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 10px;
    padding: 15px 20px;
  }
  
  .date-selector {
    order: 2;
  }
  
  .header-opt {
    order: 3;
  }
  
  .market-stats {
    grid-template-columns: 1fr;
  }
  
.institution-views {
    grid-template-columns: 1fr;
  }
  
  .content {
    padding: 15px;
  }
}
</style>