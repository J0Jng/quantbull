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
        <div class="market-stats" v-if="marketOverview">
          <div class="stat-card" v-if="marketOverview.sh_index">
            <div class="stat-icon">📈</div>
            <div class="stat-info">
              <div class="stat-value">{{ marketOverview.sh_index.value || '-' }}</div>
              <div class="stat-label">上证指数</div>
              <div class="stat-change" :class="(marketOverview.sh_index.change || 0) >= 0 ? 'positive' : 'negative'">
                {{ (marketOverview.sh_index.change || 0) >= 0 ? '+' : '' }}{{ marketOverview.sh_index.change || 0 }}%
              </div>
            </div>
          </div>
          <div class="stat-card" v-if="marketOverview.sz_index">
            <div class="stat-icon">📉</div>
            <div class="stat-info">
              <div class="stat-value">{{ marketOverview.sz_index.value || '-' }}</div>
              <div class="stat-label">深证成指</div>
              <div class="stat-change" :class="(marketOverview.sz_index.change || 0) >= 0 ? 'positive' : 'negative'">
                {{ (marketOverview.sz_index.change || 0) >= 0 ? '+' : '' }}{{ marketOverview.sz_index.change || 0 }}%
              </div>
            </div>
          </div>
          <div class="stat-card" v-if="marketOverview.cyb_index">
            <div class="stat-icon">🔬</div>
            <div class="stat-info">
              <div class="stat-value">{{ marketOverview.cyb_index.value || '-' }}</div>
              <div class="stat-label">创业板指</div>
              <div class="stat-change" :class="(marketOverview.cyb_index.change || 0) >= 0 ? 'positive' : 'negative'">
                {{ (marketOverview.cyb_index.change || 0) >= 0 ? '+' : '' }}{{ marketOverview.cyb_index.change || 0 }}%
              </div>
            </div>
          </div>
          <div class="stat-card" v-if="marketOverview.north_flow">
            <div class="stat-icon">💧</div>
            <div class="stat-info">
              <div class="stat-value">{{ marketOverview.north_flow.value || '-' }}</div>
              <div class="stat-label">北向资金</div>
              <div class="stat-change" :class="(marketOverview.north_flow.amount || 0) >= 0 ? 'positive' : 'negative'">
                {{ (marketOverview.north_flow.amount || 0) >= 0 ? '净流入' : '净流出' }}
              </div>
            </div>
          </div>
        </div>
        <div class="market-stats" v-else>
          <p class="no-data">暂无市场概览数据</p>
        </div>

        <!-- 行业板块表现 -->
        <div class="sector-performance" v-if="sectorPerformance.length > 0">
          <h3>行业板块表现</h3>
          <div class="sector-list">
            <div class="sector-item" v-for="sector in sectorPerformance" :key="sector.name">
              <span class="sector-name">{{ sector.name }}</span>
              <span class="sector-change" :class="{ positive: sector.change > 0, negative: sector.change < 0 }">
                {{ sector.change > 0 ? '+' : '' }}{{ sector.change }}%
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- 重点关注模块 -->
      <section class="module key-focus" v-if="!loading && !error && reportData">
        <h2 class="module-title">
          <span class="title-icon">⭐</span>
          重点关注
        </h2>
        <div class="focus-content">
          <div class="focus-item" v-if="todayEvents.length > 0">
            <h3>今日重要财经事件</h3>
            <ul>
              <li v-for="event in todayEvents" :key="event.id || event.time">
                <span class="event-time">{{ event.time }}</span>
                <span class="event-content">{{ event.content }}</span>
              </li>
            </ul>
          </div>
          <div class="focus-item" v-if="policyAnalysis.content">
            <h3>重大政策解读</h3>
            <div class="policy-analysis">
              <p>{{ policyAnalysis.content }}</p>
              <div class="policy-impact" v-if="policyAnalysis.impact">
                <strong>影响评估：</strong> {{ policyAnalysis.impact }}
              </div>
            </div>
          </div>
          <div class="focus-item" v-if="institutionViews.length > 0">
            <h3>机构观点汇总</h3>
            <div class="institution-views">
              <div class="view-card" v-for="view in institutionViews" :key="view.institution">
                <div class="institution-name">{{ view.institution }}</div>
                <div class="view-content">{{ view.content }}</div>
                <div class="view-rating">{{ view.rating }}</div>
              </div>
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
              <div class="stock-recommendation" :class="stock.recommendation.toLowerCase()">
                {{ stock.recommendation }}
              </div>
            </div>
            <div class="stock-price">
              <div class="current-price">{{ stock.currentPrice }}</div>
              <div class="price-change" :class="{ positive: stock.change > 0, negative: stock.change < 0 }">
                {{ stock.change > 0 ? '+' : '' }}{{ stock.change }}%
              </div>
            </div>
            <div class="stock-analysis">
              <h4>技术面分析</h4>
              <p>{{ stock.technicalAnalysis }}</p>
              <h4>基本面解读</h4>
              <p>{{ stock.fundamentalAnalysis }}</p>
            </div>
            <div class="stock-target">
              <div class="target-price">目标价位：{{ stock.targetPrice }}</div>
              <div class="upside-potential">上涨空间：{{ stock.upside }}%</div>
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
          <div class="risk-item" v-if="marketRisks.length > 0">
            <h3>当前市场风险因素</h3>
            <ul>
              <li v-for="risk in marketRisks" :key="risk.id">{{ risk.content }}</li>
            </ul>
          </div>
          <div class="risk-item" v-if="investmentTips.length > 0">
            <h3>投资注意事项</h3>
            <div class="investment-tips">
              <p v-for="(tip, index) in investmentTips" :key="index">{{ tip }}</p>
            </div>
          </div>
          <div class="risk-item" v-if="riskControls.length > 0">
            <h3>风险控制建议</h3>
            <div class="risk-control">
              <div class="control-item" v-for="(control, index) in riskControls" :key="index">
                <span class="control-icon">✅</span>
                <span>{{ control }}</span>
              </div>
            </div>
          </div>
          <!-- 默认风险提示 -->
          <div class="risk-item" v-if="marketRisks.length === 0 && investmentTips.length === 0">
            <p class="default-risk">投资有风险，入市需谨慎。请根据自身风险承受能力合理配置资产。</p>
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

