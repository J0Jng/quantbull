<template>
  <div class="quant-analysis-tool">
    <header class="header">
      <router-link to="/" class="logo">脑科学研究室 - 数据模拟中心</router-link>
      <div class="header-nav">
        <router-link to="/stock-data">历史行情数据</router-link>
        <router-link to="/dragon-tiger-list">公开异动统计</router-link>
        <router-link to="/financial-report">财报数据集</router-link>
        <router-link to="/fund-source">资金流历史统计</router-link>
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

    <div class="container">
      <h1 class="page-title">数据模拟分析工具</h1>
      <div class="module-tip">仅研究展示，不构成建议，数据或延迟误差</div>
      
      <!-- 回测模型创建与回测 -->
      <div class="section card">
        <h2 class="section-title">回测模型创建与回测</h2>
        <div class="module-tip">仅研究展示，不构成建议，历史不代表未来</div>
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
            <label for="strategy-mode">回测模型模式:</label>
            <select id="strategy-mode" v-model="backtestForm.strategy_mode" class="form-control">
              <option value="saved">已保存回测模型</option>
              <option value="builtin">内置回测模型</option>
            </select>
          </div>
          
          <div v-if="backtestForm.strategy_mode === 'saved'" class="form-group">
            <label for="saved-strategy">选择回测模型:</label>
            <select id="saved-strategy" v-model="backtestForm.strategy_id" class="form-control">
              <option value="">请选择回测模型</option>
              <option v-for="item in savedStrategies" :key="item.id" :value="item.id">
                {{ item.name }}{{ item.description ? ' - ' + item.description : '' }}
              </option>
            </select>
            <div v-if="loadingSavedStrategies" class="loading-indicator">加载回测模型列表...</div>
            <div v-if="!loadingSavedStrategies && savedStrategies.length === 0" class="info-text">
              暂无已保存的回测模型，请先<router-link to="/strategies/create">创建回测模型</router-link>
            </div>
          </div>
          
          <div v-if="backtestForm.strategy_mode === 'builtin'" class="form-group">
            <label for="strategy-name">内置回测模型:</label>
            <select id="strategy-name" v-model="backtestForm.strategy_name" class="form-control">
              <option v-for="item in builtinStrategies" :key="item.name" :value="item.name">
                {{ (item.display_name || item.name) + (item.description ? ' - ' + item.description : '') }}
              </option>
            </select>
            <div v-if="loadingBuiltin" class="loading-indicator">加载内置回测模型...</div>
          </div>

          <div v-if="backtestForm.strategy_mode === 'builtin'" class="form-group">
            <label>回测模型参数（可自定义）:</label>
            <div v-if="currentParamSchema.length" class="param-grid">
              <div v-for="field in currentParamSchema" :key="field.key" class="param-field">
                <span class="param-label">{{ field.label }}</span>
                <template v-if="field.type === 'number'">
                  <input 
                    type="number"
                    class="form-control"
                    v-model.number="builtinParameters[field.key]"
                    :min="field.min"
                    :max="field.max"
                    :step="field.step || 1"
                  />
                </template>
                <template v-else-if="field.type === 'boolean'">
                  <label class="checkbox-inline">
                    <input type="checkbox" v-model="builtinParameters[field.key]" />
                    <span>开启</span>
                  </label>
                </template>
                <template v-else>
                  <input type="text" class="form-control" v-model="builtinParameters[field.key]" />
                </template>
              </div>
            </div>
            <div v-else class="param-tip">该回测模型暂未配置参数表，请填写下方 JSON 来自定义参数（与回测模型代码示例一致）。</div>

            <div v-if="!currentParamSchema.length" class="param-json-wrapper">
              <label class="param-label">参数 JSON（会直接传给后端 parameters 字段）</label>
              <textarea
                class="form-control param-json"
                rows="4"
                v-model="builtinParamsJson"
                placeholder='{"fast_period":5,"slow_period":20}'
              ></textarea>
            </div>
          </div>
          
          <div v-if="generatedStrategy || backtestForm.strategy_code" class="form-group">
            <label>生成的回测模型代码:</label>
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
      
      <!-- 回测结束提示与详情入口 -->
      <div v-if="backtestResult" class="section card">
        <h2 class="section-title">回测已结束</h2>
        <div class="module-tip">仅研究展示，不构成建议，历史不代表未来</div>
        <p class="info-text">回测结果已生成，请前往详情查看。</p>
        <button
          class="btn-view-detail"
          @click="viewDetail(backtestResult.backtest_id || backtestResult.id)"
        >
          查看详情
        </button>
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
            {{ loadingHistory ? '加载中...' : '重新加载数据' }}
          </button>
        </div>
        <div class="module-tip">仅研究展示，不构成建议，数据或延迟误差</div>
        <div class="module-tip">仅加载最新已入库数据</div>
        
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
                  <th>回测模型类型</th>
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
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getBuiltinStrategies, getStrategies, getStrategy } from '@/services/strategyService'
import { runBacktest as runBacktestService, runBacktestAsync as runBacktestAsyncService, getBacktestResult, getBacktestList } from '@/services/backtestService'

