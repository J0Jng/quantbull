<template>
  <div>
    <!-- 动态风险提示弹窗 (登录弹窗已移至全局 LoginModal 组件) -->
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


    <!-- 顶部栏 -->
    <header class="top-bar">
      <div class="container">
        <div class="top-left">
          <h1 class="logo">量化牛牛</h1>
          <span class="slogan">专业理财平台</span>
        </div>
        <div class="top-right">
          <div class="user-menu-container" @mouseenter="onMenuEnter" @mouseleave="onMenuLeave">
            <div class="user-btn" @click="toggleUserMenu">{{ userText }}</div>
            <div class="user-dropdown" v-show="showUserMenu && logged" @mouseenter="onDropdownEnter" @mouseleave="onDropdownLeave">
              <div class="dropdown-item" @click="goToUserProfile">个人主页</div>
              <div class="dropdown-item logout" @click="handleLogout">退出登录</div>
            </div>
            <!-- 如果未登录，显示登录/注册选项 -->
            <div class="user-dropdown" v-show="showUserMenu && !logged" @mouseenter="onDropdownEnter" @mouseleave="onDropdownLeave">
              <div class="dropdown-item" @click="openLoginModal">登录</div>
              <div class="dropdown-item" @click="openLoginModal">注册</div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- 导航菜单 -->
    <nav class="main-nav">
      <div class="container">
        <ul class="nav-list">
          <li><a href="#" class="active">首页</a></li>
          <li><router-link to="/finance-channel">财经频道</router-link></li>
          <li><router-link to="/daily-insight">每日内参</router-link></li>
          <li><router-link to="/company-research">公司研报</router-link></li>
          <li><router-link to="/shop">商城</router-link></li>
          <li><router-link to="/fund-ranking">基金排行榜</router-link></li>
          <li><router-link to="/stock-data">股票数据中心</router-link></li>
          <li><a href="#" @click.prevent="scrollToSection('strategy-platform')">量化策略</a></li>
          <li><a href="#" style="color:#ff7f00">更多&gt;</a></li>
        </ul>
      </div>
    </nav>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="container">
        <!-- 财经头条板块 -->
        <h2 class="section-title">财经头条</h2>
        <router-link to="/news-list" class="more-link" style="float:right;margin-top:12px;font-size:14px;">更多&gt;</router-link>
        <section class="news-section">
          <!-- 加载状态 -->
          <div v-if="newsLoading && !bannerNews" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载财经新闻...</p>
          </div>
          
          <!-- 新闻内容 -->
          <template v-else>
            <div v-if="bannerNews" class="news-banner" @click="goToNewsDetail(bannerNews.id)">
              <div class="banner-text">
                <h3 class="mask-title">{{ bannerNews.title }}</h3>
                <p class="mask-desc">{{ bannerNews.summary || '暂无摘要' }}</p>
                <span class="banner-cta">查看详情</span>
              </div>
            </div>
            <div v-else class="empty-news">
              <p>{{ newsError || '暂无财经头条' }}</p>
            </div>
            <div class="news-list" v-if="newsList.length">
              <ul>
                <li v-for="news in newsList" :key="news.id">
                  <a href="#" @click.prevent="goToNewsDetail(news.id)">{{ news.title }}</a>
                </li>
              </ul>
            </div>
          </template>
        </section>


        <!-- 龙虎榜板块（新增切换内容容器） -->
        <h2 class="section-title">{{ dragonFailed ? '大盘指数' : '龙虎榜' }}</h2>
        <div v-if="!dragonFailed" class="tab-switch dragon-tab-switch">
          <a href="javascript:;" :class="{ active: dragonTab==='dragon-today' }" @click.prevent="dragonTab='dragon-today'">今日</a>
          <a href="javascript:;" :class="{ active: dragonTab==='dragon-5day' }" @click.prevent="dragonTab='dragon-5day'">5日</a>
          <a href="javascript:;" :class="{ active: dragonTab==='dragon-20day' }" @click.prevent="dragonTab='dragon-20day'">20日</a>
          <span v-if="dragonLoading" class="loading-indicator">加载中...</span>
        </div>
        <section class="dragon-board">
          <!-- 龙虎榜失败时显示大盘指数 -->
          <template v-if="dragonFailed">
            <!-- 大盘指数加载中 -->
            <div v-if="marketIndexLoading" class="loading-state">
              <div class="loading-spinner"></div>
              <p>正在加载大盘指数数据...</p>
            </div>
            <!-- 大盘指数数据 -->
            <div v-else-if="marketIndexData.length > 0" class="tab-content dragon-content">
              <table class="dragon-table">
                <thead>
                  <tr>
                    <th>指数名称</th>
                    <th>最新价</th>
                    <th>涨跌幅</th>
                    <th>涨跌额</th>
                    <th>更新时间</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in marketIndexData" :key="idx">
                    <td>{{ row.name }}</td>
                    <td>{{ row.price }}</td>
                    <td><span :class="row.change > 0 ? 'red' : 'green'">{{ row.changeText }}</span></td>
                    <td>{{ row.changeAmount }}</td>
                    <td>{{ row.updatedAt }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- 数据丢失 -->
            <div v-else class="error-state">
              <p>{{ marketIndexError || '数据丢失' }}</p>
              <button @click="loadMarketIndex" class="retry-btn">重试</button>
            </div>
          </template>
          
          <!-- 龙虎榜正常显示 -->
          <template v-else>
            <!-- 加载状态 -->
            <div v-if="dragonLoading && dragonTab==='dragon-today'" class="loading-state">
              <div class="loading-spinner"></div>
              <p>正在加载龙虎榜数据...</p>
            </div>
            
            <!-- 错误状态 -->
            <div v-else-if="dragonError && dragonTab==='dragon-today' && dragonToday.length === 0" class="error-state">
              <p>{{ dragonError }}</p>
              <button @click="loadDragonData(1)" class="retry-btn">重试</button>
            </div>
            
            <div v-show="dragonTab==='dragon-today' && !dragonLoading" class="tab-content dragon-content" id="dragon-today">
              <template v-if="dragonToday.length > 0">
                <table class="dragon-table">
                  <thead>
                    <tr>
                      <th>名称</th>
                      <th>最新价</th>
                      <th>涨跌幅</th>
                      <th>涨跌</th>
                      <th>净买入(亿)</th>
                      <th>买入额(亿)</th>
                      <th>卖出额(亿)</th>
                      <th>上榜次数</th>
                      <th>上榜理由</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in dragonToday" :key="idx">
                      <td>{{ row.name }}</td>
                      <td>{{ row.price }}</td>
                      <td><span :class="row.change>0 ? 'green' : 'red'">{{ row.changeText }}</span></td>
                      <td>{{ row.delta }}</td>
                      <td>{{ row.net }}</td>
                      <td>{{ row.buy }}</td>
                      <td>{{ row.sell }}</td>
                      <td>{{ row.appearCount }}</td>
                      <td>{{ row.reason }}</td>
                    </tr>
                  </tbody>
                </table>
              </template>
              <div v-else class="error-state">
                <p>数据丢失</p>
              </div>
            </div>

            <div v-show="dragonTab==='dragon-5day'" class="tab-content dragon-content" id="dragon-5day">
              <!-- 5日加载状态 -->
              <div v-if="dragonLoading && dragon5Data.length === 0" class="loading-state">
                <div class="loading-spinner"></div>
                <p>正在加载5日龙虎榜数据...</p>
              </div>
              <template v-else-if="dragon5.length > 0">
                <table class="dragon-table">
                  <thead>
                    <tr>
                      <th>名称</th>
                      <th>最新价</th>
                      <th>涨跌幅</th>
                      <th>涨跌</th>
                      <th>净买入(亿)</th>
                      <th>买入额(亿)</th>
                      <th>卖出额(亿)</th>
                      <th>上榜次数</th>
                      <th>上榜理由</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in dragon5" :key="idx">
                      <td>{{ row.name }}</td>
                      <td>{{ row.price }}</td>
                      <td><span :class="row.change>0 ? 'green' : 'red'">{{ row.changeText }}</span></td>
                      <td>{{ row.delta }}</td>
                      <td>{{ row.net }}</td>
                      <td>{{ row.buy }}</td>
                      <td>{{ row.sell }}</td>
                      <td>{{ row.appearCount }}</td>
                      <td>{{ row.reason }}</td>
                    </tr>
                  </tbody>
                </table>
              </template>
              <div v-else class="error-state">
                <p>数据丢失</p>
              </div>
            </div>

            <div v-show="dragonTab==='dragon-20day'" class="tab-content dragon-content" id="dragon-20day">
              <!-- 20日加载状态 -->
              <div v-if="dragonLoading && dragon20Data.length === 0" class="loading-state">
                <div class="loading-spinner"></div>
                <p>正在加载20日龙虎榜数据...</p>
              </div>
              <template v-else-if="dragon20.length > 0">
                <table class="dragon-table">
                  <thead>
                    <tr>
                      <th>名称</th>
                      <th>最新价</th>
                      <th>涨跌幅</th>
                      <th>涨跌</th>
                      <th>净买入(亿)</th>
                      <th>买入额(亿)</th>
                      <th>卖出额(亿)</th>
                      <th>上榜次数</th>
                      <th>上榜理由</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in dragon20" :key="idx">
                      <td>{{ row.name }}</td>
                      <td>{{ row.price }}</td>
                      <td><span :class="row.change>0 ? 'green' : 'red'">{{ row.changeText }}</span></td>
                      <td>{{ row.delta }}</td>
                      <td>{{ row.net }}</td>
                      <td>{{ row.buy }}</td>
                      <td>{{ row.sell }}</td>
                      <td>{{ row.appearCount }}</td>
                      <td>{{ row.reason }}</td>
                    </tr>
                  </tbody>
                </table>
              </template>
              <div v-else class="error-state">
                <p>数据丢失</p>
              </div>
            </div>
          </template>
        </section>

        <!-- 公司研报板块 -->
        <div class="section-header-inline">
          <h2 class="section-title">公司研报</h2>
          <div class="header-actions">
            <button v-if="companyReportsData.length > 0" @click="loadCompanyReports" class="refresh-icon-btn" :disabled="companyReportsLoading" title="刷新">
              <span v-if="companyReportsLoading">⟳</span>
              <span v-else>↻</span>
            </button>
            <router-link to="/company-research" class="more-link">查看全部 &gt;</router-link>
          </div>
        </div>
        <section class="company-report">
          <!-- 加载状态 -->
          <div v-if="companyReportsLoading && companyReportsData.length === 0" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载公司研报...</p>
          </div>
          
          <!-- 错误状态 -->
          <div v-else-if="companyReportsError && companyReportsData.length === 0" class="error-state">
            <p>{{ companyReportsError }}</p>
            <button @click="loadCompanyReports" class="retry-btn">重试</button>
          </div>
          
          <!-- 研报卡片 -->
          <div v-else class="report-cards">
            <div class="report-card" v-for="card in companyReportsData" :key="card.id" @click="viewCompanyReport(card)">
              <div class="card-body">
                <div class="stock-info">
                  <span class="stock-name">{{ card.company_name }}<span v-if="card.stock_code" class="stock-code-small">({{ card.stock_code }})</span></span>
                  <span :class="getRatingClass(card.rating)">{{ getRatingTag(card.rating) }}</span>
                </div>
                <div class="report-meta">
                  <span class="meta-item">{{ card.report_type === 'analysis' ? '深度分析' : '投研摘要' }}</span>
                  <span class="meta-item">{{ formatDate(card.created_at) }}</span>
                </div>
                <ul class="report-ul" v-if="card.tags && card.tags.length">
                  <li v-for="(t, i) in card.tags.slice(0, 3)" :key="i">{{ t }}</li>
                </ul>
                <div style="clear:both;"></div>
                <button class="view-btn" @click.stop="viewCompanyReport(card)">查看研报</button>
              </div>
            </div>
          </div>
          
          <!-- 空状态 -->
          <div v-if="!companyReportsLoading && !companyReportsError && companyReportsData.length === 0" class="error-state">
            <p>暂无公司研报数据</p>
            <button @click="loadCompanyReports" class="retry-btn">加载数据</button>
          </div>
        </section>

        <!-- 策略技术平台板块 -->
        <h2 class="section-title">策略技术平台</h2>
        <section id="strategy-platform" class="strategy-platform">
          <div class="platform-cards">
            <div class="platform-card orange">
              <h3>量化分析工具</h3>
              <p>多因子选股、量化回测、量化一站式平台</p>
              <router-link to="/quant-analysis">
                <button class="try-btn" style="color:#ff7f00;font-size:14px;border-radius: 100px;">立即体验</button>
              </router-link>
            </div>
            <div class="platform-card blue">
              <h3>策略管理工具</h3>
              <p>策略管理模块</p>
              <router-link to="/strategies">
                <button class="try-btn" style="color:#1e90ff;font-size:14px;border-radius: 100px;">立即体验</button>
              </router-link>
            </div>
            <div class="platform-card green">
              <h3>因子分析工具</h3>
              <p>实时分析因子，优化配置方案</p>
              <router-link to="/factors">
                <button class="try-btn" style="color:#00b300;font-size:14px;border-radius: 100px;">立即体验</button>
              </router-link>
            </div>
          </div>
        </section>

        <!-- 商城板块 -->
        <h2 class="section-title">商城</h2>
          <router-link to="/shop" class="more-link" style="float:right;margin-top:15px;font-size: 14px;">查看详情 &gt;</router-link>
        <section class="mall-section">
          <!-- 加载状态 -->
          <div v-if="mallProductsLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载商品...</p>
          </div>
          
          <!-- 商品卡片 -->
          <div v-else class="mall-cards">
            <div class="mall-card" v-for="product in mallProducts" :key="product.id">
              <div class="card-icon">
                <img :src="product.img || defaultProductImg" :alt="product.name" />
              </div>
              <div class="card-info">
                <span class="product-type-tag">{{ getProductTypeName(product.type) }}</span>
                <h4>{{ product.name }}</h4>
                <p>{{ product.description || '精选商品，品质保证' }}</p>
                <p class="price">{{ formatPrice(product.price) }}</p>
              </div>
              <button class="buy-btn" @click="router.push('/shop')">立即购买</button>
            </div>
            
            <!-- 无商品时显示默认 -->
            <template v-if="mallProducts.length === 0">
              <div class="mall-card">
                <div class="card-icon">
                  <img src="/4.png" alt="商品图标" />
                </div>
                <div class="card-info">
                  <h4>更多商品</h4>
                  <p>精选量化工具和服务，助力投资决策</p>
                  <p class="price">敬请期待</p>
                </div>
                <button class="buy-btn" @click="router.push('/shop')">查看商城</button>
              </div>
            </template>
          </div>
        </section>

        <!-- 基金排行榜板块 -->
        <div class="section-header-inline">
          <h2 class="section-title">基金排行榜</h2>
          <div class="header-actions">
            <router-link to="/fund-ranking" class="more-link" style="float:right;margin-top:15px;font-size: 14px;">查看详情 &gt;</router-link>
          </div>
        </div>
        <section class="fund-rank">
          <div v-if="fundsLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载基金排行榜...</p>
          </div>
          <div v-else-if="fundsError && funds.length === 0" class="error-state">
            <p>{{ fundsError }}</p>
            <button @click="loadFundRanking" class="retry-btn">重试</button>
          </div>
          <div v-else class="fund-list">
            <div class="fund-item fund-header">
              <div class="fund-col name-col">基金名称</div>
              <div class="fund-col data-col">单位净值</div>
              <div class="fund-col trend-col">日涨跌幅</div>
              <div class="fund-col data-col">近1周</div>
              <div class="fund-col data-col">近1月</div>
              <div class="fund-col data-col">近3月</div>
              <div class="fund-col data-col">近6月</div>
              <div class="fund-col data-col">近1年</div>
              <div class="fund-col data-col">近3年</div>
              <div class="fund-col btn-col">操作</div>
            </div>
            <div class="fund-item" v-for="(fund, idx) in funds" :key="idx">
              <div class="fund-col name-col">
                <div class="fund-name">{{ fund.name }}</div>
                <div class="fund-type">{{ fund.type }}</div>
              </div>
              <div class="fund-col data-col">
                <div class="data-value">{{ fund.nav }}</div>
                <div class="data-time">单位净值</div>
              </div>
              <div class="fund-col trend-col" :class="fund.trendColor">{{ fund.trend }}</div>

              <div class="fund-col data-col" v-for="(p, i) in fund.periods" :key="i">
                <div class="data-value" :class="p.class">{{ p.text }}</div>
              </div>

              <div class="fund-col btn-col">
                <button class="fav-btn small" @click="$router.push('/fund-ranking')">自选</button>
              </div>
            </div>
          </div>
        </section>

        <!-- 每日内参板块（新增切换内容容器） -->
        <h2 class="section-title">
          每日内参
        </h2>
        <router-link to="/daily-insight" class="more-link" style="float:right;margin-top:15px;font-size: 14px;">查看详情 &gt;</router-link>
        <div class="tab-switch report-tab-switch">
          <a 
            href="javascript:;" 
            :class="{ active: reportTab==='report-latest', disabled: !canAccessTodayReport() }" 
            @click.prevent="handleLatestTabClick"
            :title="canAccessTodayReport() ? '查看最新内参' : '今日内参需在16:00后查看'"
          >
            最新{{ canAccessTodayReport() ? '' : ' (16:00后可用)' }}
          </a>
          <a href="javascript:;" :class="{ active: reportTab==='report-yesterday' }" @click.prevent="reportTab='report-yesterday'">昨日</a>
        </div>
        <section class="daily-report">
          <!-- 加载状态 -->
          <div v-if="dailyReportLoading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载每日内参...</p>
          </div>
          
          <!-- 数据加载完成后的内容 -->
          <template v-else>
            <!-- 最新内参 -->
            <div v-show="reportTab==='report-latest'" class="tab-content report-content" id="report-latest">
              <div v-if="latestDailyReport" class="report-item">
                <h3>{{ latestDailyReport.title || '最新投资策略' }}</h3>
                <p>{{ truncateText(latestDailyReport.market_sentiment, 120) }}</p>
                <span class="design">系统 | AI分析</span>
                <span class="date">{{ formatReportDate(latestDailyReport.report_date) }}</span>
              </div>
              <div v-else class="report-item">
                <h3>{{ dailyReportError || '暂无最新内参' }}</h3>
                <p>{{ dailyReportError ? '请点击重试按钮重新加载' : '系统正在生成最新的投资策略分析，请稍后查看。' }}</p>
                <button v-if="dailyReportError" @click="loadDailyReports" class="retry-btn" style="margin-top: 10px;">重试</button>
              </div>
            </div>

            <!-- 昨日内参 -->
            <div v-show="reportTab==='report-yesterday'" class="tab-content report-content" id="report-yesterday">
              <div v-if="getYesterdayReport()" class="report-item">
                <h3>{{ getYesterdayReport().title }}</h3>
                <p>{{ truncateText(getYesterdayReport().market_sentiment, 120) }}</p>
                <span class="design">系统 | AI分析</span>
                <span class="date">{{ formatReportDate(getYesterdayReport().report_date) }}</span>
              </div>
              <div v-else class="report-item">
                <h3>暂无昨日内参</h3>
                <p>昨日投资策略分析暂未生成。</p>
                <button v-if="dailyReportError" @click="loadDailyReports" class="retry-btn" style="margin-top: 10px;">重试</button>
              </div>
            </div>

            <!-- 历史内参 -->
            <div v-show="reportTab==='report-history'" class="tab-content report-content" id="report-history">
              <template v-if="dailyReportHistory.length > 0">
                <div 
                  v-for="report in dailyReportHistory.slice(0, 3)" 
                  :key="report.id" 
                  class="report-item"
                >
                  <h3>{{ report.title }}</h3>
                  <p>{{ truncateText(report.market_sentiment, 100) }}</p>
                  <span class="design">系统 | AI分析</span>
                  <span class="date">{{ formatReportDate(report.report_date) }}</span>
                </div>
              </template>
              <div v-else class="report-item">
                <h3>暂无历史内参</h3>
                <p>历史投资策略分析暂未生成。</p>
                <button v-if="dailyReportError" @click="loadDailyReports" class="retry-btn" style="margin-top: 10px;">重试</button>
              </div>
            </div>
          </template>
        </section>

        <!-- AI智能服务入口 -->
        <h2 class="section-title">AI智能投研助手</h2>
        <a href="#" style="float:right;color:#ff7f00;margin-top:12px;font-size:14px;">更多功能 &gt;</a>
        <section class="ai-service-section">
          <div class="ai-service-cards">
            <!-- 智能新闻解读 -->
            <div class="ai-service-card" @click="openAiModal('news')">
              <div class="ai-icon news-icon">📰</div>
              <h3>智能新闻解读</h3>
              <p>基于新闻快讯生成深度解读分析</p>
              <div class="ai-tag">DeepSeek R1</div>
            </div>

            <!-- 策略代码生成 -->
            <div class="ai-service-card" @click="openAiModal('strategy')">
              <div class="ai-icon strategy-icon">💡</div>
              <h3>策略代码生成</h3>
              <p>AI生成Backtrader量化策略代码</p>
              <div class="ai-tag">Qwen2.5</div>
            </div>

            <!-- 投研摘要 -->
            <div class="ai-service-card" @click="openAiModal('summary')">
              <div class="ai-icon summary-icon">📊</div>
              <h3>智能投研摘要</h3>
              <p>生成结构化研究和投资建议</p>
              <div class="ai-tag">Qwen2.5</div>
            </div>

            <!-- 报告生成 -->
            <div class="ai-service-card" @click="openAiModal('report')">
              <div class="ai-icon report-icon">📈</div>
              <h3>公司研报生成</h3>
              <p>自动分析公司信息生成研究报告</p>
              <div class="ai-tag">智能路由</div>
            </div>
          </div>
        </section>

        <!-- AI服务模态框 -->
        <div v-if="showAiModal" class="ai-modal-overlay" @click="hideAiModal">
          <div class="ai-modal-content" @click.stop>
            <div class="ai-modal-header">
              <h3>{{ getAiModalTitle() }}</h3>
              <button class="close-btn" @click="hideAiModal">×</button>
            </div>
            <div class="ai-modal-body">
              <!-- 新闻解读 -->
              <div v-if="activeAiService === 'news'" class="ai-input-section">
                <textarea v-model="newsInput" placeholder="请输入财经新闻快讯..." rows="4"></textarea>
                <div class="ai-options">
                  <label>
                    股票代码：<input v-model="newsStockCode" placeholder="如：000001" type="text">
                  </label>
                  <button @click="generateNews" class="ai-submit-btn" :disabled="aiLoading">
                    {{ aiLoading ? '生成中...' : '生成解读' }}
                  </button>
                </div>
              </div>

              <!-- 策略生成 -->
              <div v-if="activeAiService === 'strategy'" class="ai-input-section">
                <textarea v-model="strategyInput" placeholder="请描述您的量化策略思路..." rows="4"></textarea>
                <div class="ai-options">
                  <label>
                    框架选择：
                    <select v-model="strategyFramework">
                      <option value="backtrader">Backtrader</option>
                      <option value="zipline">Zipline</option>
                    </select>
                  </label>
                    <button @click="generateStrategy" class="ai-submit-btn" :disabled="aiLoading">
                      {{ aiLoading ? '生成中...' : '生成策略' }}
                    </button>
                </div>
              </div>

              <!-- 投研摘要 -->
              <div v-if="activeAiService === 'summary'" class="ai-input-section">
                <textarea v-model="summaryInput" placeholder="请输入要摘要的投研内容..." rows="4"></textarea>
                <div class="ai-options">
                  <label>
                    摘要类型：
                    <select v-model="summaryType">
                      <option value="structured">结构化</option>
                      <option value="bullet">要点式</option>
                      <option value="paragraph">段落式</option>
                    </select>
                  </label>
                    <button @click="generateSummary" class="ai-submit-btn" :disabled="aiLoading">
                      {{ aiLoading ? '生成中...' : '生成摘要' }}
                    </button>
                </div>
              </div>

              <!-- 研报生成 -->
              <div v-if="activeAiService === 'report'" class="ai-input-section">
                <textarea v-model="reportInput" placeholder="请输入公司信息和市场数据..." rows="4"></textarea>
                <div class="ai-options">
                  <label>
                    <input type="checkbox" v-model="includeRisks"> 包含风险分析
                  </label>
                  <button @click="generateReport" class="ai-submit-btn" :disabled="aiLoading">
                    {{ aiLoading ? '生成中...' : '生成研报' }}
                  </button>
                </div>
              </div>

              <!-- 结果显示 -->
              <div v-if="aiResult" class="ai-result-section">
                <h4>AI生成结果：</h4>
                <div class="ai-result-content">
                  <pre>{{ aiResult }}</pre>
                </div>
                <div class="ai-result-meta">
                  <span>使用模型：{{ aiModel }}</span>
                  <span>生成时间：{{ new Date().toLocaleTimeString() }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- API状态指示器 -->
        <div class="api-status" :class="apiStatus">
          AI服务状态：{{ getApiStatusText() }}
        </div>
      </div>
    </main>

    <!-- 页脚 -->
    <FooterComponent />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import FooterComponent from './FooterComponent.vue'
import { getTopListSummary } from '@/services/marketService'
import { getMarketData } from '@/services/financeChannelService'
import { generateNewsAnalysis, generateStrategy as generateStrategyApi, generateSummary as generateSummaryApi, generateReport as generateReportApi } from '@/services/aiService'
import { getLatestDailyReport, getDailyReportList } from '@/services/dailyReportService'
import { getCompanyResearchList } from '@/services/companyResearchService'
import { getProducts, formatPrice as serviceFormatPrice } from '@/services/productService'
import { getHeadlines } from '@/services/newsService'
import { getPublicFundRanking } from '@/services/fundRankingService'
import http from '@/services/http'
import { useAuth } from '@/composables/useAuth'
import chatService from '@/services/chatService'
import { canAccessTodayReport } from '@/utils/accessControl'

// 使用全局认证
const { logged, userText, isQualifiedInvestor, showRiskTip, openLoginModal, logout, confirmRiskTip } = useAuth()

const search = ref('')
const dragonTab = ref('dragon-today')
const reportTab = ref('report-latest')

// 龙虎榜数据状态
const dragonLoading = ref(false)
const dragonError = ref('')
const dragonFailed = ref(false) // 龙虎榜加载失败标记

// 大盘指数数据（龙虎榜失败时显示）
const marketIndexData = ref([])
const marketIndexLoading = ref(false)
const marketIndexError = ref('')

// 每日内参数据状态
const dailyReportLoading = ref(false)
const dailyReportError = ref('')
const latestDailyReport = ref(null)
const dailyReportHistory = ref([])

// 公司研报数据状态
const companyReportsLoading = ref(false)
const companyReportsError = ref('')
const companyReportsData = ref([])

// 商城商品数据状态
const mallProducts = ref([])
const mallProductsLoading = ref(false)
const defaultProductImg = 'https://picsum.photos/400/300?random=0'

// 财经新闻数据状态
const newsLoading = ref(false)
const newsError = ref('')
const newsList = ref([])
const bannerNews = ref(null)

// 基金排行榜数据状态
const funds = ref([])
const fundsLoading = ref(false)
const fundsError = ref('')

// 用户菜单相关状态
const showUserMenu = ref(false)

const router = useRouter()

let menuTimeout = null
let hideTimeout = null

const onMenuEnter = () => {
  if (!logged.value) return
  clearTimeout(hideTimeout)
  menuTimeout = setTimeout(() => {
    showUserMenu.value = true
  }, 300) // 300ms延迟显示
}

const onMenuLeave = () => {
  clearTimeout(menuTimeout)
  hideTimeout = setTimeout(() => {
    if (showUserMenu.value) {
      showUserMenu.value = false
    }
  }, 200) // 200ms延迟隐藏
}

const onDropdownEnter = () => {
  clearTimeout(hideTimeout)
}

const onDropdownLeave = () => {
  hideTimeout = setTimeout(() => {
    showUserMenu.value = false
  }, 200) // 200ms延迟隐藏
}

const toggleUserMenu = () => {
  if (!logged.value) {
    openLoginModal()
    showUserMenu.value = false
  } else {
    clearTimeout(menuTimeout)
    clearTimeout(hideTimeout)
    showUserMenu.value = !showUserMenu.value
  }
}

const goToCompanyResearch = () => {
  router.push('/company-research')
}

// 退出登录处理
const handleLogout = () => {
  logout()
  showUserMenu.value = false
}

const goToUserProfile = () => {
  showUserMenu.value = false
  router.push('/profile')
}

// 跳转到新闻详情页
const goToNewsDetail = (id) => {
  router.push(`/news-detail/${id}`)
}

// 加载财经新闻数据
const loadNews = async () => {
  try {
    newsLoading.value = true
    newsError.value = ''
    const response = await getHeadlines({ page: 1, page_size: 6 })

    let items = []
    if (response?.items) {
      items = response.items
    } else if (response?.data?.items) {
      items = response.data.items
    } else if (Array.isArray(response)) {
      items = response
    }

    if (items.length > 0) {
      bannerNews.value = {
        id: items[0].id,
        title: items[0].title || '暂无标题',
        summary: items[0].summary || '暂无摘要',
        img: '/1.png'
      }
      newsList.value = items.slice(1).map(item => ({
        id: item.id,
        title: item.title || '暂无标题'
      }))
    } else {
      bannerNews.value = null
      newsList.value = []
    }
  } catch (e) {
    console.error('加载财经新闻失败:', e)
    newsError.value = '加载失败'
    bannerNews.value = null
    newsList.value = []
  } finally {
    newsLoading.value = false
  }
}

// 加载商城商品数据
const loadMallProducts = async () => {
  mallProductsLoading.value = true
  try {
    const result = await getProducts({ limit: 4 })
    if (result.success && result.data) {
      // 直接取前2个商品显示
      mallProducts.value = result.data.slice(0, 2)
    }
  } catch (error) {
    console.error('Failed to load mall products:', error)
  } finally {
    mallProductsLoading.value = false
  }
}

// 加载基金排行榜数据（公募）
const loadFundRanking = async () => {
  fundsLoading.value = true
  fundsError.value = ''

  try {
    const result = await getPublicFundRanking({
      sort_by: 'return1m',
      order: 'desc',
      page: 1,
      page_size: 3
    })

    if (!result.success) {
      fundsError.value = result.message || '加载基金排行榜失败'
      funds.value = []
      return
    }

    const payload = result.data?.data
    const items = payload?.items || []

    const uniqueByType = new Map()
    const fallback = []
    items.forEach((item) => {
      const typeKey = item.type || '—'
      if (!uniqueByType.has(typeKey)) {
        uniqueByType.set(typeKey, item)
      } else {
        fallback.push(item)
      }
    })

    const picked = Array.from(uniqueByType.values()).slice(0, 3)
    if (picked.length < 3) {
      picked.push(...fallback.slice(0, 3 - picked.length))
    }

    funds.value = picked.map((item, idx) => {
      const change = Number(item.change ?? 0)
      const trendText = `${change >= 0 ? '+' : ''}${change}%`
      const formatVal = (val) => {
        if (val === undefined || val === null || val === '—') return { text: '—', class: '' }
        const num = parseFloat(val)
        if (isNaN(num)) return { text: val, class: '' }
        const text = `${num >= 0 ? '+' : ''}${num.toFixed(2)}%`
        return { text, class: num < 0 ? 'green' : 'red' }
      }

      return {
        name: item.name || '—',
        type: item.type || '—',
        nav: item.nav ?? '—',
        trend: trendText,
        trendColor: trendText.includes('-') ? 'green' : 'red',
        periods: [
          formatVal(item.return1w),
          formatVal(item.return1m),
          formatVal(item.return3m),
          formatVal(item.return6m),
          formatVal(item.return1y),
          formatVal(item.return3y)
        ]
      }
    })
  } catch (error) {
    fundsError.value = error?.message || '加载基金排行榜失败'
    funds.value = []
  } finally {
    fundsLoading.value = false
  }
}

// 格式化价格
const formatPrice = (price) => {
  return serviceFormatPrice(price)
}

// 获取商品类型中文名
const getProductTypeName = (type) => {
  const typeMap = {
    'course': '课程',
    'factor': '因子',
    'strategy': '策略',
    'fund': '基金',
    'advisor': '投顾',
    'book': '书籍',
    'talent': '人才'
  }
  return typeMap[type] || '商品'
}

// 页面加载时的初始化（认证状态已在 App.vue 中初始化）
onMounted(() => {
  // 认证状态已由 useAuth 全局管理，不需要在这里重复初始化
  loadNews()
  loadCompanyReports()
  loadMallProducts()
  loadFundRanking()
})

// AI服务相关状态
const showAiModal = ref(false)
const activeAiService = ref('')
const aiResult = ref('')
const aiModel = ref('')
const aiLoading = ref(false)

// 输入数据
const newsInput = ref('')
const newsStockCode = ref('')
const strategyInput = ref('')
const strategyFramework = ref('backtrader')
const summaryInput = ref('')
const summaryType = ref('structured')
const reportInput = ref('')
const includeRisks = ref(true)

// API状态
const apiStatus = ref('checking') // checking, online, offline

// 统一提取 AI 返回数据
const extractPayload = (result) => result?.data?.data || result?.data || {}

// AI服务函数
const openAiModal = (service) => {
  activeAiService.value = service
  showAiModal.value = true
  aiResult.value = ''
}

const hideAiModal = () => {
  showAiModal.value = false
  activeAiService.value = ''
  // 清空输入和结果
  newsInput.value = ''
  strategyInput.value = ''
  summaryInput.value = ''
  reportInput.value = ''
  aiResult.value = ''
}

const getAiModalTitle = () => {
  const titles = {
    'news': '智能新闻解读',
    'strategy': '量化策略生成',
    'summary': '智能投研摘要',
    'report': '公司研报生成'
  }
  return titles[activeAiService.value] || 'AI智能服务'
}

// 获取API状态文本
const getApiStatusText = () => {
  const statusText = {
    'checking': '检查中...',
    'online': '服务正常',
    'offline': '服务异常'
  }
  return statusText[apiStatus.value] || '未知状态'
}

// 滚动到指定区域并添加高亮效果
const scrollToSection = (elementId) => {
  const element = document.getElementById(elementId);
  if (element) {
    // 移除之前可能存在的高亮效果
    const previousHighlighted = document.querySelector('.strategy-platform.highlighted');
    if (previousHighlighted) {
      previousHighlighted.classList.remove('highlighted');
    }
    
    // 添加高亮效果
    element.classList.add('highlighted');
    
    // 滚动到元素位置，使其位于屏幕中央
    element.scrollIntoView({ 
      behavior: 'smooth',
      block: 'center'  // 改为'center'使元素位于屏幕中央
    });
    
    // 3秒后移除高亮效果
    setTimeout(() => {
      element.classList.remove('highlighted');
    }, 3000);
  }
}

// 模拟API调用 - 实际项目中应该替换为真实API调用
const generateNews = async () => {
  if (!newsInput.value.trim()) {
    aiResult.value = '请输入新闻内容'
    return
  }

  if (!logged.value) {
    openLoginModal()
    aiResult.value = '请先登录再使用AI服务'
    return
  }

  try {
    aiLoading.value = true
    const result = await generateNewsAnalysis({
      news_flash: newsInput.value,
      stock_code: newsStockCode.value || undefined
    })

    if (result.success) {
      const payload = extractPayload(result)
      aiResult.value = payload.news_content || payload.content || 'AI未返回内容'
      aiModel.value = payload.model || '未知'
    } else {
      throw new Error(result.message || 'AI服务暂时不可用')
    }
  } catch (error) {
    aiResult.value = `生成新闻解读失败: ${error.message}`
    aiModel.value = '未知'
  } finally {
    aiLoading.value = false
  }
}

const generateStrategy = async () => {
  if (!strategyInput.value.trim()) {
    aiResult.value = '请输入策略描述'
    return
  }

  if (!logged.value) {
    openLoginModal()
    aiResult.value = '请先登录再使用AI服务'
    return
  }

  try {
    aiLoading.value = true
    const result = await generateStrategyApi({
      user_description: strategyInput.value,
      framework: strategyFramework.value
    })

    if (result.success) {
      const payload = extractPayload(result)
      const explanation = payload.explanation || ''
      const code = payload.strategy_code || payload.code || ''
      aiResult.value = code && explanation ? `${explanation}\n\n${code}` : (explanation || code || 'AI未返回内容')
      aiModel.value = payload.model || '未知'
    } else {
      throw new Error(result.message || 'AI服务暂时不可用')
    }
  } catch (error) {
    aiResult.value = `生成策略失败: ${error.message}`
    aiModel.value = '未知'
  } finally {
    aiLoading.value = false
  }
}

const generateSummary = async () => {
  if (!summaryInput.value.trim()) {
    aiResult.value = '请输入要摘要的内容'
    return
  }

  if (!logged.value) {
    openLoginModal()
    aiResult.value = '请先登录再使用AI服务'
    return
  }

  try {
    aiLoading.value = true
    const result = await generateSummaryApi({
      content: summaryInput.value,
      summary_type: summaryType.value
    })

    if (result.success) {
      const payload = extractPayload(result)
      aiResult.value = payload.summary || payload.content || 'AI未返回内容'
      aiModel.value = payload.model || '未知'
    } else {
      throw new Error(result.message || 'AI服务暂时不可用')
    }
  } catch (error) {
    aiResult.value = `生成摘要失败: ${error.message}`
    aiModel.value = '未知'
  } finally {
    aiLoading.value = false
  }
}

const generateReport = async () => {
  if (!reportInput.value.trim()) {
    aiResult.value = '请输入公司信息'
    return
  }

  if (!logged.value) {
    openLoginModal()
    aiResult.value = '请先登录再使用AI服务'
    return
  }

  try {
    aiLoading.value = true
    const result = await generateReportApi({
      company_info: reportInput.value,
      include_risks: includeRisks.value
    })

    if (result.success) {
      const payload = extractPayload(result)
      aiResult.value = payload.report_content || payload.content || 'AI未返回内容'
      aiModel.value = payload.model || '未知'
    } else {
      throw new Error(result.message || 'AI服务暂时不可用')
    }
  } catch (error) {
    aiResult.value = `生成研报失败: ${error.message}`
    aiModel.value = '未知'
  } finally {
    aiLoading.value = false
  }
}

// 检查API状态
const checkApiStatus = async () => {
  apiStatus.value = 'checking'
  try {
    const result = await chatService.checkHealth()
    if (result.success) {
      apiStatus.value = 'online'
    } else {
      apiStatus.value = 'offline'
    }
  } catch (error) {
    apiStatus.value = 'offline'
  }
}

// 辅助函数：截断文本
const truncateText = (text, maxLength) => {
  if (!text) return '暂无内容'
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 辅助函数：格式化报告日期
const formatReportDate = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
  } catch (e) {
    return dateString
  }
}

// 辅助函数：检查是否为今天
const isToday = (dateStr) => {
  if (!dateStr) return false
  try {
    const reportDate = new Date(dateStr).toISOString().split('T')[0]
    const today = new Date().toISOString().split('T')[0]
    return reportDate === today
  } catch {
    return false
  }
}

// 处理"最新"标签点击
const handleLatestTabClick = () => {
  if (!canAccessTodayReport()) {
    // 16:00前不允许查看最新（今天），自动切换到昨日
    alert('今日内参需在 16:00 后查看，已为您切换至昨日内参')
    reportTab.value = 'report-yesterday'
    return
  }
  reportTab.value = 'report-latest'
}

// 辅助函数：获取昨日报告
const getYesterdayReport = () => {
  if (!dailyReportHistory.value || dailyReportHistory.value.length === 0) return null
  
  const today = new Date().toISOString().split('T')[0]
  const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  
  // 查找昨日报告
  const yesterdayReport = dailyReportHistory.value.find(report => report.report_date === yesterday)
  if (yesterdayReport) return yesterdayReport
  
  // 如果没有昨日报告，返回最近的一个（非今日）
  return dailyReportHistory.value.find(report => report.report_date !== today) || null
}

// 加载龙虎榜数据（根据天数）
const loadDragonData = async (days = 1) => {
  dragonLoading.value = true
  dragonError.value = ''
  
  try {
    const result = await getTopListSummary(days)
    
    if (result.success && result.data?.data && result.data.data.length > 0) {
      // 转换 API 数据为前端格式
      const formattedData = result.data.data.slice(0, 10).map(item => ({
        name: item.name || '',
        price: item.close?.toFixed(2) || '-',
        change: item.pct_change || 0,
        changeText: item.pct_change ? `${item.pct_change > 0 ? '+' : ''}${item.pct_change.toFixed(2)}%` : '-',
        delta: item.pct_change?.toFixed(2) || '-',
        net: item.net_amount ? (item.net_amount / 100000000).toFixed(2) : '-', // 转换为亿
        buy: item.total_buy ? (item.total_buy / 100000000).toFixed(2) : (item.l_buy ? (item.l_buy / 100000000).toFixed(2) : '-'),
        sell: item.total_sell ? (item.total_sell / 100000000).toFixed(2) : (item.l_sell ? (item.l_sell / 100000000).toFixed(2) : '-'),
        appearCount: item.appear_count || 1,
        reason: item.reason || '-'
      }))
      
      // 根据天数存储到对应的数据中
      if (days === 1) {
        dragonTodayData.value = formattedData
        dragonFailed.value = false
      } else if (days === 5) {
        dragon5Data.value = formattedData
      } else if (days === 20) {
        dragon20Data.value = formattedData
      }
    } else {
      dragonError.value = '数据丢失'
      if (days === 1) {
        dragonFailed.value = true
        // 龙虎榜加载失败，尝试加载大盘指数作为替代
        loadMarketIndex()
      }
    }
  } catch (e) {
    console.error(`加载${days}日龙虎榜失败:`, e)
    dragonError.value = '数据丢失'
    if (days === 1) {
      dragonFailed.value = true
      // 龙虎榜加载失败，尝试加载大盘指数作为替代
      loadMarketIndex()
    }
  } finally {
    dragonLoading.value = false
  }
}

// 加载大盘指数数据（龙虎榜失败时替代显示）
const loadMarketIndex = async () => {
  marketIndexLoading.value = true
  marketIndexError.value = ''
  
  try {
    const result = await getMarketData()

    if (result?.data?.items && result.data.items.length > 0) {
      const items = result.data.items
      marketIndexData.value = items.map(item => {
        const price = Number(item.value)
        const pct = Number(item.change_pct)
        const changeAmount = Number.isFinite(price) && Number.isFinite(pct)
          ? (price * (pct / 100)).toFixed(2)
          : '-'
        const changeText = Number.isFinite(pct)
          ? `${pct > 0 ? '+' : ''}${pct.toFixed(2)}%`
          : '-'

        return {
          name: item.title || item.code || '-',
          price: Number.isFinite(price) ? price.toFixed(2) : '-',
          change: Number.isFinite(pct) ? pct : 0,
          changeText,
          changeAmount: Number.isFinite(Number(changeAmount)) ? `${pct > 0 ? '+' : ''}${changeAmount}` : '-',
          updatedAt: item.updated_at ? item.updated_at.replace('T', ' ').slice(0, 19) : '-'
        }
      })
    } else {
      marketIndexError.value = '数据丢失'
    }
  } catch (e) {
    console.error('加载大盘指数失败:', e)
    marketIndexError.value = '数据丢失'
  } finally {
    marketIndexLoading.value = false
  }
}

// 加载每日内参数据
const loadDailyReports = async () => {
  // 如果已经有数据且不是今天（或今天且已过16:00），则不重复加载
  if (latestDailyReport.value) {
    const reportDate = latestDailyReport.value.report_date
    const reportIsToday = isToday(reportDate)
    if (!reportIsToday || (reportIsToday && canAccessTodayReport())) {
      console.log('已有有效的投资方案数据，直接使用:', latestDailyReport.value)
      return
    }
  }
  
  dailyReportLoading.value = true
  dailyReportError.value = ''
  
  try {
    console.log('开始加载每日内参数据...')
    console.log('当前时间是否可访问今日报告:', canAccessTodayReport())
    
    // 加载最新报告（后端会自动过滤今天的报告如果<16:00）
    const latestResult = await getLatestDailyReport()
    console.log('最新报告API响应:', latestResult)
    
    if (latestResult.success && latestResult.data) {
      // 后端返回格式: {code: 0, message: "ok", data: {报告数据}}
      // handleRequest包装后: {success: true, data: {code: 0, message: "ok", data: {报告数据}}}
      let reportData = latestResult.data
      
      // 如果有嵌套的data字段，提取出来
      if (reportData.data && reportData.code === 0) {
        reportData = reportData.data
      }
      
      // 现在reportData应该是真正的报告数据
      if (reportData.id && reportData.report_date) {
        latestDailyReport.value = reportData
        console.log('最新报告加载成功:', reportData)
      } else {
        console.warn('最新报告数据格式异常:', reportData)
      }
    } else {
      console.warn('最新报告加载失败:', latestResult.message || '未知错误')
      
      // 兜底：如果是404且当前<16:00，提示用户
      if (latestResult.status === 404 && !canAccessTodayReport()) {
        dailyReportError.value = '今日内参需在 16:00 后查看'
      } else if (latestResult.status === 401) {
        dailyReportError.value = '认证失败，请重新登录'
      } else if (latestResult.status === 404) {
        dailyReportError.value = '暂无最新报告'
      } else {
        dailyReportError.value = latestResult.message || '加载失败'
      }
    }
    
    // 加载历史报告（后端会自动过滤今天的报告如果<16:00）
    const historyResult = await getDailyReportList({ limit: 10 })
    console.log('历史报告API响应:', historyResult)
    
    if (historyResult.success && historyResult.data) {
      let historyData = historyResult.data
      
      // 如果有嵌套的data字段，提取出来
      if (historyData.data && historyData.code === 0) {
        historyData = historyData.data
      }
      
      // 检查数据结构
      if (historyData.reports && Array.isArray(historyData.reports)) {
        dailyReportHistory.value = historyData.reports
        console.log('历史报告加载成功:', historyData.reports.length, '条记录')
      } else if (Array.isArray(historyData)) {
        dailyReportHistory.value = historyData
        console.log('历史报告加载成功:', historyData.length, '条记录')
      } else {
        console.warn('历史报告数据格式异常:', historyData)
      }
    } else {
      console.warn('历史报告加载失败:', historyResult.message || '未知错误')
    }
    
  } catch (e) {
    console.error('加载每日内参异常:', e)
    dailyReportError.value = `加载异常: ${e.message || e}`
  } finally {
    dailyReportLoading.value = false
    console.log('每日内参数据加载完成')
  }
}

// 龙虎榜数据存储
const dragonTodayData = ref([])
const dragon5Data = ref([])
const dragon20Data = ref([])

// 计算属性：根据 tab 返回对应数据（无数据时返回空数组）
const dragonToday = computed(() => dragonTodayData.value)
const dragon5 = computed(() => dragon5Data.value)
const dragon20 = computed(() => dragon20Data.value)

// 监听 tab 切换，加载对应数据
watch(dragonTab, (newTab) => {
  if (newTab === 'dragon-today' && dragonTodayData.value.length === 0 && !dragonFailed.value) {
    loadDragonData(1)
  } else if (newTab === 'dragon-5day' && dragon5Data.value.length === 0) {
    loadDragonData(5)
  } else if (newTab === 'dragon-20day' && dragon20Data.value.length === 0) {
    loadDragonData(20)
  }
})

// 页面加载时检查API状态并加载龙虎榜
onMounted(() => {
  console.log('认证状态检查:', {
    logged: logged.value,
    sessionActive: localStorage.getItem('session_active') === 'true',
    userText: userText.value
  })
  
  checkApiStatus()
  loadDragonData(1) // 默认加载今日数据
  loadDailyReports() // 加载每日内参数据
})

// 加载公司研报数据
const loadCompanyReports = async () => {
  companyReportsLoading.value = true
  companyReportsError.value = ''
  
  try {
    const result = await getCompanyResearchList({ limit: 3, offset: 0 })
    
    if (result.success && result.data) {
      const payload = result.data.data || result.data
      // 兼容 { total, items } 和直接数组
      if (payload.items) {
        companyReportsData.value = payload.items
      } else if (Array.isArray(payload)) {
        companyReportsData.value = payload
      } else {
        companyReportsData.value = []
      }
    } else {
      companyReportsError.value = result.message || '加载公司研报失败'
    }
  } catch (error) {
    console.error('加载公司研报失败:', error)
    companyReportsError.value = '网络错误，请稍后重试'
  } finally {
    companyReportsLoading.value = false
  }
}

// 查看公司研报详情
const viewCompanyReport = (report) => {
  router.push(`/company-research/${report.id}`)
}

// 评级映射
const ratingMap = {
  'buy': { tag: '买入', tagClass: 'mai-ru' },
  'add': { tag: '增持', tagClass: 'mai-ru-zeng' },
  'hold': { tag: '持有', tagClass: 'chi-you' },
  'reduce': { tag: '减持', tagClass: 'jian-chi' },
  'sell': { tag: '卖出', tagClass: 'mai-chu' }
}

const getRatingTag = (rating) => {
  return ratingMap[rating]?.tag || '持有'
}

const getRatingClass = (rating) => {
  return ratingMap[rating]?.tagClass || 'chi-you'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' })
  } catch {
    return '-'
  }
}

