<template>
  <div>
    <!-- 顶部栏 -->
    <header class="top-bar">
      <div class="container">
        <div class="top-left">
          <h1 class="logo">脑科学研究室</h1>
          <span class="slogan">历史数据研究与模拟平台</span>
        </div>
      </div>
    </header>

    <!-- 导航菜单 -->
    <nav class="main-nav">
      <div class="container">
        <ul class="nav-list">
          <li><a href="#" class="active">首页</a></li>
          <li><router-link to="/finance-channel">宏微观数据集</router-link></li>
          <li><router-link to="/daily-insight">每日数据模拟分析</router-link></li>
          <li><router-link to="/shop">研究数据样本库</router-link></li>
          <li><router-link to="/stock-data">数据模拟中心</router-link></li>
          <li><router-link to="/niu-model">脑科学技术研究中心</router-link></li>
        </ul>
      </div>
    </nav>

    <div class="risk-banner" role="note" aria-label="风险提示">
      <div class="container risk-banner__main">
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

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="container">
        <!-- 财经头条板块 -->
        <div class="section-header-inline" style="margin: 0 0 15px 0;">
          <h2 class="section-title" style="margin: 0;">宏微观数据</h2>
          <div class="header-actions">
            <button class="refresh-icon-btn" @click="loadNews(true)" :disabled="newsLoading" title="重新加载数据">
              <span v-if="!newsLoading">⟳</span>
              <span v-else>...</span>
            </button>
          </div>
        </div>
        <div class="module-tip">仅研究展示，不构成建议，数据或延迟误差</div>
        <section class="news-section">
          <!-- 加载状态 -->
          <div v-if="newsLoading && !bannerNews" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载宏微观数据快照...</p>
          </div>
          
          <!-- 新闻内容 -->
          <template v-else>
            <div v-if="bannerNews" class="news-banner">
              <div class="banner-text">
                <h3 class="mask-title">{{ bannerNews.title }}</h3>
                <p class="mask-desc">{{ bannerNews.summary || '暂无摘要' }}</p>
              </div>
            </div>
            <div v-else class="empty-news">
              <p>{{ newsError || '暂无宏微观数据快照' }}</p>
              <button v-if="newsError" @click="loadNews(true)" class="retry-btn" style="margin-top: 10px;">重试</button>
            </div>
            <div class="news-list" v-if="newsList.length">
              <ul>
                <li v-for="news in newsList" :key="news.id || news.url">
                  <span class="news-title">{{ news.title }}</span>
                </li>
              </ul>
            </div>
          </template>
        </section>

        <div class="section-header-inline" style="margin: 20px 0 15px 0;">
          <h2 class="section-title" style="margin: 0;">每日数据模拟分析</h2>
          <div class="header-actions">
            <router-link to="/daily-insight" class="more-link" style="font-size: 14px;">查看详情 &gt;</router-link>
          </div>
        </div>
        <div class="module-tip">仅研究展示，不构成建议，历史不代表未来</div>
        <div class="tab-switch report-tab-switch">
          <a 
            href="javascript:;" 
            :class="{ active: reportTab==='report-latest' }" 
            @click.prevent="handleLatestTabClick"
            title="每日 03:00 更新"
          >
            最新 (03:00更新)
          </a>
        </div>
        <section class="daily-report">
          <!-- 加载状态 -->
          <div v-if="dailyReportLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载每日数据模拟分析...</p>
          </div>
          
          <!-- 数据加载完成后的内容 -->
          <template v-else>
            <!-- 最新内参 -->
            <div v-show="reportTab==='report-latest'" class="tab-content report-content" id="report-latest">
              <div v-if="visibleLatestDailyReport" class="report-item">
                <h3>{{ visibleLatestDailyReport.title || '最新数据模拟样本' }}</h3>
                <p>{{ truncateText(visibleLatestDailyReport.market_sentiment, 120) }}</p>
                <span class="design">系统 | 研究样本</span>
                <span class="date">{{ formatReportDate(visibleLatestDailyReport.report_date) }}</span>
              </div>
              <div v-else class="report-item">
                <h3>{{ dailyReportError || (latestReportHiddenByTime ? '当日数据暂不展示' : '暂无最新内参') }}</h3>
                <p>{{ dailyReportError ? '请点击重试按钮重新加载' : (latestReportHiddenByTime ? '每日数据模拟分析将在次日 04:00 后展示。' : '系统正在生成最新的数据模拟分析样本，请稍后查看。') }}</p>
                <button v-if="dailyReportError" @click="loadDailyReports" class="retry-btn" style="margin-top: 10px;">重试</button>
              </div>
            </div>

            <!-- 昨日内参 -->
            <div v-show="reportTab==='report-yesterday'" class="tab-content report-content" id="report-yesterday">
              <div v-if="getYesterdayReport()" class="report-item">
                <h3>{{ getYesterdayReport().title }}</h3>
                <p>{{ truncateText(getYesterdayReport().market_sentiment, 120) }}</p>
                <span class="design">系统 | 研究样本</span>
                <span class="date">{{ formatReportDate(getYesterdayReport().report_date) }}</span>
              </div>
              <div v-else class="report-item">
                <h3>暂无昨日内参</h3>
                <p>昨日数据模拟分析样本暂未生成。</p>
                <button v-if="dailyReportError" @click="loadDailyReports" class="retry-btn" style="margin-top: 10px;">重试</button>
              </div>
            </div>

            <!-- 历史内参 -->
            <div v-show="reportTab==='report-history'" class="tab-content report-content" id="report-history">
              <template v-if="dailyReportHistory.length > 0">
                <div 
                  v-for="report in dailyReportHistory.slice(0, 3)" 
                  :key="report.id" 
                  class="report-item"
                >
                  <h3>{{ report.title }}</h3>
                  <p>{{ truncateText(report.market_sentiment, 100) }}</p>
                  <span class="design">系统 | 研究样本</span>
                  <span class="date">{{ formatReportDate(report.report_date) }}</span>
                </div>
              </template>
              <div v-else class="report-item">
                <h3>暂无历史内参</h3>
                <p>历史数据模拟分析样本暂未生成。</p>
                <button v-if="dailyReportError" @click="loadDailyReports" class="retry-btn" style="margin-top: 10px;">重试</button>
              </div>
            </div>
          </template>
        </section>


        <!-- 龙虎榜板块（新增切换内容容器） -->
        <div class="section-header-inline" style="margin: 20px 0 15px 0;">
          <h2 class="section-title" style="margin: 0;">{{ dragonFailed ? '大盘指数' : '公开异动统计' }}</h2>
        </div>
        <div class="module-tip">仅研究展示，不构成建议，数据或延迟误差</div>
        <div v-if="!dragonFailed" class="tab-switch dragon-tab-switch">
          <a href="javascript:;" :class="{ active: dragonTab==='dragon-today' }" @click.prevent="dragonTab='dragon-today'">今日</a>
          <a href="javascript:;" :class="{ active: dragonTab==='dragon-5day' }" @click.prevent="dragonTab='dragon-5day'">5日</a>
          <a href="javascript:;" :class="{ active: dragonTab==='dragon-20day' }" @click.prevent="dragonTab='dragon-20day'">20日</a>
          <span v-if="dragonLoading" class="loading-indicator">加载中...</span>
        </div>
        <section class="dragon-board">
          <!-- 龙虎榜失败时显示大盘指数 -->
          <template v-if="dragonFailed">
            <!-- 大盘指数加载中 -->
            <div v-if="marketIndexLoading" class="loading-state">
              <div class="loading-spinner"></div>
              <p>正在加载大盘指数数据...</p>
            </div>
            <!-- 大盘指数数据 -->
            <div v-else-if="marketIndexData.length > 0" class="tab-content dragon-content">
              <table class="dragon-table">
                <thead>
                  <tr>
                    <th>指数名称</th>
                    <th>最新价</th>
                    <th>涨跌幅</th>
                    <th>涨跌额</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in marketIndexData" :key="idx">
                    <td>{{ row.name }}</td>
                    <td>{{ row.price }}</td>
                    <td><span :class="row.change > 0 ? 'red' : 'green'">{{ row.changeText }}</span></td>
                    <td>{{ row.changeAmount }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- 数据丢失 -->
            <div v-else class="error-state">
              <p>{{ marketIndexError || '数据丢失' }}</p>
              <button @click="loadMarketIndex" class="retry-btn">重试</button>
            </div>
          </template>
          
          <!-- 龙虎榜正常显示 -->
          <template v-else>
            <!-- 加载状态 -->
            <div v-if="dragonLoading && dragonTab==='dragon-today'" class="loading-state">
              <div class="loading-spinner"></div>
              <p>正在加载龙虎榜数据...</p>
            </div>
            
            <!-- 错误状态 -->
            <div v-else-if="dragonError && dragonTab==='dragon-today' && dragonToday.length === 0" class="error-state">
              <p>{{ dragonError }}</p>
              <button @click="loadDragonData(1)" class="retry-btn">重试</button>
            </div>
            
            <div v-show="dragonTab==='dragon-today' && !dragonLoading" class="tab-content dragon-content" id="dragon-today">
              <template v-if="dragonToday.length > 0">
                <table class="dragon-table">
                  <thead>
                    <tr>
                      <th>名称</th>
                      <th>最新价</th>
                      <th>涨跌幅</th>
                      <th>涨跌</th>
                      <th>净买入(亿)</th>
                      <th>买入额(亿)</th>
                      <th>卖出额(亿)</th>
                      <th>上榜次数</th>
                      <th>上榜理由</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in dragonToday" :key="idx">
                      <td>{{ row.name }}</td>
                      <td>{{ row.price }}</td>
                      <td><span :class="row.change>0 ? 'green' : 'red'">{{ row.changeText }}</span></td>
                      <td>{{ row.delta }}</td>
                      <td>{{ row.net }}</td>
                      <td>{{ row.buy }}</td>
                      <td>{{ row.sell }}</td>
                      <td>{{ row.appearCount }}</td>
                      <td>{{ row.reason }}</td>
                    </tr>
                  </tbody>
                </table>
              </template>
              <div v-else class="error-state">
                <p>数据丢失</p>
              </div>
            </div>

            <div v-show="dragonTab==='dragon-5day'" class="tab-content dragon-content" id="dragon-5day">
              <!-- 5日加载状态 -->
              <div v-if="dragonLoading && dragon5Data.length === 0" class="loading-state">
                <div class="loading-spinner"></div>
                <p>正在加载5日龙虎榜数据...</p>
              </div>
              <template v-else-if="dragon5.length > 0">
                <table class="dragon-table">
                  <thead>
                    <tr>
                      <th>名称</th>
                      <th>最新价</th>
                      <th>涨跌幅</th>
                      <th>涨跌</th>
                      <th>净买入(亿)</th>
                      <th>买入额(亿)</th>
                      <th>卖出额(亿)</th>
                      <th>上榜次数</th>
                      <th>上榜理由</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in dragon5" :key="idx">
                      <td>{{ row.name }}</td>
                      <td>{{ row.price }}</td>
                      <td><span :class="row.change>0 ? 'green' : 'red'">{{ row.changeText }}</span></td>
                      <td>{{ row.delta }}</td>
                      <td>{{ row.net }}</td>
                      <td>{{ row.buy }}</td>
                      <td>{{ row.sell }}</td>
                      <td>{{ row.appearCount }}</td>
                      <td>{{ row.reason }}</td>
                    </tr>
                  </tbody>
                </table>
              </template>
              <div v-else class="error-state">
                <p>数据丢失</p>
              </div>
            </div>

            <div v-show="dragonTab==='dragon-20day'" class="tab-content dragon-content" id="dragon-20day">
              <!-- 20日加载状态 -->
              <div v-if="dragonLoading && dragon20Data.length === 0" class="loading-state">
                <div class="loading-spinner"></div>
                <p>正在加载20日龙虎榜数据...</p>
              </div>
              <template v-else-if="dragon20.length > 0">
                <table class="dragon-table">
                  <thead>
                    <tr>
                      <th>名称</th>
                      <th>最新价</th>
                      <th>涨跌幅</th>
                      <th>涨跌</th>
                      <th>净买入(亿)</th>
                      <th>买入额(亿)</th>
                      <th>卖出额(亿)</th>
                      <th>上榜次数</th>
                      <th>上榜理由</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in dragon20" :key="idx">
                      <td>{{ row.name }}</td>
                      <td>{{ row.price }}</td>
                      <td><span :class="row.change>0 ? 'green' : 'red'">{{ row.changeText }}</span></td>
                      <td>{{ row.delta }}</td>
                      <td>{{ row.net }}</td>
                      <td>{{ row.buy }}</td>
                      <td>{{ row.sell }}</td>
                      <td>{{ row.appearCount }}</td>
                      <td>{{ row.reason }}</td>
                    </tr>
                  </tbody>
                </table>
              </template>
              <div v-else class="error-state">
                <p>数据丢失</p>
              </div>
            </div>
          </template>
        </section>

        <!-- 研报板块 -->
        <div class="section-header-inline">
          <h2 class="section-title">公开文本索引</h2>
          <div class="header-actions">
            <button v-if="companyReportsData.length > 0" @click="loadCompanyReports" class="refresh-icon-btn" :disabled="companyReportsLoading" title="重新加载数据">
              <span v-if="companyReportsLoading">⟳</span>
              <span v-else>↻</span>
            </button>
            <router-link to="/company-research" class="more-link">查看全部 &gt;</router-link>
          </div>
        </div>
        <div class="module-tip">仅研究展示，不构成建议，历史不代表未来</div>
        <section class="company-report">
          <!-- 加载状态 -->
          <div v-if="companyReportsLoading && companyReportsData.length === 0" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载公开文本数据...</p>
          </div>
          
          <!-- 错误状态 -->
          <div v-else-if="companyReportsError && companyReportsData.length === 0" class="error-state">
            <p>{{ companyReportsError }}</p>
            <button @click="loadCompanyReports" class="retry-btn">重试</button>
          </div>
          
          <!-- 研报卡片 -->
          <div v-else class="report-cards">
            <div class="report-card" v-for="card in companyReportsData" :key="card.id" @click="viewCompanyReport(card)">
              <div class="card-body">
                <div class="stock-info">
                  <span class="stock-name">{{ card.company_name }}<span v-if="card.stock_code" class="stock-code-small">({{ card.stock_code }})</span></span>
                  <span :class="getRatingClass(card.rating)">{{ getRatingTag(card.rating) }}</span>
                </div>
                <div class="report-meta">
                  <span class="meta-item">{{ card.report_type === 'analysis' ? '结构化分析' : '文本摘要样本' }}</span>
                  <span class="meta-item">{{ formatDate(card.created_at) }}</span>
                </div>
                <ul class="report-ul" v-if="card.tags && card.tags.length">
                  <li v-for="(t, i) in card.tags.slice(0, 3)" :key="i">{{ t }}</li>
                </ul>
                <div style="clear:both;"></div>
                <button class="view-btn" @click.stop="viewCompanyReport(card)">查看报告</button>
              </div>
            </div>
          </div>
          
          <!-- 空状态 -->
          <div v-if="!companyReportsLoading && !companyReportsError && companyReportsData.length === 0" class="error-state">
            <p>暂无公司研报数据</p>
            <button @click="loadCompanyReports" class="retry-btn">加载数据</button>
          </div>
        </section>

        <!-- 脑科学研究室板块 -->
        <div class="section-header-inline">
          <h2 class="section-title">研究数据样本库</h2>
          <div class="header-actions">
            <router-link to="/shop" class="more-link" style="float:right;margin-top:15px;font-size: 14px;">查看详情 &gt;</router-link>
          </div>
        </div>
        <div class="module-tip">仅研究展示，不构成建议，数据或延迟误差</div>
        <section class="mall-section">
          <div class="strategy-list">
            <div class="strategy-item" @click="router.push('/shop')">
              <h4>指数增强策略</h4>
              <p>通过构建一个极度分散的股票组合，以较小的误差跟踪特定的市场指数...</p>
            </div>
            <div class="strategy-item" @click="router.push('/shop')">
              <h4>CTA策略</h4>
              <p>同时监控并跟踪商品期货市场的高流动性期货合约，在维持头寸分散的基础上，利用商品...</p>
            </div>
            <div class="strategy-item" @click="router.push('/shop')">
              <h4>量化对冲策略</h4>
              <p>通过量化因子叠加形成策略组合对全市场股票进行分散投资形成股票多头组合...</p>
            </div>
          </div>
        </section>

      </div>
    </main>

    <!-- 页脚 -->
    <FooterComponent />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import FooterComponent from './FooterComponent.vue'
import { getTopListSummary, getMarketOverview } from '@/services/marketService'
import { getMarketData } from '@/services/financeChannelService'
import { getLatestDailyReport, getDailyReportList, getDailyReportByDate } from '@/services/dailyReportService'
import { getCompanyResearchList } from '@/services/companyResearchService'
import { getProducts, formatPrice as serviceFormatPrice } from '@/services/productService'
import { getWeiboMediaNews } from '@/services/newsService'

// 缓存配置（与 FinanceChannelPage 保持一致）
const CACHE_DURATION = 30 * 60 * 1000 // 30分钟（毫秒）

const search = ref('')
const dragonTab = ref('dragon-today')
const reportTab = ref('report-latest')
const riskExpanded = ref(false)

// 龙虎榜数据状态
const dailyReportLoading = ref(false)
const dailyReportError = ref('')
const latestDailyReport = ref(null)
const dailyReportHistory = ref([])
const dragonLoading = ref(false)
const dragonError = ref('')
const dragonFailed = ref(false) // 龙虎榜加载失败标记

// 大盘指数数据（龙虎榜失败时显示）
const marketIndexData = ref([])
const marketIndexLoading = ref(false)
const marketIndexError = ref('')


// 公司研报数据状态
const companyReportsLoading = ref(false)
const companyReportsError = ref('')
const companyReportsData = ref([])

// 脑科学研究室商品数据状态
const mallProducts = ref([])
const mallProductsLoading = ref(false)
const defaultProductImg = 'https://picsum.photos/400/300?random=0'

// 宏微观数据快照状态
const newsLoading = ref(false)
const newsError = ref('')
const newsList = ref([])
const bannerNews = ref(null)

const router = useRouter()

// ==================== 缓存工具函数（与 FinanceChannelPage 保持一致）====================

/**
 * 从缓存中读取数据
 * @param {string} key - 缓存键
 * @returns {object|null} - 缓存数据或null
 */
function getCacheData(key) {
  try {
    const cached = localStorage.getItem(key)
    if (!cached) return null
    
    const { data, timestamp } = JSON.parse(cached)
    const now = Date.now()
    
    // 检查缓存是否过期
    if (now - timestamp > CACHE_DURATION) {
      localStorage.removeItem(key)
      return null
    }
    
    return data
  } catch (error) {
    console.error('读取缓存失败:', error)
    return null
  }
}

/**
 * 将数据保存到缓存
 * @param {string} key - 缓存键
 * @param {any} data - 要缓存的数据
 */
function setCacheData(key, data) {
  try {
    const cacheObject = {
      data,
      timestamp: Date.now()
    }
    localStorage.setItem(key, JSON.stringify(cacheObject))
  } catch (error) {
    console.error('保存缓存失败:', error)
  }
}

const goToCompanyResearch = () => {
  router.push('/company-research')
}

// 跳转到详情页
const goToNewsDetail = (id) => {
  if (!id) return
  router.push(`/news-detail/${id}`)
}


// 加载宏微观数据快照（优先使用缓存）
const loadNews = async (forceRefresh = false) => {
  // 使用与 FinanceChannelPage 相同的缓存 key，确保两个页面共享缓存
  const cacheKey = 'finance_news_default'
  
  // 如果不是强制刷新，优先从缓存读取
  if (!forceRefresh) {
    const cachedData = getCacheData(cacheKey)
    if (cachedData && Array.isArray(cachedData) && cachedData.length > 0) {
      console.log('使用缓存的财经资讯数据（HomePage）')
      
      // 使用缓存数据填充 banner 和列表
      bannerNews.value = {
        id: cachedData[0].id,
        title: cachedData[0].title || '暂无标题',
        summary: cachedData[0].summary || '暂无摘要',
        url: cachedData[0].url || cachedData[0].link || '',
        img: '/1.png'
      }
      newsList.value = cachedData.slice(1, 6).map(item => ({
        id: item.id,
        title: item.title || '暂无标题',
        url: item.url || item.link || ''
      }))
      return
    }
  }
  
  try {
    newsLoading.value = true
    newsError.value = ''
    const response = await getWeiboMediaNews({ limit: 20 })
    const payload = response?.data || response

    const items = Array.isArray(payload?.items) ? payload.items : []

    if (items.length > 0) {
      // 保存完整数据到缓存（与 FinanceChannelPage 共享）
      setCacheData(cacheKey, items)
      
      bannerNews.value = {
        id: items[0].id,
        title: items[0].title || '暂无标题',
        summary: items[0].summary || '暂无摘要',
        url: items[0].url || items[0].link || '',
        img: '/1.png'
      }
      newsList.value = items.slice(1, 6).map(item => ({
        id: item.id,
        title: item.title || '暂无标题',
        url: item.url || item.link || ''
      }))
    } else {
      bannerNews.value = null
      newsList.value = []
    }
  } catch (e) {
    console.error('加载宏微观数据快照失败:', e)
    newsError.value = '加载失败'
    bannerNews.value = null
    newsList.value = []
  } finally {
    newsLoading.value = false
  }
}

// 加载脑科学研究室商品数据
const loadMallProducts = async () => {
  mallProductsLoading.value = true
  try {
    const result = await getProducts({ limit: 4 })
    if (result.success && result.data) {
      // 直接取前2个商品显示
      mallProducts.value = result.data.slice(0, 2)
    }
  } catch (error) {
    console.error('Failed to load mall products:', error)
  } finally {
    mallProductsLoading.value = false
  }
}

// 格式化价格
const formatPrice = (price) => {
  return serviceFormatPrice(price)
}

// 获取商品类型中文名
const getProductTypeName = (type) => {
  const typeMap = {
    'course': '课程',
    'factor': '模拟参数',
    'strategy': '回测模型',
    'fund': '基金',
    'advisor': '投顾',
    'book': '书籍',
    'talent': '人才'
  }
  return typeMap[type] || '商品'
}

// 页面加载时初始化
onMounted(() => {
  loadNews()
  loadCompanyReports()
  loadMallProducts()
  loadDailyReports()
})

// 辅助函数：截断文本
const truncateText = (text, maxLength) => {
  if (!text) return '暂无内容'
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 辅助函数：格式化报告日期
const formatReportDate = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  } catch {
    return dateString
  }
}

