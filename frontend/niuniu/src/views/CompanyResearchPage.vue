<template>
  <div class="company-research-page" style="background: #fff8f0; min-height: 100vh;">
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

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input v-model="searchQuery" type="text" placeholder="搜索公司、行业、关键字..." @keyup.enter="handleSearch" />
      <button class="search-btn" @click="handleSearch">搜索</button>
    </div>

    <!-- 来源分类 -->
    <div class="category-nav">
      <span class="category-item" :class="{ active: activeSource === 'ai' }" @click="setSource('ai')">结构化文本样本</span>
      <span class="category-item" :class="{ active: activeSource === 'eastmoney' }" @click="setSource('eastmoney')">公开文本数据源</span>
    </div>
    <div class="module-tip">仅研究展示，不构成建议，历史不代表未来</div>

    <!-- 东方财富栏目筛选 -->
    <div class="sub-category-nav" v-if="activeSource === 'eastmoney'">
      <span
        v-for="item in eastmoneyCategories"
        :key="item.value"
        class="sub-category-item"
        :class="{ active: eastmoneyCategory === item.value }"
        @click="setEastmoneyCategory(item.value)"
      >
        {{ item.label }}
      </span>
    </div>

    <!-- 研报详情弹窗 -->
    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal-container">
        <div class="modal-header">
          <h2>研究报告详情</h2>
          <button class="close-btn" @click="closeDetailModal">✕</button>
        </div>
        
        <div class="modal-body">
          <!-- 加载状态 -->
          <div v-if="detailLoading" class="loading-section">
            <div class="loading-spinner"></div>
            <p>正在加载报告内容...</p>
          </div>

          <!-- 错误提示 -->
          <div v-if="detailError && !detailLoading" class="error-section">
            <div class="error-icon">⚠️</div>
            <p>{{ detailError }}</p>
            <button class="retry-btn" @click="loadReportDetail(currentReportId)">重新加载</button>
          </div>

          <!-- 研报内容 -->
          <div v-if="!detailLoading && !detailError && reportDetail" class="report-detail-content">
            <!-- 研报头部信息 -->
            <section class="detail-section report-header">
              <div class="header-main">
                <div class="header-left">
                  <h1 class="company-name">{{ reportDetail.company_name }}</h1>
                  <span v-if="reportDetail.stock_code" class="stock-code">{{ reportDetail.stock_code }}</span>
                </div>
                <div class="rating-badge" :class="reportDetail.rating">
                  {{ ratingMap[reportDetail.rating] }}
                </div>
              </div>
              
              <div class="header-meta">
                <div class="meta-item">
                  <span class="meta-label">报告类型：</span>
                  <span class="meta-value">{{ reportDetail.report_type === 'summary' ? '文本生成摘要' : '深度分析框架' }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">创建时间：</span>
                  <span class="meta-value">{{ formatDateTime(reportDetail.created_at) }}</span>
                </div>
                <div class="meta-item" v-if="reportDetail.model">
                  <span class="meta-label">处理引擎：</span>
                  <span class="meta-value">{{ reportDetail.model }}</span>
                </div>
                <div class="meta-item" v-if="reportDetail.include_risks">
                  <span class="meta-label">风险提示：</span>
                  <span class="meta-value">✅ 已包含</span>
                </div>
              </div>

              <div class="detail-links" v-if="reportDetail.url || reportDetail.pdf_url">
                <a v-if="reportDetail.url" :href="reportDetail.url" target="_blank" rel="noopener" class="link-btn">原文链接</a>
                <a v-if="reportDetail.pdf_url" :href="reportDetail.pdf_url" target="_blank" rel="noopener" class="link-btn">PDF 原文</a>
              </div>

              <div v-if="reportDetail.tags && reportDetail.tags.length > 0" class="tags-section">
                <span class="tag" v-for="tag in reportDetail.tags" :key="tag">{{ tag }}</span>
              </div>

              <div v-if="reportDetail.company_info" class="company-info">
                <h3>公司信息</h3>
                <p>{{ reportDetail.company_info }}</p>
              </div>
            </section>

            <!-- 研报正文 -->
            <section class="detail-section report-content">
              <h2 class="section-title">
                <span class="title-icon">📄</span>
                报告正文
              </h2>
              <div v-if="reportDetail.model" class="ai-disclaimer">{{ AI_DISCLAIMER }}</div>
              <div class="markdown-body" v-html="renderedContent"></div>
            </section>

            <!-- 章节导航 -->
            <section class="detail-section report-sections" v-if="reportDetail.sections && reportDetail.sections.length > 0">
              <h2 class="section-title">
                <span class="title-icon">📑</span>
                章节结构
              </h2>
              <div class="sections-list">
                <div class="section-item" v-for="(section, index) in reportDetail.sections" :key="index">
                  <span class="section-number">{{ index + 1 }}</span>
                  <span class="section-name">{{ section }}</span>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>

    <!-- 结构化文本报告草稿 -->
    <div class="ai-report-section" v-if="activeSource !== 'eastmoney'">
      <div class="ai-header">
        <h2 class="ai-title">结构化文本报告草稿</h2>
        <p class="ai-subtitle">输入文本材料，生成研究用结构化草稿与分析框架</p>
      </div>
      <div class="module-tip">仅研究展示，不构成建议，数据或延迟误差</div>
      <div class="ai-form">
        <div class="input-row">
          <div class="input-group">
            <label>公司名称 <span class="required">*</span></label>
            <input v-model="companyName" type="text" placeholder="例如：Apple" class="text-input" />
          </div>
          <div class="input-group">
            <label>样本编号</label>
            <input v-model="stockCode" type="text" placeholder="例如：000001" class="text-input" />
          </div>
        </div>
        <textarea
          v-model="reportInput"
          class="ai-textarea"
          rows="6"
          placeholder="请输入用于实验分析的文本材料（业务结构、公开信息、行业背景等；留空将自动构造基础输入）"
        ></textarea>
        <div class="ai-controls">
          <div class="control-group">
            <label>报告类型</label>
            <select v-model="reportType">
              <option value="summary">文本摘要样本</option>
              <option value="analysis">结构化分析框架样本</option>
            </select>
          </div>
          <div class="control-group">
            <label>分析倾向</label>
            <select v-model="rating">
              <option value="hold">中性</option>
              <option value="buy">积极</option>
              <option value="add">偏积极</option>
              <option value="reduce">审慎</option>
              <option value="sell">保守</option>
            </select>
          </div>
          <label class="checkbox">
            <input type="checkbox" v-model="includeRisks" />
            包含风险提示
          </label>
          <button class="generate-btn" :disabled="reportLoading || !companyName.trim()" @click="generateAiReport">
            {{ reportLoading ? '处理中...' : '生成研究草稿' }}
          </button>
        </div>

        <div v-if="reportLoading" class="loading-section">
          <div class="loading-spinner"></div>
          <p>正在处理文本并生成草稿，请稍候...</p>
        </div>

        <div v-if="reportError && !reportLoading" class="error-section">
          <p class="error-text">{{ reportError }}</p>
        </div>

        <div v-if="reportContent && !reportLoading" class="report-result">
          <div class="ai-disclaimer">{{ AI_DISCLAIMER }}</div>
          <div class="result-meta">
            <span>模型：{{ reportModel || '未知' }}</span>
            <span>Token：{{ reportTokens ?? '-' }}</span>
          </div>
          <div v-if="reportSections.length" class="section-chips">
            <span v-for="(sec, idx) in reportSections" :key="idx" class="chip">{{ sec }}</span>
          </div>
          <pre class="report-content">{{ reportContent }}</pre>
          <div class="result-actions">
            <button class="ghost-btn" @click="copyReport">复制内容</button>
            <button class="ghost-btn" @click="clearReport">清空</button>
            <span class="save-tip">💡 报告草稿已自动保存到数据库</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主容器 -->
    <div class="container">
      <!-- 全部报告 -->
      <h2 class="section-title" id="all">全部报告</h2>
      <div class="module-tip">仅研究展示，不构成建议，数据或延迟误差</div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-section">
        <div class="loading-spinner"></div>
        <p>正在加载报告数据...</p>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="error && !loading" class="error-section">
        <p class="error-text">{{ error }}</p>
        <button class="retry-btn" @click="fetchReports">重新加载数据</button>
      </div>
      
      <!-- 研报列表 -->
      <template v-if="!loading && !error">
        <div class="results-info">
          共找到 {{ filteredReports.length }} 条报告
        </div>

        <!-- 默认卡片展示 -->
        <div class="report-grid">
          <div class="report-card" v-for="item in filteredReports" :key="item.id">
            <div class="report-info">
              <div class="stock-info">
                <span class="stock-name">{{ item.name }}</span>
                <span :class="item.tagClass">{{ item.tag }}</span>
              </div>
             <ul class="report-tags">
                <li v-for="(tag, i) in item.tags" :key="i">{{ tag }}</li>
              </ul>
              <div style="clear:both;"></div>
              <button class="view-btn" @click.stop="viewCompanyReport(item)">查看报告</button>
            </div>
          </div>
        </div>
        
        <!-- 无结果提示 -->
        <div v-if="filteredReports.length === 0" class="no-results">
          <p>暂无符合条件的报告</p>
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
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import FooterComponent from '@/components/FooterComponent.vue'
import { getReportSummaries } from '@/services/reportService'
import { generateReport } from '@/services/aiService'
import { getCompanyResearchById, generateCompanyResearch, getCompanyResearchList, getEastmoneyResearchList, getEastmoneyResearchDetail } from '@/services/companyResearchService'

const router = useRouter()
const AI_DISCLAIMER = '本页面内容仅用于历史研究与数据模拟，可能存在不准确或遗漏，不构成任何投资建议。请自行核验事实与数据。'
const riskExpanded = ref(false)

// 响应式状态
const searchQuery = ref('')
const activeCategory = ref('all')
const activeSource = ref('all')
const loading = ref(true)
const error = ref('')
const reportList = ref([])
const reportInput = ref('')
const reportType = ref('summary')
const includeRisks = ref(true)
const rating = ref('hold')
const reportLoading = ref(false)
const reportError = ref('')
const reportContent = ref('')
const reportSections = ref([])
const reportModel = ref('')
const reportTokens = ref(null)
const saveLoading = ref(false)
const companyName = ref('')
const stockCode = ref('')
const eastmoneyCategory = ref('stock')

const eastmoneyCategories = [
  { value: 'stock', label: '个股报告' },
  { value: 'industry', label: '行业报告' },
  { value: 'macro', label: '宏观研究' },
  { value: 'newstock', label: '新股研究' },
  { value: 'strategy', label: '策略样本报告' }
]

// 详情弹窗相关状态
const showDetailModal = ref(false)
const detailLoading = ref(false)
const detailError = ref('')
const reportDetail = ref(null)
const currentReportId = ref(null)
const currentReportSource = ref('ai')
const currentReportMeta = ref(null)

// 评级映射
const ratingMap = {
  'buy': '积极',
  'add': '偏积极',
  'hold': '中性',
  'reduce': '审慎',
  'sell': '保守'
}

// 旧的评级映射（用于列表显示）
const ratingMapOld = {
  'buy': { tag: '买入', tagClass: 'mai-ru' },
  'add': { tag: '增持', tagClass: 'mai-ru-zeng' },
  'hold': { tag: '持有', tagClass: 'chi-you' },
  'reduce': { tag: '减持', tagClass: 'jian-chi' },
  'sell': { tag: '卖出', tagClass: 'mai-chu' }
}

const sanitizeHtml = (html) => DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })

