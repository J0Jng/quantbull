<template>
  <div class="quant-analysis-tool">
    <div class="container">
      <div class="back-to-home">
        <router-link to="/" class="back-btn">返回主页</router-link>
      </div>
      <h1 class="page-title">量化分析工具</h1>
      
      <!-- 策略创建与回测 -->
      <div class="section card">
        <h2 class="section-title">策略创建与回测</h2>
        <div class="strategy-form">
          <div class="form-group">
            <label for="stock-code">股票代码:</label>
            <input 
              id="stock-code" 
              v-model="backtestForm.stock_code" 
              type="text" 
              placeholder="例如: 000001"
              class="form-control"
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="start-date">开始日期:</label>
              <input 
                id="start-date" 
                v-model="backtestForm.start_date" 
                type="date"
                class="form-control"
              />
            </div>
            
            <div class="form-group">
              <label for="end-date">结束日期:</label>
              <input 
                id="end-date" 
                v-model="backtestForm.end_date" 
                type="date"
                class="form-control"
              />
            </div>
          </div>
          
          <div class="form-group">
            <label for="strategy-mode">策略模式:</label>
            <select id="strategy-mode" v-model="backtestForm.strategy_mode" class="form-control">
              <option value="custom">自定义策略 (AI生成)</option>
              <option value="builtin">内置策略</option>
            </select>
          </div>
          
          <div v-if="backtestForm.strategy_mode === 'custom'" class="form-group">
            <label for="strategy-description">策略描述 (用于AI生成):</label>
            <textarea 
              id="strategy-description" 
              v-model="strategyDescription" 
              placeholder="描述您的策略思路，例如：基于均线交叉的交易策略，在短期均线上穿长期均线时买入，下穿时卖出"
              rows="4"
              class="form-control"
            ></textarea>
            <button 
              class="btn-secondary" 
              :disabled="generatingStrategy" 
              @click="generateStrategy"
            >
              {{ generatingStrategy ? '生成中...' : 'AI生成策略' }}
            </button>
          </div>
          
          <div v-if="backtestForm.strategy_mode === 'builtin'" class="form-group">
            <label for="strategy-name">内置策略:</label>
            <select id="strategy-name" v-model="backtestForm.strategy_name" class="form-control">
              <option value="ma_cross">均线交叉策略</option>
              <option value="rsi">RSI策略</option>
              <option value="bollinger_bands">布林带策略</option>
            </select>
          </div>
          
          <div v-if="generatedStrategy || backtestForm.strategy_code" class="form-group">
            <label>生成的策略代码:</label>
            <pre class="code-preview">{{ generatedStrategy || backtestForm.strategy_code }}</pre>
          </div>
          
          <!-- 回测模式选择 -->
          <div class="form-group">
            <label for="backtest-mode">回测模式:</label>
            <div class="mode-toggle">
              <div class="toggle-option">
                <input 
                  type="radio" 
                  id="sync-mode" 
                  v-model="backtestMode" 
                  value="sync" 
                  class="toggle-input"
                />
                <label for="sync-mode" class="toggle-label">
                  <span class="toggle-icon">⏳</span>
                  <span class="toggle-text">同步模式</span>
                  <span class="toggle-description">快速回测，实时等待结果</span>
                </label>
              </div>
              <div class="toggle-option">
                <input 
                  type="radio" 
                  id="async-mode" 
                  v-model="backtestMode" 
                  value="async" 
                  class="toggle-input"
                />
                <label for="async-mode" class="toggle-label">
                  <span class="toggle-icon">⚡</span>
                  <span class="toggle-text">异步模式</span>
                  <span class="toggle-description">提交后继续操作，后台处理</span>
                </label>
              </div>
            </div>
            <div class="mode-tip" v-if="backtestMode === 'sync'">
              <small>适合快速回测（小数据量），界面锁定等待结果</small>
            </div>
            <div class="mode-tip" v-else>
              <small>适合长时间运行任务，可在历史记录中查看进度</small>
            </div>
          </div>
          
          <div class="form-group">
            <label for="initial-cash">初始资金:</label>
            <input 
              id="initial-cash" 
              v-model.number="backtestForm.initial_cash" 
              type="number" 
              min="1000"
              class="form-control"
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="commission">手续费率:</label>
              <input 
                id="commission" 
                v-model.number="backtestForm.commission" 
                type="number" 
                min="0" 
                max="0.01" 
                step="0.001"
                class="form-control"
              />
            </div>
            
            <div class="form-group">
              <label for="slippage">滑点:</label>
              <input 
                id="slippage" 
                v-model.number="backtestForm.slippage" 
                type="number" 
                min="0" 
                max="0.01" 
                step="0.001"
                class="form-control"
              />
            </div>
          </div>
          
          <button 
            class="btn-primary" 
            :disabled="runningBacktest" 
            @click="runBacktest"
          >
            {{ getBacktestButtonText() }}
          </button>
          
          <!-- 异步任务状态显示 -->
          <div v-if="pendingTaskId" class="async-task-status card">
            <h4>异步任务状态</h4>
            <div class="task-info">
              <div class="task-id">任务ID: {{ pendingTaskId }}</div>
              <div class="task-status" :class="taskStatus">
                状态: {{ getTaskStatusText(taskStatus) }}
              </div>
              <button 
                class="btn-secondary" 
                @click="checkAsyncTaskStatus(pendingTaskId)"
                :disabled="taskStatus === 'completed'"
              >
                刷新状态
              </button>
            </div>
            <div v-if="taskStatus === 'completed'" class="task-completed">
              <p>✅ 任务已完成！结果已显示在上方。</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 回测结果展示 -->
      <div v-if="backtestResult" class="section card">
        <h2 class="section-title">回测结果</h2>
        <div class="result-summary">
          <div class="metric-card" v-for="(value, key) in backtestResult.metrics" :key="key">
            <div class="metric-value">{{ formatMetricValue(key, value) }}</div>
            <div class="metric-label">{{ getMetricLabel(key) }}</div>
          </div>
        </div>
        
        <div class="chart-container">
          <h3>净值曲线</h3>
          <div ref="chartContainer" class="chart-placeholder">
            <!-- 图表将在这里渲染 -->
            <p>净值图表区域</p>
          </div>
        </div>
        
        <div v-if="backtestResult.ai_review" class="ai-review card">
          <h3>AI策略评价</h3>
          <div class="review-grid">
            <div class="review-item">
              <div class="review-label">策略类型</div>
              <div class="review-value">{{ backtestResult.ai_review.strategy_type }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">胜率</div>
              <div class="review-value">{{ (backtestResult.ai_review.win_rate * 100).toFixed(2) }}%</div>
            </div>
            <div class="review-item">
              <div class="review-label">交易次数</div>
              <div class="review-value">{{ backtestResult.ai_review.trade_count }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">盈亏比</div>
              <div class="review-value">{{ backtestResult.ai_review.profit_loss_ratio.toFixed(2) }}</div>
            </div>
            <div class="review-item">
              <div class="review-label">波动率</div>
              <div class="review-value">{{ (backtestResult.ai_review.volatility * 100).toFixed(2) }}%</div>
            </div>
            <div class="review-item">
              <div class="review-label">最大连续亏损</div>
              <div class="review-value">{{ backtestResult.ai_review.max_consecutive_loss }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 错误信息展示 -->
      <div v-if="error" class="error-message card">
        {{ error }}
      </div>
      
      <!-- 历史回测记录 -->
      <div class="section card">
        <div class="section-header">
          <h2 class="section-title">历史回测记录</h2>
          <button 
            class="btn-secondary" 
            :disabled="loadingHistory" 
            @click="fetchHistoryRecords"
          >
            {{ loadingHistory ? '加载中...' : '刷新' }}
          </button>
        </div>
        
        <div v-if="loadingHistory" class="loading-indicator">
          加载中...
        </div>
        
        <div v-else>
          <div class="table-container">
            <table class="history-table">
              <thead>
                <tr>
                  <th>回测ID</th>
                  <th>股票代码</th>
                  <th>回测日期范围</th>
                  <th>策略类型</th>
                  <th>年化收益率</th>
                  <th>夏普比率</th>
                  <th>最大回撤</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="record in historyRecords" :key="record.id">
                  <td>{{ record.id }}</td>
                  <td>{{ record.stock_code }}</td>
                  <td>{{ record.start_date }} 至 {{ record.end_date }}</td>
                  <td>{{ record.strategy_type }}</td>
                  <td :class="{'positive': record.annual_return > 0, 'negative': record.annual_return < 0}">
                    {{ (record.annual_return * 100).toFixed(2) }}%
                  </td>
                  <td>{{ record.sharpe_ratio.toFixed(2) }}</td>
                  <td>{{ (record.max_drawdown * 100).toFixed(2) }}%</td>
                  <td>
                    <button class="btn-view-detail" @click="viewDetail(record.id)">查看详情</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div class="pagination">
            <button 
              :disabled="currentPage === 1" 
              @click="changePage(currentPage - 1)"
            >
              上一页
            </button>
            <span>第 {{ currentPage }} 页</span>
            <button 
              :disabled="historyRecords.length < pageSize" 
              @click="changePage(currentPage + 1)"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

// 表单数据
const backtestForm = reactive({
  stock_code: '',
  start_date: '',
  end_date: '',
  strategy_mode: 'custom',
  strategy_code: null,
  strategy_name: null,
  initial_cash: 1000000,
  commission: 0.001,
  slippage: 0
})

// 状态变量
const strategyDescription = ref('')
const generatedStrategy = ref('')
const generatingStrategy = ref(false)
const runningBacktest = ref(false)
const backtestResult = ref(null)
const error = ref('')
const backtestMode = ref('sync') // sync 或 async
const pendingTaskId = ref(null) // 异步任务ID
const taskStatus = ref(null) // 异步任务状态

// 获取API基础URL
const API_BASE_URL = '/api'

// AI生成策略
const generateStrategy = async () => {
  if (!strategyDescription.value.trim()) {
    error.value = '请输入策略描述'
    return
  }
  
  generatingStrategy.value = true
  error.value = ''
  
  try {
    const response = await fetch('/api/ai/api/ai/generate/strategy', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_description: strategyDescription.value,
        framework: 'backtrader'
      })
    })
    
    if (!response.ok) {
      throw new Error(`API请求失败: ${response.status}`)
    }
    
    const data = await response.json()
    generatedStrategy.value = data.strategy_code
    backtestForm.strategy_code = data.strategy_code
  } catch (err) {
    error.value = `生成策略失败: ${err.message}`
  } finally {
    generatingStrategy.value = false
  }
}

