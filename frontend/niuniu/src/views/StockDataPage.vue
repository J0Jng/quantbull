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
          <div class="table-title">
            个股行情
            <span v-if="stockLoading" style="margin-left: 10px; color: #999; font-size: 14px;">加载中...</span>
            <span v-else-if="rawStockData.length > 0" style="margin-left: 10px; color: #999; font-size: 14px;">
              (共 {{ rawStockData.length }} 只)
            </span>
          </div>
          <table class="stock-table">
            <thead>
              <tr>
                <th>代码</th>
                <th>名称</th>
                <th>最新价</th>
                <th>涨跌幅</th>
                <th>行业</th>
                <th>换手率</th>
                <th>成交额(万)</th>
                <th>更新时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="stockLoading">
                <td colspan="8" style="text-align: center; padding: 20px; color: #999;">
                  数据加载中...
                </td>
              </tr>
              <tr v-else-if="filteredStockData.length === 0">
                <td colspan="8" style="text-align: center; padding: 20px; color: #999;">
                  {{ rawStockData.length === 0 ? '暂无数据' : '无符合条件的股票' }}
                </td>
              </tr>
              <tr 
                v-else
                v-for="stock in pagedStockData" 
                :key="stock.symbol"
                @click="selectStockForKline(stock.symbol, stock.name)"
                style="cursor: pointer;"
                :class="{ 'selected-row': stock.symbol === selectedStockCode }"
              >
                <td class="stock-code">{{ stock.symbol }}</td>
                <td>{{ stock.name }}</td>
                <td :class="stock.pct_change >= 0 ? 'rise' : 'fall'">
                  {{ stock.price ? stock.price.toFixed(2) : '--' }}
                </td>
                <td :class="stock.pct_change >= 0 ? 'rise' : 'fall'">
                  {{ stock.pct_change >= 0 ? '+' : '' }}{{ stock.pct_change ? stock.pct_change.toFixed(2) : '0.00' }}%
                </td>
                <td>{{ stock.industry || '--' }}</td>
                <td>{{ stock.turnover_rate ? stock.turnover_rate.toFixed(2) + '%' : '--' }}</td>
                <td>{{ stock.turnover ? (stock.turnover / 10000).toFixed(2) : '--' }}</td>
                <td style="font-size: 12px; color: #999;">{{ stock.update_time || '--' }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="filteredStockData.length > 0" class="pagination">
            <button class="page-btn" :disabled="currentPage === 1" @click="goToPrevPage">上一页</button>
            <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
            <button class="page-btn" :disabled="currentPage === totalPages" @click="goToNextPage">下一页</button>
          </div>
        </div>

        <!-- K线图区域 -->
        <div class="kline-area">
          <div class="kline-title">
            个股K线图
            <span v-if="selectedStockName">
              （{{ selectedStockName }} - {{ selectedStockCode }}）
            </span>
            <span v-else style="color: #999;">（请点击表格中的股票查看K线）</span>
          </div>
          <div v-if="klineLoading" class="kline-placeholder">
            <div style="color: #ff7f24;">K线数据加载中...</div>
          </div>
          <div v-else-if="klineData.length === 0" class="kline-placeholder">
            <div style="color: #999;">
              <div v-if="!selectedStockCode">请点击表格中的股票查看K线图</div>
              <div v-else>K线数据加载失败<br>请确保服务已启动且股票代码正确</div>
            </div>
          </div>
          <div v-else>
            <!-- ECharts 图表容器 -->
            <div ref="chartContainer" style="width: 100%; height: 500px;"></div>
            
            <!-- 最新交易数据摘要 -->
            <div style="margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 6px;">
              <p style="font-size: 16px; margin-bottom: 10px; color: #333;">
                <strong>最新交易日数据（{{ latestKline ? formatTradeDate(latestKline.trade_date) : '--' }}）</strong>
              </p>
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
                <div>
                  <span style="color: #666;">收盘价：</span>
                  <span style="font-weight: bold;">{{ latestKline ? latestKline.close.toFixed(2) : '--' }}</span>
                </div>
                <div>
                  <span style="color: #666;">开盘价：</span>
                  <span>{{ latestKline ? latestKline.open.toFixed(2) : '--' }}</span>
                </div>
                <div>
                  <span style="color: #666;">最高价：</span>
                  <span>{{ latestKline ? latestKline.high.toFixed(2) : '--' }}</span>
                </div>
                <div>
                  <span style="color: #666;">最低价：</span>
                  <span>{{ latestKline ? latestKline.low.toFixed(2) : '--' }}</span>
                </div>
                <div>
                  <span style="color: #666;">成交量：</span>
                  <span>{{ latestKline ? latestKline.vol.toLocaleString() : '--' }}手</span>
                </div>
                <div>
                  <span style="color: #666;">成交额：</span>
                  <span>{{ latestKline ? (latestKline.amount / 10000).toFixed(2) : '--' }}万元</span>
                </div>
              </div>
              <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid #ddd;">
                <span style="color: #666;">均线：</span>
                <span style="color: #ff7f24; margin-right: 15px;">MA5: {{ ma5Value.toFixed(2) }}</span>
                <span style="color: #008000; margin-right: 15px;">MA10: {{ ma10Value.toFixed(2) }}</span>
                <span style="color: #0000ff;">MA20: {{ ma20Value.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧辅助数据区 -->
      <div class="right-area">
        <!-- 热门板块 -->
        <div class="hot-sector">
          <div class="sector-title">热门板块</div>
          <div v-if="sectorsLoading" class="loading" style="padding: 20px; text-align: center;">
            加载中...
          </div>
          <div v-else-if="sectorsError || hotSectors.length === 0" class="data-missing">
            ⚠️ 行业数据尚未生成<br>
            <span style="font-size: 12px; color: #666;">请联系后台预热数据或稍后重试</span>
          </div>
          <div v-else class="sector-list">
            <div v-for="sector in hotSectors" :key="sector.name" class="sector-item">
              <div class="sector-name">{{ sector.name }}</div>
              <div class="sector-change" :class="sector.change !== null && sector.change >= 0 ? 'rise' : 'fall'">
                {{ sector.change !== null ? (sector.change >= 0 ? '+' : '') + sector.change.toFixed(2) + '%' : '--' }}
              </div>
              <div class="sector-leaders">
                指标：{{ sector.leaders }}
              </div>
              <div class="sector-metrics">
                <span>分数：{{ formatMetric(sector.score, 4) }}</span>
                <span>净利YoY：{{ formatMetric(sector.avg_netprofit_yoy, 2, '%') }}</span>
                <span>营收YoY：{{ formatMetric(sector.avg_revenue_yoy, 2, '%') }}</span>
                <span>ROE YoY：{{ formatMetric(sector.avg_roe_yoy, 2, '%') }}</span>
                <span>样本：{{ sector.stock_count }}只</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 涨跌分布 -->
        <div class="rise-fall-dist">
          <div class="dist-title">涨跌分布</div>
          <div v-if="statsError || marketStats.total === 0" class="data-missing">
            ⚠️ 统计数据加载中...
          </div>
          <div v-else>
            <div class="dist-item">
              <span class="dist-label">涨停</span>
              <div class="dist-bar">
                <div class="dist-rise-bar" :style="`width: ${statsPercentages.upLimit}%;`"></div>
              </div>
              <span class="dist-num">{{ marketStats.upLimit }}家</span>
            </div>
            <div class="dist-item">
              <span class="dist-label">上涨</span>
              <div class="dist-bar">
                <div class="dist-rise-bar" :style="`width: ${statsPercentages.up}%;`"></div>
              </div>
              <span class="dist-num">{{ marketStats.up }}家</span>
            </div>
            <div class="dist-item">
              <span class="dist-label">平盘</span>
              <div class="dist-bar">
                <div class="dist-rise-bar" :style="`width: ${statsPercentages.flat}%;`"></div>
              </div>
              <span class="dist-num">{{ marketStats.flat }}家</span>
            </div>
            <div class="dist-item">
              <span class="dist-label">下跌</span>
              <div class="dist-bar">
                <div class="dist-fall-bar" :style="`width: ${statsPercentages.down}%;`"></div>
              </div>
              <span class="dist-num">{{ marketStats.down }}家</span>
            </div>
            <div class="dist-item">
              <span class="dist-label">跌停</span>
              <div class="dist-bar">
                <div class="dist-fall-bar" :style="`width: ${statsPercentages.downLimit}%;`"></div>
              </div>
              <span class="dist-num">{{ marketStats.downLimit }}家</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/composables/useAuth';
import { getMarketOverview, getStockSnapshotList, getDailyQuotes } from '@/services/marketService';
import { getIndustryRank } from '@/services/fundamentalsService';
import * as echarts from 'echarts';

// 使用全局认证
const { logged, userText, openLoginModal, logout } = useAuth()

// ============================================
// 数据解包工具函数
// ============================================
const getEnvelopeData = (resp) => {
  if (resp && typeof resp === 'object' && 'code' in resp && 'data' in resp) {
    return resp.data;
  }
  return resp;
};

// 用户菜单状态
const showUserMenu = ref(false);

// 响应式数据
const marketIndexes = ref([]);
const currentTradeDate = ref(''); // 当前交易日
const rawStockData = ref([]); // 原始股票数据（用于筛选）
const klineData = ref([]);
const selectedStockCode = ref('');
const selectedStockName = ref('');
const klineLoading = ref(false);
const overviewLoading = ref(false);
const stockLoading = ref(false);

// 热门板块数据
const hotSectors = ref([]);
const sectorsLoading = ref(false);
const sectorsError = ref(false);

// 涨跌分布数据
const marketStats = ref({
  upLimit: 0,
  up: 0,
  flat: 0,
  down: 0,
  downLimit: 0,
  total: 0
});
const statsLoading = ref(false);
const statsError = ref(false);

// 筛选条件
const selectedMarket = ref('all');
const selectedSort = ref('rise');
const selectedChange = ref('all');
const searchKeyword = ref('');
const itemsPerPage = 10;
const currentPage = ref(1);

// ECharts 实例
let chartInstance = null;
const chartContainer = ref(null);

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

const formatMetric = (value, digits, suffix = '') => {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '--';
  }
  return `${Number(value).toFixed(digits)}${suffix}`;
};

// 筛选后的股票数据
const filteredStockData = computed(() => {
  let result = [...rawStockData.value];
  
  // 市场筛选
  if (selectedMarket.value !== 'all') {
    result = result.filter(stock => {
      const code = stock.symbol || stock.code;
      switch (selectedMarket.value) {
        case 'sh': return code.startsWith('60');
        case 'sz': return code.startsWith('00') && !code.startsWith('300');
        case 'cyb': return code.startsWith('300');
        case 'kcb': return code.startsWith('688');
        default: return true;
      }
    });
  }
  
  // 涨跌幅筛选
  if (selectedChange.value !== 'all') {
    result = result.filter(stock => {
      const pct = stock.pct_change;
      switch (selectedChange.value) {
        case 'gt5': return pct > 5;
        case 'bt0-5': return pct >= 0 && pct <= 5;
        case 'bt-5-0': return pct >= -5 && pct < 0;
        case 'lt-5': return pct < -5;
        default: return true;
      }
    });
  }
  
  // 搜索关键词过滤
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.trim().toLowerCase();
    result = result.filter(stock => {
      const code = stock.symbol || stock.code;
      const name = stock.name || '';
      return code.includes(keyword) || name.toLowerCase().includes(keyword);
    });
  }
  
  // 排序
  result.sort((a, b) => {
    switch (selectedSort.value) {
      case 'rise': return b.pct_change - a.pct_change;
      case 'fall': return a.pct_change - b.pct_change;
      case 'volume': return (b.turnover || 0) - (a.turnover || 0);
      case 'amount': return (b.turnover || 0) - (a.turnover || 0);
      default: return 0;
    }
  });
  
  return result;
});

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(filteredStockData.value.length / itemsPerPage));
});