const normalizeSource = (item) => {
  const raw = (
    item?.source ||
    item?.data_source ||
    item?.research_source ||
    item?.institution ||
    item?.publisher ||
    item?.origin ||
    ''
  ).toString().toLowerCase()

  if (!raw) {
    if (item?.model || item?.tokens_used || item?.report_type) {
      return 'ai'
    }
    return 'eastmoney'
  }

  if (raw.includes('ai') || raw.includes('model') || raw.includes('gpt')) {
    return 'ai'
  }
  if (raw.includes('东方财富') || raw.includes('eastmoney')) {
    return 'eastmoney'
  }
  return raw
}

// Markdown 渲染
const renderedContent = computed(() => {
  if (!reportDetail.value || !reportDetail.value.report_content) {
    return ''
  }
  
  try {
    return sanitizeHtml(marked(reportDetail.value.report_content))
  } catch (e) {
    console.error('Markdown 渲染失败:', e)
    return sanitizeHtml(`<pre>${reportDetail.value.report_content}</pre>`)
  }
})

const mapRatingTag = (raw) => {
  if (!raw) {
    return { tag: '研报', tagClass: 'chi-you' }
  }
  const normalized = String(raw).replace(/\s+/g, '')
  const ratingMap = {
    '买入': { tag: '买入', tagClass: 'mai-ru' },
    '增持': { tag: '增持', tagClass: 'mai-ru-zeng' },
    '持有': { tag: '持有', tagClass: 'chi-you' },
    '中性': { tag: '中性', tagClass: 'chi-you' },
    '减持': { tag: '减持', tagClass: 'jian-chi' },
    '卖出': { tag: '卖出', tagClass: 'mai-chu' }
  }
  return ratingMap[normalized] || { tag: normalized, tagClass: 'chi-you' }
}

