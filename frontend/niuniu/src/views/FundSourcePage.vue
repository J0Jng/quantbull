<template>
  <div class="fund-source-page">
    <header class="header">
      <router-link to="/" class="logo">脑科学研究室 - 数据模拟中心</router-link>
      <div class="header-nav">
        <router-link to="/stock-data">历史行情数据</router-link>
        <router-link to="/dragon-tiger-list">公开异动统计</router-link>
        <router-link to="/financial-report">财报数据集</router-link>
        <router-link to="/fund-source">资金流历史统计</router-link>
        <router-link to="/profit-forecast">预测数据集（研究）</router-link>
        <router-link to="/company-research">公开文本索引</router-link>
        <router-link to="/quant-analysis">数据模拟分析工具</router-link>
      </div>
    </header>

    <div class="risk-banner" role="note" aria-label="风险提示">
      <div class="risk-banner__main">
        <div class="risk-banner__text">
          <span v-if="!riskExpanded">
            仅历史研究与模拟，不荐股不建议；数据或延迟误差，后果自担
          </span>
          <span v-else>
            本页面仅用于历史数据研究与数据模拟展示，不构成投资建议，不荐股、不做交易推荐。数据可能存在延迟、误差或不完整，历史表现不代表未来；用户应自行判断并承担使用后果。在法律允许范围内，平台不对使用本页面数据产生的损失承担责任。
          </span>
        </div>
        <button class="risk-banner__toggle" type="button" @click="riskExpanded = !riskExpanded">
          {{ riskExpanded ? '收起' : '展开' }}
        </button>
      </div>
    </div>

    <div class="tabs">
      <button :class="['tab-btn', activeTab === 'market' ? 'active' : '']" @click="activeTab = 'market'">大盘资金</button>
      <button :class="['tab-btn', activeTab === 'sector' ? 'active' : '']" @click="activeTab = 'sector'">板块资金</button>
      <button :class="['tab-btn', activeTab === 'stock' ? 'active' : '']" @click="activeTab = 'stock'">个股资金</button>
    </div>
    <div class="module-tip tabs-tip">仅研究展示，不构成建议，历史不代表未来</div>
    <div class="module-tip tabs-tip">仅加载最新已入库数据</div>

    <main class="content">
      <!-- 大盘资金流向 -->
      <section v-show="activeTab === 'market'" class="card">
        <div class="card-title">
          大盘资金流向
          <span class="asof">{{ marketAsOf ? `数据时间：${marketAsOf}` : '' }}</span>
          <button class="refresh-btn" @click="loadMarketFlow(true)">重新加载数据</button>
        </div>
        <div class="module-tip">仅研究展示，不构成建议，数据或延迟误差</div>
        <div v-if="marketLoading" class="loading">加载中...</div>
        <div v-else-if="marketError" class="error-message">{{ marketError }}</div>
        <div v-else-if="marketItems.length === 0" class="empty">暂无数据</div>
        <table v-else class="table">
          <thead>
            <tr>
              <th>档位</th>
              <th>流入</th>
              <th>流出</th>
              <th>净流入</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in marketItems" :key="item.bucket">
              <td>{{ bucketLabel(item.bucket) }}</td>
              <td :class="valueClass(item.inflow)">{{ formatMoney(item.inflow) }}</td>
              <td :class="valueClass(-item.outflow)">{{ formatMoney(item.outflow) }}</td>
              <td :class="valueClass(item.net)">{{ formatMoney(item.net) }}</td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- 板块资金流向 -->
      <section v-show="activeTab === 'sector'" class="card">
        <div class="card-title">
          板块资金流向
          <span class="asof">{{ sectorAsOf ? `数据时间：${sectorAsOf}` : '' }}</span>
          <div class="controls">
            <select v-model="sectorType" class="select">
              <option value="industry">行业</option>
              <option value="concept">概念</option>
              <option value="region">地域</option>
            </select>
            <button class="refresh-btn" @click="loadSectorFlow(true)">重新加载数据</button>
          </div>
        </div>
        <div class="module-tip">仅研究展示，不构成建议，数据或延迟误差</div>
        <div v-if="sectorLoading" class="loading">加载中...</div>
        <div v-else-if="sectorError" class="error-message">{{ sectorError }}</div>
        <div v-else-if="sectorItems.length === 0" class="empty">暂无数据</div>
        <table v-else class="table">
          <thead>
            <tr>
              <th>排名</th>
              <th>板块</th>
              <th>涨跌幅</th>
              <th>主力净流入</th>
              <th>主力占比</th>
              <th>超大单净流入</th>
              <th>大单净流入</th>
              <th>中单净流入</th>
              <th>小单净流入</th>
              <th>领涨股</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in sectorItems" :key="item.rank">
              <td>{{ item.rank }}</td>
              <td>{{ item.name }}</td>
              <td :class="valueClass(item.pct_change)">{{ formatPercent(item.pct_change) }}</td>
              <td :class="valueClass(item.main_net_inflow)">{{ formatMoney(item.main_net_inflow) }}</td>
              <td :class="valueClass(item.main_net_ratio)">{{ formatPercent(item.main_net_ratio) }}</td>
              <td :class="valueClass(item.super_net_inflow)">{{ formatMoney(item.super_net_inflow) }}</td>
              <td :class="valueClass(item.large_net_inflow)">{{ formatMoney(item.large_net_inflow) }}</td>
              <td :class="valueClass(item.medium_net_inflow)">{{ formatMoney(item.medium_net_inflow) }}</td>
              <td :class="valueClass(item.small_net_inflow)">{{ formatMoney(item.small_net_inflow) }}</td>
              <td>{{ item.leader || '--' }}</td>
            </tr>
          </tbody>
        </table>
        <div class="pagination" v-if="sectorTotal > 0">
          <button class="page-btn" :disabled="sectorPage === 1" @click="changeSectorPage(sectorPage - 1)">上一页</button>
          <span class="page-info">第 {{ sectorPage }} / {{ sectorTotalPages }} 页</span>
          <button class="page-btn" :disabled="sectorPage === sectorTotalPages" @click="changeSectorPage(sectorPage + 1)">下一页</button>
        </div>
      </section>

      <!-- 个股资金流向 -->
      <section v-show="activeTab === 'stock'" class="card">
        <div class="card-title">
          个股资金流向
          <span class="asof">{{ stockAsOf ? `数据时间：${stockAsOf}` : '' }}</span>
          <div class="controls">
            <select v-model="stockMarket" class="select">
              <option value="all">全部</option>
              <option value="hsa">沪深A股</option>
              <option value="sha">沪市A股</option>
              <option value="sza">深市A股</option>
              <option value="kcb">科创板</option>
              <option value="cyb">创业板</option>
            </select>
            <select v-model="stockStat" class="select">
              <option :value="1">今日</option>
              <option :value="5">5日</option>
              <option :value="10">10日</option>
            </select>
            <button class="refresh-btn" @click="loadStockFlow(true)">重新加载数据</button>
          </div>
        </div>
        <div class="module-tip">仅研究展示，不构成建议，数据或延迟误差</div>
        <div v-if="stockLoading" class="loading">加载中...</div>
        <div v-else-if="stockError" class="error-message">{{ stockError }}</div>
        <div v-else-if="stockItems.length === 0" class="empty">暂无数据</div>
        <table v-else class="table">
          <thead>
            <tr>
              <th>排名</th>
              <th>代码</th>
              <th>名称</th>
              <th>最新价</th>
              <th>涨跌幅</th>
              <th>主力净流入</th>
              <th>超大单净流入</th>
              <th>大单净流入</th>
              <th>中单净流入</th>
              <th>小单净流入</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in stockItems" :key="item.rank">
              <td>{{ item.rank }}</td>
              <td>{{ item.code }}</td>
              <td>{{ item.name }}</td>
              <td>{{ formatNumber(item.price) }}</td>
              <td :class="valueClass(item.pct_change)">{{ formatPercent(item.pct_change) }}</td>
              <td :class="valueClass(item.main_net_inflow)">{{ formatMoney(item.main_net_inflow) }}</td>
              <td :class="valueClass(item.super_net_inflow)">{{ formatMoney(item.super_net_inflow) }}</td>
              <td :class="valueClass(item.large_net_inflow)">{{ formatMoney(item.large_net_inflow) }}</td>
              <td :class="valueClass(item.medium_net_inflow)">{{ formatMoney(item.medium_net_inflow) }}</td>
              <td :class="valueClass(item.small_net_inflow)">{{ formatMoney(item.small_net_inflow) }}</td>
            </tr>
          </tbody>
        </table>
        <div class="pagination" v-if="stockTotal > 0">
          <button class="page-btn" :disabled="stockPage === 1" @click="changeStockPage(stockPage - 1)">上一页</button>
          <span class="page-info">第 {{ stockPage }} / {{ stockTotalPages }} 页</span>
          <button class="page-btn" :disabled="stockPage === stockTotalPages" @click="changeStockPage(stockPage + 1)">下一页</button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { getMarketFundFlow, getSectorFundFlow, getStockFundFlow } from '@/services/fundFlowService'

