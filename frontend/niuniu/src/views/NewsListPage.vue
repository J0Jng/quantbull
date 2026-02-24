<template>
  <div class="news-list-page">
    <div class="breadcrumb">
      <div class="container">
        <router-link to="/">首页</router-link> > <span>财经资讯</span>
      </div>
    </div>

    <main class="main-content">
      <div class="container">
        <div v-if="newsLoading" class="loading-state">加载中...</div>
        <div v-else-if="newsError" class="error-state">{{ newsError }}</div>
        <div class="kuaixun-list" v-else>
          <div class="kuaixun-item" v-for="(item, i) in newsItems" :key="item.id || 'news'+i">
            <div class="kuaixun-time-col">
              <div class="kuaixun-time">{{ formatTime(item.time) }}</div>
              <div class="kuaixun-date">{{ formatDate(item.time) }}</div>
            </div>
            <div class="kuaixun-content">
              <div class="kuaixun-title">{{ item.title }}</div>
              <div class="kuaixun-summary">{{ item.summary }}</div>
              <div class="kuaixun-meta">
                <span class="meta-source">{{ item.source }}{{ item.author ? ' · ' + item.author : '' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getWeiboMediaNews } from '@/services/newsService'

const newsItems = ref([])
const newsLoading = ref(false)
const newsError = ref('')

function formatTime(timeStr) {
  if (!timeStr) return ''
  try {
    if (/^\d{2}:\d{2}/.test(timeStr) && timeStr.length === 5) return timeStr
    const d = new Date(timeStr)
    if (isNaN(d.getTime())) return timeStr
    return d.toTimeString().slice(0, 5)
  } catch (e) {
    return timeStr
  }
}

function formatDate(timeStr) {
  if (!timeStr) return ''
  try {
    const d = new Date(timeStr)
    if (isNaN(d.getTime())) return ''
    return `${d.getMonth() + 1}-${d.getDate()}`
  } catch (e) {
    return ''
  }
}

async function loadWeiboNews() {
  newsLoading.value = true
  newsError.value = ''

  try {
    const response = await getWeiboMediaNews({ limit: 20 })
    const payload = response?.data || response

    if (payload && payload.items && payload.items.length > 0) {
      newsItems.value = payload.items
    } else {
      newsError.value = '暂无新闻数据'
      newsItems.value = []
    }
  } catch (error) {
    console.error('加载微博新闻失败:', error)
    newsError.value = '加载失败'
    newsItems.value = []
  } finally {
    newsLoading.value = false
  }
}

onMounted(() => {
  loadWeiboNews()
})
</script>

<style scoped>
.breadcrumb {
  background: #fff;
  padding: 10px 0;
  font-size: 14px;
}

.breadcrumb a {
  color: #c83b3b;
}

.main-content {
  padding: 20px 0 40px;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  font-size: 20px;
  color: #2c3e50;
  margin: 10px 0 20px;
  padding-left: 12px;
  border-left: 4px solid #c83b3b;
  font-weight: 700;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 30px;
  color: #999;
}

.error-state {
  color: #f5222d;
}

.kuaixun-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  background: #fff;
  border-radius: 6px;
  padding: 10px 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.kuaixun-item {
  display: flex;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.kuaixun-item:last-child {
  border-bottom: none;
}

.kuaixun-time-col {
  width: 80px;
  flex-shrink: 0;
  text-align: right;
  padding-right: 15px;
  border-right: 1px solid #eee;
  margin-right: 15px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding-top: 2px;
}

.kuaixun-time {
  font-size: 16px;
  font-weight: bold;
  color: #c83b3b;
}

.kuaixun-date {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.kuaixun-content {
  flex: 1;
}

.kuaixun-title {
  font-size: 17px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
}

.kuaixun-summary {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 10px;
  text-align: justify;
}

.kuaixun-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #aaa;
}

@media (max-width: 768px) {
  .kuaixun-time-col {
    width: 60px;
    padding-right: 10px;
    margin-right: 10px;
  }

  .kuaixun-time {
    font-size: 14px;
  }
}
</style>