// 运行回测
const runBacktest = async () => {
  if (!backtestForm.stock_code) {
    error.value = '请输入股票代码'
    return
  }
  
  if (!backtestForm.start_date || !backtestForm.end_date) {
    error.value = '请选择回测日期范围'
    return
  }
  
  if (backtestForm.strategy_mode === 'custom' && !backtestForm.strategy_code) {
    error.value = '请先生成策略代码或提供自定义策略'
    return
  }
  
  if (backtestForm.strategy_mode === 'builtin' && !backtestForm.strategy_name) {
    error.value = '请选择内置策略'
    return
  }
  
  runningBacktest.value = true
  error.value = ''
  backtestResult.value = null
  pendingTaskId.value = null
  taskStatus.value = null
  
  try {
    // 准备回测数据
    const backtestPayload = {
      stock_code: backtestForm.stock_code,
      start_date: backtestForm.start_date,
      end_date: backtestForm.end_date,
      strategy_mode: backtestForm.strategy_mode,
      initial_cash: backtestForm.initial_cash,
      commission: backtestForm.commission,
      slippage: backtestForm.slippage,
      enable_ai_review: true
    }
    
    if (backtestForm.strategy_mode === 'custom') {
      backtestPayload.strategy_code = backtestForm.strategy_code
    } else {
      backtestPayload.strategy_name = backtestForm.strategy_name
    }
    
    if (backtestMode.value === 'sync') {
      // 同步模式 - 使用轮询
      await runSyncBacktest(backtestPayload)
    } else {
      // 异步模式 - 提交任务后立即返回
      await runAsyncBacktest(backtestPayload)
    }
  } catch (err) {
    error.value = `回测失败: ${err.message}`
    runningBacktest.value = false
  }
}

