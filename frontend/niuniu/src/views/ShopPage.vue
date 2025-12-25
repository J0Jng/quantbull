<template>
  <div>
    <!-- 登录弹窗 -->
    <div class="login-modal" v-show="showLogin">
      <div class="login-box">
        <span class="close-login" @click="closeLogin">&times;</span>
        <div class="login-title">量化牛牛商店 - 登录</div>
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
          <p>尊敬的用户，您正在登录量化牛牛交易平台。投资有风险，入市需谨慎。请注意：</p>
          <ul>
            <li>量化交易可能面临市场风险、流动性风险等</li>
            <li>过去业绩不代表未来表现</li>
            <li>请根据自身风险承受能力合理配置资产</li>
            <li>建议您详细了解产品风险收益特征</li>
          </ul>
        </div>
        <button class="risk-confirm-btn" @click="confirmRiskTip">我已阅读并了解风险</button>
      </div>
    </div>

    <!-- 头部 -->
    <div class="header">
      <div class="logo" @click="goHome">量化牛牛商店</div>
      <div class="header-opt">
        
        <a href="#" @click.prevent="goToOrders">我的订单</a>
        <a href="#" @click.prevent="goToCart" class="cart-link">
          购物车
          <span class="cart-badge" v-if="cartBadgeCount > 0">{{ cartBadgeCount }}</span>
        </a>
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
      <input v-model="searchQuery" type="text" placeholder="搜索因子、策略、课程、书籍等" />
      <button class="search-btn">搜索</button>
    </div>

    <!-- 分类导航 -->
    <div class="category-nav">
      <a href="#factor" class="category-item" :class="{ active: activeCategory==='factor' }" @click.prevent="go('factor')">因子</a>
      <a href="#strategy" class="category-item" :class="{ active: activeCategory==='strategy' }" @click.prevent="go('strategy')">策略</a>
      <a href="#fund" class="category-item fund" v-show="showFund" :class="{ active: activeCategory==='fund' }" @click.prevent="go('fund')">基金</a>
      <a href="#advisor" class="category-item" :class="{ active: activeCategory==='advisor' }" @click.prevent="go('advisor')">投顾</a>
      <a href="#course" class="category-item" :class="{ active: activeCategory==='course' }" @click.prevent="go('course')">课程</a>
      <a href="#book" class="category-item" :class="{ active: activeCategory==='book' }" @click.prevent="go('book')">书籍</a>
      <a href="#talent" class="category-item" :class="{ active: activeCategory==='talent' }" @click.prevent="go('talent')">人才</a>
    </div>

    <!-- 主容器 -->
    <div class="container" id="goodsContainer" :class="{ 'show-price': logged }">
      <!-- 因子分类 -->
      <h2 class="section-title" id="factor">量化因子</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="(item,i) in factorItems" :key="'f'+i">
          <img :src="item.img" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">因子</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ item.price }}</div>
          <div class="goods-btn">
            <button class="buy-btn" @click="addToCart(item, 'factor')">加入购物车</button>
            <button class="detail-btn" @click="goToGoodsDetail('factor', i)">详情</button>
          </div>
          </div>
        </div>
      </div>

      <!-- 策略分类 -->
      <h2 class="section-title" id="strategy">量化策略</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="(item,i) in strategyItems" :key="'s'+i">
          <img :src="item.img" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">策略</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ item.price }}</div>
          <div class="goods-btn">
            <button class="buy-btn" @click="addToCart(item, 'strategy')">加入购物车</button>
            <button class="detail-btn" @click="goToGoodsDetail('strategy', i)">详情</button>
          </div>
          </div>
        </div>
      </div>

      <!-- 基金分类（默认隐藏，登录后显示） -->
      <h2 class="section-title" id="fund" v-show="showFund">专属基金</h2>
      <div class="goods-grid" v-show="showFund">
        <div class="goods-card" v-for="(item,i) in fundItems" :key="'fund'+i">
          <img :src="item.img" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">基金</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ (logged && isQualifiedInvestor) ? item.price : '*****' }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item, 'fund')">预约认购</button>
              <button class="detail-btn" @click="goToGoodsDetail('fund')">详情</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 投顾分类 -->
      <h2 class="section-title" id="advisor">专业投顾</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="(item,i) in advisorItems" :key="'a'+i">
          <img :src="item.img" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">投顾</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ (logged && isQualifiedInvestor) ? item.price : '*****' }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item, 'advisor')">加入购物车</button>
              <button class="detail-btn" @click="goToGoodsDetail('advisor')">详情</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 课程分类 -->
      <h2 class="section-title" id="course">精品课程</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="(item,i) in courseItems" :key="'c'+i">
          <img :src="item.img" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">课程</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ item.price }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item, 'course')">加入购物车</button>
              <button class="detail-btn" @click="goToGoodsDetail('course')">详情</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 书籍分类 -->
      <h2 class="section-title" id="book">专业书籍</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="(item,i) in bookItems" :key="'b'+i">
          <img :src="item.img" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">书籍</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ item.price }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item, 'book')">加入购物车</button>
              <button class="detail-btn" @click="goToGoodsDetail('book')">详情</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 人才分类 -->
      <h2 class="section-title" id="talent">量化人才</h2>
      <div class="goods-grid">
        <div class="goods-card" v-for="(item,i) in talentItems" :key="'t'+i">
          <img :src="item.img" alt="" class="goods-img" loading="lazy">
          <div class="goods-info">
            <span class="goods-tag">人才</span>
            <div class="goods-name">{{ item.name }}</div>
            <div class="goods-price">{{ item.price }}</div>
            <div class="goods-btn">
              <button class="buy-btn" @click="addToCart(item, 'talent')">咨询对接</button>
              <button class="detail-btn" @click="goToGoodsDetail('talent')">详情</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 其余分类省略为简洁（可按需扩展） -->
    </div>

    <!-- 底部 -->
    <div class="footer">
      <p>量化牛牛商店 © 2025 版权所有</p>
      <p>风险提示：量化投资存在市场风险，过往业绩不代表未来收益</p>
      <p>基金专区仅对合格投资者开放，详情请联系客服</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart.js'

