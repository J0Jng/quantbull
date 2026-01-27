<template>
  <div class="fund-ranking-page">
    <!-- 顶部栏 -->
    <header class="top-bar">
      <div class="container">
        <div class="top-left">
          <h1 class="logo">量化牛牛</h1>
          <span class="slogan">专业理财平台</span>
        </div>
        <div class="top-middle">
          <input
            v-model="keyword"
            type="text"
            placeholder="输入基金代码、名称或关键词"
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button class="search-btn" @click="handleSearch">搜索</button>
        </div>
        <div class="top-right">
          <div class="user-menu-container" @mouseenter="onMenuEnter" @mouseleave="onMenuLeave">
            <div class="user-btn" @click="toggleUserMenu">{{ userText }}</div>
            <div class="user-dropdown" v-show="showUserMenu && logged" @mouseenter="onDropdownEnter" @mouseleave="onDropdownLeave">
              <div class="dropdown-item" @click="goToUserProfile">个人主页</div>
              <div class="dropdown-item logout" @click="handleLogout">退出登录</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 导航菜单 -->
    <nav class="main-nav">
      <div class="container">
        <ul class="nav-list">
          <li><router-link to="/">首页</router-link></li>
          <li><router-link to="/finance-channel">财经频道</router-link></li>
          <li><router-link to="/daily-insight">每日内参</router-link></li>
          <li><router-link to="/shop">商城</router-link></li>
          <li><router-link to="/fund-ranking">基金排行榜</router-link></li>
          <li><router-link to="/stock-data">数据中心</router-link></li>
          <li><router-link to="/niu-model">牛牛大模型</router-link></li>
        </ul>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="container">
        <!-- 页面标题 -->
        <h2 class="section-title">基金排行榜</h2>
        
        <!-- 风险提示 -->
        <div class="risk-notice">
          <p>⚠️ 投资有风险，入市需谨慎 | 过往业绩不代表未来收益</p>
        </div>

        <!-- 公募基金排行榜 -->
        <section class="public-fund-section">
          <h3 class="sub-title">公募基金排行榜</h3>
          
          <!-- 筛选和排序工具栏 -->
          <div class="filter-toolbar">
            <div class="filter-group">
              <label>基金类型：</label>
              <select v-model="publicFilter.fund_type" class="filter-select">
                <option value="">全部</option>
                <option value="stock">股票型基金</option>
                <option value="hybrid">混合型基金</option>
                <option value="bond">债券型基金</option>
                <option value="monetary">货币型基金</option>
              </select>
              
              <label>收益率区间：</label>
              <select v-model="publicFilter.return_sign" class="filter-select">
                <option value="">全部</option>
                <option value="positive">正收益</option>
                <option value="negative">负收益</option>
              </select>
              
              <label>排序方式：</label>
              <select v-model="publicFilter.sort_by" class="filter-select">
                <option value="default">默认</option>
                <option value="return1w">近1周收益率</option>
                <option value="return1m">近1月收益率</option>
                <option value="return3m">近3月收益率</option>
                <option value="return1y">近1年收益率</option>
              </select>
            </div>
          </div>
          
          <!-- 公募基金排行榜表格 -->
          <div class="fund-rank-table">
            <div class="table-header">
              <div class="rank-col">排名</div>
              <div class="name-col">基金名称</div>
              <div class="type-col">基金类型</div>
              <div class="nav-col">单位净值</div>
              <div class="change-col">日涨跌幅</div>
              <div class="return-col">近1周</div>
              <div class="return-col">近1月</div>
              <div class="return-col">近3月</div>
              <div class="return-col">近6月</div>
              <div class="return-col">近1年</div>
              <div class="return-col">近3年</div>
              <div class="action-col">操作</div>
            </div>
            
            <div 
              v-for="(fund, index) in publicFunds" 
              :key="index" 
              class="table-row"
              @click="showFundDetail(fund)"
            >
              <div class="rank-col">
                <span :class="getRankClass(index)">{{ index + 1 }}</span>
              </div>
              <div class="name-col">{{ fund.name }}</div>
              <div class="type-col">{{ fund.type }}</div>
              <div class="nav-col">{{ fund.nav }}</div>
              <div :class="['change-col', fund.change >= 0 ? 'red' : 'green']">
                {{ fund.change >= 0 ? '+' : '' }}{{ fund.change }}%
              </div>
              <div :class="['return-col', fund.return1w >= 0 ? 'red' : 'green']">
                {{ fund.return1w >= 0 ? '+' : '' }}{{ fund.return1w }}%
              </div>
              <div :class="['return-col', fund.return1m >= 0 ? 'red' : 'green']">
                {{ fund.return1m >= 0 ? '+' : '' }}{{ fund.return1m }}%
              </div>
              <div :class="['return-col', fund.return3m >= 0 ? 'red' : 'green']">
                {{ fund.return3m >= 0 ? '+' : '' }}{{ fund.return3m }}%
              </div>
              <div :class="['return-col', fund.return6m >= 0 ? 'red' : 'green']">
                {{ fund.return6m >= 0 ? '+' : '' }}{{ fund.return6m }}%
              </div>
              <div :class="['return-col', fund.return1y >= 0 ? 'red' : 'green']">
                {{ fund.return1y >= 0 ? '+' : '' }}{{ fund.return1y }}%
              </div>
              <div :class="['return-col', fund.return3y >= 0 ? 'red' : 'green']">
                {{ fund.return3y >= 0 ? '+' : '' }}{{ fund.return3y }}%
              </div>
              <div class="action-col">
                <button class="fav-btn small" @click.stop="toggleFavorite(fund)">收藏</button>
              </div>
            </div>
          </div>
        </section>

        <!-- 基金详情弹窗 -->
        <div v-if="showDetailModal" class="modal-overlay" @click="closeDetailModal">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h3>{{ selectedFund.name }}</h3>
              <button class="close-btn" @click="closeDetailModal">×</button>
            </div>
            <div class="modal-body">
              <div class="fund-info">
                <p v-if="hasValue(selectedFund.type || selectedFund.strategy)"><strong>基金类型：</strong>{{ selectedFund.type || selectedFund.strategy }}</p>
                <p v-if="hasValue(selectedFund.nav)"><strong>单位净值：</strong>{{ selectedFund.nav }}</p>
                <p v-if="hasValue(selectedFund.change)"><strong>日涨跌幅：</strong>{{ formatPercent(selectedFund.change) }}</p>
                <p v-if="hasValue(selectedFund.return1y)"><strong>近1年收益率：</strong>{{ formatPercent(selectedFund.return1y) }}</p>
                <p v-if="hasValue(selectedFund.established)"><strong>成立时间：</strong>{{ selectedFund.established }}</p>
                <p v-if="hasValue(selectedFund.annualizedReturn)"><strong>年化收益率：</strong>{{ formatPercent(selectedFund.annualizedReturn) }}</p>
                <p v-if="hasValue(selectedFund.maxDrawdown)"><strong>最大回撤：</strong>{{ formatPercent(selectedFund.maxDrawdown, false) }}</p>
                <p v-if="hasValue(selectedFund.sharpeRatio)"><strong>夏普比率：</strong>{{ formatNumber(selectedFund.sharpeRatio) }}</p>
              </div>
            </div>
          </div>
        </div>

      </div>
    </main>

    <!-- 页脚 -->
    <footer class="page-footer">
      <div class="container">
        <p>以上内容仅供参考，不构成投资建议 请遵循国家法律法规投资</p>
        <p>Copyright © 2025 量化牛牛 版权所有</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { getPublicFundRanking } from '@/services/fundRankingService'