const router = useRouter()
const route = useRoute()
const riskExpanded = ref(false)

// 表单数据
const backtestForm = reactive({
  stock_code: '',
  start_date: '',
  end_date: '',
  strategy_mode: 'saved',
  strategy_id: '',
  strategy_code: null,
  strategy_name: null,
  initial_cash: 1000000,
  commission: 0.001,
  slippage: 0
})

// 状态变量
const savedStrategies = ref([])
const loadingSavedStrategies = ref(false)
const runningBacktest = ref(false)
const backtestResult = ref(null)
const error = ref('')
const backtestMode = ref('sync') // sync 或 async
const pendingTaskId = ref(null) // 异步任务ID
const taskStatus = ref(null) // 异步任务状态
const builtinStrategies = ref([])
const loadingBuiltin = ref(false)
const builtinParameters = reactive({})
const builtinParamsJson = ref('{}')

const builtinParamSchemas = {
  ma_cross: [
    { key: 'fast_period', label: '短期均线周期', type: 'number', default: 5, min: 1, step: 1 },
    { key: 'slow_period', label: '长期均线周期', type: 'number', default: 20, min: 1, step: 1 }
  ],
  rsi: [
    { key: 'rsi_period', label: 'RSI周期', type: 'number', default: 14, min: 1, step: 1 },
    { key: 'rsi_low', label: '超卖阈值', type: 'number', default: 30, min: 1, step: 1 },
    { key: 'rsi_high', label: '超买阈值', type: 'number', default: 70, min: 1, step: 1 }
  ],
  mean_reversion_rsi: [
    { key: 'rsi_period', label: 'RSI周期', type: 'number', default: 14, min: 1, step: 1 },
    { key: 'oversold', label: '超卖阈值', type: 'number', default: 30, min: 1, step: 1 },
    { key: 'overbought', label: '超买阈值', type: 'number', default: 70, min: 1, step: 1 },
    { key: 'rebalance_frequency', label: '再平衡频率 D/W/M', type: 'text', default: 'M' }
  ],
  trend_ma: [
    { key: 'fast_period', label: '快线周期', type: 'number', default: 20, min: 1, step: 1 },
    { key: 'slow_period', label: '慢线周期', type: 'number', default: 60, min: 1, step: 1 },
    { key: 'rebalance_frequency', label: '再平衡频率 D/W/M', type: 'text', default: 'M' }
  ],
  rotation_momentum_top1: [
    { key: 'lookback', label: '动量回看期', type: 'number', default: 60, min: 5, step: 5 },
    { key: 'rebalance_frequency', label: '再平衡频率 D/W/M', type: 'text', default: 'M' }
  ],
  risk_parity_inverse_vol: [
    { key: 'lookback', label: '波动率回看期', type: 'number', default: 60, min: 5, step: 5 },
    { key: 'rebalance_frequency', label: '再平衡频率 D/W/M', type: 'text', default: 'M' }
  ],
  multifactor_topk: [
    { key: 'lookback', label: '模拟参数回看期', type: 'number', default: 60, min: 5, step: 5 },
    { key: 'top_k', label: '样本筛选数量', type: 'number', default: 10, min: 1, step: 1 },
    { key: 'rebalance_frequency', label: '再平衡频率 D/W/M', type: 'text', default: 'M' }
  ],
  pairs_trading_zscore: [
    { key: 'lookback', label: 'Z分数回看期', type: 'number', default: 60, min: 10, step: 5 },
    { key: 'entry_z', label: '开仓阈值', type: 'number', default: 2.0, step: 0.1 },
    { key: 'exit_z', label: '平仓阈值', type: 'number', default: 0.5, step: 0.1 },
    { key: 'allow_short', label: '允许做空', type: 'boolean', default: true }
  ],
  kronos_multidim_rotation: [
    { key: 'top_stocks', label: '股票持仓数量', type: 'number', default: 10, min: 1, step: 1 },
    { key: 'top_etfs', label: 'ETF持仓数量', type: 'number', default: 5, min: 0, step: 1 },
    { key: 'lookback', label: '指标回看期', type: 'number', default: 60, min: 10, step: 5 },
    { key: 'rebalance_frequency', label: '再平衡频率 D/W/M', type: 'text', default: 'D' },
    { key: 'w_tech', label: '技术面权重', type: 'number', default: 0.30, step: 0.01 },
    { key: 'w_industry', label: '行业景气权重', type: 'number', default: 0.25, step: 0.01 },
    { key: 'w_hot', label: '热点权重', type: 'number', default: 0.20, step: 0.01 },
    { key: 'w_fund', label: '基本面权重', type: 'number', default: 0.15, step: 0.01 },
    { key: 'w_sent', label: '舆情权重', type: 'number', default: 0.10, step: 0.01 },
    { key: 'risk_capital', label: '风险资本比例', type: 'number', default: 0.95, step: 0.01 },
    { key: 'max_leverage', label: '最大杠杆', type: 'number', default: 1.0, step: 0.1 },
    { key: 'force_cash', label: '强制空仓', type: 'boolean', default: false }
  ],
  legacy_backtrace_ma250: [
    { key: 'threshold', label: '阈值', type: 'number', default: 60, min: 1, step: 1 },
    { key: 'hold_bars', label: '持有周期', type: 'number', default: 10, min: 1, step: 1 },
    { key: 'data_buffer', label: '数据缓冲区', type: 'number', default: 10, min: 1, step: 1 },
    { key: 'printlog', label: '打印日志', type: 'boolean', default: false }
  ],
  legacy_climax_limitdown: [
    { key: 'threshold', label: '阈值', type: 'number', default: 10, min: 1, step: 1 },
    { key: 'hold_bars', label: '持有周期', type: 'number', default: 10, min: 1, step: 1 },
    { key: 'limit_down_pct', label: '跌停百分比', type: 'number', default: -5, min: -10, step: 1 },
    { key: 'vol_ratio_max', label: '最大成交量比率', type: 'number', default: 3.0, min: 1, step: 0.1 },
    { key: 'printlog', label: '打印日志', type: 'boolean', default: false }
  ],
  legacy_enter: [
    { key: 'threshold', label: '阈值', type: 'number', default: 60, min: 1, step: 1 },
    { key: 'hold_bars', label: '持有周期', type: 'number', default: 10, min: 1, step: 1 },
  ],
  legacy_keep_increasing: [
    { key: 'threshold', label: '阈值', type: 'number', default: 30, min: 1, step: 1 },
    { key: 'hold_bars', label: '持有周期', type: 'number', default: 10, min: 1, step: 1 },
  ],
  legacy_low_atr: [
    { key: 'threshold', label: '阈值', type: 'number', default: 10, min: 1, step: 1 },
    { key: 'hold_bars', label: '持有周期', type: 'number', default: 15, min: 1, step: 1 },
  ],
  legacy_low_backtrace: [
    { key: 'threshold', label: '阈值', type: 'number', default: 60, min: 1, step: 1 },
    { key: 'hold_bars', label: '持有周期', type: 'number', default: 15, min: 1, step: 1 },
  ],
  legacy_turtle_trade: [
    { key: 'threshold', label: '阈值', type: 'number', default: 60, min: 1, step: 1 },
    { key: 'hold_bars', label: '持有周期', type: 'number', default: 10, min: 1, step: 1 },
  ],
}

