<template>
  <div class="factor-detail-page">
    <div class="container">
      <!-- 页面导航 -->
      <div class="page-nav">
        <router-link to="/factors" class="back-btn">返回列表</router-link>
        <h1 class="page-title">模拟参数详情</h1>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-indicator">
        <p>正在加载模拟参数详情...</p>
      </div>

      <!-- 错误信息 -->
      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <!-- 模拟参数详情内容 -->
      <div v-if="!loading && factor" class="factor-detail-content">
        <div class="card factor-basic-info">
          <h2 class="section-title">{{ factor.name }}</h2>
          <div class="factor-meta">
            <div class="meta-item">
              <span class="meta-label">模拟参数ID:</span>
              <span class="meta-value">{{ factor.id }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">模拟参数代码:</span>
              <code class="meta-value code">{{ factor.code }}</code>
            </div>
            <div class="meta-item">
              <span class="meta-label">模拟参数类别:</span>
              <span :class="['meta-value', getCategoryClass(factor.category)]">
                {{ getCategoryText(factor.category) }}
              </span>
            </div>
            <div class="meta-item">
              <span class="meta-label">创建时间:</span>
              <span class="meta-value">{{ formatDate(factor.created_at) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">更新时间:</span>
              <span class="meta-value">{{ formatDate(factor.updated_at) }}</span>
            </div>
          </div>
          <div class="factor-description">
            <h3>模拟参数描述</h3>
            <p>{{ factor.description || '暂无描述' }}</p>
          </div>
        </div>

        <!-- 模拟参数计算区域 -->
        <div class="card calculation-section">
          <div class="section-header">
            <h2 class="section-title">模拟参数计算</h2>
            <button 
              class="btn-primary"
              @click="runCalculation"
              :disabled="calculating"
            >
              {{ calculating ? '计算中...' : '运行计算' }}
            </button>
          </div>

          <!-- 计算参数设置 -->
          <div class="calculation-params">
            <h3>计算参数</h3>
            <div class="param-row">
              <div class="param-group">
                <label for="start-date">开始日期:</label>
                <input 
                  id="start-date"
                  v-model="calculationParams.startDate"
                  type="date"
                  class="param-input"
                />
              </div>
              <div class="param-group">
                <label for="end-date">结束日期:</label>
                <input 
                  id="end-date"
                  v-model="calculationParams.endDate"
                  type="date"
                  class="param-input"
                />
              </div>
              <div class="param-group">
                <label for="symbol">股票代码:</label>
                <input 
                  id="symbol"
                  v-model="calculationParams.symbol"
                  type="text"
                  placeholder="如：000001.SZ"
                  class="param-input"
                />
              </div>
            </div>
          </div>

          <!-- 计算结果图表 -->
          <div v-if="calculationResult" class="calculation-result">
            <h3>计算结果</h3>
            <div class="result-stats">
              <div class="stat-item">
                <span class="stat-label">计算耗时:</span>
                <span class="stat-value">{{ calculationResult.duration }}ms</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">数据点数:</span>
                <span class="stat-value">{{ calculationResult.dataPoints }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">平均值:</span>
                <span class="stat-value">{{ calculationResult.stats?.mean?.toFixed(4) }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">标准差:</span>
                <span class="stat-value">{{ calculationResult.stats?.std?.toFixed(4) }}</span>
              </div>
            </div>

            <!-- 图表容器 -->
            <div class="chart-container">
              <div class="chart-placeholder">
                <!-- 这里可以集成ECharts等图表库 -->
                <div class="chart-mockup">
                  <div class="chart-title">模拟参数时间序列图</div>
                  <div class="mockup-graph">
                    <div v-for="(point, index) in mockData" 
                         :key="index" 
                         class="graph-bar"
                         :style="{ height: point.height + '%' }"
                         :title="`值: ${point.value}, 日期: ${point.date}`">
                    </div>
                  </div>
                  <div class="chart-x-axis">
                    <span>开始日期</span>
                    <span>结束日期</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 计算结果表格 -->
          <div v-if="calculationResult && calculationResult.data" class="result-table">
            <h3>详细数据</h3>
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>日期</th>
                    <th>模拟参数值</th>
                    <th>涨跌幅</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in tableData" :key="index">
                    <td>{{ formatTableDate(item.date) }}</td>
                    <td :class="getValueClass(item.value)">{{ item.value.toFixed(4) }}</td>
                    <td :class="getChangeClass(item.change)">
                      {{ item.change !== null ? (item.change * 100).toFixed(2) + '%' : 'N/A' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-if="calculationResult.data.length > 10" class="table-footer">
              <p>显示前10条数据，完整数据共{{ calculationResult.data.length }}条</p>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <router-link 
            v-if="!isBuiltinFactor(factor.id)"
            :to="`/factors/${factor.id}/edit`" 
            class="btn-edit"
          >
            编辑模拟参数
          </router-link>
          <span v-else class="btn-edit disabled" title="内置模拟参数不可编辑">
            编辑模拟参数
          </span>
          <button 
            v-if="!isBuiltinFactor(factor.id)"
            @click="deleteFactor" 
            class="btn-delete"
          >
            删除模拟参数
          </button>
          <span v-else class="btn-delete disabled" title="内置模拟参数不可删除">
            删除模拟参数
          </span>
          <router-link to="/factors" class="btn-secondary">
            返回列表
          </router-link>
        </div>
      </div>

      <!-- 模拟参数不存在 -->
      <div v-if="!loading && !factor" class="not-found">
        <div class="not-found-icon">🔍</div>
        <h3>模拟参数不存在</h3>
        <p>您访问的模拟参数不存在或已被删除。</p>
        <router-link to="/factors" class="btn-primary">
          返回模拟参数列表
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useFactorStore } from '@/stores/factor'

const route = useRoute()
const router = useRouter()
const factorStore = useFactorStore()

// 响应式数据
const factor = ref(null)
const loading = ref(false)
const error = ref('')
const calculating = ref(false)
const calculationResult = ref(null)

// 计算参数
const calculationParams = ref({
  startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30天前
  endDate: new Date().toISOString().split('T')[0], // 今天
  symbol: '000001.SZ'
})

// 模拟数据用于图表展示
const mockData = computed(() => {
  if (!calculationResult.value?.data) return []
  
  return calculationResult.value.data.slice(0, 20).map((item, index) => ({
    value: item.value,
    date: formatTableDate(item.date),
    height: Math.min(Math.max((item.value + 2) * 20, 10), 100) // 模拟高度
  }))
})

// 表格数据（显示前10条）
const tableData = computed(() => {
  if (!calculationResult.value?.data) return []
  return calculationResult.value.data.slice(0, 10)
})

// 获取模拟参数详情
const fetchFactor = async () => {
  loading.value = true
  error.value = ''
  
  try {
    await factorStore.fetchFactor(route.params.id)
    
    if (factorStore.error) {
      error.value = factorStore.error
    } else {
      factor.value = factorStore.currentFactor
    }
  } catch (err) {
    error.value = `获取模拟参数详情失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

// 运行模拟参数计算
const runCalculation = async () => {
  calculating.value = true
  error.value = ''
  
  try {
    // 构造符合后端 API 格式的请求参数
    const requestParams = {
      factor_id: route.params.id,
      symbol: calculationParams.value.symbol,
      start_date: calculationParams.value.startDate,
      end_date: calculationParams.value.endDate
    }
    
    const result = await factorStore.calculateFactorValue(
      route.params.id,
      requestParams
    )
    
    if (factorStore.error) {
      error.value = factorStore.error
    } else if (result) {
      // 处理返回的计算结果
      calculationResult.value = {
        duration: result.duration || 0,
        dataPoints: result.total_points || result.values?.length || 0,
        data: (result.values || []).map((item, index, arr) => ({
          date: item.date,
          value: item.value,
          change: index > 0 && arr[index - 1].value !== 0 
            ? (item.value - arr[index - 1].value) / Math.abs(arr[index - 1].value)
            : null
        })),
        stats: calculateStats(result.values || [])
      }
    }
  } catch (err) {
    error.value = `模拟参数计算失败: ${err.message}`
  } finally {
    calculating.value = false
  }
}

// 计算统计数据
const calculateStats = (values) => {
  if (!values || values.length === 0) return { mean: 0, std: 0, min: 0, max: 0 }
  
  const nums = values.map(v => v.value).filter(v => !isNaN(v))
  if (nums.length === 0) return { mean: 0, std: 0, min: 0, max: 0 }
  
  const mean = nums.reduce((a, b) => a + b, 0) / nums.length
  const variance = nums.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / nums.length
  const std = Math.sqrt(variance)
  
  return {
    mean,
    std,
    min: Math.min(...nums),
    max: Math.max(...nums)
  }
}

// 删除模拟参数
const deleteFactor = async () => {
  if (confirm('确定要删除这个模拟参数吗？此操作不可恢复。')) {
    try {
      await factorStore.removeFactor(route.params.id)
      
      if (factorStore.error) {
        error.value = factorStore.error
      } else {
        router.push('/factors')
      }
    } catch (err) {
      error.value = `删除模拟参数失败: ${err.message}`
    }
  }
}

// 辅助方法
const getCategoryClass = (category) => {
  return {
    'category-technical': category === 'technical',
    'category-fundamental': category === 'fundamental',
    'category-macro': category === 'macro'
  }
}

// 判断是否为内置模拟参数（不可编辑/删除）
const isBuiltinFactor = (factorId) => {
  return factorId && factorId.startsWith('builtin')
}

const getCategoryText = (category) => {
  const categoryMap = {
    'technical': '技术指标',
    'fundamental': '基本面模拟参数',
    'macro': '宏观模拟参数'
  }
  return categoryMap[category] || category
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

const formatTableDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  })
}

const getValueClass = (value) => {
  return value >= 0 ? 'positive' : 'negative'
}

const getChangeClass = (change) => {
  if (change === null) return 'neutral'
  return change >= 0 ? 'positive' : 'negative'
}

// 生命周期
onMounted(() => {
  fetchFactor()
})
</script>

<style scoped>
.factor-detail-page {
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
  gap: 20px;
  margin-bottom: 30px;
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

.card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #f0f0f0;
}

.loading-indicator {
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
  margin-bottom: 20px;
}

.factor-basic-info {
  padding: 25px;
}

.section-title {
  font-size: 24px;
  color: #fff;
  background: #ff7f00;
  padding: 4px 12px;
  border-radius: 3px;
  margin: 0 0 20px 0;
  display: inline-block;
  border-radius: 10px;
}

.factor-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.meta-label {
  font-weight: bold;
  color: #666;
  min-width: 80px;
}

.meta-value {
  color: #333;
}

.meta-value.code {
  font-family: monospace;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
}

.category-technical { color: #4caf50; }
.category-fundamental { color: #2196f3; }
.category-macro { color: #9c27b0; }

.factor-description h3 {
  margin-bottom: 10px;
  color: #333;
}

.factor-description p {
  line-height: 1.6;
  color: #666;
}

.calculation-section {
  padding: 25px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background-color: #ff7f00;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #e06f00;
}

.btn-primary:disabled {
  background-color: #ffa555;
  cursor: not-allowed;
}

.calculation-params {
  margin-bottom: 20px;
}

.calculation-params h3 {
  margin-bottom: 15px;
  color: #333;
}

.param-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.param-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.param-group label {
  font-weight: bold;
  color: #666;
}

.param-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.calculation-result h3 {
  margin-bottom: 15px;
  color: #333;
}

.result-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-weight: bold;
  color: #666;
}

.stat-value {
  color: #333;
  font-weight: bold;
}

.chart-container {
  margin: 20px 0;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 4px;
  border: 1px solid #e1e1e1;
}

.chart-placeholder {
  text-align: center;
  color: #666;
}

.chart-mockup {
  display: inline-block;
  text-align: center;
}

.chart-title {
  font-weight: bold;
  margin-bottom: 10px;
}

.mockup-graph {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  height: 200px;
  gap: 2px;
  padding: 20px 0;
}

.graph-bar {
  width: 8px;
  background: #ff7f00;
  border-radius: 2px;
  transition: height 0.3s;
  min-height: 5px;
}

.chart-x-axis {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #666;
}

.result-table {
  margin-top: 20px;
}

.table-container {
  overflow-x: auto;
  margin-bottom: 10px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.data-table th,
.data-table td {
  padding: 10px 15px;
  text-align: left;
  border-bottom: 1px solid #e1e1e1;
}

.data-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.data-table tr:hover {
  background-color: #f9f9f9;
}

.positive { color: #4caf50; }
.negative { color: #f44336; }
.neutral { color: #666; }

.table-footer {
  text-align: center;
  color: #666;
  font-size: 0.9rem;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
}

.btn-edit,
.btn-delete,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  text-decoration: none;
  transition: background-color 0.3s;
}

.btn-edit {
  background-color: #ff9800;
  color: white;
}

.btn-delete {
  background-color: #f44336;
  color: white;
}

.btn-secondary {
  background-color: #1e90ff;
  color: white;
}

.btn-edit:hover { background-color: #f57c00; }
.btn-delete:hover { background-color: #d32f2f; }
.btn-secondary:hover { background-color: #0077ea; }

/* 禁用状态的按钮样式 */
.btn-edit.disabled,
.btn-delete.disabled {
  background-color: #ccc;
  color: #888;
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-edit.disabled:hover,
.btn-delete.disabled:hover {
  background-color: #ccc;
}

.not-found {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.not-found-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.not-found h3 {
  margin-bottom: 10px;
  color: #333;
}

@media (max-width: 768px) {
  .container {
    width: 95%;
    padding: 0 10px;
  }
  
  .param-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .result-stats {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .meta-meta {
    grid-template-columns: 1fr;
  }
}
</style>