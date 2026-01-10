<template>
  <!-- 头部导航 -->
  <div class="stock-data-container" style="background: #fff8f0; min-height: 100vh;">
    <header class="header">
      <router-link to="/" class="logo">量化牛牛 - 股票数据中心</router-link>
      <div class="header-nav">
        <router-link to="/quant-analysis">量化策略</router-link>
        <div class="user-menu-container" @mouseenter="onMenuEnter" @mouseleave="onMenuLeave">
          <div class="user-btn" @click="toggleUserMenu">{{ userText }}</div>
          <div class="user-dropdown" v-show="showUserMenu && logged" @mouseenter="onDropdownEnter" @mouseleave="onDropdownLeave">
            <div class="dropdown-item" @click="goToUserProfile">个人主页</div>
            <div class="dropdown-item logout" @click="handleLogout">退出登录</div>
          </div>
        </div>
      </div>
    </header>

    <!-- 数据筛选栏 -->
    <div class="filter-bar">
      <div class="filter-item">
        <span class="filter-label">市场：</span>
        <select class="filter-select" v-model="selectedMarket">
          <option value="all">全部市场</option>
          <option value="sh">沪市</option>
          <option value="sz">深市</option>
          <option value="cyb">创业板</option>
          <option value="kcb">科创板</option>
        </select>
      </div>
      <div class="filter-item">
        <span class="filter-label">排序：</span>
        <select class="filter-select" v-model="selectedSort">
          <option value="rise">涨幅↑</option>
          <option value="fall">跌幅↓</option>
          <option value="volume">成交量↑</option>
          <option value="amount">成交额↑</option>
        </select>
      </div>
      <div class="filter-item">
        <span class="filter-label">涨跌幅：</span>
        <select class="filter-select" v-model="selectedChange">
          <option value="all">全部</option>
          <option value="gt5">>5%</option>
          <option value="bt0-5">0%-5%</option>
          <option value="bt-5-0">-5%-0%</option>
          <option value="lt-5"><-5%</option>
        </select>
      </div>
      <input 
        type="text" 
        class="search-input" 
        placeholder="搜索股票代码/名称"
        v-model="searchKeyword"
        @keypress="handleSearch"
      >
      <button class="refresh-btn" @click="refreshData">刷新数据</button>
    </div>

    <!-- 主容器 -->
    <div class="container">
      <!-- 左侧核心数据区 -->
      <div class="left-area">
        <!-- 大盘指数概览 -->
        <div class="market-overview">
          <div class="overview-title">大盘指数</div>
          <div class="index-grid">
            <div 
              v-for="index in marketIndexes" 
              :key="index.code" 
              class="index-item"
            >
              <div class="index-name">{{ index.name }}</div>
              <div class="index-price" :class="index.pct_change >= 0 ? 'rise' : 'fall'">{{ index.price.toFixed(2) }}</div>
              <div class="index-change" :class="index.pct_change >= 0 ? 'rise' : 'fall'">
                {{ index.pct_change >= 0 ? '+' : '' }}{{ index.pct_change.toFixed(2) }}%
              </div>
            </div>
          </div>
        </div>

        <!-- 个股数据表格 -->
        <div class="stock-table-wrap">
          <div class="table-title">个股行情（实时更新）</div>
          <table class="stock-table">
            <thead>
              <tr>
                <th>代码</th>
                <th>名称</th>
                <th>最新价</th>
                <th>涨跌幅</th>
                <th>涨跌额</th>
                <th>开盘价</th>
                <th>最高价</th>
                <th>最低价</th>
                <th>成交量(手)</th>
                <th>成交额(万)</th>
                <th>换手率</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="stock in stockData" 
                :key="stock.code"
                @click="selectStockForKline(stock.code, stock.name)"
                style="cursor: pointer;"
              >
                <td class="stock-code">{{ stock.code }}</td>
                <td>{{ stock.name }}</td>
                <td :class="stock.pct_change >= 0 ? 'rise' : 'fall'">{{ stock.price.toFixed(2) }}</td>
                <td :class="stock.pct_change >= 0 ? 'rise' : 'fall'">
                  {{ stock.pct_change >= 0 ? '+' : '' }}{{ stock.pct_change.toFixed(2) }}%
                </td>
                <td :class="stock.pct_change >= 0 ? 'rise' : 'fall'">
                  {{ stock.pct_change >= 0 ? '+' : '' }}{{ (stock.price * stock.pct_change / 100).toFixed(2) }}
                </td>
                <td>{{ (stock.price * (1 - stock.pct_change / 100 * 0.5)).toFixed(2) }}</td>
                <td>{{ (stock.price * (1 + Math.abs(stock.pct_change) / 100 * 0.3)).toFixed(2) }}</td>
                <td>{{ (stock.price * (1 - Math.abs(stock.pct_change) / 100 * 0.3)).toFixed(2) }}</td>
                <td>{{ Math.floor(stock.turnover / stock.price / 100).toLocaleString() }}</td>
                <td>{{ (stock.turnover / 10000).toFixed(2) }}</td>
                <td>{{ (Math.random() * 2).toFixed(2) }}%</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- K线图区域 -->
        <div class="kline-area">
          <div class="kline-title">个股K线图（{{ selectedStockName }} - {{ selectedStockCode }}）</div>
          <div class="kline-placeholder">
            <div v-if="klineData.length > 0">
              <div style="text-align: center; padding: 20px;">
                <p style="font-size: 18px; margin-bottom: 15px;">日K线图（最近{{ klineData.length }}个交易日）</p>
                <div style="margin: 20px 0;">
                  <p style="margin: 8px 0;"><strong>最新收盘价：</strong>{{ latestKline.close.toFixed(2) }}</p>
                  <p style="margin: 8px 0;"><strong>开盘：</strong>{{ latestKline.open.toFixed(2)}}
                    | <strong>最高：</strong>{{ latestKline.high.toFixed(2)}} 
                    | <strong>最低：</strong>{{ latestKline.low.toFixed(2)}}</p>
                  <p style="margin: 8px 0;"><strong>成交量：</strong>{{ latestKline.vol.toLocaleString()}}手 
                    | <strong>成交额：</strong>{{(latestKline.amount / 10000).toFixed(2)}}万元</p>
                </div>
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                  <p style="font-size: 16px; margin-bottom: 10px;"><strong>移动平均线：</strong></p>
                  <p style="margin: 5px 0; color: #ff7f24;">MA5: {{ ma5Value.toFixed(2) }}</p>
                  <p style="margin: 5px 0; color: #008000;">MA10: {{ ma10Value.toFixed(2) }}</p>
                  <p style="margin: 5px 0; color: #0000ff;">MA20: {{ ma20Value.toFixed(2) }}</p>
                </div>
                <p style="margin-top: 20px; color: #666; font-size: 12px;">提示：实际项目中可集成 ECharts 等图表库显示完整K线图</p>
              </div>
            </div>
            <div v-else-if="klineLoading">
              <div>加载中...</div>
            </div>
            <div v-else>
              <div>K线数据加载失败<br>请确保服务已启动且股票代码正确</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧辅助数据区 -->
      <div class="right-area">
        <!-- 热门板块 -->
        <div class="hot-sector">
          <div class="sector-title">热门板块</div>
          <div class="sector-list">
            <div class="sector-item">
              <div class="sector-name">新能源汽车</div>
              <div class="sector-change rise">+3.25%</div>
              <div class="index-change">领涨：比亚迪、宁德时代</div>
            </div>
            <div class="sector-item">
              <div class="sector-name">半导体</div>
              <div class="sector-change rise">+2.88%</div>
              <div class="index-change">领涨：中芯国际、北方华创</div>
            </div>
            <div class="sector-item">
              <div class="sector-name">白酒</div>
              <div class="sector-change fall">-0.95%</div>
              <div class="index-change">领跌：贵州茅台、五粮液</div>
            </div>
            <div class="sector-item">
              <div class="sector-name">银行</div>
              <div class="sector-change rise">+1.85%</div>
              <div class="index-change">领涨：平安银行、招商银行</div>
            </div>
            <div class="sector-item">
              <div class="sector-name">光伏</div>
              <div class="sector-change rise">+2.56%</div>
              <div class="index-change">领涨：隆基绿能、通威股份</div>
            </div>
          </div>
        </div>

        <!-- 涨跌分布 -->
        <div class="rise-fall-dist">
          <div class="dist-title">涨跌分布</div>
          <div class="dist-item">
            <span class="dist-label">涨停</span>
            <div class="dist-bar">
              <div class="dist-rise-bar" style="width: 8%;"></div>
            </div>
            <span class="dist-num">86家</span>
          </div>
          <div class="dist-item">
            <span class="dist-label">上涨</span>
            <div class="dist-bar">
              <div class="dist-rise-bar" style="width: 65%;"></div>
            </div>
            <span class="dist-num">3256家</span>
          </div>
          <div class="dist-item">
            <span class="dist-label">平盘</span>
            <div class="dist-bar">
              <div class="dist-rise-bar" style="width: 5%;"></div>
            </div>
            <span class="dist-num">258家</span>
          </div>
          <div class="dist-item">
            <span class="dist-label">下跌</span>
            <div class="dist-bar">
              <div class="dist-fall-bar" style="width: 22%;"></div>
            </div>
            <span class="dist-num">1125家</span>
          </div>
          <div class="dist-item">
            <span class="dist-label">跌停</span>
            <div class="dist-bar">
              <div class="dist-fall-bar" style="width: 2%;"></div>
            </div>
            <span class="dist-num">21家</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { getRealtimeQuotes, getDailyQuotes } from '@/services/marketService';