// 处理"最新"标签点击
const handleLatestTabClick = () => {
  reportTab.value = 'report-latest'
}

const canDisplayDailyReportByDate = (dateString) => {
  if (!dateString) return false
  const datePart = String(dateString).split('T')[0]
  const [year, month, day] = datePart.split('-').map(Number)
  if (!year || !month || !day) return true

  const unlockAt = new Date(year, month - 1, day + 1, 4, 0, 0, 0)
  return new Date() >= unlockAt
}

const getDatePart = (dateString) => {
  if (!dateString) return ''
  return String(dateString).split('T')[0]
}

const getOffsetDatePart = (dateString, offsetDays) => {
  const datePart = getDatePart(dateString)
  const [year, month, day] = datePart.split('-').map(Number)
  if (!year || !month || !day) return ''

  const date = new Date(year, month - 1, day + offsetDays)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const getPreviousDailyReport = () => {
  const latest = latestDailyReport.value
  if (!latest?.report_date) return null

  const latestDate = getDatePart(latest.report_date)
  const previousDate = getOffsetDatePart(latest.report_date, -1)

  if (!dailyReportHistory.value || dailyReportHistory.value.length === 0) return null

  const previousDayReport = dailyReportHistory.value.find(report => getDatePart(report.report_date) === previousDate)
  if (previousDayReport) return previousDayReport

  return dailyReportHistory.value.find(report => getDatePart(report.report_date) !== latestDate) || null
}

const visibleLatestDailyReport = computed(() => {
  const report = latestDailyReport.value
  if (!report?.report_date) return null
  if (canDisplayDailyReportByDate(report.report_date)) {
    return report
  }
  return getPreviousDailyReport()
})

const latestReportHiddenByTime = computed(() => {
  const report = latestDailyReport.value
  if (!report?.report_date) return false
  return !canDisplayDailyReportByDate(report.report_date)
})

// 辅助函数：获取昨日报告
const getYesterdayReport = () => {
  if (!dailyReportHistory.value || dailyReportHistory.value.length === 0) return null
  
  const today = new Date().toISOString().split('T')[0]
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  
  // 查找昨日报告
  const yesterdayReport = dailyReportHistory.value.find(report => report.report_date === yesterday)
  if (yesterdayReport) return yesterdayReport
  
  // 如果没有昨日报告，返回最近的一个（非今日）
  return dailyReportHistory.value.find(report => report.report_date !== today) || null
}

// 加载龙虎榜数据（根据天数）
const loadDragonData = async (days = 1) => {
  dragonLoading.value = true
  dragonError.value = ''
  
  try {
    const result = await getTopListSummary(days)
    
    if (result.success && result.data?.data && result.data.data.length > 0) {
      // 转换 API 数据为前端格式
      const formattedData = result.data.data.slice(0, 10).map(item => ({
        name: item.name || '',
        price: item.close?.toFixed(2) || '-',
        change: item.pct_change || 0,
        changeText: item.pct_change ? `${item.pct_change > 0 ? '+' : ''}${item.pct_change.toFixed(2)}%` : '-',
        delta: item.pct_change?.toFixed(2) || '-',
        net: item.net_amount ? (item.net_amount / 100000000).toFixed(2) : '-', // 转换为亿
        buy: item.total_buy ? (item.total_buy / 100000000).toFixed(2) : (item.l_buy ? (item.l_buy / 100000000).toFixed(2) : '-'),
        sell: item.total_sell ? (item.total_sell / 100000000).toFixed(2) : (item.l_sell ? (item.l_sell / 100000000).toFixed(2) : '-'),
        appearCount: item.appear_count || 1,
        reason: item.reason || '-'
      }))
      
      // 根据天数存储到对应的数据中
      if (days === 1) {
        dragonTodayData.value = formattedData
        dragonFailed.value = false
      } else if (days === 5) {
        dragon5Data.value = formattedData
      } else if (days === 20) {
        dragon20Data.value = formattedData
      }
    } else {
      dragonError.value = '数据丢失'
      if (days === 1) {
        dragonFailed.value = true
        // 龙虎榜加载失败，尝试加载大盘指数作为替代
        loadMarketIndex()
      }
    }
  } catch (e) {
    console.error(`加载${days}日龙虎榜失败:`, e)
    dragonError.value = '数据丢失'
    if (days === 1) {
      dragonFailed.value = true
      // 龙虎榜加载失败，尝试加载大盘指数作为替代
      loadMarketIndex()
    }
  } finally {
    dragonLoading.value = false
  }
}

// 加载大盘指数数据（龙虎榜失败时替代显示）
const loadMarketIndex = async () => {
  marketIndexLoading.value = true
  marketIndexError.value = ''
  
  try {
    const result = await getMarketData()

    if (result?.data?.items && result.data.items.length > 0) {
      const items = result.data.items
      marketIndexData.value = items.map(item => {
        const price = Number(item.value)
        const pct = Number(item.change_pct)
        const changeAmount = Number.isFinite(price) && Number.isFinite(pct)
          ? (price * (pct / 100)).toFixed(2)
          : '-'
        const changeText = Number.isFinite(pct)
          ? `${pct > 0 ? '+' : ''}${pct.toFixed(2)}%`
          : '-'

        return {
          name: item.title || item.code || '-',
          price: Number.isFinite(price) ? price.toFixed(2) : '-',
          change: Number.isFinite(pct) ? pct : 0,
          changeText,
          changeAmount: Number.isFinite(Number(changeAmount)) ? `${pct > 0 ? '+' : ''}${changeAmount}` : '-',
          updatedAt: item.updated_at ? item.updated_at.replace('T', ' ').slice(0, 19) : '-'
        }
      })
    } else {
      marketIndexError.value = '数据丢失'
    }
  } catch (e) {
    console.error('加载大盘指数失败:', e)
    marketIndexError.value = '数据丢失'
  } finally {
    marketIndexLoading.value = false
  }
}

// 加载每日数据模拟分析数据
const loadDailyReports = async () => {
  // 如果已经有数据，则不重复加载
  if (latestDailyReport.value) {
    return
  }

  dailyReportLoading.value = true
  dailyReportError.value = ''

  try {
    // 优先加载最新交易日的报告
    const overviewResult = await getMarketOverview()
    let latestTradeDate = ''
    if (overviewResult.success && overviewResult.data) {
      let overviewData = overviewResult.data
      if (overviewData.data && overviewData.code === 0) {
        overviewData = overviewData.data
      }
      latestTradeDate = overviewData.trade_date || overviewData.tradeDate || ''
    }

    if (latestTradeDate) {
      const latestByDate = await getDailyReportByDate(latestTradeDate)
      if (latestByDate.success && latestByDate.data) {
        let reportData = latestByDate.data
        if (reportData.data && reportData.code === 0) {
          reportData = reportData.data
        }
        if (reportData.id && reportData.report_date) {
          latestDailyReport.value = reportData
        }
      }
    }

    if (!latestDailyReport.value) {
      // 兜底：加载最新报告
      const latestResult = await getLatestDailyReport()

      if (latestResult.success && latestResult.data) {
        let reportData = latestResult.data
        if (reportData.data && reportData.code === 0) {
          reportData = reportData.data
        }
        if (reportData.id && reportData.report_date) {
          latestDailyReport.value = reportData
        }
      } else if (latestResult.status === 404) {
        dailyReportError.value = '暂无最新报告'
      } else if (latestResult.status === 401 || latestResult.status === 403) {
        dailyReportError.value = '暂无数据'
      } else {
        dailyReportError.value = latestResult.message || '加载失败'
      }
    }

    // 加载历史报告
    const historyResult = await getDailyReportList({ limit: 10 })

    if (historyResult.success && historyResult.data) {
      let historyData = historyResult.data

      if (historyData.data && historyData.code === 0) {
        historyData = historyData.data
      }

      if (historyData.reports && Array.isArray(historyData.reports)) {
        dailyReportHistory.value = historyData.reports
      } else if (Array.isArray(historyData)) {
        dailyReportHistory.value = historyData
      }
    }
  } catch (e) {
    dailyReportError.value = `加载异常: ${e.message || e}`
  } finally {
    dailyReportLoading.value = false
  }
}

// 龙虎榜数据存储
const dragonTodayData = ref([])
const dragon5Data = ref([])
const dragon20Data = ref([])

// 计算属性：根据 tab 返回对应数据（无数据时返回空数组）
const dragonToday = computed(() => dragonTodayData.value)
const dragon5 = computed(() => dragon5Data.value)
const dragon20 = computed(() => dragon20Data.value)

// 监听 tab 切换，加载对应数据
watch(dragonTab, (newTab) => {
  if (newTab === 'dragon-today' && dragonTodayData.value.length === 0 && !dragonFailed.value) {
    loadDragonData(1)
  } else if (newTab === 'dragon-5day' && dragon5Data.value.length === 0) {
    loadDragonData(5)
  } else if (newTab === 'dragon-20day' && dragon20Data.value.length === 0) {
    loadDragonData(20)
  }
})

// 页面加载时检查API状态并加载龙虎榜
onMounted(() => {
  loadDragonData(1) // 默认加载今日数据
})

// 加载公司研报数据
const loadCompanyReports = async () => {
  companyReportsLoading.value = true
  companyReportsError.value = ''
  
  try {
    const result = await getCompanyResearchList({ limit: 3, offset: 0 })
    
    if (result.success && result.data) {
      const payload = result.data.data || result.data
      // 兼容 { total, items } 和直接数组
      if (payload.items) {
        companyReportsData.value = payload.items
      } else if (Array.isArray(payload)) {
        companyReportsData.value = payload
      } else {
        companyReportsData.value = []
      }
    } else {
      companyReportsError.value = result.message || '加载公司研报失败'
    }
  } catch (error) {
    console.error('加载公司研报失败:', error)
    companyReportsError.value = '网络错误，请稍后重试'
  } finally {
    companyReportsLoading.value = false
  }
}

// 查看公司研报详情
const viewCompanyReport = (report) => {
  router.push(`/company-research/${report.id}`)
}

// 评级映射
const ratingMap = {
  'buy': { tag: '买入', tagClass: 'mai-ru' },
  'add': { tag: '增持', tagClass: 'mai-ru-zeng' },
  'hold': { tag: '持有', tagClass: 'chi-you' },
  'reduce': { tag: '减持', tagClass: 'jian-chi' },
  'sell': { tag: '卖出', tagClass: 'mai-chu' }
}

const getRatingTag = (rating) => {
  return ratingMap[rating]?.tag || '持有'
}

const getRatingClass = (rating) => {
  return ratingMap[rating]?.tagClass || 'chi-you'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' })
  } catch {
    return '-'
  }
}

