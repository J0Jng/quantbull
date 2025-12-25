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

      <!-- 市场概览模块 -->
      <section class="module market-overview" v-if="!loading">
        <h2 class="module-title">
          <span class="title-icon">📊</span>
          市场概览
        </h2>
        <div class="market-stats">
          <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-info">
              <div class="stat-value">3,525.68</div>
              <div class="stat-label">上证指数</div>
              <div class="stat-change positive">+1.25%</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📉</div>
            <div class="stat-info">
              <div class="stat-value">11,268.45</div>
              <div class="stat-label">深证成指</div>
              <div class="stat-change positive">+0.89%</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">🔬</div>
            <div class="stat-info">
              <div class="stat-value">2,345.12</div>
              <div class="stat-label">创业板指</div>
              <div class="stat-change negative">-0.32%</div>
            </div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">💧</div>
            <div class="stat-info">
              <div class="stat-value">+128.45亿</div>
              <div class="stat-label">北向资金</div>
              <div class="stat-change positive">净流入</div>
            </div>
          </div>
        </div>

        <!-- 行业板块表现 -->
        <div class="sector-performance">
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
      <section class="module key-focus" v-if="!loading">
        <h2 class="module-title">
          <span class="title-icon">⭐</span>
          重点关注
        </h2>
        <div class="focus-content">
          <div class="focus-item">
            <h3>今日重要财经事件</h3>
            <ul>
              <li v-for="event in todayEvents" :key="event.id">
                <span class="event-time">{{ event.time }}</span>
                <span class="event-content">{{ event.content }}</span>
              </li>
            </ul>
          </div>
          <div class="focus-item">
            <h3>重大政策解读</h3>
            <div class="policy-analysis">
              <p>{{ policyAnalysis.content }}</p>
              <div class="policy-impact">
                <strong>影响评估：</strong> {{ policyAnalysis.impact }}
              </div>
            </div>
          </div>
          <div class="focus-item">
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
      <section class="module stock-analysis" v-if="!loading">
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
      <section class="module risk-alert" v-if="!loading">
        <h2 class="module-title">
          <span class="title-icon">⚠️</span>
          风险提示
        </h2>
        <div class="risk-content">
          <div class="risk-item">
            <h3>当前市场风险因素</h3>
            <ul>
              <li v-for="risk in marketRisks" :key="risk.id">{{ risk.content }}</li>
            </ul>
          </div>
          <div class="risk-item">
            <h3>投资注意事项</h3>
            <div class="investment-tips">
              <p v-for="tip in investmentTips" :key="tip">{{ tip }}</p>
            </div>
          </div>
          <div class="risk-item">
            <h3>风险控制建议</h3>
            <div class="risk-control">
              <div class="control-item" v-for="control in riskControls" :key="control">
                <span class="control-icon">✅</span>
                <span>{{ control }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 页脚 -->
    <footer class="page-footer">
      <p>本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
      <p>量化牛牛投研团队出品</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 响应式数据
const loading = ref(true)
const selectedDate = ref(new Date().toISOString().split('T')[0])

// 市场概览数据
const sectorPerformance = ref([
  { name: '新能源', change: 3.2 },
  { name: '半导体', change: 2.1 },
  { name: '医药生物', change: 1.8 },
  { name: '消费电子', change: 1.5 },
  { name: '金融', change: -0.5 },
  { name: '房地产', change: -1.2 }
])

// 重点关注数据
const todayEvents = ref([
  { id: 1, time: '09:30', content: '国务院新闻办公室举行宏观经济形势发布会' },
  { id: 2, time: '14:00', content: '工信部召开新能源汽车产业发展座谈会' },
  { id: 3, time: '16:00', content: '央行发布金融统计数据报告' }
])

const policyAnalysis = ref({
  content: '近期央行降准释放流动性，市场资金面相对宽裕，利好实体经济融资环境。',
  impact: '短期提振市场情绪，中长期需关注政策效果传导。'
})

const institutionViews = ref([
  { institution: '中信证券', content: '看好科技成长股表现，建议关注AI产业链', rating: '积极' },
  { institution: '中金公司', content: '市场震荡上行，建议均衡配置', rating: '谨慎乐观' },
  { institution: '国泰君安', content: '关注政策受益板块，挖掘结构性机会', rating: '中性' }
])

// 个股分析数据
const stockAnalysis = ref([
  {
    code: '300750',
    name: '宁德时代',
    recommendation: '买入',
    currentPrice: '545.40',
    change: 5.23,
    technicalAnalysis: '股价突破前期高点，技术形态良好，建议关注成交量配合情况。',
    fundamentalAnalysis: '新能源车销量持续增长，公司技术领先，市场份额稳固。',
    targetPrice: '600.00',
    upside: 10.0
  },
  {
    code: '000858',
    name: '五粮液',
    recommendation: '增持',
    currentPrice: '142.30',
    change: 1.2,
    technicalAnalysis: '股价在支撑位附近震荡，等待突破确认。',
    fundamentalAnalysis: '白酒消费复苏，公司品牌优势明显，盈利能力强。',
    targetPrice: '160.00',
    upside: 12.4
  }
])

// 风险提示数据
const marketRisks = ref([
  { id: 1, content: '全球经济复苏不确定性增加' },
  { id: 2, content: '地缘政治风险持续发酵' },
  { id: 3, content: '通胀压力可能超预期' }
])

const investmentTips = ref([
  '控制仓位，避免过度集中投资',
  '关注基本面，远离概念炒作',
  '设置止损位，做好风险防范'
])

const riskControls = ref([
  '分散投资降低单一风险',
  '定期评估投资组合',
  '设置明确的止盈止损点'
])

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
  // 模拟数据加载
  setTimeout(() => {
    loading.value = false
  }, 1000)
}

const shareContent = () => {
  // 简单的分享功能实现
  if (navigator.share) {
    navigator.share({
      title: `量化牛牛每日内参 - ${formatDate(selectedDate.value)}`,
      text: '查看最新的市场分析和投资建议',
      url: window.location.href
    })
  } else {
    // 降级方案
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