const currentParamSchema = computed(() => builtinParamSchemas[backtestForm.strategy_name] || [])

const resetBuiltinParams = (strategyName) => {
  // 清空旧参数
  Object.keys(builtinParameters).forEach((k) => delete builtinParameters[k])
  const schema = builtinParamSchemas[strategyName]
  if (schema && schema.length > 0) {
    schema.forEach((field) => {
      builtinParameters[field.key] = field.default
    })
    builtinParamsJson.value = JSON.stringify(builtinParameters, null, 2)
  } else {
    builtinParamsJson.value = '{}'
  }
}

const fetchBuiltinStrategies = async () => {
  loadingBuiltin.value = true
  try {
    const result = await getBuiltinStrategies()
    if (result.success) {
      builtinStrategies.value = result.data?.data?.items || result.data?.items || []
      
      if (!backtestForm.strategy_name && builtinStrategies.value.length > 0) {
        backtestForm.strategy_name = builtinStrategies.value[0].name
      }
      if (backtestForm.strategy_name) {
        resetBuiltinParams(backtestForm.strategy_name)
      }
    } else {
      error.value = result.message || '获取内置回测模型失败'
    }
  } catch (err) {
    error.value = err.message || '获取内置回测模型失败'
  } finally {
    loadingBuiltin.value = false
  }
}