// 同步回测模式
const runSyncBacktest = async (payload) => {
  try {
    const response = await fetch('/api/quant/api/backtest/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    
    if (!response.ok) {
      throw new Error(`回测提交失败: ${response.status}`)
    }
    
    const submitResult = await response.json()
    const backtestId = submitResult.backtest_id
    
    // 使用指数退避策略进行轮询
    let retryCount = 0
    const maxRetries = 60 // 最多等待60秒
    const baseDelay = 1000 // 基础延迟1秒
    const maxDelay = 10000 // 最大延迟10秒
    
    while (retryCount < maxRetries) {
      await new Promise(resolve => {
        // 指数退避延迟
        const delay = Math.min(baseDelay * Math.pow(1.5, retryCount), maxDelay)
        setTimeout(resolve, delay)
      })
      
      const resultResponse = await fetch(`/api/quant/api/backtest/${backtestId}`)
      if (!resultResponse.ok) {
        throw new Error(`获取回测结果失败: ${resultResponse.status}`)
      }
      
      const result = await resultResponse.json()
      
      if (result.data && result.data.success) {
        backtestResult.value = result.data
        break
      }
      
      retryCount++
    }
    
    if (retryCount >= maxRetries) {
      throw new Error('回测超时，请使用异步模式或稍后查看历史记录')
    }
  } finally {
    runningBacktest.value = false
  }
}

// 异步回测模式
const runAsyncBacktest = async (payload) => {
  try {
    const response = await fetch('/api/quant/api/backtest/run_async', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })
    
    if (!response.ok) {
      throw new Error(`异步回测提交失败: ${response.status}`)
    }
    
    const submitResult = await response.json()
    pendingTaskId.value = submitResult.task_id
    taskStatus.value = 'submitted'
    
    // 显示成功消息
    error.value = `异步任务已提交！任务ID: ${submitResult.task_id}。可在历史记录中查看进度。`
  } finally {
    runningBacktest.value = false
  }
}