// 使用全局认证
const { logged, userText, openLoginModal, logout } = useAuth()

const router = useRouter()
const showUserMenu = ref(false)

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
    openLoginModal()
    showUserMenu.value = false
  } else {
    clearTimeout(menuTimeout)
    clearTimeout(hideTimeout)
    showUserMenu.value = !showUserMenu.value
  }
}

function handleLogout() {
  logout()
  showUserMenu.value = false
}

function goToUserProfile() {
  showUserMenu.value = false
  router.push('/profile')
}

const keyword = ref('')

// 公募/私募数据（由后端接口提供）
const publicFunds = ref([])
const publicTotal = ref(0)

const loadingPublic = ref(false)
const errorPublic = ref('')

const publicFilter = ref({
  fund_type: '',
  return_sign: '',
  sort_by: 'default'
})


// 模态框相关状态
const showDetailModal = ref(false);
const selectedFund = ref({});

const hasValue = (value) => value === 0 || value === 0.0 || (value !== null && value !== undefined && value !== '')

const formatPercent = (value, withSign = true) => {
  if (!hasValue(value)) return ''
  const sign = withSign && value >= 0 ? '+' : ''
  return `${sign}${value}%`
}

const formatNumber = (value) => (hasValue(value) ? String(value) : '')

// 获取排名样式
const getRankClass = (index) => {
  if (index === 0) return 'rank-first';
  if (index === 1) return 'rank-second';
  if (index === 2) return 'rank-third';
  return 'rank-normal';
};

