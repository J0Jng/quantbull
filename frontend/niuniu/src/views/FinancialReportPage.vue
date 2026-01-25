<template>
  <div class="financial-report-page">
    <header class="header">
      <router-link to="/" class="logo">量化牛牛 - 股票数据中心</router-link>
      <div class="header-nav">
        <router-link to="/stock-data">股票数据</router-link>
        <router-link to="/dragon-tiger-list">龙虎榜</router-link>
        <router-link to="/financial-report">财报</router-link>
        <router-link to="/fund-source">资金流动</router-link>
        <router-link to="/company-research">公司研报</router-link>
        <router-link to="/quant-analysis">量化分析工具</router-link>
        <div class="user-menu-container" @mouseenter="onMenuEnter" @mouseleave="onMenuLeave">
          <div class="user-btn" @click="toggleUserMenu">{{ userText }}</div>
          <div class="user-dropdown" v-show="showUserMenu && logged" @mouseenter="onDropdownEnter" @mouseleave="onDropdownLeave">
            <div class="dropdown-item" @click="goToUserProfile">个人主页</div>
            <div class="dropdown-item logout" @click="handleLogout">退出登录</div>
          </div>
        </div>
      </div>
    </header>

    <div class="filters">
      <div class="filter-item">
        <span class="label">报告期：</span>
        <select v-model="period" class="select">
          <option v-for="p in periodOptions" :key="p" :value="p">{{ p }}</option>
        </select>
      </div>
      <div class="filter-item">
        <span class="label">市场：</span>
        <select v-model="market" class="select">
          <option value="all">全部</option>
          <option value="hsa">沪深A</option>
          <option value="sha">沪市A</option>
          <option value="sza">深市A</option>
          <option value="cyb">创业板</option>
          <option value="kcb">科创板</option>
        </select>
      </div>
      <div class="filter-item" v-if="activeTab === 'yjbb' || activeTab === 'yjkb'">
        <span class="label">行业：</span>
        <input v-model="industry" class="input" placeholder="可选：行业关键词" />
      </div>
      <div class="filter-item search">
        <input v-model="searchKeyword" class="input" placeholder="搜索代码/名称" />
      </div>
      <button class="refresh-btn" @click="onRefresh">刷新</button>
    </div>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        :class="['tab-btn', activeTab === tab.value ? 'active' : '']"
        @click="setTab(tab.value)"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="table-card">
      <div class="table-header">
        <div class="title">{{ currentTabLabel }}</div>
        <div class="meta">
          <span v-if="loading">加载中...</span>
          <span v-else>共 {{ totalDisplay }} 条</span>
        </div>
      </div>

      <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

      <table class="data-table">
        <thead>
          <tr>
            <th v-for="col in currentColumns" :key="col.key">{{ col.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="currentColumns.length" class="empty">数据加载中...</td>
          </tr>
          <tr v-else-if="filteredRows.length === 0">
            <td :colspan="currentColumns.length" class="empty">暂无数据</td>
          </tr>
          <tr v-else v-for="row in pagedRows" :key="row.code + '_' + row.notice_date">
            <td v-for="col in currentColumns" :key="col.key">
              {{ formatValue(row, col) }}
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button class="page-btn" :disabled="page === 1" @click="page--">上一页</button>
        <span class="page-info">
          第 {{ page }} 页
          <span v-if="totalPages">/ {{ totalPages }} 页</span>
        </span>
        <button class="page-btn" :disabled="!canNext" @click="page++">下一页</button>
        <select v-model="pageSize" class="select small">
          <option :value="20">20</option>
          <option :value="50">50</option>
          <option :value="100">100</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getYjbb, getYjkb, getYysj } from '@/services/financialReportService'

const route = useRoute()

const tabs = [
  { label: '业绩报表', value: 'yjbb' },
  { label: '业绩快报', value: 'yjkb' },
  { label: '预约披露', value: 'yysj' }
]

const activeTab = ref('yjbb')
const periodOptions = ref([])
const period = ref('')
const market = ref('all')
const industry = ref('')
const searchKeyword = ref('')
const page = ref(1)
const pageSize = ref(50)

const loading = ref(false)
const errorMessage = ref('')
const rawRows = ref([])
const total = ref(0)

const getEnvelopeData = (resp) => {
  if (resp && typeof resp === 'object' && 'code' in resp && 'data' in resp) {
    return resp.data
  }
  return resp
}

const currentTabLabel = computed(() => {
  const tab = tabs.find(t => t.value === activeTab.value)
  return tab ? tab.label : ''
})

const columnsMap = {
  yjbb: [
    { label: '代码', key: 'code' },
    { label: '名称', key: 'name' },
    { label: '每股收益', key: 'eps', type: 'number' },
    { label: '营业收入', key: 'revenue', type: 'amount' },
    { label: '营收YoY', key: 'revenue_yoy', type: 'percent' },
    { label: '净利润', key: 'net_profit', type: 'amount' },
    { label: '净利YoY', key: 'net_profit_yoy', type: 'percent' },
    { label: 'ROE', key: 'roe', type: 'percent' },
    { label: '公告日', key: 'notice_date' }
  ],
  yjkb: [
    { label: '代码', key: 'code' },
    { label: '名称', key: 'name' },
    { label: '行业', key: 'industry' },
    { label: '每股收益', key: 'eps', type: 'number' },
    { label: '营业收入', key: 'revenue', type: 'amount' },
    { label: '营收YoY', key: 'revenue_yoy', type: 'percent' },
    { label: '净利润', key: 'net_profit', type: 'amount' },
    { label: '净利YoY', key: 'net_profit_yoy', type: 'percent' },
    { label: '公告日', key: 'notice_date' }
  ],
  yysj: [
    { label: '代码', key: 'code' },
    { label: '名称', key: 'name' },
    { label: '首次预约', key: 'first_appoint_date' },
    { label: '一次变更', key: 'change_1_date' },
    { label: '二次变更', key: 'change_2_date' },
    { label: '三次变更', key: 'change_3_date' },
    { label: '实际披露', key: 'actual_date' }
  ]
}

const currentColumns = computed(() => columnsMap[activeTab.value] || [])

const filteredRows = computed(() => {
  if (!searchKeyword.value.trim()) return rawRows.value
  const keyword = searchKeyword.value.trim().toLowerCase()
  return rawRows.value.filter(row => {
    const code = String(row.code || '').toLowerCase()
    const name = String(row.name || '').toLowerCase()
    return code.includes(keyword) || name.includes(keyword)
  })
})

const pagedRows = computed(() => {
  if (total.value && total.value > 0) return filteredRows.value
  const start = (page.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})

const totalPages = computed(() => {
  if (!total.value) return null
  return Math.max(1, Math.ceil(total.value / pageSize.value))
})

const canNext = computed(() => {
  if (!totalPages.value) return true
  return page.value < totalPages.value
})

const totalDisplay = computed(() => total.value || filteredRows.value.length)

const formatAmount = (value) => {
  if (value === null || value === undefined || value === '') return '--'
  const num = Number(value)
  if (Number.isNaN(num)) return value
  if (Math.abs(num) >= 100000000) return `${(num / 100000000).toFixed(2)}亿`
  if (Math.abs(num) >= 10000) return `${(num / 10000).toFixed(2)}万`
  return num.toFixed(2)
}

const formatValue = (row, col) => {
  const value = row[col.key]
  if (col.type === 'amount') return formatAmount(value)
  if (col.type === 'percent') {
    if (value === null || value === undefined || value === '') return '--'
    const num = Number(value)
    return Number.isNaN(num) ? value : `${num.toFixed(2)}%`
  }
  if (col.type === 'number') {
    if (value === null || value === undefined || value === '') return '--'
    const num = Number(value)
    return Number.isNaN(num) ? value : num.toFixed(2)
  }
  return value || '--'
}

const buildPeriods = () => {
  const periods = []
  const now = new Date()
  let year = now.getFullYear()
  const month = now.getMonth() + 1
  let m
  if (month >= 12) m = 12
  else if (month >= 9) m = 9
  else if (month >= 6) m = 6
  else if (month >= 3) m = 3
  else {
    year -= 1
    m = 12
  }
  for (let i = 0; i < 8; i += 1) {
    periods.push(`${year}${String(m).padStart(2, '0')}`)
    if (m === 12) m = 9
    else if (m === 9) m = 6
    else if (m === 6) m = 3
    else {
      m = 12
      year -= 1
    }
  }
  return periods
}

const loadData = async (forceRefresh = false) => {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {
      period: period.value,
      page: page.value,
      pageSize: pageSize.value,
      market: market.value,
      industry: industry.value || undefined,
      codes: route.query.code || undefined,
      refresh: forceRefresh
    }

    let result
    if (activeTab.value === 'yjbb') result = await getYjbb(params)
    if (activeTab.value === 'yjkb') result = await getYjkb(params)
    if (activeTab.value === 'yysj') result = await getYysj(params)

    if (result?.success) {
      const data = getEnvelopeData(result.data)
      rawRows.value = data?.data || []
      total.value = data?.total || 0
    } else {
      rawRows.value = []
      total.value = 0
      errorMessage.value = result?.message || '数据加载失败'
    }
  } catch (error) {
    rawRows.value = []
    total.value = 0
    errorMessage.value = error?.message || '数据加载失败'
  } finally {
    loading.value = false
  }
}

const setTab = (value) => {
  if (activeTab.value === value) return
  activeTab.value = value
}

const onRefresh = async () => {
  await loadData(true)
}

watch([activeTab, period, market, industry, pageSize], () => {
  page.value = 1
  loadData()
})

watch(page, () => {
  loadData()
})

onMounted(() => {
  periodOptions.value = buildPeriods()
  period.value = route.query.period || periodOptions.value[0]
  searchKeyword.value = route.query.code || ''
  loadData()
})
</script>

<style scoped>
.financial-report-page {
  min-height: 100vh;
  background: #fff8f0;
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
}

.logo {
  font-size: 22px;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.logo:hover {
  text-decoration: underline;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-nav a {
  color: white;
  text-decoration: none;
  font-size: 14px;
}

.header-nav .active,
.header-nav .router-link-active,
.header-nav .router-link-exact-active {
  text-decoration: underline;
}

.header-nav .user-btn {
  background-color: white;
  color: #ff7f24;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.user-menu-container {
  position: relative;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #ffb380;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  min-width: 120px;
}

.dropdown-item {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #fff3e6;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: #fff8f0;
}

.dropdown-item.logout {
  color: #ff4500;
}

.filters {
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #ffb380;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.filter-item.search {
  flex: 1;
  min-width: 200px;
}

.label {
  color: #666;
  font-size: 13px;
}

.select,
.input {
  padding: 6px 10px;
  border: 1px solid #ffb380;
  border-radius: 4px;
  outline: none;
  background: #fff;
}

.select.small {
  padding: 4px 8px;
}

.refresh-btn {
  background-color: #fff3e6;
  color: #ff7f24;
  border: 1px solid #ff7f24;
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
}

.tabs {
  display: flex;
  gap: 10px;
  padding: 16px 20px 0;
}

.tab-btn {
  background: #fff3e6;
  color: #ff7f24;
  border: 1px solid #ff7f24;
  padding: 8px 14px;
  border-radius: 4px;
  cursor: pointer;
}

.tab-btn.active {
  background: #ff7f24;
  color: #fff;
}

.table-card {
  background: white;
  margin: 16px 20px 24px;
  border-radius: 8px;
  border: 1px solid #ffb380;
  padding: 16px;
  overflow-x: auto;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.title {
  font-size: 18px;
  color: #ff7f24;
  font-weight: bold;
}

.meta {
  color: #999;
  font-size: 13px;
}

.error {
  background: #ffe8cc;
  color: #ff4500;
  border: 1px solid #ff7f24;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #fff3e6;
  color: #ff7f24;
  padding: 10px 8px;
  text-align: left;
  border-bottom: 2px solid #ffb380;
  font-size: 13px;
}

.data-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #fff3e6;
  font-size: 13px;
}

.data-table tr:hover {
  background: #fff8f0;
}

.empty {
  text-align: center;
  padding: 20px;
  color: #999;
}

.pagination {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
}

.page-btn {
  background-color: #fff3e6;
  color: #ff7f24;
  border: 1px solid #ff7f24;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 13px;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .filters {
    gap: 10px;
  }
}
</style>
