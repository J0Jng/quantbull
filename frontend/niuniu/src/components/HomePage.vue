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
        <div class="top-middle">
          <input v-model="search" type="text" placeholder="输入股票代码、名称或关键词" class="search-input" />
          <button class="search-btn">查行情</button>
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
          <div class="news-banner">
            <img src="/1.png" alt="财经头条主图" />
            <div class="banner-mask" @click="goToNewsDetail(1)">
              <h3 class="mask-title">央行：将再降准0.5个百分点 释放资金约1万亿元</h3>
              <p class="mask-desc">本次降准旨在优化流动性结构，降低实体经济融资成本，预计将带动市场融资成本进一步下行，利好中小企业和实体经济发展。</p>
            </div>
          </div>
          <div class="news-list">
            <ul>
              <li><a href="#" @click.prevent="goToNewsDetail(2)">24H：A三大集团集体高开 宁德时代涨5.1%</a></li>
              <li><a href="#" @click.prevent="goToNewsDetail(3)">国际油价涨超1% 报103美元/桶 WTI升4%</a></li>
              <li><a href="#" @click.prevent="goToNewsDetail(4)">房地产"超预期政策"密集发布 多家房企发公告</a></li>
              <li><a href="#" @click.prevent="goToNewsDetail(5)">人民币汇率企稳回升 离岸人民币兑美元涨破7.10关口</a></li>
              <li><a href="#" @click.prevent="goToNewsDetail(6)">工信部：加快推进新能源汽车充电桩建设 年内新增超20万个</a></li>
            </ul>
          </div>
        </section>

        <!-- 广告横幅 -->
        <section class="ad-banner">
            <a href="#">
            <img src="/2.png" alt="理财广告" />
          </a>
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
                    <th>成交量</th>
                    <th>成交额</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in marketIndexData" :key="idx">
                    <td>{{ row.name }}</td>
                    <td>{{ row.price }}</td>
                    <td><span :class="row.change > 0 ? 'green' : 'red'">{{ row.changeText }}</span></td>
                    <td>{{ row.volume }}</td>
                    <td>{{ row.amount }}</td>
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
        <h2 class="section-title">公司投研</h2>
        <router-link to="/company-research" class="more-link" style="float:right;margin-top:15px;font-size: 14px;">查看全部 &gt;</router-link>
        <section class="company-report">
          <div class="report-cards">
            <div class="report-card" v-for="(card, idx) in reportCards" :key="idx">
              <div class="card-body">
                <div class="stock-info">
                  <span class="stock-name">{{ card.name }}</span>
                  <span :class="card.tagClass">{{ card.tag }}</span>
                </div>
                <div class="price">{{ card.priceLabel }}：<span class="current-price">{{ card.price }}</span></div>
                <div class="profit">{{ card.profitLabel }}:<span style="float:right;">{{ card.profit }}</span></div>
                <ul class="report-ul">
                  <li v-for="(t, i) in card.tags" :key="i">{{ t }}</li>
                </ul>
                <div style="clear:both;"></div>
                <button class="view-btn" @click="goToCompanyResearch">查看研报</button>
              </div>
            </div>
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
          <div class="mall-cards">
            <div class="mall-card">
                <div class="card-icon">
                <img src="/4.png" alt="基金图标" />
              </div>
              <div class="card-info">
                <h4>黄金理财组合</h4>
                <p>黄金定投收益稳，年化收益可达6.5%</p>
                <p class="price">¥8,800</p>
              </div>
              <button class="buy-btn" @click="router.push('/shop')">立即购买</button>
            </div>
            <div class="mall-card">
                <div class="card-icon">
                <img src="/5.png" alt="AI图标" />
              </div>
              <div class="card-info">
                <h4>AI智能选股</h4>
                <p>人工智能驱动的个性化选股组合服务</p>
                <p class="price">¥15,000/年</p>
              </div>
              <button class="buy-btn" @click="router.push('/shop')">立即购买</button>
            </div>
          </div>
        </section>

        <!-- 基金排行榜板块 -->
        <h2 class="section-title">基金排行榜</h2>
        <section class="fund-rank">
          <div class="fund-list">
            <div class="fund-item" v-for="(fund, idx) in funds" :key="idx">
              <div class="fund-col check-col">
                <input type="radio" name="fund-radio" :id="'fund'+idx" />
              </div>
              <div class="fund-col num-col">{{ fund.rank }}</div>
              <div class="fund-col name-col">
                <div class="fund-name">{{ fund.name }}</div>
                <div class="fund-type">{{ fund.type }}</div>
              </div>
              <div class="fund-col data-col">
                <div class="data-value">{{ fund.nav }}</div>
                <div class="data-time">单位净值</div>
              </div>
              <div class="fund-col trend-col" :class="fund.trendColor">{{ fund.trend }}</div>

              <div class="fund-col data-col" v-for="(d, i) in fund.periods" :key="i">
                <div class="data-value">{{ d }}</div>
              </div>

              <div class="fund-col trend-img-col">
                <img :src="'/3.png'" alt="上涨走势" class="trend-img" />
              </div>
              <div class="fund-col btn-col">
                <button class="buy-btn small" @click="$router.push('/fund-ranking')">立即购买</button>
                <button class="fav-btn small" @click="$router.push('/fund-ranking')">自选</button>
              </div>
            </div>
          </div>
        </section>

        <!-- 每日内参板块（新增切换内容容器） -->
        <h2 class="section-title">每日内参</h2>
        <div class="tab-switch report-tab-switch">
          <a href="javascript:;" :class="{ active: reportTab==='report-latest' }" @click.prevent="reportTab='report-latest'">最新</a>
          <a href="javascript:;" :class="{ active: reportTab==='report-yesterday' }" @click.prevent="reportTab='report-yesterday'">昨日</a>
          <a href="javascript:;" :class="{ active: reportTab==='report-history' }" @click.prevent="reportTab='report-history'">历史</a>
        </div>
        <section class="daily-report">
          <div v-show="reportTab==='report-latest'" class="tab-content report-content" id="report-latest">
            <div class="report-item">
              <h3>新能源板块迎来布局良机</h3>
              <p>光伏、风电产业链上游价格回落，需求端政策力度大，行业景气度有望持续，建议关注具备技术壁垒和产能扩张能力的企业。</p>
              <span class="design">张明 | 首席设计师</span><span class="date">2025-12-17 09:30</span>
            </div>
            <div class="report-item">
              <h3>低估值煤炭板块存修复机会</h3>
              <p>煤炭板块估值处于低位，建议关注业绩稳健、高股息、低估值的中周期标的。</p>
            </div>
          </div>

          <div v-show="reportTab==='report-yesterday'" class="tab-content report-content" id="report-yesterday">
            <div class="report-item">
              <h3>央行逆回购操作加码 市场流动性充裕</h3>
              <p>昨日央行开展1500亿元7天期逆回购操作，中标利率2.00%，完全对冲当日到期量，市场资金面保持宽松。</p>
              <span class="design">张明 | 首席设计师</span><span class="date">2025-12-16 15:45</span>
            </div>
            <div class="report-item">
              <h3>消费板块回暖 食品饮料领涨</h3>
              <p>昨日消费板块集体走强，食品饮料板块涨幅超2%，白酒、休闲食品等细分领域表现亮眼，资金布局跨年行情。</p>
            </div>
          </div>

          <div v-show="reportTab==='report-history'" class="tab-content report-content" id="report-history">
            <div class="report-item">
              <h3>2025年12月核心数据解读</h3>
              <p>12月上旬社融数据超预期，新增人民币贷款2.8万亿元，企业中长期贷款占比提升，实体经济融资需求回暖。</p>
              <span class="design">张明 | 首席设计师</span><span class="date">2025-12-10 10:20</span>
            </div>
            <div class="report-item">
              <h3>年末资金面前瞻：流动性无虞</h3>
              <p>监管层多次表态将维护年末流动性平稳，预计12月降准落地后，市场资金利率将维持在低位，利好股市跨年行情。</p>
            </div>
          </div>
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
import { getTopListSummary, getMarketOverview, getRealtimeQuotes } from '@/services/marketService'
import { generateNewsAnalysis, generateStrategy as generateStrategyApi, generateSummary as generateSummaryApi, generateReport as generateReportApi } from '@/services/aiService'
import { useAuth } from '@/composables/useAuth'
import chatService from '@/services/chatService'

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