const username = ref('')
const password = ref('')
const showLogin = ref(false)
const errorVisible = ref(false)
const logged = ref(false)
  const userText = ref('登录/注册')
  const showFund = ref(false)
  const showUserMenu = ref(false)
  const searchQuery = ref('')
  const activeCategory = ref('factor')
  const showRiskTip = ref(false)
  const isQualifiedInvestor = ref(false)
  
  // 购物车徽章显示
  const cartBadgeCount = computed(() => cartStore.totalItems)

const router = useRouter()
const cartStore = useCartStore()

function goHome() { router.push('/') }

function goToGoodsDetail(category = 'general', itemIndex) {
  // 首先检查用户是否已登录
  if (!logged.value) {
    alert('请先登录后再查看商品详情和购买。')
    showLogin.value = true
    return
  }
  
  // 如果是基金或投顾分类，需要检查合格投资者认证
  if ((category === 'fund' || category === 'advisor') && !isQualifiedInvestor.value) {
    alert('该产品仅对合格投资者开放，请先前往个人主页完成合格投资者认证。')
    return
  }
  
  // 生成商品ID，格式为：category-index
  const goodsId = `${category}-${itemIndex || 0}`
  router.push(`/shop/goods-detail/${goodsId}`)
}

const factorItems = ref([
  { img: 'https://picsum.photos/400/300?random=1', name: '量价因子合集 - 超100个经典A股量价因子（可直接回测）', price: '¥1,299.00' },
  { img: 'https://picsum.photos/400/300?random=2', name: '基本面因子库 - 财务/估值/成长类因子（附计算代码）', price: '¥999.00' },
  { img: 'https://picsum.photos/400/300?random=3', name: '另类因子 - 舆情/资金流/产业链因子（实时更新）', price: '¥1,599.00' },
  { img: 'https://picsum.photos/400/300?random=4', name: '因子挖掘工具 - 自动化因子生成与有效性检验平台', price: '¥2,999.00' }
])

const strategyItems = ref([
  { img: 'https://picsum.photos/400/300?random=5', name: '双均线择时策略 - 年化收益25%+（附Python源码）', price: '¥699.00' },
  { img: 'https://picsum.photos/400/300?random=6', name: '多因子选股策略 - 沪深300增强（回测胜率78%）', price: '¥1,899.00' },
  { img: 'https://picsum.photos/400/300?random=7', name: 'ETF套利策略 - 无风险套利（日内交易版）', price: '¥1,499.00' },
  { img: 'https://picsum.photos/400/300?random=8', name: '商品CTA策略 - 趋势跟踪（适配期货市场）', price: '¥2,499.00' }
])

const fundItems = ref([
  { img: 'https://picsum.photos/400/300?random=9', name: '量化增强专户基金 - 最低起投100万', price: '¥1,000,000.00' },
  { img: 'https://picsum.photos/400/300?random=10', name: '量化FOF基金 - 多策略组合（年化18%）', price: '¥500,000.00' }
])

