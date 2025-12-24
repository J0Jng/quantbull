<template>
  <div class="cart-page">
    <!-- 头部导航 -->
    <div class="cart-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <span class="back-icon">←</span>
          返回商店
        </button>
        <h1 class="cart-title">购物车</h1>
        <div class="header-actions">
          <span class="cart-stats" v-if="cartStore.totalItems > 0">
            共 {{ cartStore.totalItems }} 件商品
          </span>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="cart-main" v-if="cartStore.totalItems > 0">
      <!-- 左右分栏布局 -->
      <div class="cart-layout">
        <!-- 左侧：购物车商品列表 -->
        <div class="cart-items-section">
          <div class="section-header">
            <h2>商品列表</h2>
            <button class="clear-cart-btn" @click="confirmClearCart" v-if="cartStore.totalItems > 0">
              清空购物车
            </button>
          </div>
          
          <div class="cart-items">
            <div 
              v-for="item in cartStore.items" 
              :key="`${item.id}-${item.type}`" 
              class="cart-item"
              :class="{'item-risk-high': item.riskLevel === '高风险'}"
            >
              <div class="item-image">
                <img :src="item.img" :alt="item.name" class="item-img" />
              </div>
              
              <div class="item-info">
                <div class="item-header">
                  <span class="item-tag" :style="{ backgroundColor: item.riskColor }">
                    {{ item.type === 'factor' ? '因子' : 
                       item.type === 'strategy' ? '策略' : 
                       item.type === 'fund' ? '基金' : 
                       item.type === 'advisor' ? '投顾' : 
                       item.type === 'course' ? '课程' : 
                       item.type === 'book' ? '书籍' : '人才' }}
                  </span>
                  <span class="risk-indicator" :style="{ color: item.riskColor }">
                    {{ item.riskLevel }}
                  </span>
                </div>
                
                <h3 class="item-name">{{ item.name }}</h3>
                <p class="item-price">{{ item.price }}</p>
                
                <div class="item-actions">
                  <button class="remove-btn" @click="confirmRemoveItem(item)">
                    移除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：订单摘要 -->
        <div class="order-summary-section">
          <div class="summary-card">
            <h3>订单摘要</h3>
            
            <div class="summary-details">
              <div class="summary-row">
                <span>商品数量</span>
                <span>{{ cartStore.totalItems }} 件</span>
              </div>
              <div class="summary-row">
                <span>商品总价</span>
                <span class="total-amount">{{ cartStore.formattedTotalAmount }}</span>
              </div>
              
              <div class="risk-warning" v-if="cartStore.hasHighRiskProducts">
                <div class="warning-icon">⚠️</div>
                <div class="warning-text">
                  <strong>风险提示：</strong>您的购物车中包含高风险产品，
                  购买前请确保您了解相关风险并具备相应的投资资格。
                </div>
              </div>
            </div>

            <button 
              class="checkout-btn" 
              :class="{disabled: !isCheckoutAllowed}"
              @click="proceedToCheckout"
              :disabled="!isCheckoutAllowed"
            >
              {{ checkoutButtonText }}
            </button>

            <div class="security-notice">
              <p>🔒 安全支付保障 | 📞 专业客服支持</p>
            </div>
          </div>

          <!-- 风险提示区域 -->
          <div class="risk-notice-card">
            <h4>投资风险提示</h4>
            <ul>
              <li>量化投资存在市场风险，过往业绩不代表未来表现</li>
              <li>高风险产品仅适合具备相应风险承受能力的投资者</li>
              <li>基金及投顾产品需合格投资者认证</li>
              <li>建议投资者根据自身情况合理配置资产</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 空购物车状态 -->
    <div class="empty-cart" v-else>
      <div class="empty-icon">🛒</div>
      <h2>购物车是空的</h2>
      <p>快去发现优质的量化投资产品吧！</p>
      <button class="back-to-shop-btn" @click="goToShop">
        返回商店购物
      </button>
    </div>

    <!-- 移除商品确认弹窗 -->
    <div class="confirm-modal" v-show="showRemoveConfirm">
      <div class="modal-content">
        <h3>确认移除</h3>
        <p>确定要从购物车中移除这个商品吗？</p>
        <div class="modal-actions">
          <button class="cancel-btn" @click="cancelRemove">取消</button>
          <button class="confirm-btn" @click="confirmRemove">确定移除</button>
        </div>
      </div>
    </div>

    <!-- 清空购物车确认弹窗 -->
    <div class="confirm-modal" v-show="showClearConfirm">
      <div class="modal-content">
        <h3>确认清空</h3>
        <p>确定要清空整个购物车吗？此操作不可撤销。</p>
        <div class="modal-actions">
          <button class="cancel-btn" @click="cancelClear">取消</button>
          <button class="confirm-btn" @click="confirmClear">确定清空</button>
        </div>
      </div>
    </div>

    <!-- 高风险产品确认弹窗 -->
    <div class="confirm-modal risk-confirm-modal" v-show="showRiskConfirm">
      <div class="modal-content">
        <div class="risk-icon-large">⚠️</div>
        <h3>高风险产品购买确认</h3>
        <p>您将要购买的产品包含高风险金融产品，请确认：</p>
        <ul class="risk-list">
          <li>我已了解该产品的风险特性</li>
          <li>我具备相应的风险承受能力</li>
          <li>我已阅读并理解相关风险揭示书</li>
        </ul>
        <div class="modal-actions">
          <button class="cancel-btn" @click="cancelCheckout">再考虑一下</button>
          <button class="confirm-btn risk-confirm" @click="proceedWithCheckout">确认购买</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart.js'