const pagedStockData = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  return filteredStockData.value.slice(start, start + itemsPerPage);
});

// 涨跌分布统计计算属性
const statsPercentages = computed(() => {
  const total = marketStats.value.total || 1;
  return {
    upLimit: Math.round((marketStats.value.upLimit / total) * 100),
    up: Math.round((marketStats.value.up / total) * 100),
    flat: Math.round((marketStats.value.flat / total) * 100),
    down: Math.round((marketStats.value.down / total) * 100),
    downLimit: Math.round((marketStats.value.downLimit / total) * 100)
  };
});

// 加载大盘指数概览
const loadMarketOverview = async () => {
  overviewLoading.value = true;
  
  try {
    const result = await getMarketOverview();
    
    if (result.success) {
      const data = getEnvelopeData(result.data);
      
      if (data) {
        // 保存交易日期
        currentTradeDate.value = data.trade_date || '';
        
        // 设置指数数据
        if (data.indices && data.indices.length > 0) {
          marketIndexes.value = data.indices.map(item => ({
            code: item.symbol || item.code,
            name: item.name,
            price: item.close || item.price || 0,
            pct_change: item.pct_change || 0
          }));
        } else {
          console.warn('市场概览中没有指数数据');
          marketIndexes.value = [];
        }
      }
    } else {
      console.error('加载大盘指数失败:', result.message);
      marketIndexes.value = [];
    }
  } catch (error) {
    console.error('加载大盘指数失败:', error);
    marketIndexes.value = [];
  } finally {
    overviewLoading.value = false;
  }
};

