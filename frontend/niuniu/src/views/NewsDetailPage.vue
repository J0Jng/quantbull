<template>
  <div class="news-detail-page">
    <!-- 顶部面包屑导航 -->
    <div class="breadcrumb">
      <div class="container">
        <router-link to="/">首页</router-link> > 
        <router-link to="/news-list">财经头条</router-link> > 
        <span>{{ newsDetail.title }}</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="container">
        <div class="news-detail-content">
          <!-- 左侧新闻详情 -->
          <div class="news-detail-main">
            <!-- 新闻标题区域 -->
            <div class="news-header">
              <h1 class="news-title">{{ newsDetail.title }}</h1>
              <div class="news-meta">
                <span class="publish-date">
                  <i class="icon-time"></i>{{ newsDetail.publishTime }}
                </span>
                <span class="news-source">
                  <i class="icon-source"></i>{{ newsDetail.source }}
                </span>
                <span class="view-count">
                  <i class="icon-view"></i>{{ newsDetail.viewCount }} 阅读
                </span>
              </div>
            </div>

            <!-- 新闻正文内容 -->
            <article class="news-body">
              <div v-html="newsDetail.content" class="news-content"></div>
              
              <!-- 图片展示 -->
              <div class="news-images" v-if="newsDetail.images && newsDetail.images.length">
                <img 
                  v-for="(image, index) in newsDetail.images" 
                  :key="index" 
                  :src="image.url" 
                  :alt="image.alt" 
                  class="news-image"
                />
              </div>
            </article>

            <!-- 互动功能区 -->
            <div class="interaction-section">
              <div class="interaction-buttons">
                <button 
                  :class="['like-btn', { active: isLiked }]" 
                  @click="handleLike"
                >
                  <i class="icon-like"></i>
                  <span>{{ newsDetail.likeCount }}</span>
                </button>
                <button 
                  :class="['collect-btn', { active: isCollected }]" 
                  @click="handleCollect"
                >
                  <i class="icon-collect"></i>
                  <span>收藏</span>
                </button>
                <button class="share-btn" @click="handleShare">
                  <i class="icon-share"></i>
                  <span>分享</span>
                </button>
              </div>
            </div>

            <!-- 相关新闻推荐 -->
            <div class="related-news" v-if="relatedNews.length">
              <h3 class="related-title">相关推荐</h3>
              <div class="related-list">
                <div 
                  v-for="(related, index) in relatedNews" 
                  :key="index" 
                  class="related-item"
                  @click="goToNewsDetail(related.id)"
                >
                  <h4>{{ related.title }}</h4>
                  <p>{{ related.summary }}</p>
                  <span class="related-date">{{ related.publishTime }}</span>
                </div>
              </div>
            </div>

            <!-- 评论区域 -->
            <div class="comment-section">
              <h3 class="comment-title">评论</h3>
              <!-- 评论输入框 -->
              <div class="comment-input">
                <textarea 
                  v-model="commentText" 
                  placeholder="写下您的评论..."
                  rows="3"
                ></textarea>
                <button 
                  class="submit-comment-btn" 
                  @click="submitComment"
                  :disabled="!commentText.trim()"
                >
                  发布评论
                </button>
              </div>
              
              <!-- 评论列表 -->
              <div class="comment-list">
                <div 
                  v-for="(comment, index) in comments" 
                  :key="index" 
                  class="comment-item"
                >
                  <div class="comment-avatar">
                    <img :src="comment.avatar" alt="用户头像" />
                  </div>
                  <div class="comment-content">
                    <div class="comment-header">
                      <span class="comment-author">{{ comment.author }}</span>
                      <span class="comment-time">{{ comment.time }}</span>
                    </div>
                    <p class="comment-text">{{ comment.content }}</p>
                    <div class="comment-actions">
                      <button class="comment-like-btn">
                        <i class="icon-like"></i>
                        <span>{{ comment.likeCount }}</span>
                      </button>
                      <button class="comment-reply-btn">回复</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 右侧边栏 -->
          <div class="news-sidebar">
            <!-- 广告位 -->
            <div class="ad-section">
              <a href="#">
                <img src="/2.png" alt="广告位" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 模拟新闻数据
