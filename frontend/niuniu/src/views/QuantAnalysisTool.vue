<template>
  <div class="quant-analysis-tool">
    <div class="container">
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
            {{ runningBacktest ? '回测中...' : '开始回测' }}
          </button>
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
  
  try {
    // 提交回测任务
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
    
    const response = await fetch('/api/quant/api/backtest/run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(backtestPayload)
    })
    
    if (!response.ok) {
      throw new Error(`回测提交失败: ${response.status}`)
    }
    
    const submitResult = await response.json()
    const backtestId = submitResult.backtest_id
    
    // 轮询获取回测结果
    let result
    do {
      await new Promise(resolve => setTimeout(resolve, 1000)) // 等待1秒
      
      const resultResponse = await fetch(`/api/quant/api/backtest/${backtestId}`)
      if (!resultResponse.ok) {
        throw new Error(`获取回测结果失败: ${resultResponse.status}`)
      }
      
      result = await resultResponse.json()
    } while (result.data && !result.data.success)
    
    backtestResult.value = result.data
  } catch (err) {
    error.value = `回测失败: ${err.message}`
  } finally {
    runningBacktest.value = false
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
</script>

<style scoped>
.quant-analysis-tool {
  padding: 20px 0;
  background: #f9f9f9;
  min-height: calc(100vh - 100px);
}

.container {
  width: 1200px;
  margin: 0 auto;
  position: relative;
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
}
</style>