const advisorItems = ref([
  { img: 'https://picsum.photos/400/300?random=11', name: '1v1量化投顾服务 - 定制化资产配置方案（月付）', price: '¥3,999.00/月' },
  { img: 'https://picsum.photos/400/300?random=12', name: '量化组合投顾 - 季度调仓（年付优惠）', price: '¥19,999.00/年' },
  { img: 'https://picsum.photos/400/300?random=13', name: '个性化策略定制 - 按需开发量化模型', price: '¥50,000.00起' },
  { img: 'https://picsum.photos/400/300?random=14', name: '量化风控咨询 - 策略风险评估与优化', price: '¥8,999.00/次' }
])

const courseItems = ref([
  { img: 'https://picsum.photos/400/300?random=15', name: 'Python量化入门到精通 - 零基础学量化交易', price: '¥599.00' },
  { img: 'https://picsum.photos/400/300?random=16', name: '量化因子开发实战 - 从0到1构建有效因子', price: '¥899.00' },
  { img: 'https://picsum.photos/400/300?random=17', name: '量化策略回测实战 - 避免过拟合（附案例）', price: '¥799.00' },
  { img: 'https://picsum.photos/400/300?random=18', name: '量化策略实盘部署 - 自动交易对接教程', price: '¥1,299.00' }
])

const bookItems = ref([
  { img: 'https://picsum.photos/400/300?random=19', name: '《量化投资分析（原书第3版）》- 精装版+配套源码', price: '¥168.00' },
  { img: 'https://picsum.photos/400/300?random=20', name: '《Python量化交易实战》- 进阶版（附实战案例）', price: '¥128.00' },
  { img: 'https://picsum.photos/400/300?random=21', name: '《因子投资：方法与实践》- 业内经典教材', price: '¥148.00' },
  { img: 'https://picsum.photos/400/300?random=22', name: '《量化风控：模型与实践》- 金融机构内部教材', price: '¥188.00' }
])

const talentItems = ref([
  { img: 'https://picsum.photos/400/300?random=23', name: '量化研究员推荐 - 头部券商背景（全职/兼职）', price: '¥5,000.00/人（服务费）' },
  { img: 'https://picsum.photos/400/300?random=24', name: '量化人才猎头服务 - 定向猎聘量化总监/工程师', price: '¥30,000.00/单' },
  { img: 'https://picsum.photos/400/300?random=25', name: '企业量化人才内训 - 定制化培训方案', price: '¥50,000.00/场' },
  { img: 'https://picsum.photos/400/300?random=26', name: '量化实习推荐 - 公募/私募/券商实习岗位', price: '¥1,999.00/人' }
])

function checkInvestorCertification() {
  // 检查本地存储中的合格投资者认证状态
  const investorStatus = localStorage.getItem('qualifiedInvestor')
  if (investorStatus === 'certified') {
    isQualifiedInvestor.value = true
  } else {
    isQualifiedInvestor.value = false
  }
}

  // 添加商品到购物车
  function addToCart(item, type) {
    if (!logged.value) {
      alert('请先登录后再添加商品到购物车')
      showLogin.value = true
      return
    }
    
    // 如果是基金或投顾产品，检查合格投资者认证
    if ((type === 'fund' || type === 'advisor') && !isQualifiedInvestor.value) {
      alert('该产品仅对合格投资者开放，请先前往个人主页完成合格投资者认证。')
      return
    }
    
    // 创建购物车商品对象
    const cartItem = {
      id: `${type}-${item.name.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase()}`,
      name: item.name,
      price: item.price,
      img: item.img,
      type: type
    }
    
    cartStore.addToCart(cartItem)
    
    // 显示添加成功提示
    const productTypeName = type === 'factor' ? '因子' : 
                            type === 'strategy' ? '策略' : 
                            type === 'fund' ? '基金' : 
                            type === 'advisor' ? '投顾' : 
                            type === 'course' ? '课程' : 
                            type === 'book' ? '书籍' : '人才'
    
    alert(`已成功添加 ${productTypeName} 产品到购物车！`)
  }

  // 添加事件监听器来响应认证状态变化
  function setupInvestorCertificationListener() {
    window.addEventListener('storage', (event) => {
      if (event.key === 'qualifiedInvestor') {
        checkInvestorCertification()
      }
    })
    
    // 添加自定义事件监听器，用于同一个标签页内的状态同步
    window.addEventListener('investorCertificationChanged', () => {
      checkInvestorCertification()
    })
  }

onMounted(() => {
  const status = localStorage.getItem('quantLogin')
  if (status === '123') {
    logged.value = true
    userText.value = '已登录（123）'
    showFund.value = true
    // 强制检查并设置认证状态
    isQualifiedInvestor.value = localStorage.getItem('qualifiedInvestor') === 'certified'
    // 设置认证状态变化监听
    setupInvestorCertificationListener()
  } else {
    // 如果没有登录，确保认证状态为false
    isQualifiedInvestor.value = false
  }
  // 如果未登录，默认显示登录弹窗以与原始静态页面行为一致
  if (!logged.value) showLogin.value = true
  // lazy set loading attribute for any images already rendered (redundant with loading attr)
  try {
    document.querySelectorAll('.goods-img').forEach(img => img.setAttribute('loading', 'lazy'))
  } catch (e) {}
})

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