// 页面加载时的初始化（认证状态已在 App.vue 中初始化）
onMounted(() => {
  // 认证状态已由 useAuth 全局管理，不需要在这里重复初始化
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
    const result = await getMarketOverview()
    
    if (result.success && result.data) {
      // 转换 API 数据为前端格式
      // data-service 返回: {"trade_date", "market_status", "indices": [...], "total_turnover"}
      const data = result.data.data || result.data
      if (data.indices && data.indices.length > 0) {
        // 指数名称映射
        const indexNameMap = {
          '000001.SH': '上证指数',
          '399001.SZ': '深证成指',
          '399006.SZ': '创业板指',
          '000016.SH': '上证50',
          '000300.SH': '沪深300',
          '000905.SH': '中证500',
          '000688.SH': '科创50'
        }
        
        marketIndexData.value = data.indices.map(item => {
          const symbol = item.symbol || item.code || ''
          return {
            name: indexNameMap[symbol] || item.name || symbol,
            price: item.close?.toFixed(2) || item.latest_price?.toFixed(2) || '-',
            change: item.pct_change || item.change || 0,
            changeText: item.pct_change 
              ? `${item.pct_change > 0 ? '+' : ''}${item.pct_change.toFixed(2)}%` 
              : '-',
            volume: item.vol ? (item.vol / 100000000).toFixed(2) + '亿' : '-',
            amount: item.amount ? (item.amount / 100000000).toFixed(2) + '亿' : '-'
          }
        })
      } else {
        marketIndexError.value = '数据丢失'
      }
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
  checkApiStatus()
  loadDragonData(1) // 默认加载今日数据
})

const reportCards = [
  { name: '键凯科技', tag: '买入', tagClass: 'mai-ru', priceLabel: '当前价', price: '71.25元', profitLabel: '目标价格', profit: '94.00%', tags: ['光伏', '碳中和', '新能源'] },
  { name: '宁德时代', tag: '买入', tagClass: 'mai-ru', priceLabel: '目标价', price: '544.40元', profitLabel: '机构预测', profit: '68.00%', tags: ['光伏', '碳中和', '新能源'] },
  { name: '招商银行', tag: '增持', tagClass: 'mai-ru-zeng', priceLabel: '目标价', price: '42.50元', profitLabel: '机构预测', profit: '44.30%', tags: ['光伏', '碳中和', '新能源'] }
]

const funds = [
  { rank: '01', name: '中欧医疗健康混合C', type: '混合型基金', nav: '1.3609', trend: '+1.1%', trendColor: 'green', periods: ['25.90%', '16.92%', '13.54%', '16.04%', '24.75%', '230.90%', '72.47%'] },
  { rank: '02', name: '易方达蓝筹精选混合', type: '混合型基金', nav: '4.9100', trend: '-0.5%', trendColor: 'red', periods: ['30.50%', '84.71%', '11.29%', '5.85%', '26.76%', '367.42%', '14.27%'] },
  { rank: '03', name: '华夏能源革新股票A', type: '股票型基金', nav: '2.3179', trend: '+0.7%', trendColor: 'green', periods: ['11.76%', '115.85%', '15.43%', '17.62%', '24.40%', '137.09%', '173.36%'] }
]
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
</style>