const buildEastmoneyTags = (item, categoryLabel) => {
  const tags = [categoryLabel, item.org_name, item.industry, item.rating]
  return tags.filter(Boolean)
}

const fetchAiReports = async () => {
  const params = {
    limit: 50,
    offset: 0
  }
  if (activeCategory.value !== 'all') {
    params.rating = activeCategory.value
  }

  const result = await getCompanyResearchList(params)
  if (!result || !result.success) {
    throw new Error(result?.message || '获取研报失败')
  }
  const backendResponse = result.data
  if (backendResponse.code !== 0) {
    throw new Error(backendResponse.message || '获取研报失败')
  }
  const payload = backendResponse.data
  let reports = payload?.items || []
  if (!Array.isArray(reports)) {
    reports = []
  }

  return reports.map(item => ({
    id: item.id,
    name: item.company_name || item.stock_name || item.title || '未知',
    tag: ratingMapOld[item.rating]?.tag || item.rating || '持有',
    tagClass: ratingMapOld[item.rating]?.tagClass || 'chi-you',
    priceLabel: item.price_label || '当前价',
    price: item.current_price ? `${item.current_price}元` : '-',
    profitLabel: item.profit_label || '目标价格',
    profit: item.target_return ? `${item.target_return}%` : '-',
    tags: item.tags || item.sectors || [],
    sourceType: normalizeSource(item),
    publishTime: item.created_at
  }))
}