// 使用全局认证
const { logged, userText, openLoginModal, logout } = useAuth()

// ============================================
// 默认股票代码列表
// ============================================
// 可以修改此列表来显示不同的股票
// 支持的代码格式：6位数字（如 '000001', '600000'）
const DEFAULT_STOCK_CODES = ['000001', '600000', '300750', '601318', '002594', '600519'];

// 大盘指数代码
const INDEX_CODES = {
  '000001': '上证指数',
  '399001': '深证成指',
  '399006': '创业板指',
  '000688': '科创50',
  '000300': '沪深300',
  '000905': '中证500'
};

// 用户菜单状态
const showUserMenu = ref(false);

// 响应式数据
const marketIndexes = ref([]);
const stockData = ref([]);
const klineData = ref([]);
const selectedStockCode = ref('002594');
const selectedStockName = ref('比亚迪');
const klineLoading = ref(false);

// 筛选条件
const selectedMarket = ref('all');
const selectedSort = ref('rise');
const selectedChange = ref('all');
const searchKeyword = ref('');

// 计算属性
const latestKline = computed(() => {
  if (klineData.value.length > 0) {
    return klineData.value[klineData.value.length - 1];
  }
  return null;
});

const ma5Value = computed(() => {
  if (klineData.value.length > 0) {
    const closes = klineData.value.map(item => item.close);
    const ma5 = calculateMA(closes, 5);
    return ma5[ma5.length - 1] || 0;
  }
  return 0;
});