const newsData = [
  {
    id: 1,
    title: '央行：将再降准0.5个百分点 释放资金约1万亿元',
    publishTime: '2025-12-22 09:30',
    source: '中国人民银行',
    viewCount: 12456,
    likeCount: 892,
    content: `
      <p>中国人民银行今日宣布，将于2025年12月25日起下调金融机构存款准备金率0.5个百分点（不含已执行5%存款准备金率的金融机构）。本次下调后，金融机构加权平均存款准备金率约为7.4%。</p>
      
      <p>央行相关负责人表示，此次降准旨在保持流动性合理充裕，优化金融机构资金结构，降低社会综合融资成本，加大对实体经济的支持力度。预计此次降准将释放长期资金约1万亿元。</p>
      
      <p>专家分析认为，此次降准符合市场预期，体现了货币政策的前瞻性、精准性和有效性。降准有利于稳定市场预期，增强金融机构资金配置能力，为经济高质量发展营造适宜的货币金融环境。</p>
      
      <p>此次降准后，金融机构应继续加大对小微企业、科技创新、绿色发展的支持力度，保持信贷总量适度、节奏平稳，提升服务实体经济的质效。</p>
    `,
    images: [
      { url: '/1.png', alt: '央行新闻发布会' },
      { url: '/3.png', alt: '金融市场走势图' }
    ]
  },
  {
    id: 2,
    title: 'A股三大指数集体高开 宁德时代涨5.1%',
    publishTime: '2025-12-22 09:25',
    source: '证券时报',
    viewCount: 8956,
    likeCount: 423,
    content: `
      <p>今日开盘，A股三大指数集体高开，沪指开盘报3525.68点，上涨0.45%；深成指报11268.45点，上涨0.32%；创业板指报2345.12点，上涨0.28%。</p>
      
      <p>宁德时代开盘后迅速走高，涨幅超过5.1%。公司昨日晚间发布公告称，其新一代钠离子电池技术取得重大突破，能量密度和循环寿命均达到行业领先水平。</p>
      
      <p>分析人士指出，新能源产业链个股集体走强，主要受到政策利好的推动。工信部近期发布的新能源汽车产业发展规划，为相关企业带来了新的发展机遇。</p>
      
      <p>市场人士认为，当前市场情绪较为积极，投资者对后市保持乐观态度，建议关注新能源、半导体等成长性板块的投资机会。</p>
    `,
    images: [
      { url: '/2.png', alt: 'A股市场走势' }
    ]
  },
  {
    id: 3,
    title: '国际油价涨超1% 报103美元/桶 WTI升4%',
    publishTime: '2025-12-22 09:15',
    source: '财经网',
    viewCount: 7568,
    likeCount: 312,
    content: `
      <p>受中东地缘政治紧张局势影响，国际油价持续走高。布伦特原油价格上涨至103美元/桶，涨幅1.2%；WTI原油期货价格上涨4%，报98.5美元/桶。</p>
      
      <p>分析师指出，近期中东地区局势紧张，加上OPEC+坚持减产政策，导致原油供应紧张。此外，全球经济复苏预期增强，也推动了原油需求的增长。</p>
      
      <p>能源专家表示，油价上涨可能会对全球通胀产生影响，各国央行需要密切关注能源价格走势，适时调整货币政策。</p>
      
      <p>投资建议方面，专家建议投资者关注能源股和新能源替代领域的投资机会，同时注意控制风险，合理配置资产。</p>
    `,
    images: [
      { url: '/3.png', alt: '国际油价走势图' }
    ]
  },
  {
    id: 4,
    title: '房地产"超预期政策"密集发布 多家房企发公告',
    publishTime: '2025-12-22 09:05',
    source: '经济日报',
    viewCount: 6452,
    likeCount: 245,
    content: `
      <p>近期全国多地陆续出台房地产支持政策组合拳，包括下调首付比例至15%，取消部分地区限购措施，推出购房补贴政策等，旨在稳定房地产市场预期，促进房地产行业平稳健康发展。</p>
      
      <p>多家房地产企业积极回应政策利好，万科、保利、碧桂园等头部房企发布公告称将积极配合政策实施，推出符合市场需求的新产品，并采取多项举措确保项目交付质量。</p>
      
      <p>专家认为，此次政策组合拳力度超出预期，有望对房地产市场形成实质性利好，但同时也需要警惕市场过热风险，建议采取差异化调控策略。</p>
    `,
    images: [
      { url: '/1.png', alt: '房地产政策发布会' }
    ]
  },
  {
    id: 5,
    title: '人民币汇率企稳回升 离岸人民币兑美元涨破7.10关口',
    publishTime: '2025-12-22 08:50',
    source: '外汇管理局',
    viewCount: 5834,
    likeCount: 189,
    content: `
      <p>随着国内经济复苏信号增强及美元指数走弱，离岸人民币兑美元汇率持续回升，已突破7.10重要心理关口，创近三个月来新高。</p>
      
      <p>分析人士指出，人民币汇率企稳回升的主要驱动因素包括：中国经济基本面持续向好，外贸顺差保持高位，资本流入增加，以及美元指数回调等。</p>
      
      <p>外汇管理部门表示，将继续保持人民币汇率在合理均衡水平上的基本稳定，加强预期引导，防范跨境资金异常流动风险。</p>
    `,
    images: [
      { url: '/2.png', alt: '人民币汇率走势' }
    ]
  },
  {
    id: 6,
    title: '工信部：加快推进新能源汽车充电桩建设 年内新增超20万个',
    publishTime: '2025-12-22 08:30',
    source: '工业和信息化部',
    viewCount: 7256,
    likeCount: 312,
    content: `
      <p>工信部今日举行新闻发布会表示，将进一步完善新能源汽车充电基础设施网络，计划年内新增充电桩超过20万个，覆盖更多城市和乡村地区。</p>
      
      <p>根据规划，新建充电设施将重点布局在高速公路服务区、城市公共停车场、居住小区、旅游景区等重点区域，同时推动充电设施智能化、网络化发展。</p>
      
      <p>此举旨在解决新能源汽车"充电难"问题，进一步提升用户体验，促进新能源汽车产业健康快速发展。</p>
    `,
    images: [
      { url: '/3.png', alt: '新能源充电桩' }
    ]
  }
]

