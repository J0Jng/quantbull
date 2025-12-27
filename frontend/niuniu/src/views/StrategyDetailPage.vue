<template>
  <div class="strategy-detail-page">
    <div class="container">
      <!-- 页面导航 -->
      <div class="page-nav">
        <router-link to="/strategies" class="back-btn">返回列表</router-link>
        <h1 class="page-title">策略详情</h1>
        <div class="page-actions">
          <router-link :to="`/strategies/${strategyId}/edit`" class="btn-primary">
            编辑策略
          </router-link>
          <button 
            class="btn-secondary" 
            @click="runBacktest"
            :disabled="isRunningBacktest"
          >
            {{ isRunningBacktest ? '回测中...' : '运行回测' }}
          </button>
          <button 
            class="btn-danger" 
            @click="deleteStrategy"
            :disabled="strategyData.status === 'active'"
          >
            删除策略
          </button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-indicator">
        <p>正在加载策略详情...</p>
      </div>

      <!-- 错误信息 -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-if="!loading && strategyData.id" class="strategy-content">
        <!-- 策略基本信息 -->
        <div class="basic-info-section card">
          <div class="info-header">
            <h2 class="info-title">{{ strategyData.name }}</h2>
            <span :class="['status-badge', `status-${strategyData.status}`]">
              {{ getStatusText(strategyData.status) }}
            </span>
          </div>
          
          <div class="info-grid">
            <div class="info-item">
              <label>策略ID:</label>
              <span class="strategy-id">{{ strategyData.id }}</span>
            </div>
            <div class="info-item">
              <label>创建时间:</label>
              <span>{{ formatDate(strategyData.created_at) }}</span>
            </div>
            <div class="info-item">
              <label>更新时间:</label>
              <span>{{ formatDate(strategyData.updated_at) }}</span>
            </div>
            <div class="info-item">
              <label>创建者:</label>
              <span>{{ strategyData.creator || '系统用户' }}</span>
            </div>
          </div>

          <div v-if="strategyData.description" class="description-section">
            <label>策略描述:</label>
            <p class="description-text">{{ strategyData.description }}</p>
          </div>
        </div>

        <!-- 策略代码展示 -->
        <div class="code-section card">
          <div class="section-header">
            <h3 class="section-title">策略代码</h3>
            <div class="code-actions">
              <button 
                class="btn-secondary" 
                @click="copyCode"
                :title="copyButtonText"
              >
                {{ copyButtonText }}
              </button>
              <button 
                class="btn-secondary" 
                @click="toggleCodeExpand"
              >
                {{ isCodeExpanded ? '收起' : '展开全部' }}
              </button>
            </div>
          </div>
          
          <div class="code-container" :class="{ 'expanded': isCodeExpanded }">
            <pre class="code-content"><code>{{ displayedCode }}</code></pre>
          </div>
          
          <div v-if="!isCodeExpanded && lineCount > 50" class="code-footer">
            <button class="expand-btn" @click="toggleCodeExpand">
              显示完整代码（共{{ lineCount }}行）
            </button>
          </div>
        </div>

        <!-- 策略参数 -->
        <div class="parameters-section card">
          <h3 class="section-title">策略参数</h3>
          <div class="parameters-container">
            <div v-if="strategyData.parameters && Object.keys(strategyData.parameters).length > 0" 
                 class="parameters-grid">
              <div v-for="(value, key) in strategyData.parameters" :key="key" class="parameter-item">
                <label>{{ key }}:</label>
                <span>{{ value }}</span>
              </div>
            </div>
            <div v-else class="empty-parameters">
              <p>暂无参数配置</p>
            </div>
          </div>
        </div>

        <!-- 回测历史 -->
        <div class="backtest-history-section card">
          <div class="section-header">
            <h3 class="section-title">回测历史</h3>
            <button 
              class="btn-secondary" 
              @click="fetchBacktestHistory"
              :disabled="loadingHistory"
            >
              {{ loadingHistory ? '加载中...' : '刷新' }}
            </button>
          </div>

          <div v-if="loadingHistory" class="loading-history">
            <p>正在加载回测历史...</p>
          </div>

          <div v-else-if="backtestHistory.length > 0" class="history-list">
            <div v-for="backtest in backtestHistory" :key="backtest.id" class="history-item">
              <div class="history-header">
                <span class="backtest-id">回测ID: {{ backtest.id }}</span>
                <span :class="['backtest-status', `status-${backtest.status}`]">
                  {{ getBacktestStatusText(backtest.status) }}
                </span>
              </div>
              
              <div class="history-details">
                <div class="detail-item">
                  <label>股票代码:</label>
                  <span>{{ backtest.stock_code }}</span>
                </div>
                <div class="detail-item">
                  <label>回测期间:</label>
                  <span>{{ backtest.start_date }} 至 {{ backtest.end_date }}</span>
                </div>
                <div class="detail-item">
                  <label>年化收益率:</label>
                  <span :class="getReturnClass(backtest.annual_return)">
                    {{ formatPercentage(backtest.annual_return) }}
                  </span>
                </div>
                <div class="detail-item">
                  <label>夏普比率:</label>
                  <span>{{ backtest.sharpe_ratio?.toFixed(2) || 'N/A' }}</span>
                </div>
              </div>
              
              <div class="history-actions">
                <router-link 
                  :to="`/quant-analysis?backtest=${backtest.id}`" 
                  class="btn-view"
                >
                  查看详情
                </router-link>
                <button 
                  class="btn-secondary" 
                  @click="rerunBacktest(backtest)"
                  :disabled="isRunningBacktest"
                >
                  重新回测
                </button>
              </div>
            </div>
          </div>

          <div v-else class="empty-history">
            <div class="empty-icon">📊</div>
            <p>暂无回测记录</p>
            <p class="empty-hint">运行回测以查看策略表现</p>
          </div>
        </div>

        <!-- 策略操作记录 -->
        <div class="operations-section card">
          <h3 class="section-title">操作记录</h3>
          <div class="operations-list">
            <div v-for="(operation, index) in strategyData.operations" :key="index" class="operation-item">
              <div class="operation-header">
                <span class="operation-type">{{ getOperationTypeText(operation.type) }}</span>
                <span class="operation-time">{{ formatTime(operation.timestamp) }}</span>
              </div>
              <div class="operation-details">
                <span class="operation-user">{{ operation.user }}</span>
                <span class="operation-description">{{ operation.description }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 从路由获取策略ID
const strategyId = ref(route.params.id)

// 响应式数据
const strategyData = ref({})
const loading = ref(false)
const error = ref('')
const isCodeExpanded = ref(false)
const copyButtonText = ref('复制代码')
const backtestHistory = ref([])
const loadingHistory = ref(false)
const isRunningBacktest = ref(false)

// 模拟API调用获取策略详情
const fetchStrategyDetail = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 模拟API延迟
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 模拟数据 - 实际项目中替换为真实API调用
    strategyData.value = {
      id: strategyId.value,
      name: '均线交叉策略',
      description: '基于5日均线和20日均线交叉的简单交易策略，当短期均线上穿长期均线时买入，下穿时卖出。',
      status: 'active',
      created_at: '2025-12-15T10:30:00Z',
      updated_at: '2025-12-20T14:25:00Z',
      creator: 'quant_user',
      code: `import backtrader as bt

class SimpleMovingAverage(bt.Strategy):
    params = (
        ('window', 20),
    )
    
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.window
        )
    
    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell()
    
    def stop(self):
        self.log(f'最终资产: {self.broker.getvalue():.2f}')`,
      parameters: {
        window: 20,
        threshold: 0.01,
        commission: 0.001
      },
      operations: [
        {
          type: 'create',
          timestamp: '2025-12-15T10:30:00Z',
          user: 'quant_user',
          description: '创建策略'
        },
        {
          type: 'update',
          timestamp: '2025-12-20T14:25:00Z',
          user: 'quant_user',
          description: '优化交易逻辑'
        }
      ]
    }
    
  } catch (err) {
    error.value = `获取策略详情失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

// 计算属性
const lineCount = computed(() => {
  if (!strategyData.value.code) return 0
  return strategyData.value.code.split('\n').length
})

const displayedCode = computed(() => {
  if (isCodeExpanded.value) {
    return strategyData.value.code
  }
  // 显示前50行
  const lines = strategyData.value.code.split('\n')
  return lines.slice(0, 50).join('\n')
})

// 方法
const getStatusText = (status) => {
  const statusMap = {
    'active': '活跃',
    'inactive': '非活跃',
    'draft': '草稿'
  }
  return statusMap[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

const toggleCodeExpand = () => {
  isCodeExpanded.value = !isCodeExpanded.value
}

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(strategyData.value.code)
    copyButtonText.value = '已复制!'
    setTimeout(() => {
      copyButtonText.value = '复制代码'
    }, 2000)
  } catch (err) {
    copyButtonText.value = '复制失败'
    setTimeout(() => {
      copyButtonText.value = '复制代码'
    }, 2000)
  }
}

const fetchBacktestHistory = async () => {
  loadingHistory.value = true
  
  try {
    // 模拟API调用获取回测历史
    await new Promise(resolve => setTimeout(resolve, 600))
    
    backtestHistory.value = [
      {
        id: 'BT001',
        stock_code: '000001',
        start_date: '2025-01-01',
        end_date: '2025-12-01',
        status: 'completed',
        annual_return: 0.1543,
        sharpe_ratio: 1.23
      },
      {
        id: 'BT002',
        stock_code: '000002',
        start_date: '2025-06-01',
        end_date: '2025-12-01',
        status: 'completed',
        annual_return: -0.0234,
        sharpe_ratio: -0.45
      }
    ]
  } catch (err) {
    console.error('获取回测历史失败:', err)
  } finally {
    loadingHistory.value = false
  }
}

const getBacktestStatusText = (status) => {
  const statusMap = {
    'completed': '已完成',
    'running': '运行中',
    'failed': '失败',
    'pending': '等待中'
  }
  return statusMap[status] || status
}

const formatPercentage = (value) => {
  if (value === null || value === undefined) return 'N/A'
  return (value * 100).toFixed(2) + '%'
}

const getReturnClass = (returnValue) => {
  if (returnValue > 0) return 'positive'
  if (returnValue < 0) return 'negative'
  return 'neutral'
}

const getOperationTypeText = (type) => {
  const typeMap = {
    'create': '创建',
    'update': '更新',
    'delete': '删除',
    'backtest': '回测'
  }
  return typeMap[type] || type
}

const runBacktest = async () => {
  isRunningBacktest.value = true
  
  try {
    // 模拟运行回测
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 跳转到回测页面或显示结果
    router.push(`/quant-analysis?strategy=${strategyId.value}`)
  } catch (err) {
    console.error('回测失败:', err)
  } finally {
    isRunningBacktest.value = false
  }
}

const rerunBacktest = async (backtest) => {
  isRunningBacktest.value = true
  
  try {
    await new Promise(resolve => setTimeout(resolve, 1500))
    router.push(`/quant-analysis?backtest=${backtest.id}&rerun=true`)
  } catch (err) {
    console.error('重新回测失败:', err)
  } finally {
    isRunningBacktest.value = false
  }
}

const deleteStrategy = async () => {
  if (!confirm('确定要删除这个策略吗？此操作不可恢复。')) {
    return
  }
  
  try {
    // 模拟删除操作
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 删除成功后返回到列表页面
    router.push('/strategies')
  } catch (err) {
    error.value = `删除策略失败: ${err.message}`
  }
}

// 生命周期
onMounted(() => {
  fetchStrategyDetail()
  fetchBacktestHistory()
})
</script>

<style scoped>
.strategy-detail-page {
  padding: 20px 0;
  background: #fff8f0;
  min-height: calc(100vh - 100px);
}

.container {
  width: 1200px;
  margin: 0 auto;
  position: relative;
}

.page-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.back-btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #ff7f00;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.back-btn:hover {
  background-color: #e06f00;
}

.page-title {
  font-size: 2rem;
  color: #ff7f00;
  font-weight: bold;
  margin: 0;
}

.page-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #f0f0f0;
}

.loading-indicator,
.loading-history {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-message {
  padding: 15px;
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  text-align: center;
}

.basic-info-section .info-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.info-title {
  font-size: 1.5rem;
  color: #333;
  margin: 0;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: bold;
}

.status-active {
  background: #e8f5e9;
  color: #4caf50;
}

.status-inactive {
  background: #ffebee;
  color: #f44336;
}

.status-draft {
  background: #fff3e0;
  color: #ff9800;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-item label {
  font-weight: bold;
  color: #666;
  font-size: 0.9rem;
}

.strategy-id {
  font-family: monospace;
  color: #666;
}

.description-section {
  border-top: 1px solid #f0f0f0;
  padding-top: 15px;
}

.description-section label {
  font-weight: bold;
  color: #666;
  margin-bottom: 8px;
  display: block;
}

.description-text {
  color: #333;
  line-height: 1.6;
  margin: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}

.section-title {
  font-size: 24px;
  color: #fff;
  background: #ff7f00;
  padding: 4px 12px;
  border-radius: 3px;
  margin: 0;
  display: inline-block;
  border-radius: 10px;
}

.code-actions {
  display: flex;
  gap: 10px;
}

.btn-primary, .btn-secondary, .btn-danger, .btn-view {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
  text-decoration: none;
  font-weight: bold;
}

.btn-primary {
  background-color: #ff7f00;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #e06f00;
}

.btn-secondary {
  background-color: #1e90ff;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #0077ea;
}

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #d32f2f;
}

.btn-danger:disabled {
  background-color: #ffcdd2;
  color: #666;
  cursor: not-allowed;
}

.btn-view {
  background-color: #4caf50;
  color: white;
  padding: 4px 8px;
  font-size: 0.8rem;
}

.btn-view:hover {
  background-color: #45a049;
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.code-container {
  max-height: 400px;
  overflow: hidden;
  transition: max-height 0.3s ease;
  border: 1px solid #e1e1e1;
  border-radius: 4px;
}

.code-container.expanded {
  max-height: none;
}

.code-content {
  padding: 15px;
  margin: 0;
  background: #f8f8f8;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.4;
  overflow-x: auto;
  white-space: pre;
}

.code-footer {
  text-align: center;
  padding: 10px;
  border-top: 1px solid #e1e1e1;
}

.expand-btn {
  background: none;
  border: 1px solid #ff7f00;
  color: #ff7f00;
  padding: 5px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.expand-btn:hover {
  background: #ff7f00;
  color: white;
}

.parameters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.parameter-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #e1e1e1;
}

.parameter-item label {
  font-weight: bold;
  color: #666;
  font-size: 0.9rem;
}

.empty-parameters,
.empty-history {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.empty-hint {
  font-size: 0.9rem;
  margin-top: 5px;
}

.history-item {
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  background: #f9f9f9;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 10px;
}

.backtest-id {
  font-family: monospace;
  color: #666;
}

.backtest-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-completed {
  background: #e8f5e9;
  color: #4caf50;
}

.status-running {
  background: #e3f2fd;
  color: #2196f3;
}

.status-failed {
  background: #ffebee;
  color: #f44336;
}

.status-pending {
  background: #fff3e0;
  color: #ff9800;
}

@media (max-width: 768px) {
  .container {
    width: 95%;
    padding: 0 10px;
  }
  
  .page-nav {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .page-actions {
    width: 100%;
    justify-content: flex-start;
    flex-wrap: wrap;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .history-details {
    grid-template-columns: 1fr;
  }
  
  .history-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}

.positive {
  color: #4caf50;
  font-weight: bold;
}

.negative {
  color: #f44336;
  font-weight: bold;
}

.neutral {
  color: #666;
  font-weight: normal;
}
</style>