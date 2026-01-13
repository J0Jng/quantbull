<template>
  <div class="strategy-list-page">
    <div class="container">
      <!-- 页面导航 -->
      <div class="page-nav">
        <router-link to="/" class="back-btn">返回主页</router-link>
        <h1 class="page-title">策略管理</h1>
      </div>

      <!-- 搜索和筛选区域 -->
      <div class="search-filter-section card">
        <div class="search-row">
          <div class="search-input-group">
            <input 
              v-model="searchText" 
              type="text" 
              placeholder="搜索策略名称或描述..."
              class="search-input"
              @input="handleSearch"
              @keyup.enter="handleSearch"
            />
            <button class="search-btn" @click="handleSearch">搜索</button>
          </div>
          <div class="filter-group">
            <label for="status-filter">状态筛选:</label>
            <select 
              id="status-filter" 
              v-model="statusFilter" 
              class="filter-select"
              @change="handleFilter"
            >
              <option value="all">全部</option>
              <option value="draft">草稿</option>
              <option value="active">活跃</option>
              <option value="archived">已归档</option>
            </select>
          </div>
          <router-link to="/strategies/create" class="btn-primary">
            <span class="create-icon">+</span>
            创建新策略
          </router-link>
        </div>
      </div>

      <!-- 策略列表表格 -->
      <div class="strategy-table-section card">
        <div class="table-header">
          <h2 class="section-title">策略列表</h2>
          <div class="table-actions">
            <button 
              class="btn-secondary refresh-btn" 
              @click="refreshList"
              :disabled="loading"
            >
              {{ loading ? '加载中...' : '刷新' }}
            </button>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-indicator">
          <p>正在加载策略列表...</p>
        </div>

        <!-- 错误信息 -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- 策略表格 -->
        <div v-if="!loading && strategies.length > 0" class="table-container">
          <table class="strategy-table">
            <thead>
              <tr>
                <th>策略ID</th>
                <th>策略名称</th>
                <th>策略描述</th>
                <th>状态</th>
                <th>创建时间</th>
                <th>更新时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="strategy in strategies" :key="strategy.id">
                <td class="strategy-id">{{ strategy.id }}</td>
                <td class="strategy-name">
                  <router-link :to="`/strategies/${strategy.id}`" class="name-link">
                    {{ strategy.name }}
                  </router-link>
                </td>
                <td class="strategy-description">
                  <span class="description-text">{{ strategy.description }}</span>
                </td>
                <td class="strategy-status">
                  <span :class="getStatusClass(strategy.status)">
                    {{ getStatusText(strategy.status) }}
                  </span>
                </td>
                <td class="strategy-created">{{ formatDate(strategy.created_at) }}</td>
                <td class="strategy-updated">{{ formatDate(strategy.updated_at) }}</td>
                <td class="strategy-actions">
                  <div class="action-buttons">
                    
                    <router-link 
                      :to="`/strategies/${strategy.id}/edit`" 
                      class="btn-edit"
                      title="编辑策略"
                    >
                      编辑
                    </router-link>
                    <button 
                      @click="deleteStrategy(strategy.id)" 
                      class="btn-delete"
                      title="删除策略"
                      :disabled="strategy.status === 'active'"
                    >
                      删除
                    </button>
                    <router-link 
                      :to="`/quant-analysis?strategy=${strategy.id}`" 
                      class="btn-backtest"
                      title="运行回测"
                    >
                      回测
                    </router-link>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && strategies.length === 0" class="empty-state">
          <div class="empty-icon">📊</div>
          <h3>暂无策略</h3>
          <p>您还没有创建任何策略，点击"创建新策略"开始创建您的第一个量化策略。</p>
          <router-link to="/strategies/create" class="btn-primary">
            创建新策略
          </router-link>
        </div>

        <!-- 分页控件 -->
        <div v-if="totalCount > 0" class="pagination">
          <button 
            :disabled="currentPage === 1" 
            @click="changePage(currentPage - 1)"
            class="pagination-btn"
          >
            上一页
          </button>
          <span class="page-info">
            第 {{ currentPage }} 页，共 {{ totalPages }} 页 (共 {{ totalCount }} 条)
          </span>
          <button 
            :disabled="currentPage >= totalPages" 
            @click="changePage(currentPage + 1)"
            class="pagination-btn"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStrategies, deleteStrategy as deleteStrategyApi } from '@/services/strategyService'

const router = useRouter()

// 响应式数据
const searchText = ref('')
const statusFilter = ref('all')
const strategies = ref([])
const loading = ref(false)
const error = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
let searchDebounceTimer = null

// 获取策略列表（服务端分页 + 搜索）
const fetchStrategies = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const offset = (currentPage.value - 1) * pageSize.value
    const response = await getStrategies({
      status: statusFilter.value === 'all' ? null : statusFilter.value,
      search: searchText.value.trim() || null,
      limit: pageSize.value,
      offset: offset
    })
    
    if (response.success) {
      // 适配不同的返回格式
      const data = response.data?.data || response.data || {}
      strategies.value = data.strategies || data.items || []
      totalCount.value = data.total || 0
    } else {
      error.value = response.message || '获取策略列表失败'
      strategies.value = []
      totalCount.value = 0
    }
  } catch (err) {
    error.value = `获取策略列表失败: ${err.message}`
    strategies.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}

