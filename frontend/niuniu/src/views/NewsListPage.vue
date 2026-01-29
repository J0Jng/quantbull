<template>
  <div class="news-list-page">
    <!-- 顶部面包屑导航 -->
    <div class="breadcrumb">
      <div class="container">
        <router-link to="/">首页</router-link> > <span>财经头条</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">财经头条</h2>
          <div v-if="isAdmin" class="admin-actions">
            <button @click="handleGenerateDaily" class="btn-generate" :disabled="generating">
              {{ generating ? 'AI 生成中...' : '🤖 AI生成今日头条' }}
            </button>
          </div>
        </div>
        <div class="news-content">
          <div class="news-list">
            <!-- 加载状态 -->
            <div v-if="loading" class="loading-state">
              <div class="loading-spinner"></div>
              <p>加载中...</p>
            </div>

            <!-- 错误状态 -->
            <div v-else-if="error" class="error-state">
              <p>{{ error }}</p>
              <button @click="fetchHeadlines" class="retry-btn">重试</button>
            </div>

            <!-- 空数据状态 -->
            <div v-else-if="newsItems.length === 0" class="empty-state">
              <p>暂无新闻数据</p>
            </div>

            <!-- 新闻列表 -->
            <template v-else>
              <div 
                class="news-item" 
                v-for="(item, index) in newsItems" 
                :key="item.id"
                @click="goToNewsDetail(item.id)"
              >
                <div class="news-item-header">
                  <h3>{{ item.title }}</h3>
                  <div class="news-item-actions">
                    <span class="news-date">{{ item.date }}</span>
                  </div>
                </div>
                <div class="news-item-summary">
                  {{ item.summary }}
                </div>
                <div class="news-item-tags">
                  <span v-for="(tag, tagIndex) in item.tags" :key="tagIndex" class="news-tag">{{ tag }}</span>
                </div>
              </div>
              
              <!-- 分页 -->
              <div class="pagination" v-if="totalPages > 1">
                <a 
                  href="#" 
                  class="prev" 
                  :class="{ disabled: currentPage === 1 }"
                  @click.prevent="prevPage"
                >
                  上一页
                </a>
                
                <template v-for="page in pageNumbers" :key="page">
                  <a 
                    v-if="page !== '...'"
                    href="#" 
                    class="page-number" 
                    :class="{ active: page === currentPage }"
                    @click.prevent="goToPage(page)"
                  >
                    {{ page }}
                  </a>
                  <span v-else class="ellipsis">...</span>
                </template>
                
                <a 
                  href="#" 
                  class="next"
                  :class="{ disabled: currentPage === totalPages }"
                  @click.prevent="nextPage"
                >
                  下一页
                </a>
              </div>
            </template>
          </div>
        </div>
      </div>
    </main>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getHeadlines, getHotHeadlines, generateDailyHeadlines, getEastmoneyLatestNews } from '@/services/newsService'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { isAdmin, initAuth } = useAuth()

// 数据状态
const newsItems = ref([])
const hotNews = ref([])
const loading = ref(false)
const error = ref(null)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 管理状态
const generating = ref(false)

// 计算总页数
const totalPages = computed(() => {
  return Math.ceil(total.value / pageSize.value)
})

// 生成页码数组
const pageNumbers = computed(() => {
  const pages = []
  const maxVisible = 7 // 最多显示7个页码
  
  if (totalPages.value <= maxVisible) {
    // 如果总页数小于等于7，显示所有页码
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push(i)
    }
  } else {
    // 复杂分页逻辑：显示首页、末页和当前页附近的页码
    if (currentPage.value <= 3) {
      // 当前页在前面
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(totalPages.value)
    } else if (currentPage.value >= totalPages.value - 2) {
      // 当前页在后面
      pages.push(1)
      pages.push('...')
      for (let i = totalPages.value - 4; i <= totalPages.value; i++) {
        pages.push(i)
      }
    } else {
      // 当前页在中间
      pages.push(1)
      pages.push('...')
      for (let i = currentPage.value - 1; i <= currentPage.value + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(totalPages.value)
    }
  }
  
  return pages
})