// 加载股票列表数据（使用聚合快照接口）
const loadStockData = async (forceRefresh = false) => {
  stockLoading.value = true;
  
  try {
    // 调用聚合快照接口，一次性获取所有需要的字段
    // 首次加载或手动刷新时，触发后台数据拉取
    // 不传 date 参数，让后端自动使用数据库中的最新交易日
    const result = await getStockSnapshotList({
      limit: 1000,  // 获取全部股票数据
      min_turnover: 0,
      sort: selectedSort.value || 'amount',
      refresh: forceRefresh
    });
    
    if (result.success) {
      const data = getEnvelopeData(result.data);
      let stockList = Array.isArray(data) ? data : (data?.data || []);
      
      if (stockList.length > 0) {
        // 直接使用聚合后的数据，无需在前端 merge
        rawStockData.value = stockList.map(stock => ({
          symbol: stock.symbol || stock.code,
          code: stock.code || stock.symbol,
          name: stock.name,
          industry: stock.industry,
          price: stock.price,
          latest_price: stock.latest_price || stock.price,
          pct_change: stock.pct_change,
          turnover: stock.turnover,
          turnover_rate: stock.turnover_rate,
          update_time: stock.update_time || ''
        }));
        
        // 计算涨跌分布统计
        calculateMarketStats(rawStockData.value);
        
        // 如果还没有选中股票，选择第一只
        if (!selectedStockCode.value && rawStockData.value.length > 0) {
          const firstStock = rawStockData.value[0];
          selectedStockCode.value = firstStock.symbol;
          selectedStockName.value = firstStock.name;
        }
      } else {
        console.warn('股票列表为空');
        rawStockData.value = [];
      }
    } else {
      console.error('加载股票数据失败:', result.message);
      rawStockData.value = [];
    }
  } catch (error) {
    console.error('加载股票数据失败:', error);
    rawStockData.value = [];
  } finally {
    stockLoading.value = false;
  }
};