</script>

<style scoped>
/* 龙虎榜加载状态样式 */
.loading-indicator {
  margin-left: 15px;
  color: #ff7f24;
  font-size: 12px;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: #fff8f0;
  border-radius: 8px;
  margin: 10px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #ffe0c0;
  border-top-color: #ff7f24;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p,
.error-state p {
  margin-top: 15px;
  color: #666;
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 20px;
  background: #ff7f24;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-btn:hover {
  background: #ff6a00;
}

/* 财经头条展示优化 */
.news-section {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  margin-bottom: 16px;
}

.news-banner {
  background: linear-gradient(135deg, #fff6ee 0%, #ffffff 100%);
  border: 1px solid #ffe0c0;
  border-radius: 10px;
  padding: 16px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.news-banner:hover {
  transform: none;
  box-shadow: none;
}

.banner-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mask-title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  line-height: 1.4;
}

.mask-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.banner-cta {
  align-self: flex-start;
  font-size: 12px;
  color: #ff7f24;
  background: #fff;
  border: 1px solid #ff7f24;
  padding: 4px 10px;
  border-radius: 999px;
}

.news-list {
  margin-top: 12px;
}

.news-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}

.news-title {
  color: #333;
  font-size: 14px;
  display: block;
  padding: 8px 10px;
  border-radius: 6px;
  background: #fff8f0;
}

.empty-news {
  padding: 16px;
  text-align: center;
  color: #999;
  background: #fff8f0;
  border-radius: 8px;
  margin-top: 8px;
}

.risk-banner {
  background: #fff3e6;
  border-bottom: 1px solid #ffb380;
  padding: 10px 0;
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

.module-tip {
  color: #999;
  font-size: 12px;
  line-height: 1.4;
  margin: -4px 0 10px;
}

/* 禁用的标签样式 */
.tab-switch a.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  color: #999;
}

.tab-switch a.disabled:hover {
  background-color: transparent;
  color: #999;
}

/* 公司研报模块样式优化 */
.section-header-inline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0 15px;
  clear: both;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.refresh-icon-btn {
  background: transparent;
  border: 1px solid #ff7f24;
  color: #ff7f24;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  padding: 0;
}

.refresh-icon-btn:hover:not(:disabled) {
  background: #ff7f24;
  color: white;
  transform: rotate(90deg);
}

.refresh-icon-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.report-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.report-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #ffb380;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%; /* 确保卡片填满 Grid 单元格高度 */
}

