<template>
  <div class="factor-list-page">
    <div class="container">
      <!-- 页面导航 -->
      <div class="page-nav">
        <router-link to="/" class="back-btn">返回主页</router-link>
        <h1 class="page-title">因子管理</h1>
      </div>

      <!-- 搜索和筛选区域 -->
      <div class="search-filter-section card">
        <div class="search-row">
          <div class="search-input-group">
            <input 
              v-model="searchText" 
              type="text" 
              placeholder="搜索因子名称或代码..."
              class="search-input"
              @input="handleSearch"
            />
            <button class="search-btn">搜索</button>
          </div>
          <div class="filter-group">
            <label for="category-filter">类别筛选:</label>
            <select 
              id="category-filter" 
              v-model="categoryFilter" 
              class="filter-select"
              @change="handleFilter"
            >
              <option value="all">全部因子</option>
              <option value="technical">技术指标</option>
              <option value="fundamental">基本面因子</option>
              <option value="macro">宏观因子</option>
            </select>
          </div>
          <router-link to="/factors/create" class="btn-primary">
            <span class="create-icon">+</span>
            创建新因子
          </router-link>
        </div>
      </div>

      <!-- 因子列表表格 -->
      <div class="factor-table-section card">
        <div class="table-header">
          <h2 class="section-title">因子列表</h2>
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
          <p>正在加载因子列表...</p>
        </div>

        <!-- 错误信息 -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <!-- 因子表格 -->
        <div v-if="!loading && factors.length > 0" class="table-container">
          <table class="factor-table">
            <thead>
              <tr>
                <th>因子ID</th>
                <th>因子名称</th>
                <th>因子代码</th>
                <th>因子类别</th>
                <th>因子描述</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="factor in paginatedFactors" :key="factor.id">
                <td class="factor-id">{{ factor.id }}</td>
                <td class="factor-name">
                  <router-link :to="`/factors/${factor.id}`" class="name-link">
                    {{ factor.name }}
                  </router-link>
                </td>
                <td class="factor-code">
                  <code>{{ factor.code }}</code>
                </td>
                <td class="factor-category">
                  <span :class="getCategoryClass(factor.category)">
                    {{ getCategoryText(factor.category) }}
                  </span>
                </td>
                <td class="factor-description">
                  <span class="description-text">{{ factor.description }}</span>
                </td>
                <td class="factor-created">{{ formatDate(factor.created_at) }}</td>
                <td class="factor-actions">
                  <div class="action-buttons">
                    <router-link 
                      :to="`/factors/${factor.id}`" 
                      class="btn-view"
                      title="查看详情"
                    >
                      详情
                    </router-link>
                    <router-link 
                      :to="`/factors/${factor.id}/edit`" 
                      class="btn-edit"
                      title="编辑因子"
                    >
                      编辑
                    </router-link>
                    <button 
                      @click="deleteFactor(factor.id)" 
                      class="btn-delete"
                      title="删除因子"
                    >
                      删除
                    </button>
                    <router-link 
                      :to="`/factors/${factor.id}`" 
                      class="btn-calculate"
                      title="查看详情并进行计算"
                    >
                      计算
                    </router-link>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && factors.length === 0" class="empty-state">
          <div class="empty-icon">📊</div>
          <h3>暂无因子</h3>
          <p>您还没有创建任何因子，点击"创建新因子"开始创建您的第一个量化因子。</p>
          <router-link to="/factors/create" class="btn-primary">
            创建新因子
          </router-link>
        </div>

        <!-- 分页控件 -->
        <div v-if="factors.length > 0" class="pagination">
          <button 
            :disabled="currentPage === 1" 
            @click="changePage(currentPage - 1)"
            class="pagination-btn"
          >
            上一页
          </button>
          <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
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
import { useFactorStore } from '@/stores/factor'

const router = useRouter()
const factorStore = useFactorStore()

