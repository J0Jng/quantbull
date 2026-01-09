<template>
  <!-- 登录弹窗 -->
  <div class="login-modal" v-show="showLogin">
    <div class="login-box">
      <span class="close-login" @click="closeLogin">&times;</span>
      <div class="login-title">量化牛牛财经频道 - 登录</div>
      <div class="error-tips" v-show="errorVisible">账号或密码错误，请重试！</div>
      <form class="login-form" @submit.prevent>
        <input v-model="username" type="text" placeholder="请输入账号" />
        <input v-model="password" type="password" placeholder="请输入密码" />
        <button type="button" class="login-btn" @click="submitLogin">登录</button>
      </form>
      <div class="login-tips">演示账号：123 | 演示密码：123</div>
    </div>
  </div>

  <!-- 动态风险提示弹窗 -->
  <div class="risk-modal" v-show="showRiskTip">
    <div class="risk-box">
      <div class="risk-icon">⚠️</div>
      <div class="risk-title">风险提示</div>
      <div class="risk-content">
        <p>尊敬的用户，您正在登录量化牛牛财经频道。投资有风险，入市需谨慎。请注意：</p>
        <ul>
          <li>金融市场存在波动风险，过往业绩不代表未来表现</li>
          <li>财经信息仅供参考，不构成投资建议</li>
          <li>请根据自身风险承受能力合理决策</li>
          <li>建议您详细了解产品风险收益特征</li>
        </ul>
      </div>
      <button class="risk-confirm-btn" @click="confirmRiskTip">我已阅读并了解风险</button>
    </div>
  </div>

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
            <div class="dropdown-item logout" @click="logout">退出登录</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input v-model="searchQuery" type="text" placeholder="搜索财经资讯、研报、数据等" />
      <button class="search-btn">搜索</button>
    </div>

    <!-- 分类导航 -->
    <div class="category-nav">
      <a href="#finance-news" class="category-item" :class="{ active: activeCategory==='finance-news' }" @click.prevent="go('finance-news')">财经资讯</a>
      <a href="#market-data" class="category-item" :class="{ active: activeCategory==='market-data' }" @click.prevent="go('market-data')">市场数据</a>
      <a href="#company-research" class="category-item" :class="{ active: activeCategory==='company-research' }" @click.prevent="go('company-research')">公司研报</a>
      <a href="#financial-calendar" class="category-item" :class="{ active: activeCategory==='financial-calendar' }" @click.prevent="go('financial-calendar')">财经日历</a>
      <a href="#investment-ideas" class="category-item" :class="{ active: activeCategory==='investment-ideas' }" @click.prevent="go('investment-ideas')">投资观点</a>
      <a href="#policy-regulation" class="category-item" :class="{ active: activeCategory==='policy-regulation' }" @click.prevent="go('policy-regulation')">政策法规</a>
    </div>

    <!-- 主容器 -->
    <div class="container">
      <!-- 财经资讯 -->
      <h2 class="section-title" id="finance-news">财经资讯</h2>
      <div class="news-grid">
        <div class="news-card" v-for="(item, i) in newsItems" :key="'news'+i">
          <img :src="item.img" alt="" class="news-img" loading="lazy">
          <div class="news-info">
            <div class="news-title">{{ item.title }}</div>
            <div class="news-summary">{{ item.summary }}</div>
            <div class="news-meta">
              <span class="news-source">{{ item.source }}</span>
              <span class="news-time">{{ item.time }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 市场数据 -->
      <h2 class="section-title" id="market-data">市场数据</h2>
      <div class="data-grid">
        <div class="data-card" v-for="(item, i) in marketDataItems" :key="'data'+i">
          <div class="data-title">{{ item.title }}</div>
          <div class="data-value">{{ item.value }}</div>
          <div class="data-change" :class="item.change > 0 ? 'positive' : 'negative'">
            {{ item.change > 0 ? '+' : '' }}{{ item.change }}%
          </div>
          <div class="data-chart">
            <img :src="item.chart" alt="数据图表" />
          </div>
        </div>
      </div>

      <!-- 公司研报 -->
      <h2 class="section-title" id="company-research">公司研报</h2>
      <div class="research-grid">
        <div class="research-card" v-for="(item, i) in researchItems" :key="'research'+i">
          <div class="research-title">{{ item.title }}</div>
          <div class="research-company">{{ item.company }}</div>
          <div class="research-content">{{ item.content }}</div>
          <div class="research-meta">
            <span class="research-date">{{ item.date }}</span>
            <span class="research-author">{{ item.author }}</span>
          </div>
        </div>
      </div>

      <!-- 财经日历 -->
      <h2 class="section-title" id="financial-calendar">财经日历</h2>
      <div class="calendar-grid">
        <div class="calendar-card" v-for="(item, i) in calendarItems" :key="'cal'+i">
          <div class="calendar-date">{{ item.date }}</div>
          <div class="calendar-event">{{ item.event }}</div>
          <div class="calendar-importance" :class="'importance-'+item.importance">
            重要性: {{ item.importanceText }}
          </div>
        </div>
      </div>

      <!-- 投资观点 -->
      <h2 class="section-title" id="investment-ideas">投资观点</h2>
      <div class="ideas-grid">
        <div class="ideas-card" v-for="(item, i) in ideasItems" :key="'idea'+i">
          <div class="ideas-title">{{ item.title }}</div>
          <div class="ideas-author">{{ item.author }}</div>
          <div class="ideas-content">{{ item.content }}</div>
          <div class="ideas-date">{{ item.date }}</div>
        </div>
      </div>

      <!-- 政策法规 -->
      <h2 class="section-title" id="policy-regulation">政策法规</h2>
      <div class="policy-grid">
        <div class="policy-card" v-for="(item, i) in policyItems" :key="'policy'+i">
          <div class="policy-title">{{ item.title }}</div>
          <div class="policy-summary">{{ item.summary }}</div>
          <div class="policy-date">{{ item.date }}</div>
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

const username = ref('')
const password = ref('')
const showLogin = ref(false)
const errorVisible = ref(false)
const logged = ref(false)
const userText = ref('登录/注册')
const showUserMenu = ref(false)
const searchQuery = ref('')
const activeCategory = ref('finance-news')
const showRiskTip = ref(false)
const isQualifiedInvestor = ref(false)

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
    showLogin.value = true 
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

function submitLogin() {
  if (username.value.trim() === '123' && password.value.trim() === '123') {
    // 登录成功，显示动态风险提示
    showRiskTip.value = true
    showLogin.value = false
    errorVisible.value = false
    // 清空输入框
    username.value = ''
    password.value = ''
  } else {
    errorVisible.value = true
    setTimeout(() => (errorVisible.value = false), 3000)
  }
}

function closeLogin() { 
  showLogin.value = false 
}

function confirmRiskTip() {
  showRiskTip.value = false
  logged.value = true
  userText.value = '已登录（123）'
  localStorage.setItem('quantLogin', '123')
  showUserMenu.value = false
  // 强制检查认证状态
  isQualifiedInvestor.value = localStorage.getItem('qualifiedInvestor') === 'certified'
}

function logout() {
  logged.value = false
  userText.value = '登录/注册'
  showUserMenu.value = false
  localStorage.removeItem('quantLogin')
}

// 检查本地存储中的登录状态
onMounted(() => {
  const status = localStorage.getItem('quantLogin')
  if (status === '123') {
    logged.value = true
    userText.value = '已登录（123）'
    // 强制检查并设置认证状态
    isQualifiedInvestor.value = localStorage.getItem('qualifiedInvestor') === 'certified'
  } else {
    // 如果没有登录，确保认证状态为false
    isQualifiedInvestor.value = false
  }
  // 如果未登录，默认显示登录弹窗以与原始静态页面行为一致
  if (!logged.value) showLogin.value = true
})

// 模拟数据
const newsItems = ref([
  { 
    img: 'https://picsum.photos/400/200?random=30', 
    title: '央行降准释放流动性，金融市场迎来利好', 
    summary: '央行宣布下调金融机构存款准备金率0.5个百分点，释放长期资金约1万亿元，对金融市场产生积极影响', 
    source: '财经日报', 
    time: '2小时前' 
  },
  { 
    img: 'https://picsum.photos/400/200?random=31', 
    title: '科技股大涨，创业板指数创新高', 
    summary: '科技板块全面爆发，多只龙头股涨停，市场情绪明显回暖', 
    source: '证券时报', 
    time: '4小时前' 
  },
  { 
    img: 'https://picsum.photos/400/200?random=32', 
    title: '新能源汽车销量持续增长，产业链受益', 
    summary: '多家新能源汽车厂商公布销售数据，同比增长超过50%，相关产业链公司业绩预期乐观', 
    source: '经济观察报', 
    time: '6小时前' 
  },
  { 
    img: 'https://picsum.photos/400/200?random=33', 
    title: '国际油价大幅上涨，能源板块走强', 
    summary: '受地缘政治影响，国际油价突破新高，能源板块成为市场焦点', 
    source: '金融界', 
    time: '8小时前' 
  }
])

const marketDataItems = ref([
  { title: '上证指数', value: '3,245.67', change: 1.25, chart: 'https://picsum.photos/200/100?random=40' },
  { title: '深证成指', value: '10,876.32', change: -0.34, chart: 'https://picsum.photos/200/100?random=41' },
  { title: '创业板指', value: '2,356.89', change: 2.10, chart: 'https://picsum.photos/200/100?random=42' },
  { title: '沪深300', value: '4,123.56', change: 0.78, chart: 'https://picsum.photos/200/100?random=43' },
  { title: '黄金期货', value: '456.78', change: 0.55, chart: 'https://picsum.photos/200/100?random=44' },
  { title: '美元/人民币', value: '7.1234', change: -0.23, chart: 'https://picsum.photos/200/100?random=45' }
])

const researchItems = ref([
  { title: '新能源汽车产业链深度分析', company: '比亚迪', content: '随着新能源汽车市场的快速发展，产业链上下游均迎来发展机遇。本报告深入分析了新能源汽车产业链的各个环节，包括电池、电机、电控等核心技术的发展趋势。', date: '2025-01-15', author: '李研究员' },
  { title: '人工智能技术在金融行业的应用前景', company: '招商银行', content: '人工智能技术正在深刻改变金融行业，从风控到客户服务，AI的应用越来越广泛。本报告分析了AI在金融行业的主要应用场景及未来发展趋势。', date: '2025-01-14', author: '王分析师' },
  { title: '光伏行业政策调整对产业链影响分析', company: '隆基绿能', content: '近期光伏行业政策调整，对产业链各环节产生了深远影响。本报告详细分析了政策变化对上游硅料、中游组件及下游电站建设的影响。', date: '2025-01-13', author: '张专家' },
  { title: '半导体国产化替代进程加速', company: '中芯国际', content: '在国际贸易环境变化的背景下，半导体国产化替代进程明显加速。本报告分析了国内半导体产业链的发展现状及未来机遇。', date: '2025-01-12', author: '赵博士' }
])

const calendarItems = ref([
  { date: '2025-01-20', event: '美国CPI数据发布', importance: 3, importanceText: '高' },
  { date: '2025-01-22', event: '央行货币政策会议', importance: 5, importanceText: '极高' },
  { date: '2025-01-25', event: '上市公司Q4财报发布', importance: 4, importanceText: '高' },
  { date: '2025-01-28', event: 'GDP季度数据公布', importance: 5, importanceText: '极高' },
  { date: '2025-02-01', event: '制造业PMI数据', importance: 3, importanceText: '中' },
  { date: '2025-02-05', event: '美联储利率决议', importance: 5, importanceText: '极高' }
])

const ideasItems = ref([
  { title: '2025年投资策略：科技与消费的平衡', author: '知名投资顾问 张三', content: '在当前市场环境下，建议投资者关注科技和消费两大板块的平衡配置，以应对市场波动。', date: '2025-01-15' },
  { title: '价值投资在当前市场的应用', author: '资深分析师 李四', content: '价值投资策略在当前市场依然有效，建议关注低估值、高分红的优质企业。', date: '2025-01-14' },
  { title: 'ESG投资理念的实践与思考', author: '绿色投资专家 王五', content: 'ESG投资已成为全球趋势，建议投资者将环境、社会和治理因素纳入投资决策考量。', date: '2025-01-13' },
  { title: '量化策略在A股市场的应用', author: '量化研究员 赵六', content: '量化策略在A股市场的有效性不断提升，建议投资者关注多因子模型和机器学习方法的应用。', date: '2025-01-12' }
])

const policyItems = ref([
  { title: '关于规范金融科技创新发展的指导意见', summary: '为进一步规范金融科技创新发展，防范金融风险，监管部门发布指导意见，明确金融科技创新的边界和要求。', date: '2025-01-15' },
  { title: '关于进一步优化资本市场环境的通知', summary: '为提升资本市场服务实体经济能力，监管部门发布通知，从多个方面优化资本市场环境。', date: '2025-01-10' },
  { title: '关于加强投资者保护工作的若干措施', summary: '为切实保护投资者合法权益，监管部门出台多项措施，强化投资者保护工作。', date: '2025-01-05' },
  { title: '关于推进绿色金融发展的实施方案', summary: '为推动绿色金融发展，支持经济绿色转型，相关部门联合制定实施方案，明确发展目标和路径。', date: '2024-12-28' }
])

// 移除重复的函数定义 - 这些功能已经在前面部分实现
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
.section-title{font-size:20px;color:#ff7f24;border-left:1px solid #ff7f24;padding-left:10px;margin:20px 0 15px}
/* 指定分类标题使用白色字体以匹配设计，并整体左移微调视觉对齐 */
#finance-news.section-title,
#market-data.section-title,
#company-research.section-title,
#financial-calendar.section-title,
#investment-ideas.section-title,
#policy-regulation.section-title {
  color: #ffffff;
  transform: translateX(-1px);
}
.news-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;margin-bottom:30px}
.news-card{background-color:white;border-radius:8px;overflow:hidden;border:1px solid #ffb380;transition:transform .2s}
.news-card:hover{transform:translateY(-5px);box-shadow:0 4px 12px rgba(255,127,36,.15)}
.news-img{width:100%;height:150px;object-fit:cover}
.news-info{padding:15px}
.news-title{font-size:16px;margin-bottom:8px;color:#333;font-weight:bold;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.news-summary{font-size:14px;margin-bottom:10px;color:#666;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.news-meta{display:flex;justify-content:space-between;font-size:12px;color:#999}
.data-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:15px;margin-bottom:30px}
.data-card{background-color:white;border-radius:8px;overflow:hidden;border:1px solid #ffb380;padding:15px;text-align:center}
.data-title{font-size:14px;margin-bottom:8px;color:#333}
.data-value{font-size:18px;font-weight:bold;margin-bottom:5px;color:#ff7f24}
.data-change{font-size:14px;margin-bottom:10px;font-weight:bold}
.data-change.positive{color:#e74c3c}
.data-change.negative{color:#27ae60}
.data-chart img{width:100%;height:60px;object-fit:cover}
.research-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;margin-bottom:30px}
.research-card{background-color:white;border-radius:8px;overflow:hidden;border:1px solid #ffb380;padding:15px}
.research-title{font-size:16px;margin-bottom:8px;color:#333;font-weight:bold}
.research-company{font-size:14px;margin-bottom:10px;color:#ff7f24;font-weight:bold}
.research-content{font-size:14px;margin-bottom:10px;color:#666;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.research-meta{display:flex;justify-content:space-between;font-size:12px;color:#999}
.calendar-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:15px;margin-bottom:30px}
.calendar-card{background-color:white;border-radius:8px;overflow:hidden;border:1px solid #ffb380;padding:15px}
.calendar-date{font-size:16px;margin-bottom:8px;color:#ff7f24;font-weight:bold}
.calendar-event{font-size:14px;margin-bottom:10px;color:#333}
.calendar-importance{font-size:12px;color:#666}
.importance-1, .importance-2{color:#27ae60}
.importance-3{color:#f39c12}
.importance-4, .importance-5{color:#e74c3c}
.ideas-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;margin-bottom:30px}
.ideas-card{background-color:white;border-radius:8px;overflow:hidden;border:1px solid #ffb380;padding:15px}
.ideas-title{font-size:16px;margin-bottom:8px;color:#333;font-weight:bold}
.ideas-author{font-size:14px;margin-bottom:10px;color:#ff7f24}
.ideas-content{font-size:14px;margin-bottom:10px;color:#666}
.ideas-date{font-size:12px;color:#999;text-align:right}
.policy-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:20px;margin-bottom:30px}
.policy-card{background-color:white;border-radius:8px;overflow:hidden;border:1px solid #ffb380;padding:15px}
.policy-title{font-size:16px;margin-bottom:8px;color:#333;font-weight:bold}
.policy-summary{font-size:14px;margin-bottom:10px;color:#666}
.policy-date{font-size:12px;color:#999;text-align:right}
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