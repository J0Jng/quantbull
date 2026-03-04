<template>
  <div class="backtest-detail-page">
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

    <div v-if="loading" class="loading-state">
      加载中...
    </div>
    <div v-else-if="error" class="error-state">
      {{ error }}
      <button @click="loadData" class="btn-retry">重试</button>
      <router-link to="/quant-analysis" class="btn-back">返回列表</router-link>
    </div>
    <div v-else class="detail-container">
      <div class="header">
        <h1>历史模拟详情</h1>
        <router-link to="/quant-analysis" class="btn-back">返回列表</router-link>
      </div>

      <div class="info-card card">
        <h2 class="card-title">基础信息（研究）</h2>
        <div class="module-tip">仅研究展示，不构成建议，历史不代表未来</div>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">模拟ID:</span>
            <span class="value">{{ backtestId }}</span>
          </div>
          <div class="info-item">
            <span class="label">股票代码:</span>
            <span class="value">{{ backtestData?.stock_code || 'N/A' }}</span>
          </div>
          <div class="info-item">
            <span class="label">日期范围:</span>
            <span class="value">{{ dateRange }}</span>
          </div>
          <div class="info-item">
            <span class="label">年化收益率:</span>
            <span class="value highlight">{{ formattedAnnualReturn }}</span>
          </div>
          <div class="info-item">
              <span class="label">夏普比率:</span>
              <span class="value">{{ formattedSharpe }}</span>
          </div>
          <div class="info-item">
              <span class="label">最大回撤:</span>
              <span class="value">{{ formattedDrawdown }}</span>
          </div>
        </div>
      </div>

      <div class="chart-section card">
        <div class="module-tip">净值曲线仅用于历史样本观察，不代表未来表现</div>
         <SimpleLineChart :data="chartData" />
      </div>

      <div class="data-section card">
        <h2 class="card-title">净值日历</h2>
        <div class="daily-list-container">
            <table class="daily-table">
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>净值</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="item in chartData" :key="item.date">
                        <td>{{ item.date }}</td>
                        <td>{{ item.nav.toFixed(4) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
      </div>

    <div class="actions-section">
        <button class="btn-ai-eval" @click="askAiEvaluation" :disabled="evaluating">
          {{ evaluating ? '研究解读系统整理中...' : '✨ 生成本次历史模拟研究解读' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getBacktestResult } from '../services/backtestService'
import { useChatStore } from '../stores/chat'
import chatService from '../services/chatService'
import SimpleLineChart from '../components/SimpleLineChart.vue'

const props = defineProps(['id'])
const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()

// Use ID from props or route
const backtestId = computed(() => props.id || route.params.id)

const loading = ref(true)
const error = ref('')
const backtestData = ref(null)
const dailyNav = ref([])
const evaluating = ref(false)
const riskExpanded = ref(false)

// 数据加载
const loadData = async () => {
    loading.value = true
    error.value = ''
    try {
        const res = await getBacktestResult(backtestId.value)
        
        // 解析数据结构，兼容 {success, data: {...}} 或者 {success, data: {data: ...}}
        let payload = res.data
        if (payload?.data) {
            payload = payload.data
        }
        
        if (!res.success && !payload) {
             throw new Error(res.message || '获取数据失败')
        }

        backtestData.value = payload
        
        // 解析 daily_nav
        if (Array.isArray(payload.daily_nav)) {
            dailyNav.value = payload.daily_nav
        } else if (Array.isArray(payload.equity_curve)) {
            // 兼容可能得字段名
            dailyNav.value = payload.equity_curve
        } else {
             dailyNav.value = []
        }

    } catch (err) {
        error.value = err.message || '加载详情失败'
    } finally {
        loading.value = false
    }
}

// 基础信息计算
const dateRange = computed(() => {
    if (backtestData.value?.start_date && backtestData.value?.end_date) {
        return `${backtestData.value.start_date} 至 ${backtestData.value.end_date}`
    }
    if (dailyNav.value.length > 0) {
        return `${dailyNav.value[0].date} 至 ${dailyNav.value[dailyNav.value.length - 1].date}`
    }
    return '未知'
})

const metrics = computed(() => backtestData.value?.metrics || {})

const formattedAnnualReturn = computed(() => {
    const val = metrics.value.annual_return
    if (val !== undefined && val !== null) {
        if (Math.abs(val) <= 1) {
            return (val * 100).toFixed(2) + '%'
        }
        return val.toFixed(2) + '%'
    }
    // 兜底计算
    if (dailyNav.value.length > 1) {
        const first = dailyNav.value[0].nav
        const last = dailyNav.value[dailyNav.value.length - 1].nav
        if (first > 0) {
             const totalReturn = last / first - 1
             const years = dailyNav.value.length / 252
             if (years > 0) {
                  const ann = (Math.pow(1 + totalReturn, 1 / years) - 1) * 100
                  return ann.toFixed(2) + '% (估算)'
             }
             return (totalReturn * 100).toFixed(2) + '% (总收益)'
        }
    }
    return 'N/A'
})

const formattedSharpe = computed(() => {
    return metrics.value.sharpe_ratio !== undefined 
        ? Number(metrics.value.sharpe_ratio).toFixed(3) 
        : 'N/A'
})

const formattedDrawdown = computed(() => {
    const val = metrics.value.max_drawdown
    if (val !== undefined) {
         return (Math.abs(val) * 100).toFixed(2) + '%'
    }
    return 'N/A'
})

const chartData = computed(() => {
    return dailyNav.value.map(item => ({
        date: item.date,
        // 兼容 nav 字段或 value 字段
        nav: item.nav !== undefined ? item.nav : (item.value !== undefined ? item.value : 0)
    }))
})

// 研究解读逻辑
const askAiEvaluation = async () => {
    if (evaluating.value) return 
    evaluating.value = true

    try {
        // 1. 准备 Context
        const basicInfo = {
            stock: backtestData.value?.stock_code,
            range: dateRange.value,
            return: formattedAnnualReturn.value,
            sharpe: formattedSharpe.value,
            drawdown: formattedDrawdown.value,
            strategy_name: backtestData.value?.params?.strategy_name || 'custom',
            strategy_type: backtestData.value?.params?.strategy_mode || 'unknown'
        }

        // 简化的曲线数据 (首尾 + 极值点附近)
        // 为了省 token，我们只取开头、结尾、与中间几个点
        const curveSummary = []
        const len = chartData.value.length
        if (len > 0) {
            curveSummary.push(chartData.value[0]) // start
            if (len > 10) {
                 curveSummary.push(chartData.value[Math.floor(len * 0.25)])
                 curveSummary.push(chartData.value[Math.floor(len * 0.5)])
                 curveSummary.push(chartData.value[Math.floor(len * 0.75)])
            }
            if (len > 1) curveSummary.push(chartData.value[len - 1]) // end
        }

        const promptContext = `
      历史模拟基本信息:
- 标的: ${basicInfo.stock}
- 时间段: ${basicInfo.range}
      - 模拟模式: ${basicInfo.strategy_type} (${basicInfo.strategy_name})
- 年化收益: ${basicInfo.return}
- 夏普比率: ${basicInfo.sharpe}
- 最大回撤: ${basicInfo.drawdown}

      净值曲线摘要(Nav):
${JSON.stringify(curveSummary)}
        `.trim()

        const userMessage = `请基于以下历史模拟数据给出研究解读，不提供交易建议。上下文如下：\n${promptContext}`
        
        // 2. 设置系统 Prompt
        chatStore.setSystemPrompt("你是一个历史数据研究助理。请根据用户提供的模拟数据（收益、回撤、夏普等）做客观解读。请输出：1) 数据表现要点 2) 样本局限与风险点 3) 后续研究方向。必须明确：内容仅供研究与模拟，不构成投资建议，不荐股、不做交易推荐。输出要求：1) 必须分行输出；2) 使用短句，每句不超过20字；3) 不使用“略/后续/省略号”来截断回答；4) 需要分段时用空行分隔。")
        
        // 3. 打开聊天窗口
        if (!chatStore.isChatOpen) {
            chatStore.toggleChat()
        }

        // 4. 用户消息上屏
        chatStore.addMessage("请帮我解读当前历史模拟结果（仅研究用途）", true)
        
        // 5. 发送请求 (发送带有完整 Context 的 prompt 为 message)
        const res = await chatService.sendChat(userMessage, chatStore.systemPrompt, null, 0.6, 2000)
        
        if (res.success) {
            chatStore.addMessage(res.content, false)
        } else {
          chatStore.addMessage("抱歉，研究解读服务暂时不可用: " + (res.error || '未知错误'), false)
        }

    } catch (err) {
        console.error(err)
        chatStore.addMessage("发生错误，无法获取研究解读。", false)
    } finally {
        evaluating.value = false
    }
}

onMounted(() => {
    if (backtestId.value) {
        loadData()
    } else {
        error.value = '未指定回测ID'
        loading.value = false
    }
})
</script>

<style scoped>
.backtest-detail-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  background: #fdfdfd;
  min-height: 80vh;
}

.risk-banner {
  background: #fff3e6;
  border: 1px solid #ffb380;
  border-radius: 8px;
  padding: 10px 14px;
  margin-bottom: 16px;
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
  margin-bottom: 10px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  font-size: 1.8rem;
  color: #333;
}

.btn-back {
  text-decoration: none;
  color: #666;
  border: 1px solid #ddd;
  padding: 5px 10px;
  border-radius: 4px;
  transition: all 0.3s;
}

.btn-back:hover {
  background: #f0f0f0;
  color: #333;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  border: 1px solid #eee;
}

.card-title {
  font-size: 1.2rem;
  margin-bottom: 15px;
  border-left: 4px solid #ff7f00;
  padding-left: 10px;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item .label {
  font-size: 0.85rem;
  color: #999;
  margin-bottom: 4px;
}

.info-item .value {
  font-size: 1.1rem;
  font-weight: 500;
  color: #333;
}

.info-item .value.highlight {
  color: #ff7f00;
  font-weight: bold;
}

.daily-list-container {
    max-height: 300px;
    overflow-y: auto;
}

.daily-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
}

.daily-table th, .daily-table td {
    border-bottom: 1px solid #f0f0f0;
    padding: 8px 10px;
    text-align: left;
}

.daily-table th {
    background: #fafafa;
    position: sticky;
    top: 0;
}

.actions-section {
    text-align: center;
    margin-top: 30px;
}

.btn-ai-eval {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 12px 30px;
    font-size: 1.1rem;
    border-radius: 50px;
    cursor: pointer;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}

.btn-ai-eval:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.15);
}

.btn-ai-eval:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
}

.loading-state, .error-state {
    text-align: center;
    padding: 50px;
    font-size: 1.2rem;
    color: #666;
}

.btn-retry {
    display: block;
    margin: 10px auto;
    padding: 5px 15px;
    background: #ff7f00;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}
</style>
