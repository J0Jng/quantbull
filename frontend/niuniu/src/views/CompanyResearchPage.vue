<template>
  <div class="company-research-page" style="background: #fff8f0; min-height: 100vh;">
    <!-- 头部 -->
    <div class="header">
      <div class="logo" @click="goHome">量化牛牛研报中心</div>
      <div class="header-opt">
        <router-link to="/shop">商店</router-link>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input v-model="searchQuery" type="text" placeholder="搜索公司、行业、关键字..." />
      <button class="search-btn">搜索</button>
    </div>

    <!-- 分类导航 -->
    <div class="category-nav">
      <a href="#all" class="category-item" :class="{ active: activeCategory==='all' }" @click.prevent="go('all')">全部</a>
      <a href="#buy" class="category-item" :class="{ active: activeCategory==='buy' }" @click.prevent="go('buy')">买入</a>
      <a href="#add" class="category-item" :class="{ active: activeCategory==='add' }" @click.prevent="go('add')">增持</a>
      <a href="#hold" class="category-item" :class="{ active: activeCategory==='hold' }" @click.prevent="go('hold')">持有</a>
      <a href="#reduce" class="category-item" :class="{ active: activeCategory==='reduce' }" @click.prevent="go('reduce')">减持</a>
      <a href="#sell" class="category-item" :class="{ active: activeCategory==='sell' }" @click.prevent="go('sell')">卖出</a>
    </div>

    <!-- 主容器 -->
    <div class="container">
      <!-- 全部研报 -->
      <h2 class="section-title" id="all">全部研报</h2>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-section">
        <div class="loading-spinner"></div>
        <p>正在加载研报数据...</p>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="error && !loading" class="error-section">
        <p class="error-text">{{ error }}</p>
        <button class="retry-btn" @click="fetchReports">重新加载</button>
      </div>
      
      <!-- 研报列表 -->
      <template v-if="!loading && !error">
        <div class="results-info">
          共找到 {{ filteredReports.length }} 条研报
        </div>
        <div class="report-grid">
          <div class="report-card" v-for="item in filteredReports" :key="item.id">
            <div class="report-info">
              <div class="stock-info">
                <span class="stock-name">{{ item.name }}</span>
                <span :class="item.tagClass">{{ item.tag }}</span>
              </div>
              <div class="price">{{ item.priceLabel }}：<span class="current-price">{{ item.price }}</span></div>
              <div class="profit">{{ item.profitLabel }}:<span class="profit-value" :class="{ 'positive': parseFloat(item.profit) > 0, 'negative': parseFloat(item.profit) < 0 }">{{ item.profit }}</span></div>
              <ul class="report-tags">
                <li v-for="(tag, i) in item.tags" :key="i">{{ tag }}</li>
              </ul>
              <div style="clear:both;"></div>
              <button class="view-btn" @click="viewReport(item)">查看研报</button>
            </div>
          </div>
        </div>
        
        <!-- 无结果提示 -->
        <div v-if="filteredReports.length === 0" class="no-results">
          <p>暂无符合条件的研报</p>
        </div>
      </template>
    </div>

    <!-- 底部 -->
    <FooterComponent />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FooterComponent from '@/components/FooterComponent.vue'
import { getReportSummaries } from '@/services/reportService'

const router = useRouter()

// 响应式状态
const searchQuery = ref('')
const activeCategory = ref('all')
const loading = ref(true)
const error = ref('')
const reportList = ref([])

// 评级映射
const ratingMap = {
  'buy': { tag: '买入', tagClass: 'mai-ru' },
  'add': { tag: '增持', tagClass: 'mai-ru-zeng' },
  'hold': { tag: '持有', tagClass: 'chi-you' },
  'reduce': { tag: '减持', tagClass: 'jian-chi' },
  'sell': { tag: '卖出', tagClass: 'mai-chu' }
}

// 加载研报数据
const fetchReports = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const params = {
      limit: 50,
      offset: 0
    }
    
    // 根据分类筛选
    if (activeCategory.value !== 'all') {
      params.rating = activeCategory.value
    }
    
    const result = await getReportSummaries(params)
    
    if (result.success && result.data) {
      // 转换 API 数据格式为前端展示格式
      const reports = result.data.reports || result.data.items || result.data || []
      reportList.value = reports.map(item => ({
        id: item.id,
        name: item.stock_name || item.title || '未知',
        tag: ratingMap[item.rating]?.tag || item.rating || '持有',
        tagClass: ratingMap[item.rating]?.tagClass || 'chi-you',
        priceLabel: item.price_label || '当前价',
        price: item.current_price ? `${item.current_price}元` : '-',
        profitLabel: item.profit_label || '目标价格',
        profit: item.target_return ? `${item.target_return}%` : '-',
        tags: item.tags || item.sectors || []
      }))
    } else {
      error.value = result.message || '获取研报失败'
    }
  } catch (e) {
    error.value = '加载研报数据失败'
    console.error('获取研报列表失败:', e)
  } finally {
    loading.value = false
  }
}

// 筛选后的研报列表
const filteredReports = computed(() => {
  let filtered = reportList.value
  
  // 根据分类过滤（如果 API 不支持服务端筛选）
  if (activeCategory.value !== 'all') {
    filtered = filtered.filter(item => {
      switch (activeCategory.value) {
        case 'buy': return item.tagClass === 'mai-ru'
        case 'add': return item.tagClass === 'mai-ru-zeng'
        case 'hold': return item.tagClass === 'chi-you'
        case 'reduce': return item.tagClass === 'jian-chi'
        case 'sell': return item.tagClass === 'mai-chu'
        default: return true
      }
    })
  }
  
  // 根据搜索关键词过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(item => 
      item.name.toLowerCase().includes(query) ||
      item.tags.some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  return filtered
})