// 加载已保存的回测模型列表
const loadSavedStrategies = async () => {
  loadingSavedStrategies.value = true
  try {
    const result = await getStrategies({ limit: 100, offset: 0 })
    if (result.success) {
      const data = result.data?.data || result.data || {}
      savedStrategies.value = data.strategies || data.items || []
    } else {
      error.value = `加载回测模型列表失败: ${result.message}`
    }
  } catch (err) {
    error.value = `加载回测模型列表失败: ${err.message}`
  } finally {
    loadingSavedStrategies.value = false
  }
}

// 获取选中回测模型的代码
const loadStrategyCode = async (strategyId) => {
  if (!strategyId) {
    backtestForm.strategy_code = null
    return
  }
  
  try {
    const result = await getStrategy(strategyId)
    if (result.success) {
      const data = result.data?.data || result.data || {}
      backtestForm.strategy_code = data.code
    } else {
      error.value = `获取回测模型代码失败: ${result.message}`
    }
  } catch (err) {
    error.value = `获取回测模型代码失败: ${err.message}`
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
  
  if (backtestForm.strategy_mode === 'saved' && !backtestForm.strategy_id) {
    error.value = '请选择一个回测模型'
    return
  }
  
  if (backtestForm.strategy_mode === 'saved' && !backtestForm.strategy_code) {
    error.value = '回测模型代码加载失败，请重新选择'
    return
  }
  
  if (backtestForm.strategy_mode === 'builtin' && !backtestForm.strategy_name) {
    error.value = '请选择内置回测模型'
    return
  }
  
  runningBacktest.value = true
  error.value = ''
  backtestResult.value = null
  pendingTaskId.value = null
  taskStatus.value = null
  
  try {
    // 准备回测数据
    // 前端使用 'saved' 模式，但后端 API 只接受 'custom' 或 'builtin'
    // 需要将 'saved' 映射为 'custom'
    const backtestPayload = {
      stock_code: backtestForm.stock_code,
      start_date: backtestForm.start_date,
      end_date: backtestForm.end_date,
      strategy_mode: backtestForm.strategy_mode === 'saved' ? 'custom' : backtestForm.strategy_mode,
      initial_cash: backtestForm.initial_cash,
      commission: backtestForm.commission,
      slippage: backtestForm.slippage,
      enable_ai_review: true
    }
    
    if (backtestForm.strategy_mode === 'saved') {
      backtestPayload.strategy_code = backtestForm.strategy_code
      backtestPayload.strategy_id = backtestForm.strategy_id
    } else {
      backtestPayload.strategy_name = backtestForm.strategy_name
      const schema = currentParamSchema.value
      if (schema.length > 0) {
        backtestPayload.parameters = { ...builtinParameters }
      } else {
        try {
          backtestPayload.parameters = builtinParamsJson.value ? JSON.parse(builtinParamsJson.value) : {}
        } catch (parseErr) {
          throw new Error(`参数格式错误，请检查 JSON: ${parseErr.message}`)
        }
      }
    }
    
    // 无论是 sync 还是 async，都使用 runAsyncBacktest (提交即返回ID)
    // sync 模式只是前端等待逻辑不同
    if (backtestMode.value === 'sync') {
      await runSyncBacktest(backtestPayload)
    } else {
      await runAsyncBacktest(backtestPayload)
    }
  } catch (err) {
    error.value = `回测失败: ${err.message}`
    runningBacktest.value = false
  }
}

// 同步回测模式 (实际上是提交任务后前台轮询)
const runSyncBacktest = async (payload) => {
  try {
    const submitResult = await runBacktestService(payload)
    
    if (!submitResult.success) {
      throw new Error(submitResult.message || '回测提交失败')
    }
    
    // 兼容后端返回结构：data 可能在 submitResult.data.data 或 submitResult.data 中
    const data = submitResult.data?.data || submitResult.data
    const backtestId = data?.backtest_id
    
    if (!backtestId) {
       throw new Error('未获取到 backtest_id')
    }

    // 使用指数退避回测模型进行轮询
    let retryCount = 0
    const maxRetries = 60 // 最多等待60次
    const baseDelay = 1000 // 基础延迟1秒
    const maxDelay = 10000 // 最大延迟10秒
    
    while (retryCount < maxRetries) {
      await new Promise(resolve => {
        // 指数退避延迟
        const delay = Math.min(baseDelay * Math.pow(1.1, retryCount), maxDelay)
        setTimeout(resolve, delay)
      })
      
      const resultResponse = await getBacktestResult(backtestId)
      if (!resultResponse.success) {
          // 网络错误等，继续重试
          console.warn('获取状态失败，重试中...')
          retryCount++
          continue
      }
      
      const resData = resultResponse.data?.data || resultResponse.data
      const status = resData?.status
      
      if (status === 'success') {
        backtestResult.value = resData
        // 刷新历史记录
        fetchHistoryRecords()
        break
      } else if (status === 'failed') {
         throw new Error(resData?.message || '回测失败')
      }
      // pending 或 running 继续等待
      
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
    const submitResult = await runBacktestAsyncService(payload)
    
    if (!submitResult.success) {
      throw new Error(submitResult.message || '异步回测提交失败')
    }
    
    const data = submitResult.data?.data || submitResult.data
    pendingTaskId.value = data?.backtest_id // 后端返回的是 backtest_id
    taskStatus.value = 'submitted'
    
    // 显示成功消息
    error.value = `异步任务已提交！任务ID: ${pendingTaskId.value}。可在历史记录中查看进度。`

    // 启动非阻塞轮询
    startAsyncPolling(pendingTaskId.value);

  } finally {
    runningBacktest.value = false
  }
}

// 异步轮询辅助函数
const startAsyncPolling = async (backtestId) => {
    let retryCount = 0;
    const maxRetries = 60; // 轮询上限
    
    const poll = async () => {
        if (!pendingTaskId.value || pendingTaskId.value !== backtestId) return; // 任务ID变了或被清空则停止
        if (retryCount >= maxRetries) return;

        try {
            const result = await checkAsyncTaskStatus(backtestId);
            const status = result?.status;
            
            if (status === 'success' || status === 'failed') {
                return; // 结束轮询
            }
        } catch (e) {
            console.error(e);
        }
        
        retryCount++;
        setTimeout(poll, 2000); // 每2秒轮询一次
    };
    
    setTimeout(poll, 1000);
}


// 检查异步任务状态 (此处 taskId 实为 backtestId)
const checkAsyncTaskStatus = async (taskId) => {
  try {
    const resultResponse = await getBacktestResult(taskId)
    if (!resultResponse.success) {
      throw new Error(resultResponse.message || '检查任务状态失败')
    }
    
    const result = resultResponse.data?.data || resultResponse.data
    if (result) {
      // 映射后端 status 到前端展示用的 taskStatus
      // 后端: pending, running, success, failed
      // 前端: submitted, processing, completed, failed
      
      const backendStatus = result.status;
      if (backendStatus === 'success') {
          taskStatus.value = 'completed';
          backtestResult.value = result;
          // 任务完成，清除 pending ID (或者保留让用户手动清除? 需求说成功后清空 pending id, 但为了让用户看到"已完成"状态，可以暂留，或者依靠 backtestResult 显示结果)
          // 根据需求：成功后自动展示结果并清空 pending id
          // 但为了显示上面的 "✅ 任务已完成！", 我们需要在 taskStatus 为 completed 时保留一会儿? 
          // 实际上 UI 逻辑是: v-if="pendingTaskId" 显示状态卡片。 v-if="backtestResult" 显示结果卡片。
          // 如果清空 pendingTaskId，状态卡片会消失。
          // 我们保留 pendingTaskId，让用户手动刷新也行，或者就在这里保持。
          // 需求说 "成功后自动展示结果并清空 pending id"。
          // 那就清空。
          pendingTaskId.value = null; 
          fetchHistoryRecords(); // 刷新历史
      } else if (backendStatus === 'failed') {
          taskStatus.value = 'failed';
          error.value = `任务失败: ${result.message}`
      } else if (backendStatus === 'running') {
          taskStatus.value = 'processing';
      } else {
          taskStatus.value = 'submitted';
      }
    }
    
    return result
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
    const result = await getBacktestList({
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value
    })
    
    // 兼容后端两层封装: handleRequest返回 {success, data: axiosResponse}
    // axiosResponse.data 才是 {code, message, data: {total, items}}
    // 或者直接 data: {total, items} 取决于 backend
    const payload = result.data?.data || result.data;
    
    if (result.success && payload) {
      const items = payload.items || [];
      // 映射字段以适配表格
      historyRecords.value = items.map(item => {
          const metrics = item.metrics || {};
          const params = item.params || {};
          let strategyType = '未知';
          if (params.strategy_mode === 'builtin') {
              strategyType = `builtin: ${params.strategy_name || ''}`;
          } else if (params.strategy_mode === 'custom') {
              strategyType = 'custom';
          }

          return {
              id: item.backtest_id,
              stock_code: item.stock_code,
              start_date: item.start_date,
              end_date: item.end_date,
              strategy_type: strategyType,
              annual_return: metrics.annual_return || 0,
              sharpe_ratio: metrics.sharpe_ratio || 0,
              max_drawdown: metrics.max_drawdown || 0
          };
      });
      
    } else {
      error.value = `获取历史记录失败: ${result.message}`
      historyRecords.value = [];
    }
  } catch (err) {
    error.value = `获取历史记录失败: ${err.message}`
    console.error(err)
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
  // 跳转到详情页面
  router.push({ name: 'BacktestDetail', params: { id: String(backtestId) } })
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

onMounted(async () => {
  fetchBuiltinStrategies()
  
  // 先加载已保存的回测模型列表
  await loadSavedStrategies()
  
  // 检查 URL 参数，自动选择回测模型
  const strategyId = route.query.strategy
  if (strategyId) {
    // 切换到已保存回测模型模式
    backtestForm.strategy_mode = 'saved'
    // 设置回测模型 ID（会触发 watch 自动加载代码）
    backtestForm.strategy_id = strategyId
  }
  
  fetchHistoryRecords()
})

watch(() => backtestForm.strategy_name, (newVal) => {
  if (newVal) {
    resetBuiltinParams(newVal)
  }
})

// 监听回测模型选择变化，自动加载回测模型代码
watch(() => backtestForm.strategy_id, (newId) => {
  if (newId && backtestForm.strategy_mode === 'saved') {
    loadStrategyCode(newId)
  }
})
</script>

<style scoped>
.risk-banner {
  background: #fff3e6;
  border-bottom: 1px solid #ffb380;
  padding: 10px 20px;
}

.risk-banner__main {
  max-width: 1200px;
  margin: 0 auto;
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
  margin-bottom: 8px;
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

.param-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 10px;
}

.param-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 10px;
}

.param-label {
  font-weight: bold;
  color: #333;
}

.param-tip {
  background: #f5f5f5;
  border: 1px dashed #ddd;
  padding: 10px 12px;
  border-radius: 4px;
  color: #666;
  margin-top: 6px;
}

.param-json-wrapper {
  margin-top: 10px;
}

.param-json {
  font-family: monospace;
}

.checkbox-inline {
  display: inline-flex;
  align-items: center;
  gap: 6px;
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

.info-text {
  text-align: center;
  padding: 15px;
  color: #999;
  font-size: 0.95rem;
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