// 新闻详情数据
const newsDetail = ref({})

// 互动状态
const isLiked = ref(false)
const isCollected = ref(false)
const commentText = ref('')

// 相关新闻数据
const relatedNews = ref([
  {
    id: 2,
    title: 'A股三大指数集体高开 宁德时代涨5.1%',
    summary: '今日开盘，A股三大指数集体高开，创业板指涨幅居前...',
    publishTime: '2025-12-22 09:25'
  },
  {
    id: 3,
    title: '国际油价涨超1% 报103美元/桶 WTI升4%',
    summary: '受中东地缘政治紧张局势影响，国际油价持续走高...',
    publishTime: '2025-12-22 09:15'
  },
  {
    id: 4,
    title: '房地产"超预期政策"密集发布 多家房企发公告',
    summary: '近期多地政府陆续出台房地产支持政策...',
    publishTime: '2025-12-22 09:05'
  }
])

// 热点新闻数据
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

// 评论数据
const comments = ref([
  {
    id: 1,
    author: '投资达人',
    avatar: '/avatar1.png',
    time: '2小时前',
    content: '这次降准力度很大，对市场是重大利好！',
    likeCount: 45
  },
  {
    id: 2,
    author: '财经观察',
    avatar: '/avatar2.png',
    time: '3小时前',
    content: '期待政策效果的显现，实体经济需要这样的支持。',
    likeCount: 28
  },
  {
    id: 3,
    author: '市场分析',
    avatar: '/avatar3.png',
    time: '4小时前',
    content: '降准时机把握得很好，体现了政策的精准性。',
    likeCount: 15
  }
])

// 方法
const handleLike = () => {
  isLiked.value = !isLiked.value
  if (isLiked.value) {
    newsDetail.value.likeCount++
  } else {
    newsDetail.value.likeCount--
  }
}

const handleCollect = () => {
  isCollected.value = !isCollected.value
}

const handleShare = () => {
  if (navigator.share) {
    navigator.share({
      title: newsDetail.value.title,
      text: newsDetail.value.content.substring(0, 100) + '...',
      url: window.location.href
    })
  } else {
    navigator.clipboard.writeText(window.location.href)
    alert('链接已复制到剪贴板')
  }
}

const submitComment = () => {
  if (commentText.value.trim()) {
    comments.value.unshift({
      id: Date.now(),
      author: '当前用户',
      avatar: '/avatar-default.png',
      time: '刚刚',
      content: commentText.value.trim(),
      likeCount: 0
    })
    commentText.value = ''
  }
}

const goToNewsDetail = (id) => {
  router.push(`/news-detail/${id}`)
}

// 根据ID加载新闻详情
const loadNewsDetail = (id) => {
  const newsId = parseInt(id)
  const foundNews = newsData.find(item => item.id === newsId)
  if (foundNews) {
    newsDetail.value = { ...foundNews }
  } else {
    // 如果没有找到，使用第一条新闻
    newsDetail.value = newsData[0]
  }
}

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  loadNewsDetail(newId || 1)
})