// 响应式数据
const searchText = ref('')
const categoryFilter = ref('all')
const factors = ref([])
const loading = ref(false)
const error = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 获取因子列表
const fetchFactors = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const response = await factorStore.fetchFactors({
      category: categoryFilter.value === 'all' ? null : categoryFilter.value,
      search: searchText.value.trim() || null
    })
    
    if (factorStore.error) {
      error.value = factorStore.error
    } else {
      factors.value = factorStore.factors || []
    }
  } catch (err) {
    error.value = `获取因子列表失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

// 计算属性
const filteredFactors = computed(() => {
  let filtered = factors.value
  
  // 类别筛选
  if (categoryFilter.value !== 'all') {
    filtered = filtered.filter(factor => factor.category === categoryFilter.value)
  }
  
  // 搜索筛选
  if (searchText.value.trim()) {
    const searchTerm = searchText.value.toLowerCase()
    filtered = filtered.filter(factor => 
      factor.name.toLowerCase().includes(searchTerm) ||
      factor.code.toLowerCase().includes(searchTerm) ||
      factor.description.toLowerCase().includes(searchTerm)
    )
  }
  
  return filtered
})

const totalPages = computed(() => 
  Math.ceil(filteredFactors.value.length / pageSize.value)
)

const paginatedFactors = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredFactors.value.slice(start, end)
})

// 方法
const handleSearch = () => {
  currentPage.value = 1
  fetchFactors()
}

const handleFilter = () => {
  currentPage.value = 1
  fetchFactors()
}

const refreshList = () => {
  fetchFactors()
}

const changePage = (page) => {
  currentPage.value = page
}

const deleteFactor = async (factorId) => {
  if (confirm('确定要删除这个因子吗？此操作不可恢复。')) {
    try {
      loading.value = true
      await factorStore.removeFactor(factorId)
      
      if (factorStore.error) {
        error.value = factorStore.error
      } else {
        factors.value = factors.value.filter(factor => factor.id !== factorId)
        
        // 如果当前页没有数据，回到上一页
        if (paginatedFactors.value.length === 0 && currentPage.value > 1) {
          currentPage.value = currentPage.value - 1
        }
      }
    } catch (err) {
      error.value = `删除因子失败: ${err.message}`
    } finally {
      loading.value = false
    }
  }
}

const getCategoryClass = (category) => {
  return {
    'category-technical': category === 'technical',
    'category-fundamental': category === 'fundamental',
    'category-macro': category === 'macro'
  }
}

const getCategoryText = (category) => {
  const categoryMap = {
    'technical': '技术指标',
    'fundamental': '基本面因子',
    'macro': '宏观因子'
  }
  return categoryMap[category] || category
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
  fetchFactors()
})
</script>

<style scoped>
.factor-list-page {
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

.factor-table-section {
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

.factor-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.factor-table th,
.factor-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e1e1e1;
}

.factor-table th {
  background-color: #f5f5f5;
  font-weight: bold;
  color: #333;
  position: sticky;
  top: 0;
}

.factor-table tr:hover {
  background-color: #f9f9f9;
}

.factor-id {
  font-family: monospace;
  color: #666;
}

.factor-name .name-link {
  color: #ff7f00;
  text-decoration: none;
  font-weight: bold;
}

.factor-name .name-link:hover {
  text-decoration: underline;
}

.factor-code {
  font-family: monospace;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 0.9rem;
}

.factor-description .description-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  max-width: 200px;
}

.category-technical {
  color: #4caf50;
  font-weight: bold;
}

.category-fundamental {
  color: #2196f3;
  font-weight: bold;
}

.category-macro {
  color: #9c27b0;
  font-weight: bold;
}

.factor-actions {
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
.action-buttons .btn-calculate {
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

.btn-calculate {
  background-color: #2196f3;
  color: white;
}

.btn-view:hover { background-color: #45a049; }
.btn-edit:hover { background-color: #f57c00; }
.btn-delete:hover { background-color: #d32f2f; }
.btn-calculate:hover { background-color: #1976d2; }

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
  
  .factor-table th,
  .factor-table td {
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
  .action-buttons .btn-calculate {
    padding: 3px 6px;
    font-size: 0.8rem;
  }
}
</style>