// 加载热门板块数据
const loadHotSectors = async () => {
  sectorsLoading.value = true;
  sectorsError.value = false;
  
  try {
    const result = await getIndustryRank(null, true);
    
    if (result.success) {
      const data = getEnvelopeData(result.data);
      const industries = data?.data || [];
      
      if (industries.length > 0) {
        // 使用行业排名数据直接展示（不依赖股票列表）
        const sectorsWithData = industries.map(industry => {
          const score = industry.score ?? null;
          return {
          name: industry.industry,
          change: score === null ? null : score * 100,
          leaders: '行业强度',
          score,
          avg_netprofit_yoy: industry.avg_netprofit_yoy ?? null,
          avg_revenue_yoy: industry.avg_revenue_yoy ?? null,
          avg_roe_yoy: industry.avg_roe_yoy ?? null,
          stock_count: industry.stock_count ?? 0
          };
        });
        
        hotSectors.value = sectorsWithData;
      } else {
        hotSectors.value = [];
        sectorsError.value = true;
        console.warn('行业排名数据为空，可能需要后台预热数据');
      }
    } else {
      console.error('加载热门板块失败:', result.message);
      hotSectors.value = [];
      sectorsError.value = true;
    }
  } catch (error) {
    console.error('加载热门板块失败:', error);
    sectorsError.value = true;
    hotSectors.value = [];
  } finally {
    sectorsLoading.value = false;
  }
};