const riskExpanded = ref(false)

const activeTab = ref('market')

const marketItems = ref([])
const marketAsOf = ref('')
const marketLoading = ref(false)
const marketError = ref('')

const sectorType = ref('industry')
const sectorItems = ref([])
const sectorAsOf = ref('')
const sectorLoading = ref(false)
const sectorError = ref('')
const sectorPage = ref(1)
const sectorPageSize = ref(20)
const sectorTotal = ref(0)

const stockMarket = ref('all')
const stockStat = ref(1)
const stockItems = ref([])
const stockAsOf = ref('')
const stockLoading = ref(false)
const stockError = ref('')
const stockPage = ref(1)
const stockPageSize = ref(20)
const stockTotal = ref(0)

const getEnvelopeData = (resp) => {
  if (resp && typeof resp === 'object' && 'code' in resp && 'data' in resp) {
    return resp.data
  }
  return resp
}

const bucketLabel = (bucket) => {
  const map = {
    super: '超大单',
    large: '大单',
    medium: '中单',
    small: '小单'
  }
  return map[bucket] || bucket
}

const hasValue = (value) => value === 0 || value === 0.0 || (value !== null && value !== undefined && value !== '')

const valueClass = (value) => {
  if (!hasValue(value)) return 'neutral'
  if (value > 0) return 'red'
  if (value < 0) return 'green'
  return 'neutral'
}