</script>

<style scoped>
.strategy-platform.highlighted {
  animation: highlight 2s ease;
  position: relative;
  transition: transform 0.1s;
}

@keyframes highlight {
  0% {
    background-color: transparent;
    transform: scale(1);
  }
  30% {
    background-color: rgba(255, 127, 0, 0.6);
    box-shadow: 0 0 15px rgba(255, 127, 0, 0.8);
    transform: scale(1.05);
  }
  60% {
    background-color: rgba(255, 127, 0, 0.6);
    box-shadow: 0 0 15px rgba(255, 127, 0, 0.8);
    transform: scale(1.05);
  }
  100% {
    background-color: transparent;
    transform: scale(1);
  }
}

/* 龙虎榜加载状态样式 */
.loading-indicator {
  margin-left: 15px;
  color: #ff7f24;
  font-size: 12px;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: #fff8f0;
  border-radius: 8px;
  margin: 10px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #ffe0c0;
  border-top-color: #ff7f24;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p,
.error-state p {
  margin-top: 15px;
  color: #666;
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 20px;
  background: #ff7f24;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-btn:hover {
  background: #ff6a00;
}

.fund-header {
  background: #f5f5f5;
  font-weight: bold;
}

/* 财经头条展示优化 */
.news-section {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  margin-bottom: 16px;
}

.news-banner {
  background: linear-gradient(135deg, #fff6ee 0%, #ffffff 100%);
  border: 1px solid #ffe0c0;
  border-radius: 10px;
  padding: 16px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.news-banner:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(255, 127, 36, 0.18);
}

.banner-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mask-title {
  font-size: 18px;
  font-weight: 700;
  color: #333;
  line-height: 1.4;
}

.mask-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}

.banner-cta {
  align-self: flex-start;
  font-size: 12px;
  color: #ff7f24;
  background: #fff;
  border: 1px solid #ff7f24;
  padding: 4px 10px;
  border-radius: 999px;
}

.news-list {
  margin-top: 12px;
}

.news-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}