const fetchEastmoneyReports = async () => {
  const params = {
    category: eastmoneyCategory.value,
    q: searchQuery.value.trim() || undefined,
    page: 1,
    page_size: 50
  }
  const result = await getEastmoneyResearchList(params)
  if (!result || !result.success) {
    throw new Error(result?.message || '获取东方财富研报失败')
  }
  const backendResponse = result.data
  if (backendResponse.code !== 0) {
    throw new Error(backendResponse.message || '获取东方财富研报失败')
  }
  const payload = backendResponse.data
  let reports = payload?.items || []
  if (!Array.isArray(reports)) {
    reports = []
  }

  return reports.map(item => {
    const ratingTag = mapRatingTag(item.rating)
    return {
      id: item.id,
      name: item.title || item.stock_name || item.stock_code || '研报',
      tag: ratingTag.tag,
      tagClass: ratingTag.tagClass,
      tags: buildEastmoneyTags(item, item.category_label || '东方财富'),
      sourceType: 'eastmoney',
      publishTime: item.publish_time,
      url: item.url,
      category: item.category,
      raw: item
    }
  })
}

const sortByTimeDesc = (items) => {
  return items.slice().sort((a, b) => {
    const ta = a.publishTime ? new Date(a.publishTime).getTime() : 0
    const tb = b.publishTime ? new Date(b.publishTime).getTime() : 0
    return tb - ta
  })
}

// 加载研报数据
const fetchReports = async () => {
  loading.value = true
  error.value = ''

  try {
    if (activeSource.value === 'eastmoney') {
      reportList.value = await fetchEastmoneyReports()
      return
    }

    if (activeSource.value === 'ai') {
      reportList.value = await fetchAiReports()
      return
    }

    const safeFetch = async (fn, fallback = []) => {
      try {
        return await fn()
      } catch (innerError) {
        console.warn('部分研报来源加载失败:', innerError)
        return fallback
      }
    }

    const [aiReports, eastmoneyReports] = await Promise.all([
      safeFetch(fetchAiReports, []),
      safeFetch(fetchEastmoneyReports, [])
    ])
    reportList.value = sortByTimeDesc([...aiReports, ...eastmoneyReports])
  } catch (e) {
    const errMsg = '加载研报数据失败: ' + (e.message || '未知错误')
    error.value = errMsg
    console.error('获取研报列表失败:', e)
  } finally {
    loading.value = false
  }
}

// 筛选后的研报列表
const filteredReports = computed(() => {
  let filtered = reportList.value
  
  // 根据分类过滤（如果 API 不支持服务端筛选）
  if (activeCategory.value !== 'all' && activeSource.value !== 'eastmoney') {
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

  // 根据来源过滤
  if (activeSource.value !== 'all') {
    filtered = filtered.filter(item => item.sourceType === activeSource.value)
  }
  
  // 根据搜索关键词过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(item => 
      item.name.toLowerCase().includes(query) ||
      (item.tags || []).some(tag => tag.toLowerCase().includes(query))
    )
  }
  
  return filtered
})

const extractPayload = (result) => result?.data?.data || result?.data || {}
const withDisclaimer = (content) => `${AI_DISCLAIMER}\n\n${content || 'AI 未返回内容'}`