const formatNumber = (value) => {
  if (!hasValue(value)) return '--'
  return Number(value).toFixed(2)
}

const formatPercent = (value) => {
  if (!hasValue(value)) return '--'
  const sign = value > 0 ? '+' : ''
  return `${sign}${Number(value).toFixed(2)}%`
}

const formatMoney = (value) => {
  if (!hasValue(value)) return '--'
  const num = Number(value)
  const abs = Math.abs(num)
  if (abs >= 1e8) return `${(num / 1e8).toFixed(2)}亿`
  if (abs >= 1e4) return `${(num / 1e4).toFixed(2)}万`
  return `${num.toFixed(2)}`
}

const sectorTotalPages = computed(() => Math.max(1, Math.ceil(sectorTotal.value / sectorPageSize.value)))
const stockTotalPages = computed(() => Math.max(1, Math.ceil(stockTotal.value / stockPageSize.value)))

const loadMarketFlow = async (refresh = false) => {
  marketLoading.value = true
  marketError.value = ''
  try {
    const result = await getMarketFundFlow({ market: 'hs', refresh })
    if (!result.success) {
      marketError.value = result.message || '获取大盘资金流向失败'
      marketItems.value = []
      return
    }
    const payload = getEnvelopeData(result.data)
    marketAsOf.value = payload?.as_of || ''
    marketItems.value = payload?.items || []
  } catch (e) {
    marketError.value = e?.message || '获取大盘资金流向失败'
  } finally {
    marketLoading.value = false
  }
}

const loadSectorFlow = async (refresh = false) => {
  sectorLoading.value = true
  sectorError.value = ''
  try {
    const result = await getSectorFundFlow({
      type: sectorType.value,
      page: sectorPage.value,
      page_size: sectorPageSize.value,
      refresh
    })
    if (!result.success) {
      sectorError.value = result.message || '获取板块资金流向失败'
      sectorItems.value = []
      sectorTotal.value = 0
      return
    }
    const payload = getEnvelopeData(result.data)
    sectorAsOf.value = payload?.as_of || ''
    sectorItems.value = payload?.items || []
    sectorTotal.value = payload?.total || 0
  } catch (e) {
    sectorError.value = e?.message || '获取板块资金流向失败'
  } finally {
    sectorLoading.value = false
  }
}