// 显示基金详情
const showFundDetail = (fund) => {
  selectedFund.value = fund;
  showDetailModal.value = true;
};

// 关闭详情模态框
const closeDetailModal = () => {
  showDetailModal.value = false;
};

// 收藏功能
const toggleFavorite = (fund) => {
  // 这里可以实现收藏逻辑
  alert(`已${fund.isFavorite ? '取消收藏' : '收藏'} ${fund.name}`);
};

// 显示咨询模态框
const showConsultModal = (fund) => {
  alert(`已向 ${fund.name} 发送咨询请求`);
};


async function loadPublicFunds(options = {}) {
  loadingPublic.value = true
  errorPublic.value = ''
  try {
    const params = {
      fund_type: publicFilter.value.fund_type,
      return_sign: publicFilter.value.return_sign,
      sort_by: publicFilter.value.sort_by,
      order: 'desc',
      keyword: keyword.value,
      page: 1,
      page_size: 50,
      ...(options.refresh ? { refresh: true } : {})
    }

    const result = await getPublicFundRanking(params)
    if (!result.success) {
      errorPublic.value = result.message || '获取公募基金排行榜失败'
      publicFunds.value = []
      publicTotal.value = 0
      return
    }

    const payload = result.data?.data
    publicFunds.value = payload?.items || []
    publicTotal.value = payload?.total || 0
  } catch (e) {
    errorPublic.value = e?.message || '获取公募基金排行榜失败'
    publicFunds.value = []
    publicTotal.value = 0
  } finally {
    loadingPublic.value = false
  }
}

function handleSearch() {
  loadPublicFunds({ refresh: true })
}

watch(
  () => [publicFilter.value.fund_type, publicFilter.value.return_sign, publicFilter.value.sort_by],
  () => {
    loadPublicFunds()
  }
)

onMounted(async () => {
  await loadPublicFunds()
})
</script>

<style scoped>
/* 认证提示样式 */
.qualification-prompt {
  background: #fff8e1;
  border: 1px solid #ffd54f;
  padding: 20px;
  margin: 10px 0 20px 0;
  border-radius: 4px;
  color: #5d4037;
}

.prompt-content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.prompt-detail {
  margin: 15px 0;
  font-size: 14px;
}

.qualification-list {
  text-align: left;
  margin: 15px auto;
  max-width: 400px;
  padding-left: 20px;
}

.qualification-list li {
  margin-bottom: 8px;
}

.verify-btn {
  background-color: #ff7f00;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 15px;
}

.verify-btn:hover {
  background-color: #ff6a00;
}

/* 基础样式 */
.fund-ranking-page {
  padding: 0;
  background: #fff8f0;
}

.top-bar {
  height: 60px;
  line-height: 60px;
  background: #fff8f0;
  border-bottom: 1px solid #f0f0f0;
}

.top-left {
  float: left;
}

.logo {
  font-size: 22px;
  color: #ff7f00;
  font-weight: bold;
  display: inline-block;
}

.slogan {
  font-size: 12px;
  color: #999;
  margin-left: 5px;
}

.top-middle {
  float: left;
  margin-left: 40px;
}

.search-input {
  width: 350px;
  height: 36px;
  padding: 0 12px;
  border: 2px solid #ff7f00;
  border-radius: 4px 0 0 4px;
  vertical-align: middle;
  font-size: 14px;
}

.search-btn {
  height: 36px;
  width: 80px;
  background: #ff7f00;
  color: #fff;
  border: none;
  border-radius: 0 4px 4px 0;
  vertical-align: middle;
  cursor: pointer;
  font-size: 14px;
}

.top-right {
  float: right;
  font-size: 14px;
}

.login-btn, .register-btn {
  margin-left: 20px;
}

