<template>
  <div class="daily-insight-page" style="background: #fff8f0; min-height: 100vh;">
    <!-- 头部 -->
    <div class="header">
      <div class="logo" @click="goHome">量化牛牛 - 每日内参</div>
      <div class="date-selector">
        <button class="date-btn" @click="previousDay">← 前一天</button>
        <input v-model="selectedDate" type="date" class="date-input" @change="loadDailyData" />
        <button class="date-btn" @click="nextDay">后一天 →</button>
      </div>
      <div class="header-opt">
        <a href="#" class="share-btn" @click.prevent="shareContent">分享</a>
        <router-link to="/">返回首页</router-link>
      </div>
    </div>

    <!-- 页面内容 -->
    <div class="content">
      <!-- 页面标题 -->
      <div class="page-title-section">
        <h1>每日内参</h1>
        <p class="page-subtitle">{{ formatDate(selectedDate) }} | 专业市场分析与投资建议</p>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-section">
        <div class="loading-spinner"></div>
        <p>正在加载数据...</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="error && !loading" class="error-section">
        <div class="error-icon">⚠️</div>
        <p>{{ error }}</p>
        <button class="retry-btn" @click="loadDailyData">重新加载</button>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && !error && !reportData" class="empty-section">
        <div class="empty-icon">📭</div>
        <p>该日期暂无内参数据</p>
        <button class="retry-btn" @click="loadDailyData">刷新</button>
      </div>

      <!-- 市场概览模块 -->
      <section class="module market-overview" v-if="!loading && !error && reportData">
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

        <!-- ETF推荐 -->
        <div class="etf-recommendations" v-if="etfRecommendations.length > 0">
          <h3>ETF推荐</h3>
          <div class="etf-list">
            <div class="etf-card" v-for="etf in etfRecommendations" :key="etf.code">
              <div class="etf-header">
                <div class="etf-basic">
                  <div class="etf-name">{{ etf.name }}</div>
                  <div class="etf-code">{{ etf.code }}</div>
                </div>
                <div class="etf-category">{{ etf.category }}</div>
              </div>
              <div class="etf-reasoning">
                <p>{{ etf.reasoning }}</p>
              </div>
            </div>
          </div>
        </div>
        <div v-else>
          <p class="no-data">暂无ETF推荐</p>
        </div>
      </section>

      <!-- 重点关注模块 -->
      <section class="module key-focus" v-if="!loading && !error && reportData">
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

      <!-- 个股分析模块 -->
      <section class="module stock-analysis" v-if="!loading && !error && stockAnalysis.length > 0">
        <h2 class="module-title">
          <span class="title-icon">💡</span>
          个股分析
        </h2>
        <div class="stocks-grid">
          <div class="stock-card" v-for="stock in stockAnalysis" :key="stock.code">
            <div class="stock-header">
              <div class="stock-basic">
                <div class="stock-name">{{ stock.name }}</div>
                <div class="stock-code">{{ stock.code }}</div>
              </div>
              <div class="stock-recommendation recommend">
                {{ stock.recommendation }}
              </div>
            </div>
            <!-- 因子评分 -->
            <div class="factor-scores" v-if="Object.keys(stock.factorScores).length > 0">
              <h4>因子评分</h4>
              <div class="score-tags">
                <span 
                  v-for="(score, factor) in stock.factorScores" 
                  :key="factor" 
                  class="score-tag"
                >
                  {{ factor }}: {{ typeof score === 'number' ? score.toFixed(1) : score }}
                </span>
              </div>
            </div>
            <!-- AI分析 -->
            <div class="stock-analysis">
              <h4>AI分析</h4>
              <p>{{ stock.aiAnalysis }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- 风险提示模块 -->
      <section class="module risk-alert" v-if="!loading && !error && reportData">
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

    <!-- 统一页脚 -->
    <FooterComponent />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import FooterComponent from '@/components/FooterComponent.vue'
import { getDailyReportByDate, getLatestDailyReport } from '@/services/dailyReportService'
import {
  canAccessTodayReport,
  getTodayString,
  getYesterdayString,
  getAccessDeniedMessage,
  isToday
} from '@/utils/accessControl'

const router = useRouter()

// 响应式数据
const loading = ref(true)
const error = ref('')
const selectedDate = ref(new Date().toISOString().split('T')[0])
const reportData = ref(null)

// 市场情绪（从 market_sentiment 获取）
const marketSentiment = computed(() => {
  return reportData.value?.market_sentiment || '暂无市场情绪分析'
})

// ETF 推荐
const etfRecommendations = computed(() => {
  if (reportData.value?.etf_recommendations && Array.isArray(reportData.value.etf_recommendations)) {
    return reportData.value.etf_recommendations.map(etf => ({
      code: etf.code || '',
      name: etf.name || '',
      category: etf.category || '',
      reasoning: etf.reasoning || '暂无推荐理由'
    }))
  }
  return []
})

// 重点关注 - 文章大纲
const articleSections = computed(() => {
  if (reportData.value?.article_outline?.sections && Array.isArray(reportData.value.article_outline.sections)) {
    return reportData.value.article_outline.sections
  }
  return []
})

// 个股分析（从 stock_recommendations 映射）
const stockAnalysis = computed(() => {
  if (reportData.value?.stock_recommendations && Array.isArray(reportData.value.stock_recommendations)) {
    return reportData.value.stock_recommendations.map(stock => ({
      code: stock.code || '',
      name: stock.name || '',
      recommendation: '推荐',  // 简化推荐级别
      factorScores: stock.factor_scores || {},
      aiAnalysis: stock.ai_analysis || '暂无分析',
      // 简化其他字段以匹配后端
      currentPrice: '-',
      change: 0,
      targetPrice: '-',
      upside: 0
    }))
  }
  return []
})

// 风险提示（从 risk_warning 获取）
const riskWarning = computed(() => {
  return reportData.value?.risk_warning || '投资有风险，入市需谨慎。请根据自身风险承受能力合理配置资产。'
})

// 方法
const goHome = () => {
  router.push('/')
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
}

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
  
  // 检查是否要切换到今天
  if (isToday(nextDateStr) && !canAccessTodayReport()) {
    alert(getAccessDeniedMessage())
    return
  }
  
  selectedDate.value = nextDateStr
  loadDailyData()
}