function closeLogin() { showLogin.value = false }

let menuTimeout = null
let hideTimeout = null

function onMenuEnter() {
  if (!logged.value) return
  clearTimeout(hideTimeout)
  menuTimeout = setTimeout(() => {
    showUserMenu.value = true
  }, 300) // 300ms延迟显示
}

function onMenuLeave() {
  clearTimeout(menuTimeout)
  hideTimeout = setTimeout(() => {
    if (showUserMenu.value) {
      showUserMenu.value = false
    }
  }, 200) // 200ms延迟隐藏
}

function onDropdownEnter() {
  clearTimeout(hideTimeout)
}

function onDropdownLeave() {
  hideTimeout = setTimeout(() => {
    showUserMenu.value = false
  }, 200) // 200ms延迟隐藏
}

function toggleUserMenu() { 
  if (!logged.value) {
    showLogin.value = true 
    showUserMenu.value = false
  } else {
    clearTimeout(menuTimeout)
    clearTimeout(hideTimeout)
    showUserMenu.value = !showUserMenu.value
  }
}

function logout() {
  logged.value = false
  userText.value = '登录/注册'
  showFund.value = false
  showUserMenu.value = false
  localStorage.removeItem('quantLogin')
}

function confirmRiskTip() {
  showRiskTip.value = false
  logged.value = true
  userText.value = '已登录（123）'
  localStorage.setItem('quantLogin', '123')
  showFund.value = true
  showUserMenu.value = false
  // 强制检查认证状态
  isQualifiedInvestor.value = localStorage.getItem('qualifiedInvestor') === 'certified'
}

function goToUserProfile() {
  showUserMenu.value = false
  router.push('/profile')
}

function goToCart() {
  if (!logged.value) {
    alert('请先登录后查看购物车')
    showLogin.value = true
    return
  }
  router.push('/shop/cart')
}

function goToOrders() {
  if (!logged.value) {
    alert('请先登录后查看订单')
    showLogin.value = true
    return
  }
  router.push('/shop/orders')
}

function go(id) {
  activeCategory.value = id
  const el = document.getElementById(id)
  if (el) window.scrollTo({ top: el.offsetTop - 100, behavior: 'smooth' })
}
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
.header-opt a{color:white;text-decoration:none;font-size:14px;position:relative}
.cart-link { position: relative; }
.header-opt{position:relative}
.user-menu-container{position:relative;display:inline-block}
.header-opt .user-btn{background-color:white;color:#ffffff;padding:6px 12px;border-radius:4px;cursor:pointer;position:relative}
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
#factor.section-title,
#strategy.section-title,
#fund.section-title,
#advisor.section-title,
#course.section-title,
#book.section-title,
#talent.section-title {
  color: #ffffff;
  transform: translateX(-1px);
}
.goods-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:20px;margin-bottom:30px}
.goods-card{background-color:white;border-radius:8px;overflow:hidden;border:1px solid #ffb380;transition:transform .2s}
.goods-card:hover{transform:translateY(-5px);box-shadow:0 4px 12px rgba(255,127,36,.15)}
.goods-img{width:100%;height:160px;object-fit:cover}
.goods-info{padding:15px}
.goods-name{font-size:16px;margin-bottom:8px;color:#333;display:-webkit-box;-webkit-line-clamp:2;line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.goods-tag{display:inline-flex;align-items:center;justify-content:center;height:24px;line-height:1;background-color:#ff7f24;color:#ffffff;font-size:12px;padding:0 8px;border-radius:4px;margin-bottom:8px;vertical-align:middle;transform:translateX(-1px)}
.goods-price{font-size:18px;color:#ff7f24;font-weight:bold;margin-bottom:10px;display:block}
.category-item.fund{display:none}
.buy-btn,.detail-btn{flex:1;padding:8px 0;border-radius:4px;font-size:14px;cursor:pointer;border:none}
.buy-btn{background-color:#ff7f24;color:white}
.detail-btn{background-color:white;color:#ff7f24;border:1px solid #ff7f24}
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
/* 购物车徽章样式 */
.cart-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #ff4d4f;
  color: white;
  border-radius: 10px;
  min-width: 18px;
  height: 18px;
  font-size: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  line-height: 1;
}

/* 购物车链接悬停效果 */
.cart-link:hover {
  opacity: 0.8;
}

</style>