.news-list li a {
  color: #333;
  text-decoration: none;
  font-size: 14px;
  display: block;
  padding: 8px 10px;
  border-radius: 6px;
  transition: background 0.2s ease, color 0.2s ease;
  background: #fff8f0;
}

.news-list li a:hover {
  color: #ff7f24;
  background: #fff1e3;
}

.empty-news {
  padding: 16px;
  text-align: center;
  color: #999;
  background: #fff8f0;
  border-radius: 8px;
  margin-top: 8px;
}

/* 用户菜单样式 */
.user-menu-container {
  position: relative;
  display: inline-block;
}

.user-btn {
  background-color: #000000;  /* 橙色实心背景 */
  color: white;                /* 白色字体确保清晰显示 */
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;           /* 字体加粗增强可读性 */
  border: none;               /* 移除默认边框 */
  transition: background-color 0.3s ease; /* 添加过渡效果 */
}

.user-menu-container:hover .user-btn {
  background-color: #ff6a00;  /* 鼠标悬停时稍深的橙色 */
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
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

/* 登录弹窗样式 */
.login-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,.8);
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

.login-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.login-btn.register-btn {
  background-color: #4CAF50;
}

.login-btn.register-btn:hover {
  background-color: #45a049;
}

.login-switch {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 15px;
}