const loadStockFlow = async (refresh = false) => {
  stockLoading.value = true
  stockError.value = ''
  try {
    const result = await getStockFundFlow({
      market: stockMarket.value,
      stat: stockStat.value,
      page: stockPage.value,
      page_size: stockPageSize.value,
      refresh
    })
    if (!result.success) {
      stockError.value = result.message || '获取个股资金流向失败'
      stockItems.value = []
      stockTotal.value = 0
      return
    }
    const payload = getEnvelopeData(result.data)
    stockAsOf.value = payload?.as_of || ''
    stockItems.value = payload?.items || []
    stockTotal.value = payload?.total || 0
  } catch (e) {
    stockError.value = e?.message || '获取个股资金流向失败'
  } finally {
    stockLoading.value = false
  }
}

const changeSectorPage = (page) => {
  if (page < 1 || page > sectorTotalPages.value) return
  sectorPage.value = page
  loadSectorFlow()
}

const changeStockPage = (page) => {
  if (page < 1 || page > stockTotalPages.value) return
  stockPage.value = page
  loadStockFlow()
}

watch(sectorType, () => {
  sectorPage.value = 1
  loadSectorFlow()
})

watch([stockMarket, stockStat], () => {
  stockPage.value = 1
  loadStockFlow()
})

onMounted(async () => {
  await loadMarketFlow()
  await loadSectorFlow()
  await loadStockFlow()
})
</script>

<style scoped>
.fund-source-page {
  min-height: 100vh;
  background: #fff8f0;
}

.risk-banner {
  background: #fff3e6;
  border-bottom: 1px solid #ffb380;
  padding: 10px 20px;
}

.risk-banner__main {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.risk-banner__text {
  color: #666;
  font-size: 13px;
  line-height: 1.5;
  flex: 1;
}

.risk-banner__toggle {
  background: transparent;
  border: none;
  color: #ff7f24;
  cursor: pointer;
  padding: 0;
  font-size: 13px;
  white-space: nowrap;
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

.module-tip {
  color: #999;
  font-size: 12px;
  line-height: 1.4;
}

.tabs-tip {
  padding: 6px 20px 0;
}

.tabs {
  display: flex;
  gap: 12px;
  padding: 16px 20px 0;
}

.tab-btn {
  background: #fff3e6;
  border: 1px solid #ff7f24;
  color: #ff7f24;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
}

.tab-btn.active {
  background: #ff7f24;
  color: #fff;
}

.content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  border: 1px solid #ffb380;
  padding: 20px;
}

.card-title {
  font-size: 18px;
  color: #ff7f24;
  font-weight: bold;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.select {
  padding: 6px 10px;
  border: 1px solid #ffb380;
  border-radius: 4px;
  outline: none;
}

.refresh-btn {
  background-color: #fff3e6;
  color: #ff7f24;
  border: 1px solid #ff7f24;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn:hover {
  background-color: #ffe8cc;
}

.asof {
  font-size: 12px;
  color: #666;
  margin-left: 8px;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  background-color: #fff3e6;
  color: #ff7f24;
  padding: 10px 6px;
  text-align: left;
  border-bottom: 2px solid #ffb380;
  font-size: 13px;
}

.table td {
  padding: 10px 6px;
  border-bottom: 1px solid #fff3e6;
  font-size: 13px;
}

.loading,
.empty {
  text-align: center;
  padding: 20px;
  color: #999;
}

.error-message {
  background-color: #ffe8cc;
  color: #ff4500;
  padding: 12px;
  border-radius: 4px;
  border: 1px solid #ff7f24;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 12px;
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
  font-size: 14px;
}

.red {
  color: #ff4500;
}

.green {
  color: #008000;
}

.neutral {
  color: #999;
}

@media (max-width: 1024px) {
  .content {
    padding: 16px;
  }

  .table th,
  .table td {
    font-size: 12px;
  }
}
</style>
