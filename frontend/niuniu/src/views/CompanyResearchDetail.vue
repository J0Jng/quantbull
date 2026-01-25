<template>
  <div class="company-research-detail">
    <div class="header">
      <button @click="goBack" class="back-button">← 返回</button>
      <h1 class="title">{{ research.title }}</h1>
    </div>

    <div class="research-meta">
      <div class="company-info">
        <h2>{{ research.companyName }} ({{ research.stockCode }})</h2>
        <span :class="'rating ' + research.rating?.toLowerCase()">{{ research.rating }}</span>
      </div>
      <div class="research-source">
        <span class="institution">{{ research.institution }}</span>
        <span class="date">{{ formatDate(research.publishDate) }}</span>
        <span class="analyst">分析师: {{ research.analyst }}</span>
      </div>
    </div>

    <div class="price-info" v-if="research.targetPrice">
      <div class="price-item">
        <span>目标价: </span>
        <strong>¥{{ research.targetPrice }}</strong>
      </div>
      <div class="price-item">
        <span>当前价: </span>
        <strong>¥{{ research.currentPrice }}</strong>
      </div>
      <div class="price-item">
        <span>上涨空间: </span>
        <strong :class="getUpsideClass(research.upside)">{{ research.upside }}%</strong>
      </div>
    </div>

    <div class="research-content">
      <section class="section" v-if="research.summary">
        <h3>研报摘要</h3>
        <p>{{ research.summary }}</p>
      </section>

      <section class="section" v-if="research.content">
        <h3>研报正文</h3>
        <div class="markdown-body" v-html="renderMarkdown(research.content)"></div>
      </section>

      <section class="section" v-if="research.investmentHighlight">
        <h3>投资亮点</h3>
        <p v-html="formatContent(research.investmentHighlight)"></p>
      </section>

      <section class="section" v-if="research.businessAnalysis">
        <h3>业务分析</h3>
        <p v-html="formatContent(research.businessAnalysis)"></p>
      </section>

      <section class="section" v-if="research.financialAnalysis">
        <h3>财务分析</h3>
        <p v-html="formatContent(research.financialAnalysis)"></p>
      </section>

      <section class="section" v-if="research.valuation">
        <h3>估值分析</h3>
        <p v-html="formatContent(research.valuation)"></p>
      </section>

      <section class="section risk-section" v-if="research.riskWarning">
        <h3>风险提示</h3>
        <p>{{ research.riskWarning }}</p>
      </section>
    </div>

    <div class="actions">
      <button @click="toggleFavorite" class="action-button" :class="{ favorited: isFavorite }">
        {{ isFavorite ? '★ 已收藏' : '☆ 收藏' }}
      </button>
      <button @click="shareResearch" class="action-button">分享</button>
      <button @click="downloadPDF" class="action-button" v-if="research.pdfUrl">下载PDF</button>
    </div>

    <div class="related-research" v-if="relatedResearch.length > 0">
      <h3>相关研报推荐</h3>
      <ul>
        <li v-for="item in relatedResearch" :key="item.id">
          <router-link :to="`/company-research/${item.id}`">
            {{ item.title }} - {{ item.companyName }}
          </router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCompanyResearchById, getEastmoneyResearchDetail } from '@/services/companyResearchService'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

