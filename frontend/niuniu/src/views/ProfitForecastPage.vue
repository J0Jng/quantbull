<template>
  <div class="profit-forecast-page">
      <header class="header">
      <router-link to="/" class="logo">量化牛牛 - 数据中心</router-link>
      <div class="header-nav">
        <router-link to="/stock-data">股票数据</router-link>
        <router-link to="/dragon-tiger-list">龙虎榜</router-link>
        <router-link to="/financial-report">财报</router-link>
        <router-link to="/fund-source">资金流动</router-link>
        <router-link to="/profit-forecast">盈利预测</router-link>
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

      <div class="table-card">
        <div class="filters">
          <div class="filter-left">
            <div class="filter-item" v-if="showScopeValue">
              <span class="label">范围值：</span>
              <select v-model="scopeValue" class="select">
                <option value="">全部股票</option>
                <option v-for="item in scopeOptions" :key="item.code" :value="item.code">
                  {{ item.name }}
                </option>
              </select>
            </div>
            <button class="query-btn" type="button" @click="loadData()">查询</button>
            <button class="refresh-btn" type="button" @click="onRefresh">更新数据</button>
          </div>
          <div class="filter-right">
            <select v-model="pageSize" class="select small">
              <option :value="20">20条/页</option>
              <option :value="50">50条/页</option>
              <option :value="100">100条/页</option>
            </select>
            <input v-model="searchKeyword" class="input search-input" placeholder="搜索代码/名称" />
          </div>
        </div>

        <div class="table-header">
          <div class="title">盈利预测</div>
          <div class="meta">
            <span v-if="loading">加载中...</span>
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
            <tr v-else v-for="row in pagedRows" :key="rowKey(row)">
              <td v-for="col in currentColumns" :key="col.key">
                <span v-if="col.key === 'code'" class="link code-link">
                  {{ row.code }}
                </span>
                <span v-else-if="col.key === 'name'" class="link name-link">
                  {{ row.name || '--' }}
                </span>
                <span v-else>
                  {{ formatValue(row, col) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="pagination" v-if="totalPages > 1">
          <button class="page-btn" :disabled="page <= 1" @click="onPrevPage">上一页</button>
          <div class="page-info">
            第
            <input v-model.number="page" type="number" class="page-input" :min="1" :max="totalPages" />
            / {{ totalPages }} 页
          </div>
          <button class="page-btn" :disabled="!canNext" @click="onNextPage">下一页</button>
        </div>
      </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getProfitForecast, getProfitForecastScopes } from '@/services/profitForecastService'

const router = useRouter()
const { logged, userText, openLoginModal, logout } = useAuth()
const showUserMenu = ref(false)
let menuTimeout = null
let hideTimeout = null

function onMenuEnter() {
  if (!logged.value) return
  clearTimeout(hideTimeout)
  menuTimeout = setTimeout(() => {
    showUserMenu.value = true
  }, 300)
}

function onMenuLeave() {
  clearTimeout(menuTimeout)
  hideTimeout = setTimeout(() => {
    if (showUserMenu.value) {
      showUserMenu.value = false
    }
  }, 200)
}

function onDropdownEnter() {
  clearTimeout(hideTimeout)
}

function onDropdownLeave() {
  hideTimeout = setTimeout(() => {
    showUserMenu.value = false
  }, 200)
}

function toggleUserMenu() {
  if (!logged.value) {
    openLoginModal()
    showUserMenu.value = false
  } else {
    clearTimeout(menuTimeout)
    clearTimeout(hideTimeout)
    showUserMenu.value = !showUserMenu.value
  }
}

function handleLogout() {
  logout()
  showUserMenu.value = false
}

function goToUserProfile() {
  showUserMenu.value = false
  router.push('/profile')
}

const scopeType = ref('all')
const scopeValue = ref('')
const scopes = ref({ industry: [], concept: [], region: [], market: [] })
const searchKeyword = ref('')
const page = ref(1)
const pageSize = ref(50)

const loading = ref(false)
const errorMessage = ref('')
const rawRows = ref([])
const total = ref(0)

const getEnvelopeData = (resp) => {
  let current = resp
  let guard = 0
  while (current && typeof current === 'object' && 'code' in current && 'data' in current && guard < 3) {
    current = current.data
    guard += 1
  }
  return current
}

const showScopeValue = computed(() => scopeType.value !== 'all')

const scopeOptions = computed(() => {
  if (scopeType.value === 'industry') return scopes.value.industry || []
  if (scopeType.value === 'concept') return scopes.value.concept || []
  if (scopeType.value === 'region') return scopes.value.region || []
  if (scopeType.value === 'market') return scopes.value.market || []
  return []
})

const epsLabels = computed(() => {
  const first = rawRows.value[0]
  if (!first) {
    return ['EPS1', 'EPS2', 'EPS3', 'EPS4']
  }
  const yearLabel = (year, mark) => {
    if (!year) return '--'
    return `${year}${mark || ''} EPS`
  }
  return [
    yearLabel(first.year1, first.year_mark1),
    yearLabel(first.year2, first.year_mark2),
    yearLabel(first.year3, first.year_mark3),
    yearLabel(first.year4, first.year_mark4)
  ]
})

const baseColumns = [
  { label: '序号', key: 'rank', type: 'number' },
  { label: '代码', key: 'code' },
  { label: '名称', key: 'name' },
  { label: '机构数', key: 'rating_org_num', type: 'number' },
  { label: '买入', key: 'rating_buy_num', type: 'number' },
  { label: '增持', key: 'rating_add_num', type: 'number' },
  { label: '中性', key: 'rating_neutral_num', type: 'number' },
  { label: '减持', key: 'rating_reduce_num', type: 'number' },
  { label: '卖出', key: 'rating_sale_num', type: 'number' }
]

const currentColumns = computed(() => {
  const eps = [
    { label: epsLabels.value[0], key: 'eps1', type: 'decimal' },
    { label: epsLabels.value[1], key: 'eps2', type: 'decimal' },
    { label: epsLabels.value[2], key: 'eps3', type: 'decimal' },
    { label: epsLabels.value[3], key: 'eps4', type: 'decimal' }
  ]
  return [...baseColumns, ...eps]
})

const filteredRows = computed(() => {
  if (!searchKeyword.value.trim()) return rawRows.value
  const keyword = searchKeyword.value.trim().toLowerCase()
  return rawRows.value.filter(row =>
    String(row.code || '').toLowerCase().includes(keyword) ||
    String(row.name || '').toLowerCase().includes(keyword)
  )
})

const pagedRows = computed(() => filteredRows.value)

const totalPages = computed(() => {
  if (!total.value) return Math.max(1, Math.ceil(filteredRows.value.length / pageSize.value))
  return Math.max(1, Math.ceil(total.value / pageSize.value))
})

const canNext = computed(() => page.value < totalPages.value)

const rowKey = (row) => `${row.code || ''}_${row.rank || ''}`

const formatValue = (row, col) => {
  const value = row[col.key]
  if (value === null || value === undefined || value === '') return '--'
  if (col.type === 'decimal') {
    const num = Number(value)
    return Number.isNaN(num) ? value : num.toFixed(2)
  }
  if (col.type === 'number') {
    const num = Number(value)
    return Number.isNaN(num) ? value : num
  }
  return value
}

const mapRow = (row, index) => {
  const rank = (page.value - 1) * pageSize.value + index + 1
  return {
    rank,
    code: row.SECURITY_CODE,
    name: row.SECURITY_NAME_ABBR,
    rating_org_num: row.RATING_ORG_NUM,
    rating_buy_num: row.RATING_BUY_NUM ?? 0,
    rating_add_num: row.RATING_ADD_NUM ?? 0,
    rating_neutral_num: row.RATING_NEUTRAL_NUM ?? 0,
    rating_reduce_num: row.RATING_REDUCE_NUM ?? 0,
    rating_sale_num: row.RATING_SALE_NUM ?? 0,
    year1: row.YEAR1,
    year_mark1: row.YEAR_MARK1,
    eps1: row.EPS1,
    year2: row.YEAR2,
    year_mark2: row.YEAR_MARK2,
    eps2: row.EPS2,
    year3: row.YEAR3,
    year_mark3: row.YEAR_MARK3,
    eps3: row.EPS3,
    year4: row.YEAR4,
    year_mark4: row.YEAR_MARK4,
    eps4: row.EPS4
  }
}

const loadScopes = async () => {
  const result = await getProfitForecastScopes()
  if (result?.success) {
    const data = getEnvelopeData(result.data)
    if (data) {
      scopes.value = data
    }
  }
}

const loadData = async (forceRefresh = false) => {
  loading.value = true
  errorMessage.value = ''
  try {
    const params = {
      scope_type: scopeType.value,
      scope_value: scopeValue.value || undefined,
      page: page.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value.trim() || undefined,
      refresh: forceRefresh
    }
    const result = await getProfitForecast(params)
    if (result?.success) {
      const payload = getEnvelopeData(result.data)
      const rows = Array.isArray(payload?.data) ? payload.data : []
      rawRows.value = rows.map((row, index) => mapRow(row, index))
      total.value = Number(payload?.total || 0)
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

const onRefresh = async () => {
  await loadData(true)
}

const onPrevPage = () => {
  if (page.value > 1) page.value -= 1
}

const onNextPage = () => {
  if (canNext.value) page.value += 1
}

watch([scopeType, scopeValue, pageSize], () => {
  page.value = 1
  if (scopeType.value === 'all') {
    scopeValue.value = ''
  }
  loadData()
})

watch(page, () => {
  loadData()
})

onMounted(async () => {
  await loadScopes()
  await loadData()
})
</script>

<style scoped>
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

.profit-forecast-page {
  min-height: 100vh;
  background: #fff8f0;
}

.filters {
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #ffb380;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.label {
  color: #666;
  font-size: 12px;
}

.select,
.input {
  padding: 6px 8px;
  border: 1px solid #ffb380;
  border-radius: 3px;
  outline: none;
  background: #fff;
  font-size: 12px;
}

.select.small {
  padding: 4px 8px;
}

.search-input {
  min-width: 200px;
}

.query-btn {
  background: #ff7f24;
  color: #fff;
  border: 1px solid #ff7f24;
  padding: 6px 14px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.refresh-btn {
  background-color: #fff;
  color: #ff7f24;
  border: 1px solid #ff7f24;
  padding: 6px 12px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.table-card {
  background: #fff;
  border-radius: 6px;
  border: 1px solid #ffb380;
  padding: 0;
  overflow-x: auto;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px 8px;
}

.title {
  font-size: 15px;
  color: #ff7f24;
  font-weight: 600;
}

.meta {
  color: #999;
  font-size: 12px;
}

.error {
  background: #fff5f5;
  color: #cf1322;
  border: 1px solid #ffa39e;
  padding: 10px 12px;
  border-radius: 4px;
  margin: 0 16px 12px;
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
  border-bottom: 1px solid #ffb380;
  font-size: 12px;
}

.data-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #fff3e6;
  font-size: 12px;
}

.data-table tr:hover {
  background: #fff8f0;
}

.link {
  color: #ff7f24;
  cursor: pointer;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.code-link {
  font-weight: 600;
}

.empty {
  text-align: center;
  padding: 20px;
  color: #999;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 16px 16px;
}

.page-btn {
  background: #fff;
  color: #ff7f24;
  border: 1px solid #ffb380;
  padding: 6px 12px;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

.page-btn:disabled {
  color: #ccc;
  border-color: #eee;
  cursor: not-allowed;
}

.page-info {
  font-size: 12px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-input {
  width: 60px;
  padding: 4px 6px;
  border: 1px solid #ffb380;
  border-radius: 3px;
  font-size: 12px;
  text-align: center;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-right {
    width: 100%;
  }
  .search-input {
    width: 100%;
  }
}
</style>