const router = useRouter()
const cartStore = useCartStore()

// 响应式数据
const showRemoveConfirm = ref(false)
const showClearConfirm = ref(false)
const showRiskConfirm = ref(false)
const itemToRemove = ref(null)

// 计算属性
const isCheckoutAllowed = computed(() => {
  const isLoggedIn = localStorage.getItem('quantLogin') === '123'
  if (!isLoggedIn) return false
  if (cartStore.totalItems === 0) return false
  return cartStore.canPurchaseHighRiskProducts()
})

const checkoutButtonText = computed(() => {
  if (!localStorage.getItem('quantLogin')) {
    return '请先登录'
  }
  if (cartStore.totalItems === 0) {
    return '购物车为空'
  }
  if (cartStore.hasHighRiskProducts && !localStorage.getItem('qualifiedInvestor')) {
    return '需合格投资者认证'
  }
  return `立即结算 (${cartStore.formattedTotalAmount})`
})

// 方法
const goBack = () => {
  router.back()
}

const goToShop = () => {
  router.push('/shop')
}

const confirmRemoveItem = (item) => {
  itemToRemove.value = item
  showRemoveConfirm.value = true
}

const cancelRemove = () => {
  showRemoveConfirm.value = false
  itemToRemove.value = null
}

const confirmRemove = () => {
  if (itemToRemove.value) {
    cartStore.removeFromCart(itemToRemove.value.id, itemToRemove.value.type)
  }
  showRemoveConfirm.value = false
  itemToRemove.value = null
}

const confirmClearCart = () => {
  showClearConfirm.value = true
}

const cancelClear = () => {
  showClearConfirm.value = false
}

const confirmClear = () => {
  cartStore.clearCart()
  showClearConfirm.value = false
}

const proceedToCheckout = () => {
  // 检查登录状态
  if (!localStorage.getItem('quantLogin')) {
    alert('请先登录后再进行结算')
    return
  }

  // 检查高风险产品购买资格
  if (cartStore.hasHighRiskProducts) {
    if (!localStorage.getItem('qualifiedInvestor')) {
      alert('购买高风险产品需要完成合格投资者认证，请先前往个人主页完成认证')
      return
    }
    // 显示风险确认弹窗
    showRiskConfirm.value = true
  } else {
    // 直接跳转到结算页面（这里可以扩展实际的结算流程）
    alert('即将跳转到结算页面...')
    // router.push('/checkout') // 可以扩展真实的结算页面
  }
}

const cancelCheckout = () => {
  showRiskConfirm.value = false
}

const proceedWithCheckout = () => {
  showRiskConfirm.value = false
  alert('即将跳转到结算页面...')
  // router.push('/checkout') // 可以扩展真实的结算页面
}
</script>

<style scoped>
.cart-page {
  min-height: 100vh;
  background-color: #fff8f0;
}

/* 头部样式 */
.cart-header {
  background-color: #ff7f24;
  color: white;
  padding: 15px 0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 10px rgba(255, 127, 36, 0.2);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.back-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.3s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.back-icon {
  font-size: 18px;
}

.cart-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.cart-stats {
  font-size: 14px;
  opacity: 0.9;
}

/* 主内容区域 */
.cart-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

.cart-layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 30px;
}

