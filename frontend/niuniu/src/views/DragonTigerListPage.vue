<template>
  <div class="dragon-tiger-page">
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

      <div class="table-card">
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

        <div class="filters">
          <div class="filter-left">
            <div class="filter-item" v-if="isTradeDateMode">
              <span class="label">交易日：</span>
              <input v-model="tradeDate" type="date" class="input" />
            </div>
            <div class="filter-item" v-else-if="isWindowMode">
              <span class="label">统计窗口：</span>
              <select
                v-model="days"
                class="select"
                :disabled="mode === 'stockStat' || mode === 'instSeatTrack' || mode === 'brokerRank' || mode === 'brokerStats'"
              >
                <option :value="1">近1日</option>
                <option :value="3">近3日</option>
                <option :value="5">近5日</option>
                <option :value="10">近10日</option>
                <option :value="20">近20日</option>
                <option :value="30">近30日</option>
              </select>
            </div>
            <div class="filter-item" v-if="showEndTradeDate">
              <span class="label">截止日：</span>
              <input v-model="endTradeDate" type="date" class="input" />
            </div>
            <button class="query-btn" type="button" @click="loadData()">查询</button>
            <button class="refresh-btn" type="button" @click="onRefresh">更新数据</button>
          </div>
          <div class="filter-right">
            <select v-model="pageSize" class="select small" v-if="!isFixedTopMode">
              <option :value="20">20条/页</option>
              <option :value="50">50条/页</option>
              <option :value="100">100条/页</option>
            </select>
            <input v-model="searchKeyword" class="input search-input" :placeholder="searchPlaceholder" />
          </div>
        </div>

        <div class="table-header">
          <div class="title">{{ currentTitle }}</div>
          <div class="meta">
            <span v-if="loading">加载中...</span>
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
                  class="link code-link"
                  @click="copyCode(row.code)"
                >
                  {{ row.code }}
                </span>
                <span v-else-if="col.key === 'name'" class="link name-link">
                  {{ row.name || '--' }}
                </span>
                <span v-else-if="col.type === 'percent' || highlightKeys.includes(col.key)" :class="valueClass(row, col)">
                  {{ formatValue(row, col) }}
                </span>
                <span v-else>
                  {{ formatValue(row, col) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="pagination" v-if="!isFixedTopMode && totalPages > 1">
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
import {
  getLhbStocks,
  getLhbSummary,
  getLhbInstitutionTrades,
  getLhbInstitutionSeatTrack,
  getLhbActiveBrokers,
  getLhbBrokerRank,
  getLhbBrokerOnlistStats
} from '@/services/dragonTigerService'

const modes = [
  { label: '上榜个股', value: 'stocks' },
  { label: '个股龙虎榜统计', value: 'stockStat' },
  { label: '机构买卖情况', value: 'instTrades' },
  { label: '机构席位买卖追踪', value: 'instSeatTrack' },
  { label: '每日活跃营业部', value: 'activeBroker' },
  { label: '营业部排行', value: 'brokerRank' },
  { label: '证券营业部上榜统计', value: 'brokerStats' }
]

const mode = ref('stocks')
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

const titleMap = {
  stocks: '龙虎榜上榜个股',
  stockStat: '个股龙虎榜统计',
  instTrades: '机构买卖情况',
  instSeatTrack: '机构席位买卖追踪',
  activeBroker: '每日活跃营业部',
  brokerRank: '营业部排行',
  brokerStats: '证券营业部上榜统计'
}

const currentTitle = computed(() => titleMap[mode.value] || '龙虎榜数据')

const tradeDateModes = new Set(['stocks', 'instTrades', 'activeBroker'])
const windowModes = new Set(['stockStat', 'instSeatTrack', 'brokerRank', 'brokerStats'])

const isTradeDateMode = computed(() => tradeDateModes.has(mode.value))
const isWindowMode = computed(() => windowModes.has(mode.value))
const showEndTradeDate = computed(() =>
  windowModes.has(mode.value) && mode.value !== 'brokerRank' && mode.value !== 'brokerStats'
)
const isFixedTopMode = computed(() => false)

const highlightKeys = ['net_buy_amount', 'net_buy_ratio']

const columnsMap = {
  stocks: [
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
  stockStat: [
    { label: '代码', key: 'code' },
    { label: '名称', key: 'name' },
    { label: '上榜次数', key: 'appear_count', type: 'number' },
    { label: '买入额', key: 'buy_amount', type: 'amount' },
    { label: '卖出额', key: 'sell_amount', type: 'amount' },
    { label: '净买入', key: 'net_buy_amount', type: 'amount' },
    { label: '买卖总额', key: 'total_amount', type: 'amount' }
  ],
  instTrades: [
    { label: '代码', key: 'code' },
    { label: '名称', key: 'name' },
    { label: '收盘价', key: 'close', type: 'number' },
    { label: '涨跌幅', key: 'pct_change', type: 'percent' },
    { label: '机构买入次数', key: 'buy_count', type: 'number' },
    { label: '机构卖出次数', key: 'sell_count', type: 'number' },
    { label: '买入额', key: 'buy_amount', type: 'amount' },
    { label: '卖出额', key: 'sell_amount', type: 'amount' },
    { label: '净买入', key: 'net_buy_amount', type: 'amount' },
    { label: '成交额', key: 'turnover', type: 'amount' },
    { label: '上榜原因', key: 'reason' }
  ],
  instSeatTrack: [
    { label: '代码', key: 'code' },
    { label: '名称', key: 'name' },
    { label: '收盘价', key: 'close', type: 'number' },
    { label: '涨跌幅', key: 'pct_change', type: 'percent' },
    { label: '净买入', key: 'net_buy_amount', type: 'amount' },
    { label: '买入额', key: 'buy_amount', type: 'amount' },
    { label: '买入次数', key: 'buy_count', type: 'number' },
    { label: '卖出额', key: 'sell_amount', type: 'amount' },
    { label: '卖出次数', key: 'sell_count', type: 'number' },
    { label: '净买入占比', key: 'net_buy_ratio', type: 'percent' }
  ],
  activeBroker: [
    { label: '营业部', key: 'broker_name' },
    { label: '买入次数', key: 'buy_count', type: 'number' },
    { label: '卖出次数', key: 'sell_count', type: 'number' },
    { label: '买入额', key: 'buy_amount', type: 'amount' },
    { label: '卖出额', key: 'sell_amount', type: 'amount' },
    { label: '净买入', key: 'net_buy_amount', type: 'amount' },
    { label: '活跃股票', key: 'stocks' }
  ],
  brokerRank: [
    { label: '营业部', key: 'broker_name' },
    { label: '1日买入次数', key: 'buy_times_1d', type: 'number' },
    { label: '1日平均涨幅', key: 'avg_increase_1d', type: 'percent' },
    { label: '1日上涨概率', key: 'rise_probability_1d', type: 'percent' },
    { label: '2日买入次数', key: 'buy_times_2d', type: 'number' },
    { label: '2日平均涨幅', key: 'avg_increase_2d', type: 'percent' },
    { label: '2日上涨概率', key: 'rise_probability_2d', type: 'percent' },
    { label: '3日买入次数', key: 'buy_times_3d', type: 'number' },
    { label: '3日平均涨幅', key: 'avg_increase_3d', type: 'percent' },
    { label: '3日上涨概率', key: 'rise_probability_3d', type: 'percent' },
    { label: '5日买入次数', key: 'buy_times_5d', type: 'number' },
    { label: '5日平均涨幅', key: 'avg_increase_5d', type: 'percent' },
    { label: '5日上涨概率', key: 'rise_probability_5d', type: 'percent' },
    { label: '10日买入次数', key: 'buy_times_10d', type: 'number' },
    { label: '10日平均涨幅', key: 'avg_increase_10d', type: 'percent' },
    { label: '10日上涨概率', key: 'rise_probability_10d', type: 'percent' }
  ],
  brokerStats: [
    { label: '营业部', key: 'broker_name' },
    { label: '上榜总额', key: 'total_amount', type: 'amount' },
    { label: '买入额', key: 'buy_amount', type: 'amount' },
    { label: '买入次数', key: 'buy_count', type: 'number' },
    { label: '卖出额', key: 'sell_amount', type: 'amount' },
    { label: '卖出次数', key: 'sell_count', type: 'number' }
  ]
}

const currentColumns = computed(() => columnsMap[mode.value] || [])

const searchFieldsMap = {
  stocks: ['code', 'name', 'reason'],
  stockStat: ['code', 'name'],
  instTrades: ['code', 'name', 'reason'],
  instSeatTrack: ['code', 'name'],
  activeBroker: ['broker_name', 'stocks'],
  brokerRank: ['broker_name'],
  brokerStats: ['broker_name']
}

const searchPlaceholder = computed(() => {
  if (mode.value === 'activeBroker' || mode.value.startsWith('broker')) return '搜索营业部/股票'
  if (mode.value.startsWith('inst')) return '搜索代码/名称/原因'
  return '搜索代码/名称'
})

const filteredRows = computed(() => {
  if (!searchKeyword.value.trim()) return rawRows.value
  const keyword = searchKeyword.value.trim().toLowerCase()
  const fields = searchFieldsMap[mode.value] || ['code', 'name', 'broker_name', 'org_name', 'seat_name']
  return rawRows.value.filter(row =>
    fields.some(field => String(row[field] || '').toLowerCase().includes(keyword))
  )
})

const sortedRows = computed(() => {
  if (mode.value === 'stockStat') {
    return [...filteredRows.value].sort((a, b) => {
      const aVal = Number(a.appear_count)
      const bVal = Number(b.appear_count)
      const aNaN = Number.isNaN(aVal)
      const bNaN = Number.isNaN(bVal)
      if (aNaN && bNaN) return 0
      if (aNaN) return 1
      if (bNaN) return -1
      return bVal - aVal
    })
  }
  if (mode.value === 'stocks') {
    return [...filteredRows.value].sort((a, b) => {
      const aCode = String(a.code || '')
      const bCode = String(b.code || '')
      if (!aCode && !bCode) return 0
      if (!aCode) return 1
      if (!bCode) return -1
      return aCode.localeCompare(bCode)
    })
  }
  return [...filteredRows.value].sort((a, b) => {
    const aVal = Number(a.rank)
    const bVal = Number(b.rank)
    const aNaN = Number.isNaN(aVal)
    const bNaN = Number.isNaN(bVal)
    if (aNaN && bNaN) return 0
    if (aNaN) return 1
    if (bNaN) return -1
    return aVal - bVal
  })
})

const shouldSlice = computed(() => sortedRows.value.length > pageSize.value)

const pagedRows = computed(() => {
  if (!shouldSlice.value) return sortedRows.value
  const start = (page.value - 1) * pageSize.value
  return sortedRows.value.slice(start, start + pageSize.value)
})

const totalPages = computed(() => {
  if (!total.value) {
    return Math.max(1, Math.ceil(sortedRows.value.length / pageSize.value))
  }
  return Math.max(1, Math.ceil(total.value / pageSize.value))
})

const canNext = computed(() => page.value < totalPages.value)

const totalDisplay = computed(() => total.value || sortedRows.value.length)

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

const valueClass = (row, col) => {
  const value = row[col.key]
  const num = Number(value)
  if (Number.isNaN(num)) return ''
  if (num > 0) return 'pos'
  if (num < 0) return 'neg'
  return ''
}

const rowKey = (row) => {
  if (tradeDateModes.has(mode.value)) {
    return `${row.code || row.broker_name || ''}_${row.trade_date || ''}_${row.reason || ''}`
  }
  return `${row.code || row.broker_name || ''}_${row.end_trade_date || ''}_${row.window_days || ''}`
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
    if (mode.value === 'stocks') {
      result = await getLhbStocks({
        tradeDate: tradeDate.value || undefined,
        page: page.value,
        pageSize: pageSize.value,
        refresh: forceRefresh
      })
    } else if (mode.value === 'stockStat') {
      result = await getLhbSummary({
        days: days.value,
        endTradeDate: endTradeDate.value || undefined,
        page: page.value,
        pageSize: pageSize.value,
        refresh: forceRefresh
      })
    } else if (mode.value === 'instTrades') {
      result = await getLhbInstitutionTrades({
        tradeDate: tradeDate.value || undefined,
        page: page.value,
        pageSize: pageSize.value,
        refresh: forceRefresh
      })
    } else if (mode.value === 'instSeatTrack') {
      result = await getLhbInstitutionSeatTrack({
        days: days.value,
        endTradeDate: endTradeDate.value || undefined,
        page: page.value,
        pageSize: pageSize.value,
        refresh: forceRefresh
      })
    } else if (mode.value === 'activeBroker') {
      result = await getLhbActiveBrokers({
        tradeDate: tradeDate.value || undefined,
        page: page.value,
        pageSize: pageSize.value,
        refresh: forceRefresh
      })
    } else if (mode.value === 'brokerRank') {
      result = await getLhbBrokerRank({
        days: days.value,
        endTradeDate: endTradeDate.value || undefined,
        page: page.value,
        pageSize: pageSize.value,
        refresh: forceRefresh
      })
    } else {
      result = await getLhbBrokerOnlistStats({
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
      if (tradeDateModes.has(mode.value) && data?.trade_date && !tradeDate.value) {
        tradeDate.value = data.trade_date
      }
      if (windowModes.has(mode.value) && data?.end_trade_date && !endTradeDate.value) {
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

const onPrevPage = () => {
  if (page.value > 1) page.value -= 1
}

const onNextPage = () => {
  if (canNext.value) page.value += 1
}

watch([mode, tradeDate, endTradeDate, days, pageSize], () => {
  if (mode.value === 'stocks') {
    pageSize.value = pageSize.value || 50
  }
  if (mode.value === 'stockStat') {
    days.value = 30
  }
  if (mode.value === 'instSeatTrack') {
    days.value = 30
  }
  if (mode.value === 'brokerRank') {
    days.value = 30
  }
  if (mode.value === 'brokerStats') {
    days.value = 90
  }
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

.dragon-tiger-page {
  min-height: 100vh;
  background: #fff8f0;
}

.page-header {
  padding: 8px 0 16px;
}

.breadcrumb {
  font-size: 12px;
  color: #999;
  margin-bottom: 6px;
}

.breadcrumb-link {
  color: inherit;
  text-decoration: none;
}

.breadcrumb-link:hover {
  color: #ff7f24;
  text-decoration: underline;
}

.breadcrumb-sep {
  color: inherit;
}

.page-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.page-title {
  font-size: 22px;
  color: #333;
  font-weight: 600;
}

.collect-btn {
  background: #ffffff;
  color: #2f6fed;
  border: 1px solid #d6e4ff;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
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

.tabs {
  display: flex;
  gap: 20px;
  border-bottom: 1px solid #ffb380;
  padding: 0 16px;
}

.tab-btn {
  background: transparent;
  color: #666;
  border: none;
  padding: 12px 2px;
  cursor: pointer;
  font-size: 14px;
  border-bottom: 2px solid transparent;
}

.tab-btn.active {
  color: #ff7f24;
  border-bottom-color: #ff7f24;
  font-weight: 600;
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

.copy-tip {
  background: #f6ffed;
  color: #389e0d;
  border: 1px dashed #b7eb8f;
  padding: 8px 12px;
  border-radius: 4px;
  margin: 0 16px 10px;
  font-size: 12px;
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


.pos {
  color: #cf1322;
}

.neg {
  color: #389e0d;
}

@media (max-width: 768px) {
  .page-title-row {
    flex-direction: column;
    align-items: flex-start;
  }
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