// 获取财经头条列表
const fetchHeadlines = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('开始获取财经头条列表...')
    const response = await getHeadlines({
      page: currentPage.value,
      page_size: pageSize.value
    })
    
    console.log('API 响应:', response)
    console.log('响应数据类型:', typeof response)
    console.log('响应 items:', response?.items)
    console.log('响应 data:', response?.data)
    
    // 兼容不同的响应格式
    let items = []
    let totalCount = 0
    
    if (response) {
      // 情况1: 直接返回 { items, page, page_size, total }
      if (response.items) {
        items = response.items
        totalCount = response.total || 0
      }
      // 情况2: 包装在 data 中 { data: { items, page, page_size, total } }
      else if (response.data && response.data.items) {
        items = response.data.items
        totalCount = response.data.total || 0
      }
      // 情况3: 直接是数组
      else if (Array.isArray(response)) {
        items = response
        totalCount = response.length
      }
    }
    
    console.log('解析后的 items:', items)
    console.log('解析后的 total:', totalCount)
    
    newsItems.value = items
    total.value = totalCount
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (err) {
    console.error('获取财经头条失败:', err)
    console.error('错误详情:', JSON.stringify(err, null, 2))
    error.value = err.message || '加载新闻失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 获取热点聚焦列表
const fetchHotHeadlines = async () => {
  try {
    console.log('开始获取热点聚焦列表...')
    const response = await getHotHeadlines({ limit: 8 })
    console.log('热点 API 响应:', response)
    
    // 兼容不同的响应格式
    let items = []
    if (response) {
      if (response.items) {
        items = response.items
      } else if (response.data && response.data.items) {
        items = response.data.items
      } else if (Array.isArray(response)) {
        items = response
      }
    }
    
    console.log('解析后的热点 items:', items)
    hotNews.value = items
  } catch (err) {
    console.error('获取热点聚焦失败:', err)
    console.error('错误详情:', JSON.stringify(err, null, 2))
  }
}

// 跳转到详情页
const goToNewsDetail = (id) => {
  router.push(`/news-detail/${id}`)
}

// 跳转到热点新闻详情页
const goToHotNews = (id) => {
  router.push(`/news-detail/${id}`)
}

// AI 生成今日头条
const handleGenerateDaily = async () => {
  if (!confirm('确定要使用 AI 生成今日财经头条吗？\n\n将基于数据库中最新 10 条新闻生成，可能需要 30-60 秒。')) {
    return
  }
  
  generating.value = true
  
  try {
    console.log('开始拉取最新新闻...')
    await getEastmoneyLatestNews({
      limit: 50,
      refresh: true,
      save_to_db: true
    })

    console.log('开始生成今日头条...')
    const result = await generateDailyHeadlines({
      limit: 10,
      hours: 24,
      force: false
    })
    
    console.log('生成结果:', result)
    const data = result.data || result
    
    alert(`生成成功！\n\n创建了 ${data.created_count ?? 0} 条财经头条\n基于 ${data.source_news_count ?? 0} 条源新闻`)
    
    // 刷新列表
    currentPage.value = 1
    await fetchHeadlines()
    await fetchHotHeadlines()
  } catch (err) {
    console.error('生成失败:', err)
    alert(err.message || '生成失败，请稍后重试')
  } finally {
    generating.value = false
  }
}

// 分页操作
const goToPage = (page) => {
  if (page === '...' || page === currentPage.value || page < 1 || page > totalPages.value) {
    return
  }
  currentPage.value = page
  fetchHeadlines()
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchHeadlines()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchHeadlines()
  }
}

// 组件挂载时加载数据
onMounted(async () => {
  await initAuth()
  fetchHeadlines()
  fetchHotHeadlines()
})
</script>

<style scoped>
.breadcrumb {
  background: #fff;
  padding: 10px 0;
  font-size: 14px;
}

.breadcrumb a {
  color: #ff7f00;
}

.news-content {
  display: flex;
  gap: 20px;
  margin-top: 15px;
}

.news-list {
  flex: 3;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
  min-height: 500px;
}

.sidebar {
  flex: 1;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #ff7f00;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #f56c6c;
}

.retry-btn {
  margin-top: 15px;
  padding: 8px 20px;
  background: #ff7f00;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.retry-btn:hover {
  background: #e67300;
}

/* 空数据状态 */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #999;
}

.news-item {
  padding: 20px 0;
  border-bottom: 1px dashed #ddd;
  cursor: pointer;
  transition: all 0.3s ease;
}

.news-item:hover {
  background: #fff6ee;
  transform: translateX(5px);
}

.news-item:last-child {
  border-bottom: none;
}

.news-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.news-item-header h3 {
  font-size: 18px;
  color: #333;
  font-weight: bold;
}

.news-item-header h3:hover {
  color: #ff7f00;
}

.news-date {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
  margin-left: 15px;
}

.news-item-summary {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
}

.news-item-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.news-tag {
  font-size: 12px;
  background: #f5f5f5;
  color: #666;
  padding: 4px 8px;
  border-radius: 3px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
  gap: 10px;
  flex-wrap: wrap;
}

.pagination a,
.pagination .ellipsis {
  display: inline-block;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s;
}

.pagination .ellipsis {
  border: none;
  color: #999;
  cursor: default;
}

.pagination a:hover:not(.disabled) {
  background: #ff7f00;
  color: #fff;
  border-color: #ff7f00;
}

.pagination a.active {
  background: #ff7f00;
  color: #fff;
  border-color: #ff7f00;
}

.pagination a.disabled {
  color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.sidebar-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ff7f00;
}

.hot-news {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
  margin-bottom: 20px;
}

.hot-news ul li {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px dashed #eee;
}

.hot-news ul li:last-child {
  border-bottom: none;
}

.hot-index {
  display: inline-block;
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  background: #f5f5f5;
  border-radius: 3px;
  font-size: 12px;
  margin-right: 10px;
  flex-shrink: 0;
}

.hot-index.top-three {
  background: #ff7f00;
  color: #fff;
}

.hot-news a {
  font-size: 14px;
  color: #333;
  flex: 1;
}

.hot-news a:hover {
  color: #ff7f00;
}

/* 管理功能样式 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.admin-actions {
  display: flex;
  gap: 10px;
}

.btn-generate {
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
}

.btn-generate:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-generate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.news-item-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>