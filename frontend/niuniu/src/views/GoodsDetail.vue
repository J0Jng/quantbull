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

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载商品详情中...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="loadError" class="error-container">
      <div class="error-icon">😕</div>
      <h2>商品不存在</h2>
      <p>抱歉，您请求的商品不存在或已下架</p>
      <button class="back-btn" @click="goShop">返回商店</button>
    </div>

    <template v-else>
      <!-- 面包屑导航 -->
      <div class="breadcrumb">
        <a href="#" @click.prevent="goShop">首页</a> > 
        <a href="#" @click.prevent="goShop">{{ productTypeName }}</a> > 
        {{ currentGoods?.name || '商品详情' }}
      </div>

      <!-- 商品详情核心区 -->
      <div class="detail-container">
        <!-- 商品主图 -->
        <div class="goods-img">
          <img :src="currentGoods?.img || defaultImg" :alt="currentGoods?.name" class="main-img">
        </div>

        <!-- 商品信息 -->
        <div class="goods-info">
          <span class="goods-tag">{{ productTypeName }}</span>
          <h1 class="goods-title">{{ currentGoods?.name || '加载中...' }}</h1>

          <!-- 价格区域 -->
          <div class="price-area">
            <div class="price-label">售价</div>
            <div class="current-price">{{ formatPrice(currentGoods?.price) }}</div>
            <div class="origin-price" v-if="currentGoods?.original_price">
              原价：{{ formatPrice(currentGoods?.original_price) }}
            </div>
          </div>

          <!-- 购买按钮区域 -->
          <div class="buy-area">
            <button class="buy-btn" @click="handleBuy">{{ buyButtonText }}</button>
            <div class="trial-btn" v-if="currentGoods?.type === 'course'" @click="showTrialModal">
              免费试听
            </div>
            <button class="cart-btn" @click="addToCart">加入购物车</button>
          </div>

          <!-- 商品基础信息 -->
          <div class="course-info" v-if="hasDetailInfo">
            <div class="course-info-item" v-if="currentGoods?.duration">
              <div class="course-label">课程课时：</div>
              <div class="course-value">{{ currentGoods.duration }}</div>
            </div>
            <div class="course-info-item" v-if="currentGoods?.target_audience">
              <div class="course-label">适合人群：</div>
              <div class="course-value">{{ currentGoods.target_audience }}</div>
            </div>
            <div class="course-info-item" v-if="currentGoods?.learning_method">
              <div class="course-label">学习方式：</div>
              <div class="course-value">{{ currentGoods.learning_method }}</div>
            </div>
            <div class="course-info-item" v-if="currentGoods?.start_time">
              <div class="course-label">开课时间：</div>
              <div class="course-value">{{ currentGoods.start_time }}</div>
            </div>
            <div class="course-info-item" v-if="currentGoods?.instructor">
              <div class="course-label">讲师：</div>
              <div class="course-value">{{ currentGoods.instructor }}</div>
            </div>
          </div>

          <!-- 商品描述 -->
          <div class="goods-description" v-if="currentGoods?.description">
            <div class="description-title">商品简介</div>
            <p>{{ currentGoods.description }}</p>
          </div>
        </div>
      </div>

      <!-- 课程详情/大纲 Tab -->
      <div class="goods-detail" v-if="hasTabContent">
        <div class="tab-nav">
          <div 
            class="tab-item" 
            v-if="parsedOutline.length > 0"
            :class="{ active: activeTab === 'outline' }"
            @click="activeTab = 'outline'"
          >
            课程大纲
          </div>
          <div 
            class="tab-item" 
            v-if="currentGoods?.detail_content"
            :class="{ active: activeTab === 'detail' }"
            @click="activeTab = 'detail'"
          >
            详细介绍
          </div>
          <div 
            class="tab-item" 
            v-if="parsedFaq.length > 0"
            :class="{ active: activeTab === 'faq' }"
            @click="activeTab = 'faq'"
          >
            常见问题
          </div>
        </div>
        <div class="tab-content">
          <div v-if="activeTab === 'outline' && parsedOutline.length > 0">
            <div class="outline-item" v-for="(chapter, idx) in parsedOutline" :key="idx">
              <div class="outline-title">{{ chapter.title }}</div>
              <p v-for="(item, itemIdx) in chapter.items" :key="itemIdx">{{ item }}</p>
            </div>
          </div>
          <div v-if="activeTab === 'detail' && currentGoods?.detail_content">
            <div class="detail-text">{{ currentGoods.detail_content }}</div>
          </div>
          <div v-if="activeTab === 'faq' && parsedFaq.length > 0">
            <div class="faq-item" v-for="(item, idx) in parsedFaq" :key="idx">
              <p><strong>Q: {{ item.q }}</strong></p>
              <p>A: {{ item.a }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 相关推荐 -->
      <div class="recommend" v-if="relatedProducts.length > 0">
        <div class="recommend-title">猜你喜欢</div>
        <div class="recommend-grid">
          <div 
            class="recommend-card" 
            v-for="item in relatedProducts" 
            :key="item.id"
            @click="goToProduct(item.id)"
          >
            <img :src="item.img || defaultImg" :alt="item.name" class="recommend-img">
            <div class="recommend-name">{{ item.name }}</div>
            <div class="recommend-price">{{ formatPrice(item.price) }}</div>
          </div>
        </div>
      </div>
    </template>

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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart.js'
import { getProduct, getProducts, formatPrice as serviceFormatPrice, ProductTypeName } from '@/services/productService'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const router = useRouter()
const cartStore = useCartStore()

// 状态
const currentGoods = ref(null)
const loading = ref(true)
const loadError = ref(false)
const relatedProducts = ref([])
const defaultImg = 'https://picsum.photos/600/400?random=0'

// 商品类型名称
const productTypeName = computed(() => {
  if (!currentGoods.value?.type) return '商品'
  return ProductTypeName[currentGoods.value.type] || '商品'
})

// 购买按钮文字
const buyButtonText = computed(() => {
  const type = currentGoods.value?.type
  if (type === 'fund') return '预约认购'
  if (type === 'talent') return '咨询对接'
  if (type === 'advisor') return '预约咨询'
  return '立即购买'
})

// 是否有详情信息
const hasDetailInfo = computed(() => {
  const g = currentGoods.value
  return g?.duration || g?.target_audience || g?.learning_method || g?.start_time || g?.instructor
})

// 解析课程大纲（JSON）
const parsedOutline = computed(() => {
  if (!currentGoods.value?.outline) return []
  try {
    return JSON.parse(currentGoods.value.outline)
  } catch {
    return []
  }
})

// 解析常见问题（JSON）
const parsedFaq = computed(() => {
  if (!currentGoods.value?.faq) return []
  try {
    return JSON.parse(currentGoods.value.faq)
  } catch {
    return []
  }
})

// 是否有Tab内容
const hasTabContent = computed(() => {
  return parsedOutline.value.length > 0 || currentGoods.value?.detail_content || parsedFaq.value.length > 0
})

// 格式化价格
function formatPrice(price) {
  return serviceFormatPrice(price)
}

// 从后端加载商品数据
async function loadGoodsData() {
  loading.value = true
  loadError.value = false
  
  try {
    const result = await getProduct(props.id)
    if (result.success && result.data) {
      currentGoods.value = result.data
      // 设置默认Tab
      if (parsedOutline.value.length > 0) {
        activeTab.value = 'outline'
      } else if (currentGoods.value.detail_content) {
        activeTab.value = 'detail'
      } else if (parsedFaq.value.length > 0) {
        activeTab.value = 'faq'
      }
      // 加载相关推荐
      await loadRelatedProducts()
    } else {
      loadError.value = true
    }
  } catch (error) {
    console.error('Error loading product:', error)
    loadError.value = true
  } finally {
    loading.value = false
  }
}

// 加载相关推荐（同类型商品）
async function loadRelatedProducts() {
  if (!currentGoods.value?.type) return
  
  try {
    const result = await getProducts({ type: currentGoods.value.type, limit: 5 })
    if (result.success && result.data) {
      // 排除当前商品
      relatedProducts.value = result.data
        .filter(p => p.id !== currentGoods.value.id)
        .slice(0, 4)
    }
  } catch (error) {
    console.error('Error loading related products:', error)
  }
}

// 跳转到其他商品
function goToProduct(productId) {
  router.push(`/shop/goods-detail/${productId}`)
}

// 监听ID变化
watch(() => props.id, () => {
  loadGoodsData()
})

// 初始化
onMounted(() => {
  loadGoodsData()
})

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
  if (!currentGoods.value) return
  
  const cartItem = {
    id: currentGoods.value.id,
    name: currentGoods.value.name,
    price: formatPrice(currentGoods.value.price),
    rawPrice: currentGoods.value.price,
    img: currentGoods.value.img || defaultImg,
    type: currentGoods.value.type
  }
  
  cartStore.addToCart(cartItem)
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

/* 加载状态 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
  color: #ff7f24;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #ffb380;
  border-top-color: #ff7f24;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 错误状态 */
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100px 20px;
  text-align: center;
}

.error-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.error-container h2 {
  color: #ff7f24;
  margin-bottom: 10px;
}

.error-container p {
  color: #666;
  margin-bottom: 20px;
}

.back-btn {
  background-color: #ff7f24;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
}

.back-btn:hover {
  background-color: #ff6a00;
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

/* 商品描述 */
.goods-description {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ffebcd;
}

.description-title {
  font-size: 16px;
  color: #ff7f24;
  margin-bottom: 10px;
  font-weight: 500;
}

.goods-description p {
  color: #666;
  line-height: 1.8;
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

/* 详细内容文本 */
.detail-text {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #333;
}

/* FAQ样式 */
.faq-item {
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #ffebcd;
}

.faq-item:last-child {
  border-bottom: none;
}

.faq-item p {
  margin-bottom: 5px;
}

.faq-item strong {
  color: #ff7f24;
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
  cursor: pointer;
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