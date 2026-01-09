<template>
  <!-- 商品详情页面 -->
  <div class="product-detail">
    <!-- 头部 -->
    <div class="header">
      <div class="logo" @click="goHome">量化牛牛商店</div>
      <div class="header-nav">
        <a href="#" @click.prevent="goShop">首页</a>
        <a href="#">教育培训</a>
        <a href="#">我的订单</a>
        <a href="#">购物车</a>
      </div>
    </div>

    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <a href="#" @click.prevent="goShop">首页</a> > 
      <a href="#" @click.prevent="goShop">教育培训</a> > 
      <a href="#" @click.prevent="goShop">理财课程</a> > 
      理财入门实战课
    </div>

    <!-- 商品详情核心区 -->
    <div class="detail-container">
      <!-- 商品主图 -->
      <div class="goods-img">
        <img src="https://picsum.photos/600/400" alt="理财入门实战课" class="main-img">
      </div>

      <!-- 商品信息 -->
      <div class="goods-info">
        <span class="goods-tag">{{ currentGoods?.category || '商品' }}</span>
        <h1 class="goods-title">{{ currentGoods?.title || '加载中...' }}</h1>

        <!-- 价格区域 -->
        <div class="price-area">
          <div class="price-label">售价</div>
          <div class="current-price">¥{{ currentGoods?.price?.toFixed(2) || '0.00' }}</div>
          <div class="origin-price">原价：¥{{ currentGoods?.originalPrice?.toFixed(2) || '0.00' }}</div>
        </div>

        <!-- 规格选择 -->
        <div class="spec-area">
          <div class="spec-title">选择课程版本</div>
          <div 
            class="spec-option" 
            :class="{ active: selectedSpec === 'basic' }"
            @click="selectedSpec = 'basic'"
          >
            基础版（视频课+讲义）
          </div>
          <div 
            class="spec-option" 
            :class="{ active: selectedSpec === 'advanced' }"
            @click="selectedSpec = 'advanced'"
          >
            进阶版（视频课+讲义+1v1答疑）
          </div>
          <div 
            class="spec-option" 
            :class="{ active: selectedSpec === 'premium' }"
            @click="selectedSpec = 'premium'"
          >
            至尊版（全套+社群+实操指导）
          </div>
        </div>

        <!-- 购买按钮区域 -->
        <div class="buy-area">
          <button class="buy-btn" @click="handleBuy">立即购买</button>
          <div class="trial-btn" @click="showTrialModal">
            免费试听
          </div>
          <button class="cart-btn" @click="addToCart">加入购物车</button>
        </div>

        <!-- 课程基础信息 -->
        <div class="course-info">
          <div class="course-info-item">
            <div class="course-label">课程课时：</div>
            <div class="course-value">12课时（每课时45分钟）</div>
          </div>
          <div class="course-info-item">
            <div class="course-label">适合人群：</div>
            <div class="course-value">零基础理财新手、上班族、宝妈</div>
          </div>
          <div class="course-info-item">
            <div class="course-label">学习方式：</div>
            <div class="course-value">录播视频（永久回放）+ 在线答疑</div>
          </div>
          <div class="course-info-item">
            <div class="course-label">开课时间：</div>
            <div class="course-value">购买后立即开课</div>
          </div>
          <div class="course-info-item">
            <div class="course-label">讲师：</div>
            <div class="course-value">张老师（10年理财实战经验）</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 课程详情/大纲 Tab -->
    <div class="goods-detail">
      <div class="tab-nav">
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'outline' }"
          @click="activeTab = 'outline'"
        >
          课程大纲
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'detail' }"
          @click="activeTab = 'detail'"
        >
          课程详情
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'review' }"
          @click="activeTab = 'review'"
        >
          学员评价
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'faq' }"
          @click="activeTab = 'faq'"
        >
          常见问题
        </div>
      </div>
      <div class="tab-content">
        <div v-if="activeTab === 'outline'">
          <div class="outline-item">
            <div class="outline-title">第1章：理财基础认知（2课时）</div>
            <p>1.1 为什么普通人必须理财？破除"理财=有钱"误区</p>
            <p>1.2 理财的核心原则：风险与收益的平衡</p>
          </div>
          <div class="outline-item">
            <div class="outline-title">第2章：低风险理财工具实操（4课时）</div>
            <p>2.1 基金入门：货币基金、债券基金怎么选？</p>
            <p>2.2 国债逆回购：零风险的短期理财神器</p>
            <p>2.3 银行理财：避开坑，选对高收益产品</p>
            <p>2.4 实操演练：手把手教你买入第一只基金</p>
          </div>
          <div class="outline-item">
            <div class="outline-title">第3章：中高收益理财技巧（4课时）</div>
            <p>3.1 股票入门：新手如何选股、看盘？</p>
            <p>3.2 指数基金定投：懒人躺赚的核心策略</p>
            <p>3.3 资产配置：不同收入阶段的理财组合</p>
            <p>3.4 避坑指南：远离高风险理财骗局</p>
          </div>
          <div class="outline-item">
            <div class="outline-title">第4章：实战复盘与答疑（2课时）</div>
            <p>4.1 学员案例拆解：从月光到月存5000的理财方案</p>
            <p>4.2 一对一答疑：解决你的个性化理财问题</p>
          </div>
        </div>
        <div v-if="activeTab === 'detail'">
          <h3>课程详细介绍</h3>
          <p>本课程专为零基础理财小白设计，从最基础的理财认知开始，逐步深入讲解各种理财工具的使用方法和实战技巧。</p>
          <p>课程特色：实战导向、案例丰富、通俗易懂、注重风险控制</p>
        </div>
        <div v-if="activeTab === 'review'">
          <h3>学员评价</h3>
          <p>"老师讲解很细致，零基础也能学会！"</p>
          <p>"课程内容实用，已经成功开始理财了"</p>
        </div>
        <div v-if="activeTab === 'faq'">
          <h3>常见问题</h3>
          <p><strong>Q: 需要什么基础？</strong> A: 零基础即可</p>
          <p><strong>Q: 课程有效期多长？</strong> A: 永久有效</p>
        </div>
      </div>
    </div>

    <!-- 相关推荐 -->
    <div class="recommend">
      <div class="recommend-title">猜你喜欢</div>
      <div class="recommend-grid">
        <div class="recommend-card">
          <img src="https://picsum.photos/300/200" alt="量化投资进阶班" class="recommend-img">
          <div class="recommend-name">量化投资进阶班</div>
          <div class="recommend-price">¥299.00</div>
        </div>
        <div class="recommend-card">
          <img src="https://picsum.photos/300/200" alt="家庭资产配置课" class="recommend-img">
          <div class="recommend-name">家庭资产配置课</div>
          <div class="recommend-price">¥159.00</div>
        </div>
        <div class="recommend-card">
          <img src="https://picsum.photos/300/200" alt="基金定投实战课" class="recommend-img">
          <div class="recommend-name">基金定投实战课</div>
          <div class="recommend-price">¥89.00</div>
        </div>
        <div class="recommend-card">
          <img src="https://picsum.photos/300/200" alt="股票入门必修课" class="recommend-img">
          <div class="recommend-name">股票入门必修课</div>
          <div class="recommend-price">¥129.00</div>
        </div>
      </div>
    </div>

    <!-- 试听弹窗 -->
    <div class="modal-mask" v-show="showModal">
      <div class="modal-content">
        <span class="close-modal" @click="closeModal">&times;</span>
        <div class="trial-video">
          <img src="https://picsum.photos/800/400" alt="试看视频封面" style="width:100%;height:100%;object-fit:cover;border-radius:8px;">
        </div>
        <div class="trial-tips">🎬 正在播放免费试看内容（限时3分钟）</div>
        <div class="countdown">{{ countdownText }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { watch } from 'vue'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const router = useRouter()
const currentGoods = ref(null)

// 根据ID加载商品数据
function loadGoodsData() {
  // 模拟商品数据映射
  const goodsDataMap = {
    'factor-0': {
      title: '量价因子合集 - 超100个经典A股量价因子（可直接回测）',
      price: 1299.00,
      originalPrice: 1999.00,
      category: '因子',
      description: '包含100+个经过验证的A股量价因子...'
    },
    'strategy-0': {
      title: '双均线择时策略 - 年化收益25%+（附Python源码）',
      price: 699.00,
      originalPrice: 999.00,
      category: '策略',
      description: '经典双均线策略，附带完整Python实现...'
    },
    // 其他模拟商品数据...
  }

  // 检查商品是否存在
  if (goodsDataMap[props.id]) {
    currentGoods.value = goodsDataMap[props.id]
  } else {
    currentGoods.value = {
      title: '商品不存在',
      price: 0,
      originalPrice: 0,
      category: '错误',
      description: '抱歉，您请求的商品不存在或已下架'
    }
    // 可以在这里添加错误提示逻辑
  }
}

// 监听ID变化
watch(() => props.id, () => {
  loadGoodsData()
})

// 初始化加载
loadGoodsData()
const selectedSpec = ref('basic')
const activeTab = ref('outline')
const showModal = ref(false)
const countdownText = ref('剩余试看时间：03:00')
let countdownTimer = null
let minutes = 2
let seconds = 59

function goHome() {
  router.push('/')
}

function goShop() {
  router.push('/shop')
}

function handleBuy() {
  alert('购买功能开发中...')
}

function addToCart() {
  alert('已加入购物车')
}

function showTrialModal() {
  showModal.value = true
  startCountdown()
}

function closeModal() {
  showModal.value = false
  resetCountdown()
}

function startCountdown() {
  minutes = 2
  seconds = 59
  countdownText.value = '剩余试看时间：03:00'
  
  countdownTimer = setInterval(() => {
    if (seconds === 0) {
      if (minutes === 0) {
        clearInterval(countdownTimer)
        countdownText.value = '试看时间已结束！'
        setTimeout(() => {
          showModal.value = false
          resetCountdown()
        }, 2000)
        return
      }
      minutes--
      seconds = 59
    } else {
      seconds--
    }
    const displayMin = minutes < 10 ? `0${minutes}` : minutes
    const displaySec = seconds < 10 ? `0${seconds}` : seconds
    countdownText.value = `剩余试看时间：0${displayMin}:${displaySec}`
  }, 1000)
}

function resetCountdown() {
  if (countdownTimer) {
    clearInterval(countdownTimer)
    countdownTimer = null
  }
  countdownText.value = '剩余试看时间：03:00'
  minutes = 2
  seconds = 59
}

onUnmounted(() => {
  resetCountdown()
})
</script>

<style scoped>
/* 全局重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: "微软雅黑", sans-serif;
}

.product-detail {
  background-color: #fff8f0;
  color: #333;
  min-height: 100vh;
}

/* 头部导航 */
.header {
  background-color: #ff7f24;
  padding: 12px 20px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 22px;
  font-weight: bold;
  cursor: pointer;
}

.logo:hover {
  opacity: 0.8;
}

.header-nav a {
  color: white;
  text-decoration: none;
  margin-left: 20px;
  font-size: 14px;
  cursor: pointer;
}

.header-nav a:hover {
  text-decoration: underline;
}

/* 面包屑导航 */
.breadcrumb {
  padding: 10px 20px;
  font-size: 14px;
  color: #666;
  background-color: white;
}

.breadcrumb a {
  color: #ff7f24;
  text-decoration: none;
  cursor: pointer;
}

.breadcrumb a:hover {
  color: #ff9933;
}

/* 商品详情容器 */
.detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

/* 商品主图区 */
.goods-img {
  flex: 1;
  min-width: 300px;
}

.main-img {
  width: 100%;
  border-radius: 8px;
  border: 1px solid #ffb380;
}

/* 商品信息区 */
.goods-info {
  flex: 2;
  min-width: 300px;
}

.goods-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 15px;
  border-bottom: 2px solid #ff9933;
  padding-bottom: 10px;
}