const router = useRouter()

// 响应式数据
const loading = ref(true)
const error = ref('')
const selectedDate = ref(new Date().toISOString().split('T')[0])
const reportData = ref(null)

// 市场概览数据（从 API 获取或使用默认值）
const marketOverview = computed(() => {
  if (reportData.value?.market_overview) {
    return reportData.value.market_overview
  }
  return null
})

// 行业板块表现
const sectorPerformance = computed(() => {
  if (reportData.value?.sector_performance) {
    return reportData.value.sector_performance
  }
  return []
})

// 重点关注 - 今日事件
const todayEvents = computed(() => {
  if (reportData.value?.key_events) {
    return reportData.value.key_events
  }
  return []
})

// 政策分析
const policyAnalysis = computed(() => {
  if (reportData.value?.policy_analysis) {
    return reportData.value.policy_analysis
  }
  return { content: '暂无政策分析', impact: '' }
})

// 机构观点
const institutionViews = computed(() => {
  if (reportData.value?.institution_views) {
    return reportData.value.institution_views
  }
  return []
})

// 个股分析（从 stock_recommendations 映射）
const stockAnalysis = computed(() => {
  if (reportData.value?.stock_recommendations) {
    return reportData.value.stock_recommendations.map(stock => ({
      code: stock.stock_code || stock.code,
      name: stock.stock_name || stock.name,
      recommendation: stock.rating || stock.recommendation || '持有',
      currentPrice: stock.current_price || stock.price || '-',
      change: stock.change_pct || stock.change || 0,
      technicalAnalysis: stock.technical_analysis || stock.reason || '',
      fundamentalAnalysis: stock.fundamental_analysis || '',
      targetPrice: stock.target_price || '-',
      upside: stock.upside_potential || stock.upside || 0
    }))
  }
  return []
})

// 风险提示
const marketRisks = computed(() => {
  if (reportData.value?.risk_warnings) {
    return reportData.value.risk_warnings.map((content, id) => ({ id, content }))
  }
  return []
})

// 投资建议
const investmentTips = computed(() => {
  if (reportData.value?.investment_tips) {
    return reportData.value.investment_tips
  }
  return []
})

// 风险控制
const riskControls = computed(() => {
  if (reportData.value?.risk_controls) {
    return reportData.value.risk_controls
  }
  return []
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
  selectedDate.value = date.toISOString().split('T')[0]
  loadDailyData()
}

const loadDailyData = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const result = await getDailyReportByDate(selectedDate.value)
    
    if (result.success && result.data) {
      reportData.value = result.data
    } else {
      // 如果指定日期没有报告，尝试获取最新报告
      const latestResult = await getLatestDailyReport()
      if (latestResult.success && latestResult.data) {
        reportData.value = latestResult.data
        // 更新日期为实际报告日期
        if (latestResult.data.report_date) {
          selectedDate.value = latestResult.data.report_date
        }
      } else {
        error.value = result.message || '暂无数据'
        reportData.value = null
      }
    }
  } catch (e) {
    error.value = '加载数据失败，请稍后重试'
    console.error('加载每日内参失败:', e)
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