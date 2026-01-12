<template>
  <div class="news-list-page">
    <!-- 顶部面包屑导航 -->
    <div class="breadcrumb">
      <div class="container">
        <router-link to="/">首页</router-link> > <span>财经头条</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="container">
        <h2 class="section-title">财经头条</h2>
        <div class="news-content">
          <div class="news-list">
            <div 
              class="news-item" 
              v-for="(item, index) in newsItems" 
              :key="index"
              @click="goToNewsDetail(item.id)"
            >
              <div class="news-item-header">
                <h3>{{ item.title }}</h3>
                <span class="news-date">{{ item.date }}</span>
              </div>
              <div class="news-item-summary">
                {{ item.summary }}
              </div>
              <div class="news-item-tags">
                <span v-for="(tag, tagIndex) in item.tags" :key="tagIndex" class="news-tag">{{ tag }}</span>
              </div>
            </div>
            
            <!-- 分页 -->
            <div class="pagination">
              <a href="#" class="prev">上一页</a>
              <a href="#" class="page-number active">1</a>
              <a href="#" class="page-number">2</a>
              <a href="#" class="page-number">3</a>
              <a href="#" class="page-number">4</a>
              <a href="#" class="page-number">5</a>
              <span>...</span>
              <a href="#" class="page-number">10</a>
              <a href="#" class="next">下一页</a>
            </div>
          </div>
          
          <!-- 右侧热门推荐 -->
          <div class="sidebar">
            <div class="hot-news">
              <h3 class="sidebar-title">热点聚焦</h3>
              <ul>
                <li v-for="(hotItem, hotIndex) in hotNews" :key="hotIndex">
                  <span :class="hotIndex < 3 ? 'hot-index top-three' : 'hot-index'">{{ hotIndex + 1 }}</span>
                  <a href="#" @click.prevent="goToHotNews(hotItem.id)">{{ hotItem.title }}</a>
                </li>
              </ul>
            </div>
            
            <div class="ad-section">
              <a href="#">
                <img src="/2.png" alt="广告位">
              </a>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const newsItems = ref([
  {
    id: 1,
    title: '央行：将再降准0.5个百分点 释放资金约1万亿元',
    date: '2025-12-22 09:30',
    summary: '本次降准旨在优化流动性结构，降低实体经济融资成本，预计将带动市场融资成本进一步下行，利好中小企业和实体经济发展。',
    tags: ['货币政策', '降准', '流动性']
  },
  {
    id: 2,
    title: 'A股三大指数集体高开 宁德时代涨5.1%',
    date: '2025-12-22 09:25',
    summary: '今日开盘，A股三大指数集体高开，创业板指涨幅居前。宁德时代发布公告称其新一代电池技术取得突破，股价应声大涨。',
    tags: ['股市', '宁德时代', '创业板']
  },
  {
    id: 3,
    title: '国际油价涨超1% 报103美元/桶 WTI升4%',
    date: '2025-12-22 09:15',
    summary: '受中东地缘政治紧张局势影响，国际油价持续走高，布伦特原油价格上涨至103美元/桶，WTI原油期货价格上涨4%。',
    tags: ['国际油价', '能源', '地缘政治']
  },
  {
    id: 4,
    title: '房地产"超预期政策"密集发布 多家房企发公告',
    date: '2025-12-22 09:05',
    summary: '近期多地政府陆续出台房地产支持政策，包括放宽限购、下调首付比例等措施，多家房地产企业积极响应并发布相关公告。',
    tags: ['房地产', '政策', '限购']
  },
  {
    id: 5,
    title: '人民币汇率企稳回升 离岸人民币兑美元涨破7.10关口',
    date: '2025-12-22 08:50',
    summary: '随着国内经济复苏信号增强及美元指数走弱，离岸人民币兑美元汇率持续回升，已突破7.10重要关口。',
    tags: ['人民币', '汇率', '外汇']
  },
  {
    id: 6,
    title: '工信部：加快推进新能源汽车充电桩建设 年内新增超20万个',
    date: '2025-12-22 08:30',
    summary: '工信部表示将进一步完善新能源汽车充电基础设施网络，计划年内新增充电桩超过20万个，覆盖更多城市和乡村地区。',
    tags: ['新能源汽车', '充电桩', '基建']
  }
])

const hotNews = ref([
  { id: 7, title: '美联储议息会议即将召开 市场密切关注政策动向' },
  { id: 8, title: '黄金价格突破每盎司2200美元 创历史新高' },
  { id: 9, title: '人工智能芯片需求激增 相关企业订单排至明年' },
  { id: 10, title: '全球供应链逐步恢复 但通胀压力依然存在' },
  { id: 11, title: '绿色能源投资持续增长 碳中和目标推动产业发展' },
  { id: 12, title: '数字货币发展加速 多国央行推进CBDC试点' },
  { id: 13, title: '生物医药行业迎来新机遇 创新药研发持续推进' },
  { id: 14, title: '跨境电商蓬勃发展 海外消费市场不断拓展' }
])

const goToNewsDetail = (id) => {
  router.push(`/news-detail/${id}`)
}

// 跳转到热点新闻详情页
const goToHotNews = (id) => {
  router.push(`/news-detail/${id}`)
}
</script>

<style scoped>
.breadcrumb {
  background: #fff;
  padding: 10px 0;
  font-size: 14px;
}

.breadcrumb a {
  color: #ff7f00;
}

.news-content {
  display: flex;
  gap: 20px;
  margin-top: 15px;
}

.news-list {
  flex: 3;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
}

.sidebar {
  flex: 1;
}

.news-item {
  padding: 20px 0;
  border-bottom: 1px dashed #ddd;
  cursor: pointer;
  transition: all 0.3s ease;
}

.news-item:hover {
  background: #fff6ee;
  transform: translateX(5px);
}

.news-item:last-child {
  border-bottom: none;
}

.news-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.news-item-header h3 {
  font-size: 18px;
  color: #333;
  font-weight: bold;
}

.news-item-header h3:hover {
  color: #ff7f00;
}

.news-date {
  font-size: 12px;
  color: #999;
}

.news-item-summary {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 15px;
}

.news-item-tags {
  display: flex;
  gap: 8px;
}

.news-tag {
  font-size: 12px;
  background: #f5f5f5;
  color: #666;
  padding: 4px 8px;
  border-radius: 3px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
  gap: 10px;
}

.pagination a {
  display: inline-block;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  color: #333;
  text-decoration: none;
  font-size: 14px;
}

.pagination a:hover,
.pagination a.active {
  background: #ff7f00;
  color: #fff;
  border-color: #ff7f00;
}

.sidebar-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ff7f00;
}

.hot-news {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #eee;
  margin-bottom: 20px;
}

.hot-news ul li {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px dashed #eee;
}

.hot-news ul li:last-child {
  border-bottom: none;
}

.hot-index {
  display: inline-block;
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  background: #f5f5f5;
  border-radius: 3px;
  font-size: 12px;
  margin-right: 10px;
}

.hot-index.top-three {
  background: #ff7f00;
  color: #fff;
}

.hot-news a {
  font-size: 14px;
  color: #333;
}

.hot-news a:hover {
  color: #ff7f00;
}

.ad-section img {
  width: 100%;
  border-radius: 8px;
}
</style>