const promptPreview = computed(() => {
  if (!companyName.value.trim()) return ''
  
  const typeLabel = reportType.value === 'analysis' ? '深度分析框架' : '文本生成摘要'
  const riskLabel = includeRisks.value ? '并包含风险因素' : '可不包含风险因素'
  
  // 如果用户输入了公司信息，使用用户输入；否则使用公司名称和股票代码
  let companyInfo = reportInput.value.trim()
  if (!companyInfo) {
    companyInfo = `公司名称：${companyName.value.trim()}`
    if (stockCode.value.trim()) {
      companyInfo += `\n样本编号：${stockCode.value.trim()}`
    }
  }
  
  return `请基于以下公司信息生成${typeLabel}报告，${riskLabel}。\n\n公司信息：\n${companyInfo}`
})

function goHome() {
  router.push('/')
}

async function viewReport(item) {
  currentReportId.value = item.id
  showDetailModal.value = true
  await loadReportDetail(item.id)
}

// 查看研报详情（跳转到详情页面）
function viewCompanyReport(report) {
  if (report.sourceType === 'eastmoney') {
    const encodedId = encodeURIComponent(report.id)
    const encodedUrl = report.url ? encodeURIComponent(report.url) : ''
    router.push({
      path: `/company-research/${encodedId}`,
      query: {
        source: 'eastmoney',
        category: report.category,
        url: encodedUrl,
        title: report.name
      }
    })
    return
  }
  router.push(`/company-research/${report.id}`)
}

function closeDetailModal() {
  showDetailModal.value = false
  reportDetail.value = null
  detailError.value = ''
  currentReportMeta.value = null
}

async function loadReportDetail(reportId) {
  detailLoading.value = true
  detailError.value = ''
  
  try {
    if (!reportId) {
      detailError.value = '缺少研报 ID'
      return
    }
    
    if (currentReportSource.value === 'eastmoney') {
      const params = {
        id: reportId,
        url: currentReportMeta.value?.url,
        category: currentReportMeta.value?.category
      }
      console.log('开始加载东方财富研报详情，参数:', params)
      const result = await getEastmoneyResearchDetail(params)
      console.log('东方财富研报详情接口返回:', result)

      if (!result || !result.success) {
        detailError.value = result?.message || '加载失败'
        return
      }
      const backendResponse = result.data
      if (backendResponse.code !== 0) {
        detailError.value = backendResponse.message || '加载失败'
        return
      }
      const data = backendResponse.data
      const content = data.content || data.summary || ''
      reportDetail.value = {
        company_name: data.stock_name || data.title || currentReportMeta.value?.name || '东方财富研报',
        stock_code: data.stock_code || currentReportMeta.value?.raw?.stock_code,
        rating: data.rating || currentReportMeta.value?.raw?.rating,
        report_type: 'summary',
        created_at: data.publish_time,
        tags: buildEastmoneyTags(currentReportMeta.value?.raw || {}, currentReportMeta.value?.raw?.category_label || '东方财富'),
        report_content: content,
        url: data.url || currentReportMeta.value?.url,
        pdf_url: data.pdf_url
      }
      return
    }

    console.log('开始加载研报详情，ID:', reportId)
    const result = await getCompanyResearchById(reportId)
    console.log('研报详情接口返回:', result)
    
    // 检查响应是否成功
    if (!result || !result.success) {
      detailError.value = result?.message || '加载失败'
      return
    }
    
    // 统一解包：后端返回 {code, message, data: {研报对象}}
    // handleRequest 包装为 {success: true, data: {code, message, data}}
    const backendResponse = result.data
    
    // 检查后端状态码
    if (backendResponse.code !== 0) {
      detailError.value = backendResponse.message || '加载失败'
      return
    }
    
    // 提取实际数据：研报对象
    const data = backendResponse.data
    console.log('提取的研报详情:', data)
    
    reportDetail.value = data
  } catch (e) {
    console.error('加载研报详情失败:', e)
    detailError.value = e.message || '加载失败，请重试'
  } finally {
    detailLoading.value = false
  }
}

function formatDateTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function go(id) {
  activeCategory.value = id
  // 切换分类时重新加载数据
  fetchReports()
}

function setSource(source) {
  activeSource.value = source
  if (source === 'eastmoney' && !eastmoneyCategory.value) {
    eastmoneyCategory.value = 'stock'
  }
  fetchReports()
}

function setEastmoneyCategory(category) {
  eastmoneyCategory.value = category
  fetchReports()
}

// 搜索处理
function handleSearch() {
  if (activeSource.value === 'eastmoney' || activeSource.value === 'all') {
    fetchReports()
  }
}

