<template>
  <div class="research-detail">
    <div class="header">
      <button @click="goBack" class="back-button">← 返回</button>
      <h1 class="title">{{ report.title }}</h1>
    </div>

    <div class="report-meta">
      <div class="stock-info">
        <h2>{{ report.stockName }} ({{ report.stockCode }})</h2>
        <span :class="'rating ' + report.rating.toLowerCase()">{{ report.rating }}</span>
      </div>
      <div class="report-source">
        <span class="institution">{{ report.institution }}</span>
        <span class="date">{{ formatDate(report.date) }}</span>
        <span class="analyst">分析师: {{ report.analyst }}</span>
      </div>
    </div>

    <div class="price-comparison">
      <div class="target-price">
        <span>目标价: </span>
        <strong>{{ report.targetPrice }}</strong>
      </div>
      <div class="current-price">
        <span>当前价: </span>
        <strong>{{ report.currentPrice }}</strong>
      </div>
      <div class="upside">
        <span>上涨空间: </span>
        <strong :class="getUpsideClass(report.upside)">{{ report.upside }}%</strong>
      </div>
    </div>

    <div class="report-content">
      <section class="section">
        <h3>基本面分析</h3>
        <p>{{ report.fundamentalAnalysis }}</p>
      </section>

      <section class="section">
        <h3>技术面分析</h3>
        <p>{{ report.technicalAnalysis }}</p>
      </section>

      <section class="section">
        <h3>行业前景</h3>
        <p>{{ report.industryOutlook }}</p>
      </section>

      <section class="section risk-section">
        <h3>风险提示</h3>
        <p>{{ report.riskWarning }}</p>
      </section>
    </div>

    <div class="actions">
      <button @click="toggleFavorite" class="action-button">
        {{ isFavorite ? '★ 已收藏' : '☆ 收藏' }}
      </button>
      <button @click="shareReport" class="action-button">分享</button>
    </div>

    <div class="related-reports">
      <h3>相关研报推荐</h3>
      <ul>
        <li v-for="related in relatedReports" :key="related.id">
          <router-link :to="'/research-detail/' + related.id">{{ related.title }}</router-link>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReportStore } from '@/stores/report'

export default {
  setup() {
    const route = useRoute()
    const router = useRouter()
    const reportStore = useReportStore()
    
    // 添加默认值确保页面能正常渲染
    const report = ref({
      id: '',
      title: '加载中...',
      stockName: '',
      stockCode: '',
      rating: '',
      institution: '',
      date: '',
      analyst: '',
      targetPrice: '',
      currentPrice: '',
      upside: '',
      fundamentalAnalysis: '',
      technicalAnalysis: '',
      industryOutlook: '',
      riskWarning: ''
    })
    const relatedReports = ref([])
    const isFavorite = ref(false)

    const fetchReport = async (id) => {
      try {
        // 这里应该调用API获取研报详情
        // 模拟数据
        report.value = {
          id: id,
          title: `研报详情 - ${id}`,
          stockName: '腾讯控股',
          stockCode: '00700.HK',
          rating: '买入',
          institution: '中金公司',
          date: '2025-12-20',
          analyst: '张伟',
          targetPrice: '450.00',
          currentPrice: '380.50',
          upside: '18.3',
          fundamentalAnalysis: '公司核心业务保持稳健增长，新业务布局初见成效。公司在游戏、社交、云计算等领域均保持领先地位，未来三年业绩有望实现翻倍增长。',
          technicalAnalysis: '股价近期突破关键阻力位，形成上升趋势。技术指标显示多头格局，MACD金叉向上，RSI处于强势区域。',
          industryOutlook: '互联网行业政策环境改善，行业估值有望修复。随着数字化转型加速，长期增长前景看好。',
          riskWarning: '宏观经济下行风险；行业监管政策变化；新业务进展不及预期；市场竞争加剧。'
        }
        
        // 获取相关研报
        relatedReports.value = [
          { id: '2', title: '腾讯控股：游戏业务复苏带动业绩增长' },
          { id: '3', title: '互联网行业2026年投资回测模型' },
          { id: '4', title: '人工智能在金融领域的应用前景分析' }
        ]
        
        // 检查是否已收藏
        isFavorite.value = reportStore.isFavorite(id)
      } catch (error) {
        console.error('加载研报详情失败:', error)
        report.value.title = '研报加载失败'
      }
    }

    const goBack = () => {
      router.go(-1)
    }

    const toggleFavorite = () => {
      isFavorite.value = !isFavorite.value
      if (isFavorite.value) {
        reportStore.addFavorite(report.value.id)
      } else {
        reportStore.removeFavorite(report.value.id)
      }
    }

    const shareReport = () => {
      // 实现分享功能
      alert('研报已分享')
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const getUpsideClass = (upside) => {
      return upside > 0 ? 'positive' : 'negative'
    }

    onMounted(() => {
      fetchReport(route.params.id)
    })

    return {
      report,
      relatedReports,
      isFavorite,
      goBack,
      toggleFavorite,
      shareReport,
      formatDate,
      getUpsideClass
    }
  }
}
</script>

<style scoped>
.research-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  color: #333;
}

.header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.back-button {
  background: none;
  border: none;
  color: #ff7f24;
  font-size: 16px;
  cursor: pointer;
  margin-right: 20px;
}

.title {
  color: #ff7f24;
  margin: 0;
}

.report-meta {
  background: #f8f8f8;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.stock-info {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.stock-info h2 {
  margin: 0;
  margin-right: 15px;
}

.rating {
  padding: 3px 8px;
  border-radius: 3px;
  font-weight: bold;
  font-size: 14px;
}

.rating.buy {
  background: #e6f7e6;
  color: #009944;
}

.rating.sell {
  background: #ffe6e6;
  color: #d0021b;
}

.rating.hold {
  background: #fff7e6;
  color: #f5a623;
}

.report-source {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #666;
}

.price-comparison {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.price-comparison div {
  flex: 1;
}

.price-comparison strong {
  font-size: 18px;
}

.price-comparison .positive {
  color: #009944;
}

.price-comparison .negative {
  color: #d0021b;
}

.section {
  margin-bottom: 25px;
}

.section h3 {
  color: #ff7f24;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.risk-section {
  background: #fff5f5;
  padding: 15px;
  border-radius: 5px;
}

.actions {
  display: flex;
  gap: 15px;
  margin: 30px 0;
}

.action-button {
  padding: 8px 15px;
  background: #ff7f24;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.action-button:hover {
  background: #e6731a;
}

.related-reports {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.related-reports ul {
  list-style: none;
  padding: 0;
}

.related-reports li {
  margin: 10px 0;
}

.related-reports a {
  color: #ff7f24;
  text-decoration: none;
}

.related-reports a:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .price-comparison {
    flex-direction: column;
    gap: 10px;
  }
  
  .report-source {
    flex-direction: column;
    gap: 5px;
  }
}
</style>