<template>
  <div class="fund-ranking-page">
    <!-- 登录弹窗 -->
    <div class="login-modal" v-show="showLogin">
      <div class="login-box">
        <span class="close-login" @click="closeLogin">&times;</span>
        <div class="login-title">量化牛牛基金 - 登录</div>
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
          <p>尊敬的用户，您正在登录量化牛牛基金平台。投资有风险，入市需谨慎。请注意：</p>
          <ul>
            <li>基金投资可能面临市场风险、流动性风险等</li>
            <li>过去业绩不代表未来表现</li>
            <li>请根据自身风险承受能力合理配置资产</li>
            <li>建议您详细了解产品风险收益特征</li>
          </ul>
        </div>
        <button class="risk-confirm-btn" @click="confirmRiskTip">我已阅读并了解风险</button>
      </div>
    </div>

    <!-- 顶部栏 -->
    <header class="top-bar">
      <div class="container">
        <div class="top-left">
          <h1 class="logo">量化牛牛</h1>
          <span class="slogan">专业理财平台</span>
        </div>
        <div class="top-middle">
          <input type="text" placeholder="输入基金代码、名称或关键词" class="search-input" />
          <button class="search-btn">搜索</button>
        </div>
        <div class="top-right">
          <div class="user-menu-container" @mouseenter="onMenuEnter" @mouseleave="onMenuLeave">
            <div class="user-btn" @click="toggleUserMenu">{{ userText }}</div>
            <div class="user-dropdown" v-show="showUserMenu && logged" @mouseenter="onDropdownEnter" @mouseleave="onDropdownLeave">
              <div class="dropdown-item" @click="goToUserProfile">个人主页</div>
              <div class="dropdown-item logout" @click="logout">退出登录</div>
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
          <li><router-link to="/company-research">公司研报</router-link></li>
          <li><router-link to="/shop">商城</router-link></li>
          <li><router-link to="/fund-ranking" class="active">基金排行榜</router-link></li>
          <li><a href="#" style="color:#ff7f00">更多&gt;</a></li>
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
              <select class="filter-select">
                <option value="">全部</option>
                <option value="stock">股票型基金</option>
                <option value="hybrid">混合型基金</option>
                <option value="bond">债券型基金</option>
                <option value="monetary">货币型基金</option>
              </select>
              
              <label>收益率区间：</label>
              <select class="filter-select">
                <option value="">全部</option>
                <option value="positive">正收益</option>
                <option value="negative">负收益</option>
              </select>
              
              <label>排序方式：</label>
              <select class="filter-select">
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
              <div :class="['change-col', fund.change >= 0 ? 'green' : 'red']">
                {{ fund.change >= 0 ? '+' : '' }}{{ fund.change }}%
              </div>
              <div :class="['return-col', fund.return1w >= 0 ? 'green' : 'red']">
                {{ fund.return1w >= 0 ? '+' : '' }}{{ fund.return1w }}%
              </div>
              <div :class="['return-col', fund.return1m >= 0 ? 'green' : 'red']">
                {{ fund.return1m >= 0 ? '+' : '' }}{{ fund.return1m }}%
              </div>
              <div :class="['return-col', fund.return3m >= 0 ? 'green' : 'red']">
                {{ fund.return3m >= 0 ? '+' : '' }}{{ fund.return3m }}%
              </div>
              <div :class="['return-col', fund.return6m >= 0 ? 'green' : 'red']">
                {{ fund.return6m >= 0 ? '+' : '' }}{{ fund.return6m }}%
              </div>
              <div :class="['return-col', fund.return1y >= 0 ? 'green' : 'red']">
                {{ fund.return1y >= 0 ? '+' : '' }}{{ fund.return1y }}%
              </div>
              <div :class="['return-col', fund.return3y >= 0 ? 'green' : 'red']">
                {{ fund.return3y >= 0 ? '+' : '' }}{{ fund.return3y }}%
              </div>
              <div class="action-col">
                <button class="fav-btn small" @click.stop="toggleFavorite(fund)">收藏</button>
                <button class="buy-btn small" @click.stop="buyPublicFund(fund)">购买</button>
              </div>
            </div>
          </div>
        </section>

        <!-- 私募基金排行榜 -->
        <section class="private-fund-section">
          <h3 class="sub-title">私募基金排行榜</h3>
          <p class="private-notice">⚠️ 仅对合格投资者开放</p>
          
          <!-- 筛选和排序工具栏 -->
          <div class="filter-toolbar">
            <div class="filter-group">
              <label>策略类型：</label>
              <select class="filter-select">
                <option value="">全部</option>
                <option value="equity">股票策略</option>
                <option value="futures">期货策略</option>
                <option value="hedge">对冲策略</option>
                <option value="composite">复合策略</option>
              </select>
              
              <label>风险等级：</label>
              <select class="filter-select">
                <option value="">全部</option>
                <option value="low">低风险</option>
                <option value="medium">中风险</option>
                <option value="high">高风险</option>
              </select>
              
              <label>排序方式：</label>
              <select class="filter-select">
                <option value="default">默认</option>
                <option value="return1y">近1年收益率</option>
                <option value="sharpe">夏普比率</option>
                <option value="maxdrawdown">最大回撤</option>
              </select>
            </div>
          </div>
          
          <!-- 私募基金排行榜表格 -->
          <div class="fund-rank-table">
            <div class="table-header">
              <div class="rank-col">排名</div>
              <div class="name-col">基金名称</div>
              <div class="strategy-col">策略类型</div>
              <div class="established-col">成立时间</div>
              <div class="return-col">近1月</div>
              <div class="return-col">近3月</div>
              <div class="return-col">近1年</div>
              <div class="return-col">年化收益率</div>
              <div class="risk-col">最大回撤</div>
              <div class="risk-col">夏普比率</div>
              <div class="action-col">操作</div>
            </div>
            
            <div 
              v-for="(fund, index) in privateFunds" 
              :key="index" 
              class="table-row"
              @click="showFundDetail(fund)"
            >
              <div class="rank-col">
                <span :class="getRankClass(index)">{{ index + 1 }}</span>
              </div>
              <div class="name-col">{{ fund.name }}</div>
              <div class="strategy-col">{{ fund.strategy }}</div>
              <div class="established-col">{{ fund.established }}</div>
              <div class="return-col">
                {{ isQualifiedInvestor ? (fund.return1m >= 0 ? '+' : '') + fund.return1m + '%' : '认证后可见' }}
              </div>
              <div class="return-col">
                {{ isQualifiedInvestor ? (fund.return3m >= 0 ? '+' : '') + fund.return3m + '%' : '认证后可见' }}
              </div>
              <div class="return-col">
                {{ isQualifiedInvestor ? (fund.return1y >= 0 ? '+' : '') + fund.return1y + '%' : '认证后可见' }}
              </div>
              <div class="return-col">
                {{ isQualifiedInvestor ? (fund.annualizedReturn >= 0 ? '+' : '') + fund.annualizedReturn + '%' : '认证后可见' }}
              </div>
              <div class="risk-col">{{ isQualifiedInvestor ? fund.maxDrawdown + '%' : '认证后可见' }}</div>
              <div class="risk-col">{{ isQualifiedInvestor ? fund.sharpeRatio : '认证后可见' }}</div>
              <div class="action-col">
                <button class="consult-btn small" @click.stop="showConsultModal(fund)">咨询</button>
                <button class="buy-btn small" @click.stop="checkQualification(fund)">购买</button>
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
                <p><strong>基金类型：</strong>{{ selectedFund.type || selectedFund.strategy }}</p>
                <p><strong>单位净值：</strong>{{ selectedFund.nav || 'N/A' }}</p>
                <p><strong>日涨跌幅：</strong>{{ selectedFund.change ? (selectedFund.change >= 0 ? '+' : '') + selectedFund.change + '%' : 'N/A' }}</p>
                <p><strong>近1年收益率：</strong>{{ (selectedFund.return1y && isQualifiedInvestor) ? (selectedFund.return1y >= 0 ? '+' : '') + selectedFund.return1y + '%' : '认证后可见' }}</p>
                <p><strong>成立时间：</strong>{{ selectedFund.established || 'N/A' }}</p>
                <p><strong>年化收益率：</strong>{{ (selectedFund.annualizedReturn && isQualifiedInvestor) ? (selectedFund.annualizedReturn >= 0 ? '+' : '') + selectedFund.annualizedReturn + '%' : '认证后可见' }}</p>
                <p><strong>最大回撤：</strong>{{ (selectedFund.maxDrawdown && isQualifiedInvestor) ? selectedFund.maxDrawdown + '%' : '认证后可见' }}</p>
                <p><strong>夏普比率：</strong>{{ (selectedFund.sharpeRatio && isQualifiedInvestor) ? selectedFund.sharpeRatio : '认证后可见' }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 合格投资者验证弹窗 -->
        <div v-if="showQualificationModal" class="modal-overlay" @click="closeQualificationModal">
          <div class="modal-content" @click.stop>
            <div class="modal-header">
              <h3>合格投资者验证</h3>
              <button class="close-btn" @click="closeQualificationModal">×</button>
            </div>
            <div class="modal-body">
              <p>私募基金仅对合格投资者开放，购买前需要进行合格投资者认证。</p>
              <div class="qualification-form">
                <div class="form-group">
                  <label>年收入证明（万元）：</label>
                  <input type="number" v-model="qualification.income" placeholder="请输入年收入">
                </div>
                <div class="form-group">
                  <label>金融资产证明（万元）：</label>
                  <input type="number" v-model="qualification.assets" placeholder="请输入金融资产">
                </div>
                <div class="form-group">
                  <label>投资经验（年）：</label>
                  <input type="number" v-model="qualification.experience" placeholder="请输入投资经验">
                </div>
              </div>
              <div class="modal-actions">
                <button class="confirm-btn" @click="verifyQualification">提交验证</button>
                <button class="cancel-btn" @click="closeQualificationModal">取消</button>
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

// 登录相关状态
const username = ref('')
const password = ref('')
const showLogin = ref(false)
const errorVisible = ref(false)
const logged = ref(false)
const userText = ref('登录/注册')
const showUserMenu = ref(false)
const showRiskTip = ref(false)
const isQualifiedInvestor = ref(false)

const router = useRouter()

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
  showUserMenu.value = false
  localStorage.removeItem('quantLogin')
  localStorage.removeItem('qualifiedInvestor')
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

function goToUserProfile() {
  showUserMenu.value = false
  router.push('/profile')
}

onMounted(() => {
  const status = localStorage.getItem('quantLogin')
  if (status === '123') {
    logged.value = true
    userText.value = '已登录（123）'
    // 强制检查认证状态
    isQualifiedInvestor.value = localStorage.getItem('qualifiedInvestor') === 'certified'
  }
})

// 公募基金数据
const publicFunds = ref([
  { name: '中欧医疗健康混合C', type: '混合型基金', nav: '1.3609', change: 1.1, return1w: 2.9, return1m: 1.5, return3m: 4.2, return6m: 6.8, return1y: 12.5, return3y: 35.7 },
  { name: '易方达蓝筹精选混合', type: '混合型基金', nav: '4.9100', change: -0.5, return1w: -1.2, return1m: 0.8, return3m: 3.1, return6m: 5.2, return1y: 9.8, return3y: 28.6 },
  { name: '华夏能源革新股票A', type: '股票型基金', nav: '2.3179', change: 0.7, return1w: 1.8, return1m: 2.3, return3m: 5.6, return6m: 8.1, return1y: 15.2, return3y: 42.3 },
  { name: '广发科技先锋混合', type: '混合型基金', nav: '1.7856', change: 2.3, return1w: 3.2, return1m: 4.1, return3m: 7.2, return6m: 10.5, return1y: 18.7, return3y: 51.2 },
  { name: '汇添富消费行业混合', type: '混合型基金', nav: '3.2560', change: -0.8, return1w: -1.5, return1m: -0.5, return3m: 1.8, return6m: 3.2, return1y: 7.4, return3y: 22.1 },
  { name: '富国天惠成长混合', type: '混合型基金', nav: '2.8950', change: 0.3, return1w: 0.8, return1m: 1.2, return3m: 2.5, return6m: 4.8, return1y: 8.9, return3y: 26.8 },
  { name: '嘉实新兴产业股票', type: '股票型基金', nav: '2.4560', change: 1.5, return1w: 2.1, return1m: 2.8, return3m: 6.1, return6m: 9.2, return1y: 13.5, return3y: 38.4 },
  { name: '南方中证500ETF联接', type: '指数型基金', nav: '1.2345', change: -0.2, return1w: -0.5, return1m: 0.5, return3m: 2.3, return6m: 4.1, return1y: 6.8, return3y: 19.7 },
  { name: '博时黄金ETF', type: '商品基金', nav: '4.5678', change: 0.1, return1w: 0.3, return1m: 0.8, return3m: 1.5, return6m: 2.7, return1y: 4.2, return3y: 12.8 },
  { name: '招商中证白酒指数', type: '指数型基金', nav: '1.1234', change: 1.8, return1w: 2.5, return1m: 3.2, return3m: 5.8, return6m: 7.4, return1y: 11.3, return3y: 31.6 }
]);

// 私募基金数据
const privateFunds = ref([
  { name: '启林量化精选', strategy: '股票策略', established: '2018-03-15', return1m: 2.3, return3m: 5.6, return1y: 18.2, annualizedReturn: 16.8, maxDrawdown: -8.2, sharpeRatio: 1.8 },
  { name: '九坤量化对冲', strategy: '对冲策略', established: '2017-06-20', return1m: 1.8, return3m: 4.2, return1y: 15.7, annualizedReturn: 14.3, maxDrawdown: -6.5, sharpeRatio: 2.1 },
  { name: '明汯量化100', strategy: '股票策略', established: '2016-09-12', return1m: 1.5, return3m: 3.8, return1y: 17.4, annualizedReturn: 15.9, maxDrawdown: -7.1, sharpeRatio: 1.9 },
  { name: '衍复宏观对冲', strategy: '宏观策略', established: '2019-01-08', return1m: 0.9, return3m: 2.1, return1y: 12.8, annualizedReturn: 13.2, maxDrawdown: -5.3, sharpeRatio: 1.6 },
  { name: '诚奇多策略', strategy: '复合策略', established: '2018-11-30', return1m: 2.1, return3m: 4.9, return1y: 16.5, annualizedReturn: 15.7, maxDrawdown: -6.8, sharpeRatio: 1.7 },
  { name: '灵均量化选股', strategy: '股票策略', established: '2017-04-15', return1m: 1.2, return3m: 3.4, return1y: 14.2, annualizedReturn: 13.8, maxDrawdown: -7.9, sharpeRatio: 1.5 },
  { name: '淡水泉成长精选', strategy: '股票策略', established: '2015-08-22', return1m: 0.8, return3m: 2.7, return1y: 13.6, annualizedReturn: 12.9, maxDrawdown: -9.2, sharpeRatio: 1.4 },
  { name: '高毅资产', strategy: '股票策略', established: '2019-05-10', return1m: 1.6, return3m: 3.9, return1y: 15.1, annualizedReturn: 14.6, maxDrawdown: -7.5, sharpeRatio: 1.6 },
  { name: '景林全球配置', strategy: '股票策略', established: '2016-12-05', return1m: 1.3, return3m: 3.1, return1y: 12.4, annualizedReturn: 13.1, maxDrawdown: -8.7, sharpeRatio: 1.3 },
  { name: '重阳战略', strategy: '股票策略', established: '2018-07-18', return1m: 0.9, return3m: 2.5, return1y: 11.8, annualizedReturn: 12.4, maxDrawdown: -8.1, sharpeRatio: 1.2 }
]);

// 模态框相关状态
const showDetailModal = ref(false);
const showQualificationModal = ref(false);
const selectedFund = ref({});
const qualification = ref({
  income: null,
  assets: null,
  experience: null
});

// 获取排名样式
const getRankClass = (index) => {
  if (index === 0) return 'rank-first';
  if (index === 1) return 'rank-second';
  if (index === 2) return 'rank-third';
  return 'rank-normal';
};

// 显示基金详情
const showFundDetail = (fund) => {
  // 检查是否是私募基金且用户未认证
  if (fund.strategy && !isQualifiedInvestor.value) {
    if (!logged.value) {
      // 未登录，提示登录
      showLogin.value = true;
    } else {
      // 已登录但未认证，提醒去个人主页认证
      alert('需要去个人主页进行合格投资者认证');
      router.push('/profile');
    }
    return;
  }
  
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

// 检查购买资格
const checkQualification = (fund) => {
  if (!logged.value) {
    showLogin.value = true
    return
  }
  
  if (!isQualifiedInvestor.value) {
    showQualificationModal.value = true
    selectedFund.value = fund
  } else {
    // 已经认证为合格投资者，可以直接购买
    alert('您已是合格投资者，可以进行私募基金购买操作')
  }
};

// 公募基金购买函数
const buyPublicFund = (fund) => {
  if (!logged.value) {
    showLogin.value = true
    return
  }
  
  if (confirm(`确定要购买 ${fund.name} 吗？`)) {
    alert(`成功购买 ${fund.name}，金额将自动从账户中扣除`)
  }
};

// 关闭资格验证模态框
const closeQualificationModal = () => {
  showQualificationModal.value = false;
  qualification.value = { income: null, assets: null, experience: null };
};

// 验证资格
const verifyQualification = () => {
  if (qualification.value.income >= 50 || qualification.value.assets >= 300 || qualification.value.experience >= 2) {
    alert('资格验证通过，您已成为合格投资者')
    isQualifiedInvestor.value = true
    localStorage.setItem('qualifiedInvestor', 'certified')
    closeQualificationModal()
  } else {
    alert('您不符合合格投资者标准，无法购买该私募基金')
  }
};
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
  background: #f9f9f9;
}

.top-bar {
  height: 60px;
  line-height: 60px;
  background: #fff;
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
  background: #fff;
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
  background: #f9f9f9;
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