const loadDailyData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 检查是否试图访问今天的报告
    if (isToday(selectedDate.value) && !canAccessTodayReport()) {
      // 16:00 前不允许访问今天，自动回退到昨天
      error.value = getAccessDeniedMessage()
      selectedDate.value = getYesterdayString()
      // 继续加载昨天的数据
    }
    
    const result = await getDailyReportByDate(selectedDate.value)
    console.log('getDailyReportByDate响应:', result)
    
    if (result.success && result.data) {
      // 提取真正的报告数据
      let data = result.data
      if (data.data && data.code === 0) {
        data = data.data
      }
      
      if (data.id && data.report_date) {
        reportData.value = data
        error.value = '' // 清除错误信息
        console.log('报告数据加载成功:', data)
      } else {
        throw new Error('数据格式异常')
      }
    } else {
      // 指定日期没有报告，显示空状态，保持用户选择的日期
      console.log(`${selectedDate.value} 日期无数据`)
      error.value = `${formatDate(selectedDate.value)} 暂无内参数据`
      reportData.value = null
    }
  } catch (e) {
    // 处理 403 错误（后端返回的门禁拒绝）
    if (e.status === 403) {
      error.value = getAccessDeniedMessage()
      // 自动回退到昨天
      selectedDate.value = getYesterdayString()
      // 重新加载昨天的数据
      setTimeout(() => loadDailyData(), 100)
    } else {
      error.value = '加载数据失败，请稍后重试'
    }
    console.error('加载每日内参失败:', e)
    reportData.value = null
  } finally {
    loading.value = false
  }
}

const shareContent = () => {
  if (navigator.share) {
    navigator.share({
      title: `量化牛牛每日内参 - ${formatDate(selectedDate.value)}`,
      text: '查看最新的市场分析和投资建议',
      url: window.location.href
    })
  } else {
    navigator.clipboard.writeText(window.location.href)
    alert('链接已复制到剪贴板')
  }
}

// 生命周期
onMounted(() => {
  loadDailyData()
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
  padding: 6px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.header-opt a:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.share-btn {
  background: rgba(255, 255, 255, 0.2);
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

.loading-section {
  text-align: center;
  padding: 60px 20px;
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

/* ETF推荐样式 */
.etf-recommendations h3 {
  color: #ff7f00;
  margin-bottom: 15px;
  font-size: 16px;
}

.etf-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 15px;
}

.etf-card {
  border: 2px solid #ffb380;
  border-radius: 8px;
  padding: 15px;
  background: #fff;
}

.etf-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.etf-basic .etf-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.etf-basic .etf-code {
  font-size: 12px;
  color: #666;
}

.etf-category {
  background: #ff7f00;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.etf-reasoning p {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
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

/* 因子评分样式 */
.factor-scores {
  margin-bottom: 15px;
}

.factor-scores h4 {
  color: #333;
  margin: 10px 0 8px;
  font-size: 14px;
}

.score-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.score-tag {
  background: #f0f8ff;
  color: #333;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  border: 1px solid #d0e7ff;
}

/* 推荐级别样式 */
.stock-recommendation.recommend {
  background: #4CAF50;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
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

/* 个股分析样式 */
.stocks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.stock-card {
  border: 2px solid #ffb380;
  border-radius: 8px;
  padding: 15px;
  background: #fff;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f0f0f0;
}

.stock-basic .stock-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.stock-basic .stock-code {
  font-size: 12px;
  color: #666;
}

.stock-recommendation {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.stock-recommendation.买入 { background: #18A44B; }
.stock-recommendation.增持 { background: #F5A623; }
.stock-recommendation.持有 { background: #4A90E2; }

.stock-price {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.current-price {
  font-size: 20px;
  font-weight: bold;
  color: #ff7f00;
}

.stock-analysis h4 {
  color: #333;
  margin: 10px 0 5px;
  font-size: 14px;
}

.stock-analysis p {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}

.stock-target {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px dashed #f0f0f0;
  font-size: 13px;
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
  
  .stocks-grid {
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