// 计算涨跌分布统计
const calculateMarketStats = (stockList) => {
  if (!stockList || stockList.length === 0) {
    statsError.value = true;
    return;
  }
  
  statsError.value = false;
  const stats = {
    upLimit: 0,
    up: 0,
    flat: 0,
    down: 0,
    downLimit: 0,
    total: stockList.length
  };
  
  stockList.forEach(stock => {
    const pct = stock.pct_change;
    if (pct >= 9.9) {
      stats.upLimit++;
    } else if (pct > 0.1) {
      stats.up++;
    } else if (pct >= -0.1 && pct <= 0.1) {
      stats.flat++;
    } else if (pct > -9.9) {
      stats.down++;
    } else {
      stats.downLimit++;
    }
  });
  
  marketStats.value = stats;
};

// 规范化日线数据（兼容 YYYY-MM-DD / YYYYMMDD）
const normalizeDailyItem = (item) => {
  const tradeDate = String(item.trade_date || '').replace(/-/g, '');
  return {
    ...item,
    trade_date: tradeDate,
    open: Number(item.open) || 0,
    close: Number(item.close) || 0,
    low: Number(item.low) || 0,
    high: Number(item.high) || 0,
    vol: Number(item.vol) || 0,
    amount: Number(item.amount) || 0
  };
};