export default {
  name: 'CompanyResearchDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    const research = ref({
      id: '',
      title: '加载中...',
      companyName: '',
      stockCode: '',
      rating: '',
      institution: '',
      publishDate: '',
      analyst: '',
      targetPrice: null,
      currentPrice: null,
      upside: null,
      summary: '',
      investmentHighlight: '',
      businessAnalysis: '',
      financialAnalysis: '',
      valuation: '',
      riskWarning: '',
      content: '',
      pdfUrl: ''
    })

    const relatedResearch = ref([])
    const isFavorite = ref(false)

    const goBack = () => {
      router.back()
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })
    }

    const formatContent = (content) => {
      if (!content) return ''
      const sanitized = DOMPurify.sanitize(content, { ALLOWED_TAGS: [], ALLOWED_ATTR: [] })
      return sanitized.replace(/\n/g, '<br>')
    }
    
    const renderMarkdown = (content) => {
      if (!content) return ''
      try {
        return DOMPurify.sanitize(marked(content), { USE_PROFILES: { html: true } })
      } catch (e) {
        console.error('Markdown 渲染失败:', e)
        return DOMPurify.sanitize(`<pre>${content}</pre>`, { USE_PROFILES: { html: true } })
      }
    }

    const getUpsideClass = (upside) => {
      if (!upside) return ''
      return upside > 0 ? 'positive' : 'negative'
    }

    const toggleFavorite = () => {
      isFavorite.value = !isFavorite.value
      // TODO: 调用 API 保存收藏状态
      console.log('Toggle favorite:', isFavorite.value)
    }

    const shareResearch = () => {
      // TODO: 实现分享功能
      if (navigator.share) {
        navigator.share({
          title: research.value.title,
          text: research.value.summary,
          url: window.location.href
        }).catch(err => console.log('分享失败:', err))
      } else {
        // 复制链接到剪贴板
        navigator.clipboard.writeText(window.location.href)
        alert('链接已复制到剪贴板')
      }
    }

    const downloadPDF = () => {
      if (research.value.pdfUrl) {
        window.open(research.value.pdfUrl, '_blank')
      }
    }

    const fetchResearchDetail = async () => {
      const rawId = String(route.params.id || '')
      const id = rawId ? decodeURIComponent(rawId) : ''
      const source = String(route.query.source || 'ai')
      try {
        console.log('正在加载研报详情，ID:', id)
        
        if (source === 'eastmoney') {
          const rawUrl = typeof route.query.url === 'string' ? route.query.url : ''
          const decodedUrl = rawUrl ? decodeURIComponent(rawUrl) : ''
          const rawCategory = typeof route.query.category === 'string' ? route.query.category : ''
          const rawTitle = typeof route.query.title === 'string' ? route.query.title : ''
          const params = {
            id,
            url: decodedUrl,
            category: rawCategory
          }
          const result = await getEastmoneyResearchDetail(params)
          console.log('东方财富研报详情 API 返回:', result)

          if (!result || !result.success) {
            console.error('获取研报详情失败:', result?.message)
            alert('获取研报详情失败: ' + (result?.message || '未知错误'))
            return
          }

          const backendResponse = result.data
          if (backendResponse.code !== 0) {
            console.error('后端返回错误:', backendResponse.message)
            alert('获取研报详情失败: ' + (backendResponse.message || '未知错误'))
            return
          }

          const data = backendResponse.data
          console.log('提取的东方财富研报详情:', data)

          research.value = {
            id,
            title: data.title || rawTitle || '东方财富研报',
            companyName: data.stock_name || data.title || rawTitle || '东方财富研报',
            stockCode: data.stock_code || '-',
            rating: data.rating || '中性',
            institution: data.org_name || data.institution || '东方财富',
            publishDate: data.publish_time,
            analyst: data.analyst || '',
            targetPrice: null,
            currentPrice: null,
            upside: null,
            summary: data.summary || extractSummary(data.content),
            investmentHighlight: '',
            businessAnalysis: '',
            financialAnalysis: '',
            valuation: '',
            riskWarning: '',
            content: data.content || '',
            pdfUrl: data.pdf_url || ''
          }
          return
        }

        const result = await getCompanyResearchById(id)
        console.log('研报详情 API 返回:', result)

        // 检查响应是否成功
        if (!result || !result.success) {
          console.error('获取研报详情失败:', result?.message)
          alert('获取研报详情失败: ' + (result?.message || '未知错误'))
          return
        }

        // 统一解包：后端返回 {code, message, data: {研报对象}}
        const backendResponse = result.data

        // 检查后端状态码
        if (backendResponse.code !== 0) {
          console.error('后端返回错误:', backendResponse.message)
          alert('获取研报详情失败: ' + (backendResponse.message || '未知错误'))
          return
        }

        // 提取实际数据：研报对象
        const data = backendResponse.data
        console.log('提取的研报详情:', data)

        // 评级映射
        const ratingMap = {
          'buy': '买入',
          'add': '增持',
          'hold': '持有',
          'reduce': '减持',
          'sell': '卖出'
        }

        // 映射后端数据到前端字段
        research.value = {
          id: data.id,
          title: `${data.company_name} - ${ratingMap[data.rating] || data.rating}`,
          companyName: data.company_name,
          stockCode: data.stock_code || '-',
          rating: ratingMap[data.rating] || data.rating,
          institution: 'AI 生成',
          publishDate: data.created_at,
          analyst: data.model || 'AI',
          targetPrice: null,
          currentPrice: null,
          upside: null,
          summary: extractSummary(data.report_content),
          investmentHighlight: '',
          businessAnalysis: '',
          financialAnalysis: '',
          valuation: '',
          riskWarning: data.include_risks ? '详见研报正文风险提示章节' : '',
          content: data.report_content || '',
          pdfUrl: ''
        }
        
        // TODO: 获取相关研报（暂时留空）
        relatedResearch.value = []
        
      } catch (error) {
        console.error('获取研报详情失败:', error)
        alert('获取研报详情失败: ' + (error.message || '网络错误'))
      }
    }
    
    // 从 Markdown 内容中提取摘要（第一段或前200字）
    const extractSummary = (content) => {
      if (!content) return ''
      
      // 移除 Markdown 标题符号
      let text = content.replace(/^#+\s+/gm, '')
      // 移除加粗、斜体等格式
      text = text.replace(/[*_`]/g, '')
      // 获取第一段或前200字
      const firstPara = text.split('\n\n')[0]
      if (firstPara.length > 200) {
        return firstPara.substring(0, 200) + '...'
      }
      return firstPara
    }

    onMounted(() => {
      fetchResearchDetail()
    })

    return {
      research,
      relatedResearch,
      isFavorite,
      goBack,
      formatDate,
      formatContent,
      renderMarkdown,
      getUpsideClass,
      toggleFavorite,
      shareResearch,
      downloadPDF
    }
  }
}
</script>

<style scoped>
.company-research-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
}

.header {
  margin-bottom: 30px;
}

.back-button {
  background: transparent;
  border: none;
  color: #1890ff;
  font-size: 16px;
  cursor: pointer;
  padding: 8px 0;
  margin-bottom: 15px;
  transition: color 0.3s;
}

.back-button:hover {
  color: #40a9ff;
}

.title {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  margin: 0;
  line-height: 1.4;
}

.research-meta {
  background: #f5f5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.company-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.company-info h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.rating {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
}

.rating.买入 {
  background: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.rating.增持 {
  background: #e6f7ff;
  color: #1890ff;
  border: 1px solid #91d5ff;
}

.rating.中性 {
  background: #fffbe6;
  color: #faad14;
  border: 1px solid #ffe58f;
}

.research-source {
  display: flex;
  gap: 20px;
  color: #666;
  font-size: 14px;
}

.price-info {
  display: flex;
  gap: 30px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.price-item {
  flex: 1;
}

.price-item span {
  color: #666;
  margin-right: 5px;
}

.price-item strong {
  font-size: 20px;
  color: #333;
}

.positive {
  color: #52c41a !important;
}

.negative {
  color: #ff4d4f !important;
}

.research-content {
  margin-bottom: 30px;
}

.section {
  margin-bottom: 30px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.section h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
  border-left: 4px solid #1890ff;
  padding-left: 12px;
}

.section p {
  margin: 0;
  line-height: 1.8;
  color: #666;
  white-space: pre-wrap;
}

.risk-section {
  background: #fff7e6;
  border: 1px solid #ffd591;
}

.risk-section h3 {
  border-left-color: #faad14;
  color: #d46b08;
}

.actions {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.action-button {
  padding: 10px 24px;
  border: 1px solid #d9d9d9;
  background: #fff;
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.action-button:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.action-button.favorited {
  background: #1890ff;
  color: #fff;
  border-color: #1890ff;
}

.related-research {
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}

.related-research h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
}

.related-research ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.related-research li {
  margin-bottom: 10px;
}

.related-research a {
  color: #1890ff;
  text-decoration: none;
  transition: color 0.3s;
}

.related-research a:hover {
  color: #40a9ff;
  text-decoration: underline;
}

/* Markdown 内容样式 */
.markdown-body {
  line-height: 1.8;
  color: #333;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body h1 {
  font-size: 24px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.markdown-body h2 {
  font-size: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.markdown-body h3 {
  font-size: 18px;
}

.markdown-body h4 {
  font-size: 16px;
}

.markdown-body p {
  margin-bottom: 16px;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 28px;
  margin-bottom: 16px;
}

.markdown-body li {
  margin-bottom: 8px;
}

.markdown-body strong {
  font-weight: 600;
  color: #000;
}

.markdown-body em {
  font-style: italic;
}

.markdown-body code {
  background: #f6f8fa;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
}

.markdown-body pre {
  background: #f6f8fa;
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 16px;
}

.markdown-body pre code {
  background: transparent;
  padding: 0;
}

.markdown-body blockquote {
  border-left: 4px solid #dfe2e5;
  padding-left: 16px;
  color: #666;
  margin: 0 0 16px 0;
}

.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 16px;
}

.markdown-body table th,
.markdown-body table td {
  border: 1px solid #dfe2e5;
  padding: 8px 12px;
}

.markdown-body table th {
  background: #f6f8fa;
  font-weight: 600;
}

@media (max-width: 768px) {
  .company-research-detail {
    padding: 15px;
  }

  .title {
    font-size: 22px;
  }

  .company-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .research-source {
    flex-direction: column;
    gap: 8px;
  }

  .price-info {
    flex-direction: column;
    gap: 15px;
  }

  .actions {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
  }
}
</style>