function goHome() {
  router.push('/')
}

function viewReport(item) {
  // 使用真实的研报 ID
  router.push(`/company-research/research-detail/${item.id}`)
}

function go(id) {
  activeCategory.value = id
  // 切换分类时重新加载数据
  fetchReports()
}

// 搜索处理
function handleSearch() {
  // 本地搜索，无需重新请求 API
}

// 生命周期
onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
/* 复用商店页面的样式并稍作调整 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "微软雅黑", sans-serif;
}

.company-research-page {
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

.header-opt {
  display: flex;
  align-items: center;
  gap: 20px;
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

.search-bar {
  padding: 15px 20px;
  background-color: white;
  display: flex;
  gap: 10px;
  align-items: center;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.search-bar input {
  flex: 1;
  padding: 12px 15px;
  border: 1px solid #ffb380;
  border-radius: 6px;
  outline: none;
  font-size: 14px;
  transition: border-color 0.3s;
}

.search-bar input:focus {
  border-color: #ff7f24;
  box-shadow: 0 0 0 2px rgba(255, 127, 36, 0.2);
}

.search-btn {
  background-color: #ff7f24;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background-color: #ff6a00;
}

.category-nav {
  background-color: #ff9933;
  padding: 12px 20px;
  overflow-x: auto;
  white-space: nowrap;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.category-item {
  display: inline-block;
  color: white;
  text-decoration: none;
  padding: 8px 18px;
  margin-right: 8px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.category-item.active {
  background-color: #ff7f24;
  font-weight: bold;
}

.category-item:hover:not(.active) {
  background-color: rgba(255, 255, 255, 0.2);
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.section-title {
  font-size: 22px;
  color: #ffffff;
  border-left: 4px solid #ff7f24;
  padding-left: 12px;
  margin: 20px 0 15px;
  font-weight: bold;
}

.results-info {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.report-card {
  background-color: white;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #ffb380;
  transition: all 0.3s ease;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  min-width: 300px;
}

.report-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(255, 127, 36, 0.25);
  border-color: #ff7f24;
}

.report-info .stock-info {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #f0f0f0;
}

.stock-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.report-tags {
  margin: 15px 0;
  overflow: hidden;
}

.report-tags li {
  background: linear-gradient(to right, #ffeedd, #fff6ee);
  padding: 4px 8px;
  font-size: 12px;
  float: left;
  margin-right: 8px;
  margin-bottom: 8px;
  border-radius: 3px;
  color: #ff7f24;
}

.price,
.profit {
  font-size: 14px;
  margin-top: 8px;
  color: #666;
}

.current-price {
  float: right;
  color: #ff7f24;
  font-weight: bold;
  font-size: 16px;
}

.profit-value {
  float: right;
  font-weight: bold;
}

.profit-value.positive {
  color: #18A44B;
}

.profit-value.negative {
  color: #C62828;
}

.view-btn {
  font-size: 14px;
  padding: 10px 0;
  color: #ff7f24;
  border: 1px solid #ff7f24;
  border-radius: 6px;
  cursor: pointer;
  width: 100%;
  margin-top: 15px;
  background: #fff;
  transition: all 0.3s;
  font-weight: bold;
}

.view-btn:hover {
  background-color: #ff7f24;
  color: white;
  box-shadow: 0 4px 12px rgba(255, 127, 36, 0.3);
}

.no-results {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 16px;
}

.no-results p {
  margin: 0;
}

.footer {
  background-color: #ff7f24;
  color: white;
  text-align: center;
  padding: 25px;
  margin-top: 40px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.footer p {
  margin: 5px 0;
  font-size: 14px;
}

/* 标签样式 */
.mai-ru {
  float: right;
  background: linear-gradient(to bottom, #DDFCE6, #c8f5d2);
  padding: 4px 8px;
  color: #18A44B;
  font-size: 12px;
  display: block;
  border-radius: 3px;
  font-weight: bold;
}

.mai-ru-zeng {
  float: right;
  background: linear-gradient(to bottom, #FCF5C4, #f5ecaa);
  padding: 4px 8px;
  color: #976A1C;
  font-size: 12px;
  display: block;
  border-radius: 3px;
  font-weight: bold;
}

.chi-you {
  float: right;
  background: linear-gradient(to bottom, #E0E0E0, #d0d0d0);
  padding: 4px 8px;
  color: #333333;
  font-size: 12px;
  display: block;
  border-radius: 3px;
  font-weight: bold;
}

.jian-chi {
  float: right;
  background: linear-gradient(to bottom, #FFE0B2, #ffd090);
  padding: 4px 8px;
  color: #FF6D00;
  font-size: 12px;
  display: block;
  border-radius: 3px;
  font-weight: bold;
}

.mai-chu {
  float: right;
  background: linear-gradient(to bottom, #FFCDD2, #fba4ab);
  padding: 4px 8px;
  color: #C62828;
  font-size: 12px;
  display: block;
  border-radius: 3px;
  font-weight: bold;
}

@media (max-width: 768px) {
  .report-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 15px;
  }
  
  .category-item {
    padding: 6px 12px;
  }
  
  .container {
    padding: 15px;
  }
  
  .report-card {
    padding: 15px;
    min-width: unset;
  }
}

@media (min-width: 769px) and (max-width: 1200px) {
  .report-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
  }
  
  .report-card {
    min-width: unset;
  }
}

@media (min-width: 1201px) and (max-width: 1400px) {
  .report-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }
  
  .report-card {
    min-width: unset;
  }
}

@media (min-width: 1401px) {
  .report-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }

  .report-card {
    min-width: 300px;
  }
}
</style>