// 检查异步任务状态
const checkAsyncTaskStatus = async (taskId) => {
  try {
    const response = await fetch(`/api/quant/api/backtest/${taskId}`)
    if (!response.ok) {
      throw new Error(`检查任务状态失败: ${response.status}`)
    }
    
    const result = await response.json()
    if (result.data) {
      taskStatus.value = result.data.success ? 'completed' : 'processing'
      
      if (result.data.success) {
        backtestResult.value = result.data
        pendingTaskId.value = null
      }
    }
    
    return result.data
  } catch (err) {
    console.error('检查任务状态时出错:', err)
    return null
  }
}

// 格式化指标值
const formatMetricValue = (key, value) => {
  if (typeof value === 'number') {
    if (key.includes('rate') || key.includes('ratio') || key.includes('return') || key.includes('drawdown')) {
      return (value * 100).toFixed(2) + '%'
    }
    return value.toFixed(2)
  }
  return value
}

// 获取指标标签
const getMetricLabel = (key) => {
  const labels = {
    annual_return: '年化收益率',
    sharpe_ratio: '夏普比率',
    max_drawdown: '最大回撤',
    total_return: '总收益率',
    volatility: '波动率',
    win_rate: '胜率'
  }
  return labels[key] || key
}

// 历史记录相关变量
const historyRecords = ref([])
const loadingHistory = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)

// 获取历史回测记录
const fetchHistoryRecords = async () => {
  loadingHistory.value = true
  error.value = ''
  
  try {
    const response = await fetch(`/api/quant/api/backtest?limit=${pageSize.value}&offset=${(currentPage.value - 1) * pageSize.value}`)
    
    if (!response.ok) {
      throw new Error(`获取历史记录失败: ${response.status}`)
    }
    
    const data = await response.json()
    historyRecords.value = data.records || []
  } catch (err) {
    error.value = `获取历史记录失败: ${err.message}`
  } finally {
    loadingHistory.value = false
  }
}

// 切换分页
const changePage = (page) => {
  currentPage.value = page
  fetchHistoryRecords()
}

// 查看详情
const viewDetail = (backtestId) => {
  // 这里可以跳转到详情页面或显示模态框
  console.log(`查看回测详情: ${backtestId}`)
}

// 获取回测按钮文本
const getBacktestButtonText = () => {
  if (runningBacktest.value) {
    return backtestMode.value === 'sync' ? '回测中...' : '提交中...'
  }
  return backtestMode.value === 'sync' ? '开始回测' : '异步提交'
}

// 获取任务状态文本
const getTaskStatusText = (status) => {
  const statusMap = {
    'submitted': '已提交',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || '未知'
}

// 初始化时获取历史记录
fetchHistoryRecords()
</script>

<style scoped>
.quant-analysis-tool {
  padding: 20px 0;
  background: #fff8f0;
  min-height: calc(100vh - 100px);
}

.container {
  width: 1200px;
  margin: 0 auto;
  position: relative;
}

.back-to-home {
  position: absolute;
  left: 0;
  top: 0;
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
  margin-bottom: 30px;
  text-align: center;
  color: #ff7f00;
  font-weight: bold;
}

.card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #f0f0f0;
}