const generateAiReport = async () => {
  if (!companyName.value.trim()) {
    reportError.value = '请输入公司名称'
    return
  }

  reportLoading.value = true
  reportError.value = ''
  reportContent.value = ''
  reportSections.value = []
  reportModel.value = ''
  reportTokens.value = null

  try {
    // 构建公司信息
    let companyInfo = reportInput.value.trim()
    if (!companyInfo) {
      companyInfo = `公司名称：${companyName.value.trim()}`
      if (stockCode.value.trim()) {
        companyInfo += `\n样本编号：${stockCode.value.trim()}`
      }
      companyInfo += '\n\n请基于公开信息进行文本生成分析。'
    }
    
    console.log('开始生成报告草稿，参数:', {
      company_info: companyInfo,
      report_type: reportType.value,
      include_risks: includeRisks.value
    })
    
    const result = await generateReport({
      company_info: companyInfo,
      report_type: reportType.value,
      include_risks: includeRisks.value
    })

    if (result.success) {
      const payload = extractPayload(result)
      const content = payload.report_content || payload.content || '文本处理服务未返回内容'
      reportContent.value = withDisclaimer(content)
      reportSections.value = payload.sections || []
      reportModel.value = payload.model || ''
      reportTokens.value = payload.tokens_used ?? null
      
      console.log('报告草稿生成成功，开始自动保存到数据库...')
      
      // 自动保存到数据库
      try {
        const saveResult = await generateCompanyResearch({
          company_name: companyName.value.trim(),
          stock_code: stockCode.value.trim() || undefined,
          rating: rating.value,
          company_info: companyInfo,
          report_type: reportType.value,
          include_risks: includeRisks.value,
          tags: [],
          force: false
        })
        
        console.log('保存接口返回:', saveResult)
        
        // 检查保存结果
        if (!saveResult || !saveResult.success) {
          console.warn('自动保存失败:', saveResult?.message)
          reportError.value = '报告草稿生成成功，但保存失败：' + (saveResult?.message || '未知错误')
        } else {
          const saveBackendResponse = saveResult.data
          if (saveBackendResponse.code === 0) {
            console.log('报告草稿已自动保存到数据库')
            // 刷新研报列表
            await fetchReports()
            // 显示成功提示
            setTimeout(() => {
              alert('报告草稿生成成功并已保存到数据库！')
            }, 100)
          } else {
            console.warn('保存失败，后端返回:', saveBackendResponse)
            reportError.value = '报告草稿生成成功，但保存失败：' + (saveBackendResponse.message || '未知错误')
          }
        }
      } catch (saveError) {
        console.error('自动保存报告草稿失败:', saveError)
        reportError.value = '报告草稿生成成功，但保存失败：' + (saveError.message || '网络错误')
      }
    } else {
      reportError.value = result.message || '生成报告草稿失败'
    }
  } catch (e) {
    reportError.value = '生成报告草稿失败: ' + (e.message || '未知错误')
    console.error('生成报告草稿失败:', e)
  } finally {
    reportLoading.value = false
  }
}

const copyText = async (text) => {
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
      return true
    }
  } catch (e) {
    return false
  }
  return false
}

const copyPrompt = async () => {
  if (!promptPreview.value) return
  const ok = await copyText(promptPreview.value)
  if (!ok) {
    alert('复制失败，请手动复制')
  }
}

const copyReport = async () => {
  if (!reportContent.value) return
  const ok = await copyText(reportContent.value)
  if (!ok) {
    alert('复制失败，请手动复制')
  }
}

const clearReport = () => {
  reportContent.value = ''
  reportSections.value = []
  reportModel.value = ''
  reportTokens.value = null
  reportError.value = ''
}

const saveReportToDatabase = async () => {
  if (!companyName.value.trim()) {
    alert('请输入公司名称')
    return
  }
  
  if (!reportContent.value) {
    alert('没有可保存的研报内容')
    return
  }
  
  saveLoading.value = true
  
  try {
    // 构建公司信息，如果用户没有输入，则使用公司名称和股票代码
    let companyInfo = reportInput.value.trim()
    if (!companyInfo) {
      companyInfo = `公司名称：${companyName.value.trim()}`
      if (stockCode.value.trim()) {
        companyInfo += ` 股票代码：${stockCode.value.trim()}`
      }
    }
    
    const result = await generateCompanyResearch({
      company_name: companyName.value.trim(),
      stock_code: stockCode.value.trim() || undefined,
      rating: rating.value,
      company_info: companyInfo,
      report_type: reportType.value,
      include_risks: includeRisks.value,
      tags: [],
      force: false
    })
    
    if (result.success) {
      alert('研报已成功保存到数据库！')
      // 刷新研报列表
      await fetchReports()
      // 清空表单
      clearReport()
      companyName.value = ''
      stockCode.value = ''
      reportInput.value = ''
    } else {
      alert('保存失败：' + (result.message || '未知错误'))
    }
  } catch (e) {
    console.error('保存研报失败:', e)
    alert('保存失败：' + (e.message || '网络错误'))
  } finally {
    saveLoading.value = false
  }
}