const ma10Value = computed(() => {
  if (klineData.value.length > 0) {
    const closes = klineData.value.map(item => item.close);
    const ma10 = calculateMA(closes, 10);
    return ma10[ma10.length - 1] || 0;
  }
  return 0;
});

const ma20Value = computed(() => {
  if (klineData.value.length > 0) {
    const closes = klineData.value.map(item => item.close);
    const ma20 = calculateMA(closes, 20);
    return ma20[ma20.length - 1] || 0;
  }
  return 0;
});

// 加载大盘指数概览
const loadMarketOverview = async () => {
  const indexCodes = Object.keys(INDEX_CODES);
  
  try {
    const result = await getRealtimeQuotes(indexCodes);
    
    if (result.success && result.data) {
      const data = result.data.data || result.data;
      if (data && data.length > 0) {
        marketIndexes.value = data.map(item => {
          const name = INDEX_CODES[item.code] || item.name;
          return { ...item, name };
        });
      } else {
        console.error('暂无指数数据');
      }
    } else {
      console.error('加载大盘指数失败:', result.message);
    }
  } catch (error) {
    console.error('加载大盘指数失败:', error);
  }
};

// 加载股票数据
const loadStockData = async (codes = DEFAULT_STOCK_CODES) => {
  try {
    const result = await getRealtimeQuotes(codes);
    
    if (result.success && result.data) {
      const data = result.data.data || result.data;
      stockData.value = data || [];
      
      // 如果有失败的代码，显示提示
      const failedCodes = result.data.failed_codes;
      if (failedCodes && failedCodes.length > 0) {
        console.warn('部分股票数据获取失败:', failedCodes);
      }
    } else {
      console.error('加载股票数据失败:', result.message);
    }
  } catch (error) {
    console.error('加载股票数据失败:', error);
  }
};

// 加载K线数据
const loadKlineData = async (code, name) => {
  klineLoading.value = true;
  
  // 计算日期范围（最近30天）
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 30);
  
  const startDateStr = formatDate(startDate);
  const endDateStr = formatDate(endDate);
  
  try {
    const result = await getDailyQuotes({
      codes: [code],
      start_date: startDateStr,
      end_date: endDateStr
    });
    
    if (result.success && result.data) {
      const data = result.data.data || result.data;
      klineData.value = data || [];
    } else {
      console.error('加载K线数据失败:', result.message);
      klineData.value = [];
    }
  } catch (error) {
    console.error('加载K线数据失败:', error);
    klineData.value = [];
  } finally {
    klineLoading.value = false;
  }
};