// 加载K线数据并渲染图表
const loadKlineData = async (code, name) => {
  if (!code) return;
  
  klineLoading.value = true;
  
  // 计算日期范围（最近120个交易日，实际取180天范围）
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - 180);
  
  const startDateStr = formatDate(startDate);
  const endDateStr = formatDate(endDate);
  
  try {
    const result = await getDailyQuotes({
      codes: [code],
      start_date: startDateStr,
      end_date: endDateStr
    });
    
    if (result.success) {
      const data = getEnvelopeData(result.data);
      let dailyData = data?.data || data || [];
      
      if (Array.isArray(dailyData) && dailyData.length > 0) {
        // 统一数据格式
        dailyData = dailyData.map(normalizeDailyItem);
        // 按交易日期升序排序（Tushare 常为降序）
        dailyData.sort((a, b) => {
          const dateA = String(a.trade_date);
          const dateB = String(b.trade_date);
          return dateA.localeCompare(dateB);
        });
        
        // 只取最近120个交易日
        if (dailyData.length > 120) {
          dailyData = dailyData.slice(-120);
        }
        
        klineData.value = dailyData;
        
        // 等待 DOM 更新后渲染图表
        await nextTick();
        renderKlineChart();
      } else {
        console.warn('K线数据为空');
        klineData.value = [];
      }
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

// 渲染 K 线图表
const renderKlineChart = () => {
  if (!chartContainer.value || klineData.value.length === 0) return;
  
  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
  
  // 创建新实例
  chartInstance = echarts.init(chartContainer.value);
  
  // 准备数据
  const dates = klineData.value.map(item => {
    const dateStr = String(item.trade_date || '').replace(/-/g, '');
    if (dateStr.length === 8) {
      return `${dateStr.substring(4, 6)}-${dateStr.substring(6, 8)}`;
    }
    return dateStr;
  });
  
  const values = klineData.value.map(item => [
    item.open,
    item.close,
    item.low,
    item.high
  ]);
  
  const volumes = klineData.value.map(item => item.vol || 0);
  
  // 计算 MA 线
  const closes = klineData.value.map(item => item.close);
  const ma5 = calculateMA(closes, 5);
  const ma10 = calculateMA(closes, 10);
  const ma20 = calculateMA(closes, 20);
  
  // 配置选项
  const option = {
    backgroundColor: '#fff',
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: function(params) {
        let result = params[0].name + '<br/>';
        params.forEach(param => {
          if (param.seriesType === 'candlestick') {
            const data = param.data;
            if (Array.isArray(data)) {
              result += `开盘: ${data[0]}<br/>`;
              result += `收盘: ${data[1]}<br/>`;
              result += `最低: ${data[2]}<br/>`;
              result += `最高: ${data[3]}<br/>`;
            }
          } else if (param.seriesType === 'line') {
            result += `${param.seriesName}: ${param.data !== null ? param.data.toFixed(2) : '--'}<br/>`;
          } else if (param.seriesType === 'bar') {
            result += `成交量: ${param.data}手<br/>`;
          }
        });
        return result;
      }
    },
    legend: {
      data: ['日K', 'MA5', 'MA10', 'MA20', '成交量'],
      top: 10
    },
    grid: [
      {
        left: '10%',
        right: '8%',
        top: '15%',
        height: '50%'
      },
      {
        left: '10%',
        right: '8%',
        top: '70%',
        height: '15%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        scale: true,
        boundaryGap: false,
        axisLine: { onZero: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 0,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        top: '90%',
        start: 0,
        end: 100
      }
    ],
    series: [
      {
        name: '日K',
        type: 'candlestick',
        data: values,
        itemStyle: {
          color: '#ef232a',
          color0: '#14b143',
          borderColor: '#ef232a',
          borderColor0: '#14b143'
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: ma5,
        smooth: true,
        lineStyle: {
          opacity: 0.8,
          width: 1,
          color: '#ff7f24'
        },
        showSymbol: false
      },
      {
        name: 'MA10',
        type: 'line',
        data: ma10,
        smooth: true,
        lineStyle: {
          opacity: 0.8,
          width: 1,
          color: '#008000'
        },
        showSymbol: false
      },
      {
        name: 'MA20',
        type: 'line',
        data: ma20,
        smooth: true,
        lineStyle: {
          opacity: 0.8,
          width: 1,
          color: '#0000ff'
        },
        showSymbol: false
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: {
          color: function(params) {
            const index = params.dataIndex;
            if (index === 0) return '#ef232a';
            const current = klineData.value[index];
            return current.close >= current.open ? '#ef232a' : '#14b143';
          }
        }
      }
    ]
  };
  
  chartInstance.setOption(option);
  
  // 图表初始化完成后立即适配一次
  chartInstance.resize();
};

// 数据或容器就绪后重新渲染（避免容器尺寸为 0）
watch([klineData, chartContainer], async () => {
  if (!chartContainer.value || klineData.value.length === 0) return;
  await nextTick();
  requestAnimationFrame(() => {
    renderKlineChart();
  });
});

// 筛选条件变化时重置分页
watch([selectedMarket, selectedSort, selectedChange, searchKeyword, rawStockData], () => {
  currentPage.value = 1;
});

watch(totalPages, (val) => {
  if (currentPage.value > val) {
    currentPage.value = val;
  }
});

// 窗口大小调整处理
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize();
  }
};

// 选择股票用于K线图
const selectStockForKline = (code, name) => {
  selectedStockCode.value = code;
  selectedStockName.value = name;
  loadKlineData(code, name);
};

const goToPrevPage = () => {
  if (currentPage.value > 1) currentPage.value -= 1;
};

const goToNextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value += 1;
};

