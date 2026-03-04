<template>
  <div class="news-detail-page">
    <!-- 顶部面包屑导航 -->
    <div class="breadcrumb">
      <div class="container">
        <router-link to="/">首页</router-link> > 
        <router-link to="/finance-channel">宏微观数据</router-link> > 
        <span>{{ newsDetail.title }}</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="container">
        <div class="news-detail-content">
          <!-- 左侧新闻详情 -->
          <div class="news-detail-main">
            <!-- 新闻标题区域 -->
            <div class="news-header">
              <h1 class="news-title">{{ newsDetail.title }}</h1>
              <div class="news-meta">
                <span class="publish-date">
                  <i class="icon-time"></i>{{ newsDetail.publishTime }}
                </span>
                <span v-if="newsDetail.source" class="news-source">
                  <i class="icon-source"></i>{{ newsDetail.source }}
                </span>
                <span v-if="newsDetail.viewCount !== null" class="view-count">
                  <i class="icon-view"></i>{{ newsDetail.viewCount }} 阅读
                </span>
              </div>
            </div>

            <!-- 新闻正文内容 -->
            <article class="news-body">
              <div v-html="displayContent" class="news-content"></div>
              
              <!-- 图片展示 -->
              <div class="news-images" v-if="newsDetail.images && newsDetail.images.length">
                <img 
                  v-for="(image, index) in newsDetail.images" 
                  :key="index" 
                  :src="image.url" 
                  :alt="image.alt" 
                  class="news-image"
                />
              </div>
            </article>

            <!-- 互动功能区 -->
            <div class="interaction-section">
              <div class="interaction-buttons">
                <button 
                  :class="['like-btn', { active: isLiked }]" 
                  @click="handleLike"
                >
                  <i class="icon-like"></i>
                  <span>{{ newsDetail.likeCount }}</span>
                </button>
                <button 
                  :class="['collect-btn', { active: isCollected }]" 
                  @click="handleCollect"
                >
                  <i class="icon-collect"></i>
                  <span>收藏</span>
                </button>
                <button class="share-btn" @click="handleShare">
                  <i class="icon-share"></i>
                  <span>分享</span>
                </button>
              </div>
            </div>

          </div>

          <!-- 右侧边栏 -->
          <div class="news-sidebar"></div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import DOMPurify from 'dompurify'
import { useRoute, useRouter } from 'vue-router'
import { getHeadlineDetail } from '@/services/newsService'

const route = useRoute()
const router = useRouter()

// 新闻详情数据
const newsDetail = ref({
  title: '',
  publishTime: '',
  source: '',
  viewCount: null,
  likeCount: 0,
  summary: '',
  content: '',
  images: []
})

// 互动状态
const isLiked = ref(false)
const isCollected = ref(false)

// 方法
const handleLike = () => {
  isLiked.value = !isLiked.value
  if (isLiked.value) {
    newsDetail.value.likeCount++
  } else {
    newsDetail.value.likeCount--
  }
}

const handleCollect = () => {
  isCollected.value = !isCollected.value
}

const handleShare = () => {
  if (navigator.share) {
    navigator.share({
      title: newsDetail.value.title,
      text: (newsDetail.value.summary || '').substring(0, 100) + '...',
      url: window.location.href
    })
  } else {
    navigator.clipboard.writeText(window.location.href)
    alert('链接已复制到剪贴板')
  }
}

const goToNewsDetail = (id) => {
  router.push(`/news-detail/${id}`)
}

// 根据ID加载新闻详情
const loadNewsDetail = async (id) => {
  const newsId = parseInt(id)
  if (!newsId) {
    return
  }
  try {
    const response = await getHeadlineDetail(newsId)
    const data = response?.data || response
    newsDetail.value = {
      title: data?.title || '',
      publishTime: data?.date || '',
      source: data?.source || '财经头条',
      viewCount: data?.viewCount ?? null,
      likeCount: data?.likeCount ?? 0,
      summary: data?.summary || '',
      content: data?.content || '',
      images: data?.images || []
    }
  } catch (err) {
    console.error('获取新闻详情失败:', err)
    alert(err.message || '获取新闻详情失败')
  }
}

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  loadNewsDetail(newId)
})

// 生命周期
onMounted(() => {
  // 从路由参数获取新闻ID并加载详情
  loadNewsDetail(route.params.id)
})

const sanitizeHtml = (html) => DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })

const displayContent = computed(() => {
  if (newsDetail.value.content) {
    return sanitizeHtml(newsDetail.value.content)
  }
  if (newsDetail.value.summary) {
    return sanitizeHtml(`<p>${newsDetail.value.summary}</p>`)
  }
  return sanitizeHtml('<p>暂无正文内容</p>')
})
</script>

<style scoped>
.news-detail-page {
  min-height: 100vh;
  background-color: #fff8f0;
}

.breadcrumb {
  background: #fff;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.breadcrumb a {
  color: #ff7f00;
}

.breadcrumb span {
  color: #666;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

.news-detail-content {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.news-detail-main {
  flex: 3;
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.news-header {
  border-bottom: 2px solid #ffebd8;
  padding-bottom: 20px;
  margin-bottom: 25px;
}

.news-title {
  font-size: 28px;
  color: #333;
  line-height: 1.4;
  margin-bottom: 15px;
  font-weight: bold;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  color: #999;
  font-size: 14px;
}

.news-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.news-body {
  margin-bottom: 30px;
}

.news-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
}

.news-content p {
  margin-bottom: 20px;
}

.news-images {
  margin: 25px 0;
}

.news-image {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.interaction-section {
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
  padding: 20px 0;
  margin: 25px 0;
}

.interaction-buttons {
  display: flex;
  gap: 15px;
}

.interaction-buttons button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.interaction-buttons button:hover {
  border-color: #ff7f00;
  color: #ff7f00;
}

.interaction-buttons button.active {
  background: #ff7f00;
  color: #fff;
  border-color: #ff7f00;
}


/* 响应式设计 */
@media (max-width: 768px) {
  .news-detail-content {
    flex-direction: column;
  }
  
  .news-title {
    font-size: 22px;
  }
  
  .news-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .interaction-buttons {
    flex-wrap: wrap;
  }
  
}

/* 图标样式 */
.icon-time::before { content: '🕒 '; }
.icon-source::before { content: '📰 '; }
.icon-view::before { content: '👁️ '; }
.icon-like::before { content: '👍 '; }
.icon-collect::before { content: '⭐ '; }
.icon-share::before { content: '📤 '; }
</style>