.login-switch a {
  color: #ff7f24;
  text-decoration: none;
  font-weight: bold;
}

.login-switch a:hover {
  text-decoration: underline;
}

.login-tips {
  text-align: center;
  font-size: 13px;
  color: #999;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.error-tips {
  color: #ff4500;
  text-align: center;
  margin-bottom: 10px;
  padding: 8px;
  background-color: #fff0f0;
  border-radius: 4px;
}

.success-tips {
  color: #4CAF50;
  text-align: center;
  margin-bottom: 10px;
  padding: 8px;
  background-color: #f0fff0;
  border-radius: 4px;
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

/* 禁用的标签样式 */
.tab-switch a.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  color: #999;
}

.tab-switch a.disabled:hover {
  background-color: transparent;
  color: #999;
}

/* 公司研报模块样式优化 */
.section-header-inline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 20px 0 15px;
  clear: both;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.refresh-icon-btn {
  background: transparent;
  border: 1px solid #ff7f24;
  color: #ff7f24;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  padding: 0;
}

.refresh-icon-btn:hover:not(:disabled) {
  background: #ff7f24;
  color: white;
  transform: rotate(90deg);
}

.refresh-icon-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.report-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.report-card {
  background: white;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid #ffb380;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  height: 100%; /* 确保卡片填满 Grid 单元格高度 */
}