// 刷新数据
const refreshData = async () => {
  await loadMarketOverview();
  // 强制刷新：触发后台数据拉取
  await loadStockData(true);
  await loadHotSectors();
  
  if (selectedStockCode.value) {
    await loadKlineData(selectedStockCode.value, selectedStockName.value);
  }
};

// 搜索股票
const handleSearch = async (event) => {
  if (event.key === 'Enter') {
    const keyword = searchKeyword.value.trim();
    
    if (!keyword) {
      // 清空搜索，重新加载完整列表
      await loadStockData();
      return;
    }
    
    // 如果是6位数字代码，可以精确查询
    if (/^\d{6}$/.test(keyword)) {
      try {
        // 使用快照接口查询单个股票
        const result = await getStockSnapshotList({
          limit: 1000  // 获取更多数据用于搜索
        });
        
        if (result.success) {
          const data = getEnvelopeData(result.data);
          const snapshotList = data?.data || data || [];
          
          // 查找匹配的股票
          const matchedStock = snapshotList.find(s => 
            s.code === keyword || s.symbol === keyword
          );
          
          if (matchedStock) {
            // 更新股票列表（单独显示）
            rawStockData.value = [{
              symbol: matchedStock.symbol || matchedStock.code,
              code: matchedStock.code || matchedStock.symbol,
              name: matchedStock.name,
              industry: matchedStock.industry,
              price: matchedStock.price,
              latest_price: matchedStock.latest_price || matchedStock.price,
              pct_change: matchedStock.pct_change,
              turnover: matchedStock.turnover || 0,
              turnover_rate: matchedStock.turnover_rate,
              update_time: matchedStock.update_time || ''
            }];
            
            // 同时加载 K 线
            selectStockForKline(matchedStock.code, matchedStock.name);
            
            return;
          }
        }
        
        console.warn('未找到股票:', keyword);
      } catch (error) {
        console.error('搜索股票失败:', error);
      }
    }
    
    // 否则作为关键词筛选（由计算属性 filteredStockData 处理）
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

// 格式化交易日期显示
const formatTradeDate = (dateStr) => {
  if (!dateStr) return '--';
  const str = String(dateStr);
  if (str.length === 8) {
    return `${str.substring(0, 4)}-${str.substring(4, 6)}-${str.substring(6, 8)}`;
  }
  return str;
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
onMounted(async () => {
  window.addEventListener('resize', handleResize);
  // 按依赖顺序加载
  await loadMarketOverview();
  
  // 首次尝试从数据库加载
  await loadStockData(false);
  
  // 如果没有数据，触发后台数据刷新
  if (rawStockData.value.length === 0) {
    console.log('数据库无数据，触发后台刷新...');
    await loadStockData(true);
  }
  
  // 股票数据加载完成后再加载板块数据（依赖股票的行业映射）
  await loadHotSectors();
  
  // 如果有选中的股票，加载 K 线
  if (selectedStockCode.value) {
    await loadKlineData(selectedStockCode.value, selectedStockName.value);
  }
});

// 组件卸载时清理
onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (chartInstance) {
    chartInstance.dispose();
    chartInstance = null;
  }
});
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

.stock-table tr.selected-row {
  background-color: #ffe8cc;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 12px;
}

.page-btn {
  background-color: #fff3e6;
  color: #ff7f24;
  border: 1px solid #ff7f24;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
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
  text-align: center;
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

.sector-leaders {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
}

.sector-metrics {
  margin-top: 6px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 4px 10px;
  font-size: 12px;
  color: #666;
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

.data-missing {
  text-align: center;
  padding: 20px;
  color: #999;
  font-size: 14px;
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