.goods-tag {
  display: inline-block;
  background-color: #ff9933;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-bottom: 15px;
}

/* 价格区域 */
.price-area {
  background-color: #fff3e6;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.price-label {
  font-size: 14px;
  color: #666;
}

.current-price {
  font-size: 28px;
  color: #ff7f24;
  font-weight: bold;
  margin: 10px 0;
}

.origin-price {
  font-size: 14px;
  color: #999;
  text-decoration: line-through;
}

/* 规格选择 */
.spec-area {
  margin-bottom: 20px;
}

.spec-title {
  font-size: 16px;
  color: #333;
  margin-bottom: 10px;
}

.spec-option {
  display: inline-block;
  border: 1px solid #ffb380;
  padding: 8px 16px;
  border-radius: 4px;
  margin-right: 10px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.spec-option.active {
  background-color: #ff7f24;
  color: white;
  border-color: #ff7f24;
}

.spec-option:hover {
  border-color: #ff7f24;
  transform: translateY(-2px);
}

/* 购买按钮区域 */
.buy-area {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.buy-btn {
  flex: 2;
  background-color: #ff7f24;
  color: white;
  border: none;
  padding: 12px 0;
  border-radius: 8px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.buy-btn:hover {
  background-color: #ff9933;
}

.trial-btn {
  flex: 1;
  background-color: #fff3e6;
  color: #ff7f24;
  border: 1px solid #ff7f24;
  padding: 12px 0;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  text-align: center;
  transition: all 0.3s;
}

.trial-btn:hover {
  background-color: #ffe8cc;
  transform: translateY(-2px);
}

.cart-btn {
  flex: 1;
  background-color: white;
  color: #ff7f24;
  border: 1px solid #ff7f24;
  padding: 12px 0;
  border-radius: 8px;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s;
}

.cart-btn:hover {
  background-color: #fff3e6;
  transform: translateY(-2px);
}

/* 课程信息 */
.course-info {
  border-top: 1px solid #ffebcd;
  padding-top: 20px;
}

.course-info-item {
  display: flex;
  margin-bottom: 10px;
}

.course-label {
  width: 100px;
  color: #666;
}

.course-value {
  color: #333;
}

/* 商品详情/课程大纲 */
.goods-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 30px;
}

.tab-nav {
  display: flex;
  border-bottom: 2px solid #ff9933;
  margin-bottom: 20px;
}

.tab-item {
  padding: 10px 20px;
  background-color: #ffb380;
  color: white;
  cursor: pointer;
  margin-right: 5px;
  transition: background-color 0.3s;
}

.tab-item.active {
  background-color: #ff9933;
}

.tab-item:hover {
  background-color: #ff9933;
}

.tab-content {
  padding: 20px;
  background-color: white;
  border-radius: 0 0 8px 8px;
  line-height: 1.8;
  min-height: 200px;
}

.outline-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #ffebcd;
}

.outline-title {
  font-size: 16px;
  color: #ff7f24;
  margin-bottom: 8px;
}

/* 相关推荐 */
.recommend {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px 50px;
}

.recommend-title {
  font-size: 20px;
  color: #ff7f24;
  border-left: 4px solid #ff7f24;
  padding-left: 10px;
  margin-bottom: 20px;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
}

.recommend-card {
  background-color: white;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #ffb380;
  transition: transform 0.3s;
}

.recommend-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(255, 127, 36, 0.15);
}

.recommend-img {
  width: 100%;
  border-radius: 4px;
  margin-bottom: 10px;
}

.recommend-name {
  font-size: 16px;
  margin-bottom: 8px;
}

.recommend-price {
  color: #ff7f24;
  font-weight: bold;
}

/* 试听弹窗样式 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.modal-content {
  width: 80%;
  max-width: 800px;
  background: white;
  border-radius: 10px;
  padding: 20px;
  position: relative;
}

.close-modal {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 24px;
  color: #ff7f24;
  cursor: pointer;
}

.trial-video {
  width: 100%;
  height: 400px;
  background: #f5f5f5;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 15px;
}

.trial-tips {
  color: #ff7f24;
  font-weight: 500;
  text-align: center;
}

.countdown {
  color: #ff4500;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
  margin-top: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .detail-container {
    flex-direction: column;
  }
  
  .buy-area {
    flex-direction: column;
  }
  
  .recommend-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }
  
  .modal-content {
    width: 95%;
    padding: 15px;
  }
  
  .trial-video {
    height: 200px;
  }
}
</style>