// 选择股票用于K线图
const selectStockForKline = (code, name) => {
  selectedStockCode.value = code;
  selectedStockName.value = name;
  loadKlineData(code, name);
};

// 刷新数据
const refreshData = () => {
  loadMarketOverview();
  loadStockData();
  loadKlineData(selectedStockCode.value, selectedStockName.value);
};

// 搜索股票
const handleSearch = (event) => {
  if (event.key === 'Enter') {
    if (searchKeyword.value.trim()) {
      if (/^\d{6}$/.test(searchKeyword.value.trim())) {
        loadStockData([searchKeyword.value.trim()]);
      } else {
        console.log('股票名称搜索功能需要先获取股票列表，请输入6位股票代码');
      }
    } else {
      loadStockData();
    }
  }
};

// 计算移动平均线
const calculateMA = (data, period) => {
  const result = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(null);
    } else {
      const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
      result.push(sum / period);
    }
  }
  return result;
};

// 格式化日期为 YYYYMMDD
const formatDate = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}${month}${day}`;
};

const router = useRouter();

// 用户菜单交互
let menuTimeout = null;
let hideTimeout = null;

function onMenuEnter() {
  if (!logged.value) return;
  clearTimeout(hideTimeout);
  menuTimeout = setTimeout(() => {
    showUserMenu.value = true;
  }, 300); // 300ms延迟显示
}

function onMenuLeave() {
  clearTimeout(menuTimeout);
  hideTimeout = setTimeout(() => {
    if (showUserMenu.value) {
      showUserMenu.value = false;
    }
  }, 200); // 200ms延迟隐藏
}

function onDropdownEnter() {
  clearTimeout(hideTimeout);
}

function onDropdownLeave() {
  hideTimeout = setTimeout(() => {
    showUserMenu.value = false;
  }, 200); // 200ms延迟隐藏
}

function toggleUserMenu() { 
  if (!logged.value) {
    openLoginModal()
    showUserMenu.value = false;
  } else {
    clearTimeout(menuTimeout);
    clearTimeout(hideTimeout);
    showUserMenu.value = !showUserMenu.value;
  }
}

function handleLogout() {
  logout();
  showUserMenu.value = false;
}

function goToUserProfile() {
  showUserMenu.value = false;
  router.push('/profile');
}

// 页面加载时初始化数据
onMounted(() => {
  loadMarketOverview();
  loadStockData();
  
  // 页面加载时加载默认K线图
  setTimeout(() => {
    loadKlineData(selectedStockCode.value, selectedStockName.value);
  }, 1000);
});

// ============================================
// 使用说明
// ============================================
// 1. 确保 data-service 服务已启动（默认端口 8000）
// 2. 点击"刷新数据"按钮可以重新加载所有数据
// 3. 点击表格中的股票行可以查看该股票的K线图
// 4. 在搜索框输入6位股票代码可以查询特定股票
// 5. 如果数据加载失败，请检查：
//    - data-service 服务是否正常运行
//    - API_BASE_URL 配置是否正确
//    - 浏览器控制台是否有错误信息
</script>

<style scoped>
.stock-data-container {
  background-color: #fff8f0;
  min-height: 100vh;
}

.header {
  background-color: #ff7f24;
  padding: 12px 20px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 99;
}

.logo {
  font-size: 22px;
  font-weight: bold;
  color: white;
  text-decoration: none; /* 去除默认下划线 */
}

.logo:hover {
  text-decoration: underline; /* 鼠标悬停时显示下划线 */
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-nav a {
  color: white;
  text-decoration: none;
  font-size: 14px;
}

.header-nav .active {
  text-decoration: underline;
}

.header-nav .user-btn {
  background-color: white;
  color: #ff7f24;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.filter-bar {
  background-color: white;
  padding: 15px 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
  border-bottom: 1px solid #ffb380;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-label {
  color: #666;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ffb380;
  border-radius: 4px;
  outline: none;
  color: #333;
}

.filter-select:focus {
  border-color: #ff7f24;
}

.search-input {
  flex: 1;
  min-width: 200px;
  padding: 8px 15px;
  border: 1px solid #ffb380;
  border-radius: 4px;
  outline: none;
}

.search-input:focus {
  border-color: #ff7f24;
}

.refresh-btn {
  background-color: #fff3e6;
  color: #ff7f24;
  border: 1px solid #ff7f24;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn:hover {
  background-color: #ffe8cc;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
  display: grid;
  grid-template-columns: 3fr 1fr;
  gap: 20px;
}

.market-overview {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #ffb380;
  margin-bottom: 20px;
}

.overview-title {
  font-size: 18px;
  color: #ff7f24;
  font-weight: bold;
  margin-bottom: 15px;
  border-bottom: 1px solid #fff3e6;
  padding-bottom: 10px;
}

.index-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 15px;
}

.index-item {
  padding: 12px;
  border-radius: 6px;
  background-color: #fff8f0;
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
  z-index: 9999;
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
  outline: none;
}

.login-form input:focus {
  border-color: #ff7f24;
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
  margin-bottom: 10px;
}

.user-menu-container {
  position: relative;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #ffb380;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  min-width: 120px;
}

.dropdown-item {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #fff3e6;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: #fff8f0;
}

.dropdown-item.logout {
  color: #ff4500;
}

.index-name {
  font-size: 16px;
  margin-bottom: 8px;
}

.index-price {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 5px;
}

.rise {
  color: #ff4500;
}

.fall {
  color: #008000;
}

.index-change {
  font-size: 14px;
}

.stock-table-wrap {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #ffb380;
  overflow-x: auto;
  margin-bottom: 20px;
}

.table-title {
  font-size: 18px;
  color: #ff7f24;
  font-weight: bold;
  margin-bottom: 15px;
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
}

.stock-table th {
  background-color: #fff3e6;
  color: #ff7f24;
  padding: 12px 8px;
  text-align: left;
  border-bottom: 2px solid #ffb380;
}

.stock-table td {
  padding: 12px 8px;
  border-bottom: 1px solid #fff3e6;
}

.stock-table tr:hover {
  background-color: #fff8f0;
}

.stock-code {
  color: #666;
}

.kline-area {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #ffb380;
  margin-bottom: 20px;
}

.kline-title {
  font-size: 18px;
  color: #ff7f24;
  font-weight: bold;
  margin-bottom: 15px;
  border-bottom: 1px solid #fff3e6;
  padding-bottom: 10px;
}

.kline-placeholder {
  width: 100%;
  height: 400px;
  background-color: #f5f5f5;
  border-radius: 6px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #ff7f24;
  font-size: 16px;
}

.hot-sector {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #ffb380;
  height: fit-content;
}

.sector-title {
  font-size: 18px;
  color: #ff7f24;
  font-weight: bold;
  margin-bottom: 15px;
  border-bottom: 1px solid #fff3e6;
  padding-bottom: 10px;
}

.sector-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sector-item {
  padding: 10px;
  border-radius: 6px;
  background-color: #fff8f0;
}

.sector-name {
  font-size: 15px;
  margin-bottom: 5px;
}

.sector-change {
  font-size: 14px;
  font-weight: bold;
}

.rise-fall-dist {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #ffb380;
  margin-top: 20px;
  height: fit-content;
}

.dist-title {
  font-size: 18px;
  color: #ff7f24;
  font-weight: bold;
  margin-bottom: 15px;
  border-bottom: 1px solid #fff3e6;
  padding-bottom: 10px;
}

.dist-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.dist-label {
  color: #666;
}

.dist-bar {
  flex: 1;
  height: 12px;
  background-color: #fff3e6;
  border-radius: 6px;
  margin: 0 10px;
  overflow: hidden;
}

.dist-rise-bar {
  height: 100%;
  background-color: #ff4500;
}

.dist-fall-bar {
  height: 100%;
  background-color: #008000;
}

.dist-num {
  color: #333;
  font-weight: bold;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #ff7f24;
  font-size: 16px;
}

.error-message {
  background-color: #ffe8cc;
  color: #ff4500;
  padding: 12px;
  border-radius: 4px;
  margin: 10px 0;
  border: 1px solid #ff7f24;
}

/* 响应式适配 */
@media (max-width: 1024px) {
  .container {
    grid-template-columns: 1fr;
  }
  .index-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
}

@media (max-width: 768px) {
  .filter-bar {
    gap: 10px;
  }
  .filter-item {
    width: 100%;
  }
  .stock-table th, .stock-table td {
    padding: 8px 4px;
    font-size: 12px;
  }
  .kline-placeholder {
    height: 300px;
  }
}
</style>