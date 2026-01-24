<template>
  <div class="dragon-tiger-page">
    <header class="header">
      <router-link to="/" class="logo">量化牛牛 - 龙虎榜</router-link>
      <nav class="header-nav">
        <router-link to="/dragon-tiger-list">龙虎榜</router-link>
        <router-link to="/financial-report">财报</router-link>
        <router-link to="/fund-source">资金流动</router-link>
        <router-link to="/company-research">公司研报</router-link>
        <router-link to="/quant-analysis">量化策略</router-link>
      </nav>
    </header>

    <div class="filters">
      <div class="filter-item" v-if="mode === 'daily'">
        <span class="label">交易日：</span>
        <input v-model="tradeDate" type="date" class="input" />
      </div>
      <div class="filter-item" v-else>
        <span class="label">统计窗口：</span>
        <select v-model="days" class="select">
          <option :value="1">近1日</option>
          <option :value="3">近3日</option>
          <option :value="5">近5日</option>
          <option :value="10">近10日</option>
          <option :value="20">近20日</option>
          <option :value="30">近30日</option>
        </select>
      </div>
      <div class="filter-item" v-if="mode === 'summary'">
        <span class="label">截止日：</span>
        <input v-model="endTradeDate" type="date" class="input" />
      </div>
      <div class="filter-item search">
        <input v-model="searchKeyword" class="input" placeholder="搜索代码/名称" />
      </div>
      <button class="refresh-btn" @click="onRefresh">刷新</button>
    </div>

    <div class="tabs">
      <button
        v-for="m in modes"
        :key="m.value"
        :class="['tab-btn', mode === m.value ? 'active' : '']"
        @click="mode = m.value"
      >
        {{ m.label }}
      </button>
    </div>

    <div class="table-card">
      <div class="table-header">
        <div class="title">{{ currentTitle }}</div>
        <div class="meta">
          <span v-if="loading">加载中...</span>
          <span v-else>共 {{ totalDisplay }} 条</span>
        </div>
      </div>

      <div v-if="copyMessage" class="copy-tip">{{ copyMessage }}</div>
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
              <span
                v-if="col.key === 'code'"
                class="code-link"
                @click="copyCode(row.code)"
              >
                {{ row.code }}
              </span>
              <span v-else-if="col.key === 'name'">
                {{ row.name || '--' }}
              </span>
              <span v-else>
                {{ formatValue(row, col) }}
              </span>
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
import { getLhbStocks, getLhbSummary } from '@/services/dragonTigerService'

const modes = [
  { label: '当日上榜', value: 'daily' },
  { label: '多日汇总', value: 'summary' }
]

const mode = ref('daily')
const tradeDate = ref('')
const endTradeDate = ref('')
const days = ref(5)
const searchKeyword = ref('')
const page = ref(1)
const pageSize = ref(50)

const loading = ref(false)
const errorMessage = ref('')
const rawRows = ref([])
const total = ref(0)
const copyMessage = ref('')

const getEnvelopeData = (resp) => {
  let current = resp
  let guard = 0
  while (current && typeof current === 'object' && 'code' in current && 'data' in current && guard < 3) {
    current = current.data
    guard += 1
  }
  return current
}

const resolveRows = (payload) => {
  if (Array.isArray(payload)) return payload
  if (payload && Array.isArray(payload.data)) return payload.data
  if (payload && payload.data && Array.isArray(payload.data.data)) return payload.data.data
  return []
}

const currentTitle = computed(() => (mode.value === 'daily' ? '龙虎榜上榜个股' : '龙虎榜多日汇总'))

const columnsMap = {
  daily: [
    { label: '排名', key: 'rank', type: 'number' },
    { label: '代码', key: 'code' },
    { label: '名称', key: 'name' },
    { label: '收盘价', key: 'close', type: 'number' },
    { label: '涨跌幅', key: 'pct_change', type: 'percent' },
    { label: '买入额', key: 'buy_amount', type: 'amount' },
    { label: '卖出额', key: 'sell_amount', type: 'amount' },
    { label: '净买入', key: 'net_buy_amount', type: 'amount' },
    { label: '成交额', key: 'turnover', type: 'amount' },
    { label: '上榜原因', key: 'reason' }
  ],
  summary: [
    { label: '排名', key: 'rank', type: 'number' },
    { label: '代码', key: 'code' },
    { label: '名称', key: 'name' },
    { label: '上榜次数', key: 'appear_count', type: 'number' },
    { label: '买入额', key: 'buy_amount', type: 'amount' },
    { label: '卖出额', key: 'sell_amount', type: 'amount' },
    { label: '净买入', key: 'net_buy_amount', type: 'amount' },
    { label: '买卖总额', key: 'total_amount', type: 'amount' }
  ]
}

const currentColumns = computed(() => columnsMap[mode.value] || [])

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
    return Number.isNaN(num) ? value : num
  }
  return value || '--'
}

const rowKey = (row) => {
  if (mode.value === 'daily') {
    return `${row.code || ''}_${row.trade_date || ''}_${row.reason || ''}`
  }
  return `${row.code || ''}_${row.end_trade_date || ''}_${row.window_days || ''}`
}

const copyCode = async (code) => {
  if (!code) return
  try {
    await navigator.clipboard.writeText(String(code))
    copyMessage.value = `已复制 ${code}`
    setTimeout(() => {
      copyMessage.value = ''
    }, 1500)
  } catch (e) {
    copyMessage.value = '复制失败'
  }
}

const loadData = async (forceRefresh = false) => {
  loading.value = true
  errorMessage.value = ''
  try {
    let result
    if (mode.value === 'daily') {
      result = await getLhbStocks({
        tradeDate: tradeDate.value || undefined,
        page: page.value,
        pageSize: pageSize.value,
        refresh: forceRefresh
      })
    } else {
      result = await getLhbSummary({
        days: days.value,
        endTradeDate: endTradeDate.value || undefined,
        page: page.value,
        pageSize: pageSize.value,
        refresh: forceRefresh
      })
    }

    if (result?.success) {
      const data = getEnvelopeData(result.data)
      rawRows.value = resolveRows(data)
      const totalValue = data?.total ?? data?.data?.total
      total.value = typeof totalValue === 'number' ? totalValue : rawRows.value.length
      if (mode.value === 'daily' && data?.trade_date && !tradeDate.value) {
        tradeDate.value = data.trade_date
      }
      if (mode.value === 'summary' && data?.end_trade_date && !endTradeDate.value) {
        endTradeDate.value = data.end_trade_date
      }
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

watch([mode, tradeDate, endTradeDate, days, pageSize], () => {
  page.value = 1
  loadData()
})

watch(page, () => {
  loadData()
})

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dragon-tiger-page {
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
  font-size: 20px;
  font-weight: bold;
  color: white;
  text-decoration: none;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-nav a {
  color: white;
  text-decoration: none;
  font-size: 14px;
}

.header-nav .router-link-active {
  text-decoration: underline;
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

.copy-tip {
  background: #fff8f0;
  color: #ff7f24;
  border: 1px dashed #ffb380;
  padding: 8px 10px;
  border-radius: 4px;
  margin-bottom: 10px;
  font-size: 13px;
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

.code-link {
  color: #ff7f24;
  cursor: pointer;
  text-decoration: underline;
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