// 计算总页数
const totalPages = computed(() => 
  Math.ceil(totalCount.value / pageSize.value)
)

// 方法
const handleSearch = () => {
  // Debounce 搜索
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
  
  searchDebounceTimer = setTimeout(() => {
    currentPage.value = 1
    fetchStrategies()
  }, 300)
}

const handleFilter = () => {
  currentPage.value = 1
  fetchStrategies()
}

const refreshList = () => {
  fetchStrategies()
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchStrategies()
}

const deleteStrategy = async (strategyId) => {
  if (confirm('确定要删除这个策略吗？此操作不可恢复。')) {
    try {
      loading.value = true
      
      const response = await deleteStrategyApi(strategyId)
      
      if (response.success) {
        // 删除成功，重新获取当前页数据
        // 如果当前页没有数据了且不是第一页，回到上一页
        if (strategies.value.length === 1 && currentPage.value > 1) {
          currentPage.value = currentPage.value - 1
        }
        await fetchStrategies()
      } else {
        error.value = response.message || '删除策略失败'
      }
    } catch (err) {
      error.value = `删除策略失败: ${err.message}`
    } finally {
      loading.value = false
    }
  }
}

const getStatusClass = (status) => {
  return {
    'status-active': status === 'active',
    'status-inactive': status === 'archived',
    'status-draft': status === 'draft'
  }
}

const getStatusText = (status) => {
  const statusMap = {
    'active': '活跃',
    'draft': '草稿',
    'archived': '已归档'
  }
  return statusMap[status] || status
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 生命周期
onMounted(() => {
  fetchStrategies()
})
</script>

<style scoped>
.strategy-list-page {
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

.search-filter-section {
  padding: 15px 20px;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 20px;
  justify-content: space-between;
}

.search-input-group {
  display: flex;
  flex: 1;
  max-width: 400px;
}

.search-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 1rem;
}

.search-btn {
  padding: 10px 20px;
  background-color: #ff7f00;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-btn:hover {
  background-color: #e06f00;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background-color: #ff7f00;
  color: white;
  text-decoration: none;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #e06f00;
}

.create-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.strategy-table-section {
  padding: 15px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
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

.btn-secondary {
  padding: 8px 16px;
  background-color: #1e90ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #0077ea;
}

.btn-secondary:disabled {
  background-color: #87cefa;
  cursor: not-allowed;
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
}

.table-container {
  overflow-x: auto;
  margin-bottom: 20px;
}

.strategy-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.strategy-table th,
.strategy-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e1e1e1;
}

.strategy-table th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #333;
  position: sticky;
  top: 0;
}

.strategy-table tr:hover {
  background-color: #f9f9f9;
}

.strategy-id {
  font-family: monospace;
  color: #666;
}

.strategy-name .name-link {
  color: #ff7f00;
  text-decoration: none;
  font-weight: bold;
}

.strategy-name .name-link:hover {
  text-decoration: underline;
}

.strategy-description .description-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  max-width: 200px;
}

.status-active {
  color: #4caf50;
  font-weight: bold;
}

.status-inactive {
  color: #f44336;
  font-weight: bold;
}

.status-draft {
  color: #ff9800;
  font-weight: bold;
}

.strategy-actions {
  min-width: 200px;
}

.action-buttons {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.action-buttons .btn-view,
.action-buttons .btn-edit,
.action-buttons .btn-delete,
.action-buttons .btn-backtest {
  padding: 4px 8px;
  font-size: 0.85rem;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-view {
  background-color: #4caf50;
  color: white;
}

.btn-edit {
  background-color: #ff9800;
  color: white;
}

.btn-delete {
  background-color: #f44336;
  color: white;
}

.btn-delete:disabled {
  background-color: #ffcdd2;
  color: #666;
  cursor: not-allowed;
}

.btn-backtest {
  background-color: #2196f3;
  color: white;
}

.btn-view:hover { background-color: #45a049; }
.btn-edit:hover { background-color: #f57c00; }
.btn-delete:hover:not(:disabled) { background-color: #d32f2f; }
.btn-backtest:hover { background-color: #1976d2; }

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin-bottom: 10px;
  color: #333;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.pagination-btn {
  padding: 8px 16px;
  background-color: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #ff7f00;
  color: white;
  border-color: #ff7f00;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .container {
    width: 95%;
    padding: 0 10px;
  }
  
  .search-row {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .search-input-group {
    max-width: none;
  }
  
  .strategy-table th,
  .strategy-table td {
    padding: 8px;
    font-size: 0.85rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 3px;
  }
  
  .action-buttons .btn-view,
  .action-buttons .btn-edit,
  .action-buttons .btn-delete,
  .action-buttons .btn-backtest {
    padding: 3px 6px;
    font-size: 0.8rem;
  }
}
</style>