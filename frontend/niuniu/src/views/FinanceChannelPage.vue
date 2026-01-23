<template>
  <div>
    <!-- 头部 -->
    <div class="header">
      <div class="logo" @click="goHome">量化牛牛财经频道</div>
      <div class="header-opt">
        <a href="/news-detail">财经资讯</a>
        <a href="/company-research">公司研报</a>
        <div class="user-menu-container" @mouseenter="onMenuEnter" @mouseleave="onMenuLeave">
          <div class="user-btn" @click="toggleUserMenu">{{ userText }}</div>
          <div class="user-dropdown" v-show="showUserMenu && logged" @mouseenter="onDropdownEnter" @mouseleave="onDropdownLeave">
            <div class="dropdown-item" @click="goToUserProfile">个人主页</div>
            <div class="dropdown-item logout" @click="handleLogout">退出登录</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input v-model="searchQuery" type="text" placeholder="搜索财经资讯、研报、数据等" @keyup.enter="handleSearch" />
      <button class="search-btn" @click="handleSearch">搜索</button>
    </div>

    <!-- 分类导航 -->
    <div class="category-nav">
      <a href="#finance-news" class="category-item" :class="{ active: activeCategory==='finance-news' }" @click.prevent="go('finance-news')">财经资讯</a>
      <a href="#market-data" class="category-item" :class="{ active: activeCategory==='market-data' }" @click.prevent="go('market-data')">市场数据</a>
      <a href="#investment-ideas" class="category-item" :class="{ active: activeCategory==='investment-ideas' }" @click.prevent="go('investment-ideas')">投资观点</a>
      <a href="#policy-regulation" class="category-item" :class="{ active: activeCategory==='policy-regulation' }" @click.prevent="go('policy-regulation')">政策法规</a>
    </div>

    <!-- 主容器 -->
    <div class="container">
      <!-- 财经资讯 -->
      <h2 class="section-title" id="finance-news">财经资讯</h2>
      <div v-if="newsLoading" style="text-align: center; padding: 40px; color: #999;">
        加载中...
      </div>
      <div v-else-if="newsError" style="text-align: center; padding: 40px; color: #ff4444;">
        {{ newsError }}
      </div>
      <div class="news-grid" v-else>
        <div class="news-card" v-for="(item, i) in newsItems" :key="item.id || 'news'+i">
          <div class="news-info">
            <div class="news-title">{{ item.title }}</div>
            <div class="news-summary">{{ item.summary }}</div>
            <div class="news-meta">
              <span class="news-source">{{ item.source }}{{ item.author ? ' · ' + item.author : '' }}</span>
              <span class="news-time">{{ item.time }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 市场数据 -->
      <h2 class="section-title" id="market-data">
        市场数据
        <span v-if="marketCached" class="cache-badge">缓存数据</span>
      </h2>
      <div v-if="marketLoading" style="text-align: center; padding: 40px; color: #999;">
        加载中...
      </div>
      <div v-else-if="marketError" style="text-align: center; padding: 40px; color: #ff4444;">
        {{ marketError }}
      </div>
      <div class="data-grid" v-else>
        <div class="data-card" v-for="(item, i) in marketDataItems" :key="'data'+i">
          <div class="data-title">{{ item.title }}</div>
          <div class="data-value">{{ item.value }}</div>
          <div class="data-change" :class="item.change_pct > 0 ? 'positive' : 'negative'">
            {{ item.change_pct > 0 ? '+' : '' }}{{ item.change_pct }}%
          </div>
          <div class="data-time">{{ item.updated_at }}</div>
        </div>
      </div>


      <!-- 投资观点 -->
      <h2 class="section-title" id="investment-ideas">
        投资观点
        <span v-if="ideasCached" class="cache-badge">缓存数据</span>
      </h2>
      <div v-if="ideasLoading" style="text-align: center; padding: 40px; color: #999;">
        加载中...
      </div>
      <div v-else-if="ideasError" style="text-align: center; padding: 40px; color: #ff4444;">
        {{ ideasError }}
      </div>
      <div class="ideas-grid" v-else>
        <div class="ideas-card" v-for="(item, i) in ideasItems" :key="'idea'+i">
          <div class="ideas-title">{{ item.title }}</div>
          <div class="ideas-author">{{ item.author }}</div>
          <div class="ideas-content">{{ item.content }}</div>
          <div class="ideas-meta">
            <span class="ideas-source">{{ item.source }}</span>
            <span class="ideas-date">{{ item.date }}</span>
          </div>
        </div>
      </div>

      <!-- 政策法规 -->
      <h2 class="section-title" id="policy-regulation">
        政策法规
        <span v-if="policyCached" class="cache-badge">缓存数据</span>
      </h2>
      <div v-if="policyLoading" style="text-align: center; padding: 40px; color: #999;">
        加载中...
      </div>
      <div v-else-if="policyError" style="text-align: center; padding: 40px; color: #ff4444;">
        {{ policyError }}
      </div>
      <div class="policy-grid" v-else>
        <div class="policy-card" v-for="(item, i) in policyItems" :key="'policy'+i">
          <div class="policy-title" :class="{ clickable: !!item.url }" @click="item.url && openUrl(item.url)">{{ item.title }}</div>
          <div class="policy-summary">{{ item.summary }}</div>
          <div class="policy-meta">
            <span class="policy-source">{{ item.source }}</span>
            <span class="policy-date">{{ item.date }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部 -->
    <div class="footer">
      <p>量化牛牛财经频道 © 2025 版权所有</p>
      <p>风险提示：投资有风险，入市需谨慎。以上内容仅供参考，不构成投资建议</p>
      <p>基金投资需谨慎，过往业绩不代表未来收益</p>
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
  if (el) window.scrollTo({ top: el.offsetTop - 100, behavior: 'smooth' })
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

// 页面加载时获取所有数据
onMounted(() => {
  loadWeiboNews()
  loadMarketData()
  loadIdeas()
  loadPolicies()
})
</script>

<style scoped>
/* 直接复用原页面样式（简化并保留核心） */
*{margin:0;padding:0;box-sizing:border-box;font-family:"微软雅黑",sans-serif}
body{background-color:#fff8f0;color:#333}
.login-modal{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.8);display:flex;justify-content:center;align-items:center;z-index:9999}
.login-box{width:90%;max-width:400px;background:white;border-radius:10px;padding:30px;position:relative;border:2px solid #ff7f24}
.close-login{position:absolute;top:15px;right:15px;font-size:24px;color:#ff7f24;cursor:pointer}
.login-title{font-size:22px;color:#ff7f24;text-align:center;margin-bottom:20px;font-weight:bold}
.login-form{display:flex;flex-direction:column;gap:15px}
.login-form input{padding:12px 15px;border:1px solid #ffb380;border-radius:6px}
.login-btn{background-color:#ff7f24;color:white;border:none;padding:12px 0;border-radius:6px;cursor:pointer}
.login-btn:hover{background-color:#ff6a00}
.login-tips{ text-align:center;font-size:14px;color:#666;margin-top:10px }
.error-tips{color:#ff4500;text-align:center}
.header{background-color:#ff7f24;padding:12px 20px;color:white;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:99}
.logo{font-size:22px;font-weight:bold;color:#ffffff;cursor:pointer}
.header-opt{display:flex;align-items:center;gap:20px}
.header-opt a{color:white;text-decoration:none;font-size:14px}
.header-opt{position:relative}
.user-menu-container{position:relative;display:inline-block}
.header-opt .user-btn{background-color:white;color:#ff7f24;padding:6px 12px;border-radius:4px;cursor:pointer;position:relative}
.user-menu-container:hover .user-btn{background-color:#f5f5f5}
.user-dropdown{position:absolute;top:100%;right:0;background-color:white;border:1px solid #ddd;border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.15);z-index:1000;margin-top:5px;min-width:120px}
.dropdown-item{padding:8px 12px;cursor:pointer;font-size:14px;color:#333;border-bottom:1px solid #f0f0f0}
.dropdown-item:hover{background-color:#f5f5f5}
.dropdown-item.logout{color:#ff4444;border-bottom:none}
.dropdown-item.logout:hover{background-color:#ffe6e6}
.search-bar{padding:15px 20px;background-color:white;display:flex;gap:10px;align-items:center}
.search-bar input{flex:1;padding:10px 15px;border:1px solid #ffb380;border-radius:6px;outline:none}
.search-btn{background-color:#ff7f24;color:white;border:none;padding:10px 25px;border-radius:6px}
.category-nav{background-color:#ff9933;padding:12px 20px;overflow-x:auto;white-space:nowrap}
.category-item{display:inline-block;color:white;text-decoration:none;padding:6px 18px;margin-right:8px;border-radius:4px;font-size:15px;cursor:pointer}
.category-item.active{background-color:#ff7f24;font-weight:bold}
.container{max-width:1200px;margin:0 auto;padding:20px}
.section-title{font-size:20px;color:#ff7f24;border-left:1px solid #ff7f24;padding-left:10px;margin:20px 0 15px;display:flex;align-items:center;gap:10px}
.cache-badge{font-size:12px;color:#999;background:#f0f0f0;padding:2px 8px;border-radius:3px;font-weight:normal}
/* 指定分类标题使用白色字体以匹配设计，并整体左移微调视觉对齐 */
#finance-news.section-title,
#market-data.section-title,
#company-research.section-title,
#investment-ideas.section-title,
#policy-regulation.section-title {
  color: #ffffff;
  transform: translateX(-1px);
}
.news-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;margin-bottom:30px}
.news-card{background-color:white;border-radius:8px;overflow:hidden;border:1px solid #ffb380;transition:transform .2s;padding:15px}
.news-card:hover{transform:translateY(-5px);box-shadow:0 4px 12px rgba(255,127,36,.15)}
.news-info{display:flex;flex-direction:column;gap:8px}
.news-title{font-size:16px;color:#333;font-weight:bold;white-space:normal;word-break:break-word}
.news-summary{font-size:14px;color:#666;white-space:normal;word-break:break-word;line-height:1.5}
.news-meta{display:flex;justify-content:space-between;font-size:12px;color:#999;padding-top:5px}
.data-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:15px;margin-bottom:30px}
.data-card{background-color:white;border-radius:8px;border:1px solid #ffb380;padding:15px;text-align:center;display:flex;flex-direction:column;gap:8px}
.data-title{font-size:14px;color:#333;font-weight:bold}
.data-value{font-size:22px;font-weight:bold;color:#ff7f24}
.data-change{font-size:16px;font-weight:bold}
.data-change.positive{color:#e74c3c}
.data-change.negative{color:#27ae60}
.data-time{font-size:11px;color:#999;margin-top:auto}
.ideas-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;margin-bottom:30px}
.ideas-card{background-color:white;border-radius:8px;border:1px solid #ffb380;padding:15px;display:flex;flex-direction:column;gap:10px}
.ideas-title{font-size:16px;color:#333;font-weight:bold;line-height:1.4}
.ideas-author{font-size:14px;color:#ff7f24}
.ideas-content{font-size:14px;color:#666;line-height:1.6;flex:1}
.ideas-meta{display:flex;justify-content:space-between;font-size:12px;color:#999;padding-top:5px;border-top:1px solid #f0f0f0}
.ideas-source{color:#666}
.ideas-date{text-align:right}
.policy-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;margin-bottom:30px}
.policy-card{background-color:white;border-radius:8px;border:1px solid #ffb380;padding:15px;display:flex;flex-direction:column;gap:10px}
.policy-title{font-size:16px;color:#333;font-weight:bold;line-height:1.4}
.policy-title.clickable{color:#ff7f24;cursor:pointer}
.policy-title.clickable:hover{text-decoration:underline}
.policy-summary{font-size:14px;color:#666;line-height:1.6;flex:1}
.policy-meta{display:flex;justify-content:space-between;font-size:12px;color:#999;padding-top:5px;border-top:1px solid #f0f0f0}
.policy-source{color:#666}
.policy-date{text-align:right}
.footer{background-color:#ff7f24;color:white;text-align:center;padding:20px;margin-top:40px}

/* 动态风险提示样式 */
.risk-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.risk-box {
  width: 90%;
  max-width: 500px;
  background: white;
  border-radius: 10px;
  padding: 30px;
  position: relative;
  border: 3px solid #ff9933;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.risk-icon {
  font-size: 40px;
  text-align: center;
  margin-bottom: 15px;
}

.risk-title {
  font-size: 24px;
  color: #ff4500;
  text-align: center;
  margin-bottom: 20px;
  font-weight: bold;
}

.risk-content {
  margin-bottom: 25px;
  line-height: 1.6;
}

.risk-content p {
  margin-bottom: 15px;
  color: #333;
}

.risk-content ul {
  padding-left: 20px;
  margin-bottom: 15px;
}

.risk-content li {
  margin-bottom: 8px;
  color: #666;
}

.risk-confirm-btn {
  background-color: #ff7f24;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
  display: block;
  margin: 0 auto;
  transition: background-color 0.3s;
}

.risk-confirm-btn:hover {
  background-color: #ff6a00;
}
</style>