.section-title {
  font-size: 24px;
  color: #fff;
  background: #ff7f00;
  padding: 4px 12px;
  border-radius: 3px;
  margin: 15px 0 20px 0;
  display: inline-block;
  border-radius: 10px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-row .form-group {
  flex: 1;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-control:focus {
  border-color: #ff7f00;
  outline: none;
}

.code-preview {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: monospace;
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #ddd;
  background: #f8f8f8;
}

.btn-primary,
.btn-secondary {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
  font-weight: bold;
}

.btn-primary {
  background-color: #ff7f00;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #e06f00;
}

.btn-primary:disabled {
  background-color: #ffa555;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #1e90ff;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #0077ea;
}

.btn-secondary:disabled {
  background-color: #87cefa;
  cursor: not-allowed;
}

.result-summary {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  text-align: center;
  padding: 15px;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.metric-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #ff7f00;
}

.metric-label {
  font-size: 0.9rem;
  color: #666;
  margin-top: 5px;
}

.chart-container {
  margin: 30px 0;
}

.chart-container h3 {
  margin-bottom: 15px;
  color: #333;
}

.chart-placeholder {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
  border-radius: 8px;
  border: 1px dashed #ddd;
}

.ai-review {
  margin-top: 30px;
  background: #fffbe6;
  border: 1px solid #ffe58f;
}

.ai-review h3 {
  margin-bottom: 15px;
  color: #333;
}

.review-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.review-item {
  display: flex;
  flex-direction: column;
  padding: 15px;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.review-label {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 5px;
}

.review-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.error-message {
  padding: 15px;
  background-color: #ffebee;
  color: #c62828;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  margin-top: 20px;
}

/* 历史记录区域样式 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.loading-indicator {
  text-align: center;
  padding: 20px;
  color: #666;
}

.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e1e1e1;
}

.history-table th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #333;
}

.history-table tr:hover {
  background-color: #f9f9f9;
}

.positive {
  color: #4caf50;
  font-weight: bold;
}

.negative {
  color: #f44336;
  font-weight: bold;
}

.btn-view-detail {
  padding: 6px 12px;
  background-color: #ff7f00;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-view-detail:hover {
  background-color: #e06f00;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.pagination button {
  padding: 8px 16px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination button:hover:not(:disabled) {
  background-color: #ff7f00;
  color: white;
  border-color: #ff7f00;
}

  .pagination button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* 模式切换样式 */
  .mode-toggle {
    display: flex;
    gap: 10px;
    margin-top: 10px;
  }

  .toggle-option {
    flex: 1;
  }

  .toggle-input {
    display: none;
  }

  .toggle-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 15px;
    border: 2px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #f8f8f8;
    text-align: center;
  }

  .toggle-input:checked + .toggle-label {
    border-color: #ff7f00;
    background-color: #fff8f0;
    box-shadow: 0 0 10px rgba(255, 127, 0, 0.2);
  }

  .toggle-icon {
    font-size: 1.5rem;
    margin-bottom: 5px;
  }

  .toggle-text {
    font-weight: bold;
    color: #333;
    margin-bottom: 2px;
  }

  .toggle-description {
    font-size: 0.8rem;
    color: #666;
  }

  .mode-tip {
    margin-top: 5px;
    padding: 5px 10px;
    background: #f0f8ff;
    border-radius: 4px;
    border-left: 3px solid #1e90ff;
  }

  .mode-tip small {
    color: #4169e1;
  }

  /* 异步任务状态样式 */
  .async-task-status {
    margin-top: 20px;
    border-left: 4px solid #1e90ff;
    background: #f8fdff;
  }

  .async-task-status h4 {
    color: #1e90ff;
    margin: 0 0 15px 0;
    font-size: 1.1rem;
  }

  .task-info {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    align-items: center;
    margin-bottom: 10px;
  }

  .task-id {
    font-family: monospace;
    background: #f0f0f0;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  .task-status {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: bold;
  }

  .task-status.submitted {
    background: #fff3cd;
    color: #856404;
    border: 1px solid #ffeaa7;
  }

  .task-status.processing {
    background: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
  }

  .task-status.completed {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
  }

  .task-status.failed {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
  }

  .task-completed {
    padding: 10px;
    background: #d4edda;
    border-radius: 4px;
    text-align: center;
  }

  .task-completed p {
    margin: 0;
    color: #155724;
    font-weight: bold;
  }

  /* 响应式调整 */
  @media (max-width: 768px) {
    .mode-toggle {
      flex-direction: column;
    }
    
    .task-info {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .toggle-label {
      padding: 10px;
    }
    
    .toggle-icon {
      font-size: 1.2rem;
    }
  }

@media (max-width: 768px) {
  .container {
    width: 95%;
    padding: 0 10px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .result-summary {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
  
  .review-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .history-table th,
  .history-table td {
    padding: 8px;
    font-size: 0.9rem;
  }
  
  .btn-view-detail {
    padding: 4px 8px;
    font-size: 0.8rem;
  }
}
</style>