.report-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(255, 127, 36, 0.25);
  border-color: #ff7f24;
}

.card-body {
  padding: 20px;
  flex: 1; /* 内容撑满剩余空间 */
  display: flex;
  flex-direction: column;
}

.stock-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #f0f0f0;
}

.stock-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  flex: 1;
  margin-right: 10px; /* 防止与标签太紧凑 */
  line-height: 1.4;
  white-space: nowrap; /* 不换行 */
  overflow: hidden; /* 隐藏溢出 */
  text-overflow: ellipsis; /* 显示省略号 */
}

.stock-code-small {
  font-size: 12px;
  color: #999;
  font-weight: normal;
  margin-left: 4px;
  white-space: nowrap; /* 股票代码不换行 */
}

.report-meta {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
}

.meta-item {
  color: #999;
}

.report-ul {
  list-style: none;
  padding: 0;
  margin: 12px 0;
  display: flex;
  flex-wrap: wrap; /* 允许标签换行，避免截断 */
  gap: 8px; /* 使用 gap 代替 margin 控制间距 */
}

.report-ul li {
  background: linear-gradient(to right, #ffeedd, #fff6ee);
  padding: 4px 8px;
  font-size: 12px;
  border-radius: 3px;
  color: #ff7f24;
  white-space: nowrap; /* 标签内文字不换行 */
}

.view-btn {
  width: 100%;
  padding: 10px;
  background: white;
  border: 1px solid #ff7f24;
  color: #ff7f24;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.3s;
  margin-top: auto; /* 将按钮推到底部，对齐更整齐 */
}

.view-btn:hover {
  background: #ff7f24;
  color: white;
  box-shadow: 0 4px 12px rgba(255, 127, 36, 0.3);
}

/* 评级标签样式 */
.mai-ru {
  background: linear-gradient(to bottom, #DDFCE6, #c8f5d2);
  padding: 4px 10px;
  color: #18A44B;
  font-size: 12px;
  border-radius: 4px;
  font-weight: bold;
  white-space: nowrap;
}

.mai-ru-zeng {
  background: linear-gradient(to bottom, #FCF5C4, #f5ecaa);
  padding: 4px 10px;
  color: #976A1C;
  font-size: 12px;
  border-radius: 4px;
  font-weight: bold;
  white-space: nowrap;
}

.chi-you {
  background: linear-gradient(to bottom, #E0E0E0, #d0d0d0);
  padding: 4px 10px;
  color: #333333;
  font-size: 12px;
  border-radius: 4px;
  font-weight: bold;
  white-space: nowrap;
}

.jian-chi {
  background: linear-gradient(to bottom, #FFE0B2, #ffd090);
  padding: 4px 10px;
  color: #FF6D00;
  font-size: 12px;
  border-radius: 4px;
  font-weight: bold;
  white-space: nowrap;
}

.mai-chu {
  background: linear-gradient(to bottom, #FFCDD2, #fba4ab);
  padding: 4px 10px;
  color: #C62828;
  font-size: 12px;
  border-radius: 4px;
  font-weight: bold;
  white-space: nowrap;
}

/* 商品类型标签样式 */
.product-type-tag {
  display: inline-block;
  background: linear-gradient(to right, #ff7f24, #ff9933);
  color: white;
  padding: 3px 8px;
  font-size: 11px;
  border-radius: 3px;
  margin-bottom: 8px;
  font-weight: 500;
}

.active {
  color: #ff7f24;
  font-weight: bold;
}

.red {
  color: #eb445a; /* 红色表示上涨 */
}

.green {
  color: #2dd36f; /* 绿色表示下跌 */
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .report-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .report-cards {
    grid-template-columns: 1fr;
  }
  
  .section-header-inline {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