.report-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(255, 127, 36, 0.25);
  border-color: #ff7f24;
}

.card-body {
  padding: 20px;
  flex: 1; /* 内容撑满剩余空间 */
  display: flex;
  flex-direction: column;
}

.stock-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #f0f0f0;
}

.stock-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  flex: 1;
  margin-right: 10px; /* 防止与标签太紧凑 */
  line-height: 1.4;
  white-space: nowrap; /* 不换行 */
  overflow: hidden; /* 隐藏溢出 */
  text-overflow: ellipsis; /* 显示省略号 */
}

.stock-code-small {
  font-size: 12px;
  color: #999;
  font-weight: normal;
  margin-left: 4px;
  white-space: nowrap; /* 股票代码不换行 */
}

.report-meta {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
}

.meta-item {
  color: #999;
}

.report-ul {
  list-style: none;
  padding: 0;
  margin: 12px 0;
  display: flex;
  flex-wrap: wrap; /* 允许标签换行，避免截断 */
  gap: 8px; /* 使用 gap 代替 margin 控制间距 */
}

.report-ul li {
  background: linear-gradient(to right, #ffeedd, #fff6ee);
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 3px;
  color: #ff7f24;
  white-space: nowrap; /* 标签内文字不换行 */
}

.view-btn {
  width: 100%;
  padding: 10px;
  background: white;
  border: 1px solid #ff7f24;
  color: #ff7f24;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.3s;
  margin-top: auto; /* 将按钮推到底部，对齐更整齐 */
}

.view-btn:hover {
  background: #ff7f24;
  color: white;
  box-shadow: 0 4px 12px rgba(255, 127, 36, 0.3);
}

/* 评级标签样式 */
.mai-ru {
  background: linear-gradient(to bottom, #DDFCE6, #c8f5d2);
  padding: 4px 10px;
  color: #18A44B;
  font-size: 12px;
  border-radius: 4px;
  font-weight: bold;
  white-space: nowrap;
}

.mai-ru-zeng {
  background: linear-gradient(to bottom, #FCF5C4, #f5ecaa);
  padding: 4px 10px;
  color: #976A1C;
  font-size: 12px;
  border-radius: 4px;
  font-weight: bold;
  white-space: nowrap;
}

.chi-you {
  background: linear-gradient(to bottom, #E0E0E0, #d0d0d0);
  padding: 4px 10px;
  color: #333333;
  font-size: 12px;
  border-radius: 4px;
  font-weight: bold;
  white-space: nowrap;
}

.jian-chi {
  background: linear-gradient(to bottom, #FFE0B2, #ffd090);
  padding: 4px 10px;
  color: #FF6D00;
  font-size: 12px;
  border-radius: 4px;
  font-weight: bold;
  white-space: nowrap;
}

.mai-chu {
  background: linear-gradient(to bottom, #FFCDD2, #fba4ab);
  padding: 4px 10px;
  color: #C62828;
  font-size: 12px;
  border-radius: 4px;
  font-weight: bold;
  white-space: nowrap;
}

/* 商品类型标签样式 */
.dragon-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 15px;
}

.dragon-table th,
.dragon-table td {
  padding: 12px 8px;
  text-align: center;
  border-bottom: 1px solid #f0f0f0;
  white-space: nowrap;
}

.dragon-table th {
  background-color: #fafafa;
  color: #333;
  font-weight: 500;
}

.dragon-table td {
  color: #666;
  font-size: 14px;
}

.product-type-tag {
  display: inline-block;
  background: linear-gradient(to right, #ff7f24, #ff9933);
  color: white;
  padding: 3px 8px;
  font-size: 11px;
  border-radius: 3px;
  margin-bottom: 8px;
  font-weight: 500;
}

.active {
  color: #ff7f24;
  font-weight: bold;
}

.red {
  color: #eb445a; /* 红色表示上涨 */
}

.green {
  color: #2dd36f; /* 绿色表示下跌 */
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .report-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .report-cards {
    grid-template-columns: 1fr;
  }
  
  .section-header-inline {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
.compliance-card h1 {
  margin: 0 0 10px;
  color: #333;
}

.strategy-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 10px;
}

.strategy-item {
  background: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 6px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.strategy-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 127, 36, 0.15);
}

.strategy-item h4 {
  margin: 0 0 10px;
  font-size: 16px;
  color: #8c4b00;
}

.strategy-item p {
  margin: 0;
  color: #666;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (max-width: 768px) {
  .strategy-list {
    grid-template-columns: 1fr;
  }
}
</style>