// 生命周期
onMounted(() => {
  // 从路由参数获取新闻ID并加载详情
  loadNewsDetail(route.params.id || 1)
})
</script>

<style scoped>
.news-detail-page {
  min-height: 100vh;
  background-color: #fff8f0;
}

.breadcrumb {
  background: #fff;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.breadcrumb a {
  color: #ff7f00;
}

.breadcrumb span {
  color: #666;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

.news-detail-content {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.news-detail-main {
  flex: 3;
  background: #fff;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.news-header {
  border-bottom: 2px solid #ffebd8;
  padding-bottom: 20px;
  margin-bottom: 25px;
}

.news-title {
  font-size: 28px;
  color: #333;
  line-height: 1.4;
  margin-bottom: 15px;
  font-weight: bold;
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  color: #999;
  font-size: 14px;
}

.news-meta span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.news-body {
  margin-bottom: 30px;
}

.news-content {
  font-size: 16px;
  line-height: 1.8;
  color: #333;
}

.news-content p {
  margin-bottom: 20px;
}

.news-images {
  margin: 25px 0;
}

.news-image {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.interaction-section {
  border-top: 1px solid #f0f0f0;
  border-bottom: 1px solid #f0f0f0;
  padding: 20px 0;
  margin: 25px 0;
}

.interaction-buttons {
  display: flex;
  gap: 15px;
}

.interaction-buttons button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.interaction-buttons button:hover {
  border-color: #ff7f00;
  color: #ff7f00;
}

.interaction-buttons button.active {
  background: #ff7f00;
  color: #fff;
  border-color: #ff7f00;
}

.related-news {
  margin: 30px 0;
  padding: 25px;
  background: #fff6ee;
  border-radius: 8px;
}

.related-title {
  font-size: 20px;
  color: #ff7f00;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ffb380;
}

.related-list {
  display: grid;
  gap: 15px;
}

.related-item {
  padding: 15px;
  border: 1px solid #ffebd8;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.related-item:hover {
  background: #ffebd8;
  transform: translateY(-2px);
}

.related-item h4 {
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
}

.related-item p {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 8px;
}

.related-date {
  font-size: 12px;
  color: #999;
}

.comment-section {
  margin-top: 30px;
}

.comment-title {
  font-size: 20px;
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ff7f00;
}

.comment-input {
  margin-bottom: 25px;
}

.comment-input textarea {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  resize: vertical;
  font-size: 14px;
  margin-bottom: 15px;
}

.comment-input textarea:focus {
  outline: none;
  border-color: #ff7f00;
}

.submit-comment-btn {
  padding: 10px 25px;
  background: #ff7f00;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.submit-comment-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.submit-comment-btn:hover:not(:disabled) {
  background: #e06f00;
}

.comment-list {
  display: grid;
  gap: 20px;
}

.comment-item {
  display: flex;
  gap: 15px;
  padding: 20px;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  background: #fff;
}

.comment-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment-author {
  font-weight: bold;
  color: #333;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-text {
  color: #333;
  line-height: 1.6;
  margin-bottom: 15px;
}

.comment-actions {
  display: flex;
  gap: 15px;
}

.comment-actions button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 5px;
}

.comment-actions button:hover {
  color: #ff7f00;
}

.news-sidebar {
  flex: 1;
}

.hot-news {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.sidebar-title {
  font-size: 18px;
  color: #333;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ff7f00;
}

.hot-news ul li {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px dashed #eee;
}

.hot-news ul li:last-child {
  border-bottom: none;
}

.hot-index {
  width: 24px;
  height: 24px;
  line-height: 24px;
  text-align: center;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 12px;
}

.hot-index.top-three {
  background: #ff7f00;
  color: #fff;
}

.hot-news a {
  font-size: 14px;
  color: #333;
  flex: 1;
}

.hot-news a:hover {
  color: #ff7f00;
}

.ad-section img {
  width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .news-detail-content {
    flex-direction: column;
  }
  
  .news-title {
    font-size: 22px;
  }
  
  .news-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .interaction-buttons {
    flex-wrap: wrap;
  }
  
  .comment-item {
    flex-direction: column;
    text-align: center;
  }
  
  .comment-header {
    flex-direction: column;
    gap: 5px;
  }
}

/* 图标样式 */
.icon-time::before { content: '🕒 '; }
.icon-source::before { content: '📰 '; }
.icon-view::before { content: '👁️ '; }
.icon-like::before { content: '👍 '; }
.icon-collect::before { content: '⭐ '; }
.icon-share::before { content: '📤 '; }
</style>