/* 购物车商品列表 */
.cart-items-section {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.section-header h2 {
  color: #333;
  font-size: 20px;
  margin: 0;
}

.clear-cart-btn {
  background: #ff4d4f;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.clear-cart-btn:hover {
  background: #ff7875;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.cart-item {
  display: flex;
  gap: 15px;
  padding: 20px;
  border: 2px solid #ffb380;
  border-radius: 8px;
  background: white;
  transition: all 0.3s ease;
}

.cart-item:hover {
  border-color: #ff7f24;
  box-shadow: 0 4px 12px rgba(255, 127, 36, 0.15);
}

.cart-item.item-risk-high {
  border-left: 4px solid #ff4d4f;
}

.item-image {
  flex-shrink: 0;
}

.item-img {
  width: 100px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-tag {
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.risk-indicator {
  font-size: 12px;
  font-weight: bold;
}

.item-name {
  font-size: 16px;
  color: #333;
  margin: 0;
  line-height: 1.4;
}

.item-price {
  font-size: 18px;
  color: #ff7f24;
  font-weight: bold;
  margin: 0;
}

.item-actions {
  margin-top: auto;
}

.remove-btn {
  background: #ff4d4f;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background-color 0.3s;
}

.remove-btn:hover {
  background: #ff7875;
}

/* 订单摘要 */
.order-summary-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.summary-card h3 {
  color: #333;
  font-size: 18px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.summary-details {
  margin-bottom: 25px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.total-amount {
  font-size: 20px;
  color: #ff7f24;
  font-weight: bold;
}

.risk-warning {
  background: #fff2e8;
  border: 1px solid #ffd591;
  border-radius: 6px;
  padding: 15px;
  margin-top: 15px;
  display: flex;
  gap: 10px;
}

.warning-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.warning-text {
  font-size: 14px;
  color: #d46b08;
  line-height: 1.4;
}

.checkout-btn {
  width: 100%;
  background: #ff7f24;
  color: white;
  border: none;
  padding: 15px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.checkout-btn:hover:not(.disabled) {
  background: #ff6a00;
  transform: translateY(-2px);
}

.checkout-btn.disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.security-notice {
  text-align: center;
  margin-top: 15px;
  font-size: 12px;
  color: #666;
}

/* 风险提示卡片 */
.risk-notice-card {
  background: #fff2e8;
  border: 2px solid #ffd591;
  border-radius: 12px;
  padding: 20px;
}

.risk-notice-card h4 {
  color: #d46b08;
  margin-bottom: 15px;
  font-size: 16px;
}

.risk-notice-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.risk-notice-card li {
  padding: 5px 0;
  color: #8c531b;
  font-size: 14px;
  line-height: 1.4;
  position: relative;
  padding-left: 15px;
}

.risk-notice-card li:before {
  content: "•";
  color: #ff7f24;
  position: absolute;
  left: 0;
}

/* 空购物车状态 */
.empty-cart {
  text-align: center;
  padding: 80px 20px;
  max-width: 500px;
  margin: 0 auto;
}

.empty-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.empty-cart h2 {
  color: #666;
  margin-bottom: 10px;
}

.empty-cart p {
  color: #999;
  margin-bottom: 30px;
}

.back-to-shop-btn {
  background: #ff7f24;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.back-to-shop-btn:hover {
  background: #ff6a00;
}

/* 确认弹窗 */
.confirm-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 30px;
  max-width: 400px;
  width: 90%;
  text-align: center;
}

.modal-content h3 {
  color: #333;
  margin-bottom: 15px;
}

.modal-content p {
  color: #666;
  margin-bottom: 25px;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.cancel-btn, .confirm-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.cancel-btn {
  background: #f0f0f0;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.confirm-btn {
  background: #ff7f24;
  color: white;
}

.confirm-btn:hover {
  background: #ff6a00;
}

/* 风险确认弹窗特殊样式 */
.risk-confirm-modal .modal-content {
  max-width: 450px;
}

.risk-icon-large {
  font-size: 40px;
  margin-bottom: 15px;
}

.risk-list {
  text-align: left;
  margin: 15px 0;
  padding-left: 20px;
}

.risk-list li {
  margin-bottom: 8px;
  color: #666;
}

.risk-confirm {
  background: #ff4d4f;
}

.risk-confirm:hover {
  background: #ff7875;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .cart-layout {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .cart-item {
    flex-direction: column;
    text-align: center;
  }
  
  .item-image {
    align-self: center;
  }
  
  .modal-actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .cart-main {
    padding: 20px 15px;
  }
  
  .cart-items-section,
  .summary-card {
    padding: 20px;
  }
}
</style>