/* 登录弹窗样式 */
.login-modal {
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

.login-box {
  width: 90%;
  max-width: 400px;
  background: white;
  border-radius: 10px;
  padding: 30px;
  position: relative;
  border: 2px solid #ff7f24;
}

.close-login {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 24px;
  color: #ff7f24;
  cursor: pointer;
}

.login-title {
  font-size: 22px;
  color: #ff7f24;
  text-align: center;
  margin-bottom: 20px;
  font-weight: bold;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.login-form input {
  padding: 12px 15px;
  border: 1px solid #ffb380;
  border-radius: 6px;
}

.login-btn {
  background-color: #ff7f24;
  color: white;
  border: none;
  padding: 12px 0;
  border-radius: 6px;
  cursor: pointer;
}

.login-btn:hover {
  background-color: #ff6a00;
}

.login-tips {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 10px;
}

.error-tips {
  color: #ff4500;
  text-align: center;
  margin-bottom: 15px;
}

/* 用户菜单样式 */
.user-menu-container {
  position: relative;
  display: inline-block;
}

.user-btn {
  background-color: white;
  color: #ff7f00;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  min-width: 80px;
  text-align: center;
  border: 1px solid #ff7f00;
}

.user-menu-container:hover .user-btn {
  background-color: #f5f5f5;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  margin-top: 5px;
  min-width: 120px;
}

.dropdown-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
}

.dropdown-item:hover {
  background-color: #f5f5f5;
}

.dropdown-item.logout {
  color: #ff4444;
  border-bottom: none;
}

.dropdown-item.logout:hover {
  background-color: #ffe6e6;
}

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
  z-index: 10001;
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

.register-btn {
  color: #ff7f00;
}

.main-nav {
  height: 40px;
  line-height: 40px;
  background: #fff8f0;
  border-bottom: 2px solid #ff7f00;
}

.nav-list {
  display: flex;
}

.nav-list li {
  margin-right: 30px;
}

.nav-list li a {
  font-size: 14px;
  color: #333;
  padding: 0 2px;
}

.nav-list li a.active, .nav-list li a:hover {
  color: #ff7f00;
  border-bottom: 2px solid #ff7f00;
}

.main-content {
  padding: 15px 0;
  background: #fff8f0;
}

.section-title {
  font-size: 24px;
  color: #fff;
  background: #ff7f00;
  padding: 4px 12px;
  border-radius: 10px;
  margin: 15px 0;
  display: inline-block;
}

.sub-title {
  font-size: 20px;
  color: #ff7f00;
  margin: 20px 0 10px 0;
  padding-left: 10px;
  border-left: 4px solid #ff7f00;
}

.risk-notice {
  background: #fff8e1;
  border: 1px solid #ffd54f;
  padding: 10px;
  margin: 10px 0 20px 0;
  border-radius: 4px;
  color: #5d4037;
}

.private-notice {
  color: #e65100;
  font-weight: bold;
  margin-bottom: 10px;
  font-size: 14px;
}

.filter-toolbar {
  background: #fff;
  padding: 10px;
  margin-bottom: 10px;
  border-radius: 4px;
  border: 1px solid #eee;
}

.filter-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-group label {
  font-size: 14px;
  color: #666;
}

.filter-select {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.fund-rank-table {
  background: #fff;
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #eee;
  margin-bottom: 20px;
}

.table-header {
  display: flex;
  background: #f5f5f5;
  border-bottom: 1px solid #eee;
  font-weight: bold;
  padding: 10px 0;
}

.table-row {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: #fff6ee;
}

.rank-col {
  width: 6%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.name-col {
  width: 18%;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: 10px;
}

.type-col, .strategy-col {
  width: 10%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-col, .change-col, .return-col, .risk-col, .established-col {
  width: 8%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-col {
  width: 12%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.rank-first {
  color: #ff5722;
  font-weight: bold;
  font-size: 18px;
}

.rank-second {
  color: #ff9800;
  font-weight: bold;
  font-size: 18px;
}

.rank-third {
  color: #4caf50;
  font-weight: bold;
  font-size: 18px;
}

.rank-normal {
  color: #666;
  font-weight: normal;
  font-size: 16px;
}

.green {
  color: #00b300;
}

.red {
  color: #ff3333;
}

.fav-btn, .buy-btn, .consult-btn {
  font-size: 12px;
  padding: 4px 8px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  margin: 0 2px;
}

.fav-btn {
  background: #fff;
  color: #ff7f00;
  border: 1px solid #ff7f00;
}

.buy-btn {
  background: #ff7f00;
  color: #fff;
}

.consult-btn {
  background: #2196f3;
  color: #fff;
}

.confirm-btn {
  background: #ff7f00;
  color: #fff;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}

.cancel-btn {
  background: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-header .close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.fund-info p {
  margin: 8px 0;
  line-height: 1.5;
}

.qualification-form {
  margin: 15px 0;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}

.modal-actions {
  margin-top: 20px;
  text-align: center;
}

.page-footer {
  background: #333;
  color: #fff;
  padding: 110px 0;
  margin-top: 30px;
  width: 100%;
  box-sizing: border-box;
}

.page-footer .container p {
  text-align: center;
  font-size: 12px;
  color: #aaa;
  margin: 5px 0;
}
</style>