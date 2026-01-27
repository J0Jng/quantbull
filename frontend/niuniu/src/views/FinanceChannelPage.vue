<template>
  <div class="page-wrapper">
    <!-- 头部 -->
    <div class="header">
      <div class="logo" @click="goHome">量化牛牛财经频道</div>
      <div class="header-opt">
        <div class="user-menu-container" @mouseenter="onMenuEnter" @mouseleave="onMenuLeave">
          <div class="user-btn" @click="toggleUserMenu">{{ userText }}</div>
          <div class="user-dropdown" v-show="showUserMenu && logged" @mouseenter="onDropdownEnter" @mouseleave="onDropdownLeave">
            <div class="dropdown-item" @click="goToUserProfile">个人主页</div>
            <div class="dropdown-item logout" @click="handleLogout">退出登录</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分类导航 -->
    <div class="category-nav">
      <a href="#finance-news" class="category-item" :class="{ active: activeCategory==='finance-news' }" @click.prevent="go('finance-news')">财经资讯</a>
      <a href="#market-data" class="category-item" :class="{ active: activeCategory==='market-data' }" @click.prevent="go('market-data')">市场数据</a>
      <a href="#investment-ideas" class="category-item" :class="{ active: activeCategory==='investment-ideas' }" @click.prevent="go('investment-ideas')">投资观点</a>
      <a href="#policy-regulation" class="category-item" :class="{ active: activeCategory==='policy-regulation' }" @click.prevent="go('policy-regulation')">政策法规</a>
      <a href="/video" class="category-item" :class="{ active: activeCategory==='video' }" @click.prevent="goVideo">视频中心</a>
    </div>

    <!-- 主容器 -->
    <div class="container">
      <div class="main-content">
        
        <!-- 财经资讯 (快讯风格) -->
        <h2 class="section-title" id="finance-news">财经资讯</h2>
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
                <span class="meta-action">分享</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 市场数据 (列表风格) -->
        <h2 class="section-title" id="market-data">
          市场数据
        </h2>
        <div v-if="marketLoading" class="loading-state">加载中...</div>
        <div v-else-if="marketError" class="error-state">{{ marketError }}</div>
        <div class="data-table" v-else>
          <div class="data-header">
            <div class="th name">名称</div>
            <div class="th value">最新价</div>
            <div class="th change">涨跌幅</div>
            <div class="th time">更新时间</div>
          </div>
          <div class="data-row" v-for="(item, i) in marketDataItems" :key="'data'+i">
            <div class="td name">{{ item.title }}</div>
            <div class="td value price-font">{{ item.value }}</div>
            <div class="td change" :class="getChangeClass(item.change_pct)">
              {{ item.change_pct > 0 ? '+' : '' }}{{ item.change_pct }}%
            </div>
            <div class="td time">{{ item.updated_at }}</div>
          </div>
        </div>

        <!-- 投资观点 (列表风格) -->
        <h2 class="section-title" id="investment-ideas">
          投资观点
          <span v-if="ideasCached" class="cache-badge">缓存</span>
        </h2>
        <div v-if="ideasLoading" class="loading-state">加载中...</div>
        <div v-else-if="ideasError" class="error-state">{{ ideasError }}</div>
        <div class="article-list" v-else>
          <div class="article-item" v-for="(item, i) in ideasItems" :key="'idea'+i">
            <div class="article-main">
              <div class="article-title" :class="{ clickable: !!item.url }" @click="item.url && openUrl(item.url)">
                {{ item.title }}
              </div>
              <div class="article-summary">{{ item.content }}</div>
              <div class="article-footer">
                <span class="author" v-if="item.author">{{ item.author }}</span>
                <span class="source">{{ item.source }}</span>
                <span class="date">{{ formatIdeaDate(item.date) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 政策法规 (列表风格) -->
        <h2 class="section-title" id="policy-regulation">
          政策法规
        </h2>
        <div v-if="policyLoading" class="loading-state">加载中...</div>
        <div v-else-if="policyError" class="error-state">{{ policyError }}</div>
        <div class="article-list" v-else>
          <div class="article-item" v-for="(item, i) in policyItems" :key="'policy'+i">
             <div class="article-main">
              <div class="article-title" :class="{ clickable: !!item.url }" @click="item.url && openUrl(item.url)">
                {{ item.title }}
              </div>
              <div class="article-summary">{{ item.summary }}</div>
              <div class="article-footer">
                <span class="source">{{ item.source }}</span>
                <span class="date">{{ item.date }}</span>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 底部 -->
    <div class="footer">
      <p>量化牛牛财经频道 © 2025 版权所有</p>
      <p>风险提示：投资有风险，入市需谨慎。以上内容仅供参考，不构成投资建议</p>
    </div>

    <!-- 悬浮按钮 (左下角) -->
    <div class="scroll-top-btn" @click="scrollToTop" title="返回顶部">
      <span class="icon">↑</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { getWeiboMediaNews } from '@/services/newsService'
import { getMarketData, getIdeas, getPolicies } from '@/services/financeChannelService'

// 使用全局认证
const { logged, userText, isQualifiedInvestor, openLoginModal, logout } = useAuth()

const showUserMenu = ref(false)
const searchQuery = ref('')
const activeCategory = ref('finance-news')

// 新闻数据相关
const newsItems = ref([])
const newsLoading = ref(false)
const newsError = ref('')
const newsCached = ref(false)

// 市场数据相关
const marketDataItems = ref([])
const marketLoading = ref(false)
const marketError = ref('')
const marketCached = ref(false)


// 投资观点相关
const ideasItems = ref([])
const ideasLoading = ref(false)
const ideasError = ref('')
const ideasCached = ref(false)

// 政策法规相关
const policyItems = ref([])
const policyLoading = ref(false)
const policyError = ref('')
const policyCached = ref(false)

const router = useRouter()

function goHome() { 
  router.push('/') 
}

function goToUserProfile() {
  showUserMenu.value = false
  router.push('/profile')
}

function go(id) {
  activeCategory.value = id
  const el = document.getElementById(id)
  if (el) window.scrollTo({ top: el.offsetTop - 120, behavior: 'smooth' })
}

function goVideo() {
  activeCategory.value = 'video'
  router.push('/video')
}

function toggleUserMenu() {
  if (!logged.value) {
    openLoginModal()
    showUserMenu.value = false
  } else {
    showUserMenu.value = !showUserMenu.value
  }
}

function onMenuEnter() {
  if (!logged.value) return
  showUserMenu.value = true
}

function onMenuLeave() {
  setTimeout(() => {
    showUserMenu.value = false
  }, 300)
}

function onDropdownEnter() {
  showUserMenu.value = true
}

function onDropdownLeave() {
  showUserMenu.value = false
}

function handleLogout() {
  logout()
  showUserMenu.value = false
}

function openUrl(url) {
  if (!url) return
  window.open(url, '_blank')
}

function formatIdeaDate(value) {
  if (!value) return ''
  const normalized = String(value).replace('T', ' ').trim()
  const match = normalized.match(/^(\d{4}-\d{2}-\d{2})(?:\s*(\d{2}:\d{2}))?/)
  if (match) {
    return match[2] ? `${match[1]} ${match[2]}` : match[1]
  }
  return normalized
}

// 时间格式化辅助
function formatTime(timeStr) {
  if (!timeStr) return ''
  try {
    // 尝试解析，如果是 HH:mm 格式直接返回
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

function getChangeClass(change) {
  const val = parseFloat(change)
  if (isNaN(val)) return ''
  if (val > 0) return 'text-red'
  if (val < 0) return 'text-green'
  return ''
}


// 加载微博财经新闻
async function loadWeiboNews(keyword = null) {
  newsLoading.value = true
  newsError.value = ''
  
  try {
    const response = await getWeiboMediaNews({ limit: 20, keyword })
    const payload = response?.data || response
    
    if (payload && payload.items && payload.items.length > 0) {
      newsItems.value = payload.items
      newsCached.value = payload.cached || false
      
      // 如果数据过期（stale），显示提示
      if (payload.stale) {
        console.warn('使用了过期的缓存数据')
      }
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

// 加载市场数据
async function loadMarketData() {
  marketLoading.value = true
  marketError.value = ''
  
  try {
    const response = await getMarketData()
    const payload = response?.data || response
    
    if (payload && payload.items && payload.items.length > 0) {
      marketDataItems.value = payload.items
      marketCached.value = payload.cached || false
      
      if (payload.stale) {
        console.warn('市场数据使用了过期缓存')
      }
    } else {
      marketError.value = '暂无市场数据'
      marketDataItems.value = []
    }
  } catch (error) {
    console.error('加载市场数据失败:', error)
    marketError.value = '加载失败'
    marketDataItems.value = []
  } finally {
    marketLoading.value = false
  }
}


// 加载投资观点
async function loadIdeas(keyword = null) {
  ideasLoading.value = true
  ideasError.value = ''
  
  try {
    const response = await getIdeas({ limit: 10, keyword })
    const payload = response?.data || response
    
    if (payload && payload.items && payload.items.length > 0) {
      ideasItems.value = payload.items
      ideasCached.value = payload.cached || false
      
      if (payload.stale) {
        console.warn('观点数据使用了过期缓存')
      }
    } else {
      ideasError.value = '暂无观点数据'
      ideasItems.value = []
    }
  } catch (error) {
    console.error('加载投资观点失败:', error)
    ideasError.value = '加载失败'
    ideasItems.value = []
  } finally {
    ideasLoading.value = false
  }
}

// 加载政策法规
async function loadPolicies(keyword = null) {
  policyLoading.value = true
  policyError.value = ''
  
  try {
    const response = await getPolicies({ limit: 10, keyword })
    const payload = response?.data || response
    
    if (payload && payload.items && payload.items.length > 0) {
      policyItems.value = payload.items
      policyCached.value = payload.cached || false
      
      if (payload.stale) {
        console.warn('政策数据使用了过期缓存')
      }
    } else {
      policyError.value = '暂无政策数据'
      policyItems.value = []
    }
  } catch (error) {
    console.error('加载政策法规失败:', error)
    policyError.value = '加载失败'
    policyItems.value = []
  } finally {
    policyLoading.value = false
  }
}

// 搜索处理
function handleSearch() {
  const keyword = searchQuery.value.trim()
  loadWeiboNews(keyword)
  loadIdeas(keyword)
  loadPolicies(keyword)
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 页面加载时获取所有数据
onMounted(() => {
  loadWeiboNews()
  loadMarketData()
  loadIdeas()
  loadPolicies()
})
</script>

<style scoped>
/* 全局重置与基础样式 */
*{margin:0;padding:0;box-sizing:border-box;font-family:"Microsoft YaHei",sans-serif}
.page-wrapper {
  background-color: #f6f8fa; /* 浅灰背景，更商务 */
  min-height: 100vh;
  color: #333;
}

/* 头部样式 */
.header{background-color:#c83b3b;padding:12px 20px;color:white;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:99; box-shadow: 0 2px 4px rgba(0,0,0,0.1);}
.logo{font-size:22px;font-weight:bold;color:#ffffff;cursor:pointer}
.header-opt{display:flex;align-items:center;gap:20px}
.user-menu-container{position:relative;display:inline-block}
.header-opt .user-btn{background-color:rgba(255,255,255,0.2);color:#fff;padding:6px 15px;border-radius:20px;cursor:pointer;font-size:14px;}
.user-menu-container:hover .user-btn{background-color:rgba(255,255,255,0.3)}
.user-dropdown{position:absolute;top:100%;right:0;background-color:white;border:1px solid #ddd;border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.15);z-index:1000;margin-top:8px;min-width:120px}
.dropdown-item{padding:8px 15px;cursor:pointer;font-size:14px;color:#333;border-bottom:1px solid #f0f0f0}
.dropdown-item:hover{background-color:#f5f5f5}
.dropdown-item.logout{color:#c83b3b;}

/* 搜索栏 */
.search-bar{padding:15px 20px;background-color:white;display:flex;gap:15px;align-items:center; border-bottom: 1px solid #eee;}
.search-bar input{flex:1;padding:10px 15px;border:2px solid #f0f0f0;border-radius:4px;outline:none; transition:border-color 0.2s}
.search-bar input:focus{border-color: #c83b3b;}
.search-btn{background-color:#c83b3b;color:white;border:none;padding:10px 30px;border-radius:4px;cursor:pointer; font-weight: bold;}
.search-btn:hover{background-color:#b53232;}

/* 分类导航 */
.category-nav{background-color:#fff;padding:0 20px;overflow-x:auto;white-space:nowrap; border-bottom: 1px solid #ddd; box-shadow: 0 2px 4px rgba(0,0,0,0.05);}
.category-item{display:inline-block;color:#666;text-decoration:none;padding:15px 20px;margin-right:0;font-size:16px;cursor:pointer; border-bottom: 3px solid transparent;}
.category-item:hover{color: #c83b3b;}
.category-item.active{color:#c83b3b;border-bottom-color:#c83b3b;font-weight:bold}

/* 容器与布局 */
.container{max-width:1000px;margin:20px auto;padding:0 20px;}
.main-content { background: white; padding: 20px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.section-title{font-size:20px;color:#2c3e50;margin:30px 0 20px;padding-left:12px;border-left:4px solid #c83b3b; font-weight: 700; display: flex; align-items: center; gap: 10px;}
.cache-badge{font-size:12px;color:#999;background:#f5f5f5;padding:2px 8px;border-radius:3px;font-weight:normal}

/* 加载/错误状态 */
.loading-state, .error-state { text-align: center; padding: 30px; color: #999; }
.error-state { color: #f5222d; }

/* 快讯列表风格 (List Style) */
.kuaixun-list { display: flex; flex-direction: column; gap: 0; }
.kuaixun-item { display: flex; padding: 15px 0; border-bottom: 1px solid #f0f0f0; position: relative; }
.kuaixun-item:last-child { border-bottom: none; }
.kuaixun-time-col { width: 80px; flex-shrink: 0; text-align: right; padding-right: 15px; border-right: 1px solid #eee; margin-right: 15px; display: flex; flex-direction: column; justify-content: flex-start; padding-top: 2px;}
.kuaixun-time { font-size: 16px; font-weight: bold; color: #c83b3b; }
.kuaixun-date { font-size: 12px; color: #999; margin-top: 4px; }

.kuaixun-content { flex: 1; }
.kuaixun-title { font-size: 17px; font-weight: bold; color: #333; margin-bottom: 8px; line-height: 1.4; }
.kuaixun-summary { font-size: 14px; color: #666; line-height: 1.6; margin-bottom: 10px; text-align: justify; }
.kuaixun-meta { display: flex; justify-content: space-between; font-size: 12px; color: #aaa; }
.meta-action { cursor: pointer; color: #6699ff; }

/* 市场数据 (Table List Style) */
.data-table { border: 1px solid #eee; border-radius: 4px; overflow: hidden; }
.data-header { display: flex; background: #f9f9f9; padding: 12px 15px; border-bottom: 1px solid #eee; font-weight: bold; color: #666; font-size: 14px; }
.data-row { display: flex; padding: 12px 15px; border-bottom: 1px solid #eee; align-items: center; background: white; transition: background 0.1s; }
.data-row:last-child { border-bottom: none; }
.data-row:hover { background: #fdfdfd; }

.th, .td { flex: 1; text-align: right; }
.th.name, .td.name { flex: 1.5; text-align: left; color: #333; font-weight: 500; }
.td.value { font-weight: bold; color: #333; }
.td.time { color: #999; font-size: 13px; }
.change { font-weight: bold; }
.text-red { color: #f5222d; }
.text-green { color: #52c41a; }
.price-font { font-family: "D-DIN", "Arial", sans-serif; }

/* 投资观点/政策法规 (Generic Article List) */
.article-list { display: flex; flex-direction: column; }
.article-item { padding: 15px 0; border-bottom: 1px dashed #eee; }
.article-main { display: flex; flex-direction: column; gap: 8px; }
.article-title { font-size: 17px; font-weight: bold; color: #333; line-height: 1.4; transition: color 0.2s; }
.article-title.clickable:hover { color: #c83b3b; cursor: pointer; text-decoration: underline;}
.article-summary { font-size: 14px; color: #666; line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.article-footer { display: flex; gap: 15px; font-size: 12px; color: #999; margin-top: 5px; }
.article-footer .source { background: #f5f5f5; padding: 2px 6px; border-radius: 2px; }

/* 底部 */
.footer{background-color:#333;color:#ccc;text-align:center;padding:30px 20px;margin-top:40px}
.footer p { margin-bottom: 10px; font-size: 14px; }

/* 响应式微调 */
@media (max-width: 768px) {
  .kuaixun-time-col { width: 60px; padding-right: 10px; margin-right: 10px; }
  .kuaixun-time { font-size: 14px; }
  .header-opt .user-btn { padding: 4px 10px; }
}

/* 悬浮按钮 - 左下角 */
.scroll-top-btn {
  position: fixed;
  bottom: 30px;
  left: 30px;
  width: 44px;
  height: 44px;
  background-color: #c83b3b;
  color: white;
  border-radius: 50%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 1000;
  transition: all 0.3s;
  opacity: 0.8;
}

.scroll-top-btn:hover {
  background-color: #a02828;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
  opacity: 1;
}

.scroll-top-btn .icon {
  font-size: 24px;
  font-weight: bold;
  line-height: 1;
  margin-top: -2px; /* Visual adjustment */
}
</style>