// 生命周期
onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
/* 复用商店页面的样式并稍作调整 */

.header-nav {
  display: flex;
  align-items: center;
  gap: 20px;
}

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

.module-tip {
  color: #999;
  font-size: 12px;
  line-height: 1.4;
  padding: 6px 20px 0;
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

.ai-report-section {
  max-width: 1400px;
  margin: 0 auto 10px;
  padding: 0 20px;
}

.ai-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.ai-title {
  font-size: 22px;
  color: #ff7f24;
  font-weight: bold;
  margin: 0;
}

.ai-subtitle {
  color: #666;
  font-size: 14px;
}

.ai-form {
  background: #ffffff;
  border: 1px solid #ffb380;
  border-radius: 10px;
  padding: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.input-row {
  display: flex;
  gap: 15px;
  margin-bottom: 12px;
}

.input-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-group label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.required {
  color: #ff4d4f;
  margin-left: 2px;
}

.text-input {
  padding: 10px 12px;
  border: 1px solid #ffb380;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.text-input:focus {
  border-color: #ff7f24;
  box-shadow: 0 0 0 2px rgba(255, 127, 36, 0.2);
}

.ai-textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #ffb380;
  border-radius: 8px;
  resize: vertical;
  font-size: 14px;
  line-height: 1.6;
  outline: none;
}

.ai-textarea:focus {
  border-color: #ff7f24;
  box-shadow: 0 0 0 2px rgba(255, 127, 36, 0.2);
}

.ai-controls {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
  font-size: 14px;
}

.control-group select {
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #ffb380;
  outline: none;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #333;
}

.generate-btn {
  background-color: #ff7f24;
  color: white;
  border: none;
  padding: 10px 18px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.generate-btn:disabled {
  background-color: #ffd0b0;
  cursor: not-allowed;
}

.prompt-preview {
  background: #fff7ef;
  border: 1px dashed #ffb380;
  border-radius: 8px;
  padding: 12px;
  margin-top: 14px;
}

.prompt-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13px;
  color: #333;
  margin-bottom: 8px;
}

.prompt-content {
  white-space: pre-wrap;
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

.report-result {
  margin-top: 14px;
  border: 1px solid #ffe0cc;
  border-radius: 8px;
  padding: 12px;
  background: #fffaf6;
}

.ai-disclaimer {
  margin-bottom: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
  color: #a65300;
  background-color: rgba(255, 127, 0, 0.1);
  border: 1px solid rgba(255, 127, 0, 0.25);
}

.report-content {
  white-space: pre-wrap;
  line-height: 1.7;
  color: #333;
  font-size: 14px;
}

.result-meta {
  display: flex;
  gap: 16px;
  color: #666;
  font-size: 13px;
  margin-bottom: 8px;
}

.section-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.chip {
  background: #ffeedd;
  color: #ff7f24;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.result-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.ghost-btn {
  background: #fff;
  border: 1px solid #ffb380;
  color: #ff7f24;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.ghost-btn:hover {
  background: #fff7ef;
  border-color: #ff7f24;
}

.primary-btn {
  background: #52c41a;
  border: 1px solid #52c41a;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
  font-weight: 500;
}

.primary-btn:hover:not(:disabled) {
  background: #73d13d;
  border-color: #73d13d;
}

.primary-btn:disabled {
  background: #d9d9d9;
  border-color: #d9d9d9;
  cursor: not-allowed;
  opacity: 0.6;
}

.save-tip {
  color: #52c41a;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: 500;
}

.category-nav {
  background-color: #ff9933;
  padding: 12px 20px;
  overflow-x: auto;
  white-space: nowrap;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.sub-category-nav {
  background-color: #fff3e8;
  padding: 10px 20px;
  overflow-x: auto;
  white-space: nowrap;
  border-bottom: 1px solid #ffd9bf;
}

.sub-category-item {
  display: inline-block;
  color: #ff7f24;
  text-decoration: none;
  padding: 6px 14px;
  margin-right: 8px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.3s;
}

.sub-category-item.active {
  background-color: #ff7f24;
  color: #fff;
  border-color: #ff7f24;
  font-weight: 600;
}

.sub-category-item:hover:not(.active) {
  background-color: #ffe6d5;
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

.container .section-title {
  font-size: 22px;
  color: #ffffff;
  border-left: 4px solid #ff7f24;
  padding-left: 12px;
  margin: 15px 0 15px;
  font-weight: bold;
}

.results-info {
  color: #666;
  font-size: 14px;
  margin-bottom: 15px;
}

.loading-section,
.error-section {
  text-align: center;
  padding: 40px 20px;
  background: white;
  border-radius: 10px;
  margin: 20px 0;
  border: 1px solid #ffb380;
}

.loading-spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #ff7f24;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-section {
  border-color: #ff4d4f;
}

.error-section p {
  color: #ff4d4f;
  margin-bottom: 15px;
}

.retry-btn {
  background: #ff7f24;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.retry-btn:hover {
  background: #ff6a00;
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

.view-btn.small {
  width: auto;
  padding: 6px 12px;
  margin-top: 0;
  font-size: 12px;
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

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  overflow-y: auto;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 1000px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 20px 25px;
  border-bottom: 2px solid #ffb380;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(to right, #fff6ee, #fff);
}

.modal-header h2 {
  color: #ff7f24;
  font-size: 22px;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.3s;
}

.close-btn:hover {
  background: #f0f0f0;
  color: #ff7f24;
}

.modal-body {
  padding: 25px;
  overflow-y: auto;
  flex: 1;
}

.report-detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #f0f0f0;
}

/* 研报头部 */
.report-header {
  border-top: 4px solid #ff7f24;
}

.header-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}

.company-name {
  font-size: 24px;
  color: #333;
  font-weight: bold;
  margin: 0;
}

.stock-code {
  font-size: 14px;
  color: #666;
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 4px;
}

.rating-badge {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: bold;
  color: white;
  white-space: nowrap;
}

.rating-badge.buy { background: #18A44B; }
.rating-badge.add { background: #F5A623; }
.rating-badge.hold { background: #4A90E2; }
.rating-badge.reduce { background: #F39C12; }
.rating-badge.sell { background: #C62828; }

.header-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  padding: 15px 0;
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-links {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.link-btn {
  background: #fff7ef;
  border: 1px solid #ffb380;
  color: #ff7f24;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  text-decoration: none;
  transition: all 0.3s;
}

.link-btn:hover {
  background: #ff7f24;
  color: #fff;
}

.meta-item {
  display: flex;
  gap: 5px;
}

.meta-label {
  color: #999;
  font-size: 14px;
}

.meta-value {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.tags-section {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 15px;
}

.tag {
  background: #ff7f24;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
}

.company-info {
  margin-top: 20px;
  padding: 15px;
  background: #fff6ee;
  border-radius: 6px;
  border-left: 4px solid #ff7f24;
}

.company-info h3 {
  color: #ff7f24;
  font-size: 16px;
  margin: 0 0 8px 0;
}

.company-info p {
  color: #666;
  line-height: 1.6;
  font-size: 14px;
  margin: 0;
}

/* 研报正文 */
.report-content {
  line-height: 1.8;
}

.section-title {
  font-size: 18px;
  color: #ff7f24;
  margin: 0 0 15px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 20px;
}

.markdown-body {
  color: #333;
  font-size: 15px;
}

.markdown-body :deep(h1) {
  font-size: 22px;
  color: #333;
  margin: 18px 0 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #ff7f24;
}

.markdown-body :deep(h2) {
  font-size: 19px;
  color: #ff7f24;
  margin: 16px 0 10px;
}

.markdown-body :deep(h3) {
  font-size: 16px;
  color: #666;
  margin: 14px 0 8px;
}

.markdown-body :deep(p) {
  margin: 10px 0;
  line-height: 1.8;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 10px 0;
  padding-left: 25px;
}

.markdown-body :deep(li) {
  margin: 5px 0;
}

.markdown-body :deep(strong) {
  color: #333;
  font-weight: 600;
}

.markdown-body :deep(code) {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
}

.markdown-body :deep(pre) {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 15px 0;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid #ff7f24;
  padding-left: 15px;
  margin: 15px 0;
  color: #666;
  font-style: italic;
}

/* 章节结构 */
.sections-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #fff6ee;
  border-radius: 6px;
  border-left: 3px solid #ff7f24;
}

.section-number {
  background: #ff7f24;
  color: white;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 13px;
  flex-shrink: 0;
}

.section-name {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

@media (max-width: 768px) {
  .modal-container {
    max-width: 100%;
    margin: 0;
    border-radius: 0;
    max-height: 100vh;
  }
  
  .modal-body {
    padding: 15px;
  }
  
  .header-main {
    flex-direction: column;
  }
  
  .header-meta {
    grid-template-columns: 1fr;
  }
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