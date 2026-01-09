<template>
  <div class="order-page">
    <!-- 头部导航 -->
    <div class="order-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <span class="back-icon">←</span>
          返回商店
        </button>
        <h1 class="order-title">我的订单</h1>
        <div class="header-actions">
          <span class="order-stats" v-if="orderStore.totalOrders > 0">
            共 {{ orderStore.totalOrders }} 笔订单
          </span>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="order-main" v-if="isLoggedIn">
      <!-- 订单统计区域 -->
      <div class="order-stats-section">
        <div class="stats-card">
          <h3>订单统计</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">总订单数</span>
              <span class="stat-value">{{ orderStore.totalOrders }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总消费金额</span>
              <span class="stat-value">{{ orderStore.formattedTotalAmount }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 订单筛选区域 -->
      <div class="order-filter-section">
        <div class="filter-card">
          <div class="filter-group">
            <label>订单状态：</label>
            <select v-model="filterStatus" class="filter-select">
              <option value="">全部</option>
              <option value="待付款">待付款</option>
              <option value="已付款">已付款</option>
              <option value="处理中">处理中</option>
              <option value="已完成">已完成</option>
              <option value="已取消">已取消</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>产品类型：</label>
            <select v-model="filterType" class="filter-select">
              <option value="">全部</option>
              <option value="factor">量化因子</option>
              <option value="strategy">策略</option>
              <option value="fund">基金</option>
              <option value="advisor">投顾</option>
              <option value="course">课程</option>
              <option value="book">书籍</option>
              <option value="talent">人才</option>
            </select>
          </div>
          
          <div class="filter-group">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="搜索订单号或产品名称" 
              class="search-input"
            >
          </div>
        </div>
      </div>

      <!-- 订单列表区域 -->
      <div class="order-list-section">
        <div class="order-list">
          <div class="order-card">
            <div class="order-header">
              <span class="order-id">订单号: ORD-20251224-001</span>
              <span class="order-date">2025-12-24</span>
              <span class="order-status" style="color: #52c41a; background-color: #f6ffed">
                已完成
              </span>
            </div>
            
            <div class="order-items">
              <div class="order-item">
                <img src="/1.png" alt="动量因子策略" class="item-image">
                <div class="item-info">
                  <div class="item-header">
                    <span class="item-tag" style="background-color: #faad14">因子</span>
                    <span class="risk-indicator" style="color: #faad14">中风险</span>
                  </div>
                  <h4 class="item-name">动量因子策略</h4>
                  <p class="item-price">¥299.00</p>
                </div>
              </div>
            </div>
            
            <div class="order-footer">
              <span class="order-total">总金额: ¥299.00</span>
              <div class="order-actions">
                <button class="action-btn detail-btn">
                  查看详情
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 未登录状态 -->
    <div class="login-required" v-else>
      <div class="login-icon">🔒</div>
      <h2>请先登录</h2>
      <p>登录后即可查看您的订单</p>
      <button class="login-btn" @click="goToLogin">
        前往登录
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useOrderStore } from '@/stores/order.js'

const router = useRouter()
const orderStore = useOrderStore()

// 筛选条件
const filterStatus = ref('')
const filterType = ref('')
const searchQuery = ref('')

// 筛选后的订单
const filteredOrders = computed(() => {
  return orderStore.orders.filter(order => {
    // 状态筛选
    if (filterStatus.value && order.status !== filterStatus.value) {
      return false
    }
    
    // 产品类型筛选
    if (filterType.value && !order.items.some(item => item.type === filterType.value)) {
      return false
    }
    
    // 搜索查询
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      const matchesOrderId = order.id.toLowerCase().includes(query)
      const matchesProductName = order.items.some(item => 
        item.name.toLowerCase().includes(query)
      )
      return matchesOrderId || matchesProductName
    }
    
    return true
  })
})

// 检查订单是否包含高风险产品
const hasHighRiskItems = (order) => {
  return order.items.some(item => item.riskLevel === '高风险')
}

// 获取订单状态样式
const getStatusStyle = (status) => {
  const styles = {
    '待付款': { color: '#ff4d4f', backgroundColor: '#fff2f0' },
    '已付款': { color: '#1890ff', backgroundColor: '#e6f7ff' },
    '处理中': { color: '#faad14', backgroundColor: '#fffbe6' },
    '已完成': { color: '#52c41a', backgroundColor: '#f6ffed' },
    '已取消': { color: '#666', backgroundColor: '#f0f0f0' }
  }
  return styles[status] || {}
}

// 订单操作
const payOrder = (orderId) => {
  alert(`支付订单: ${orderId}`)
  // 实际支付逻辑
}

const cancelOrder = (orderId) => {
  if (confirm('确定要取消此订单吗？')) {
    alert(`取消订单: ${orderId}`)
    // 实际取消逻辑
  }
}

const viewOrderDetail = (orderId) => {
  alert(`查看订单详情: ${orderId}`)
  // 实际查看详情逻辑
}

// 检查登录状态
const isLoggedIn = computed(() => {
  return localStorage.getItem('quantLogin') === '123'
})

const goBack = () => {
  router.back()
}

const goToLogin = () => {
  router.push('/profile')
}
</script>

<style scoped>
.order-page {
  min-height: 100vh;
  background-color: #fff8f0;
}

/* 头部样式 */
.order-header {
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
  align-items: center;
  width: 100%;
}

.order-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  flex: 1;
  text-align: center;
}

.header-actions {
  margin-left: auto;
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

.order-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.order-stats {
  font-size: 14px;
  opacity: 0.9;
}

/* 主内容区域 */
.order-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

/* 订单统计区域 */
.order-stats-section {
  margin-bottom: 30px;
}

.stats-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stats-card h3 {
  color: #333;
  font-size: 20px;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  border: 2px solid #ffb380;
  border-radius: 8px;
  background: white;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  color: #ff7f24;
  font-weight: bold;
}

/* 订单筛选区域 */
.order-filter-section {
  margin-bottom: 20px;
}

.filter-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-select, .search-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.search-input {
  min-width: 200px;
}

/* 订单列表区域 */
.order-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.order-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  border: 2px solid #ffb380;
}

.order-card.order-high-risk {
  border-left: 4px solid #ff4d4f;
}

.order-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
  gap: 20px;
}

.order-id {
  font-weight: bold;
  color: #333;
}

.order-date {
  color: #666;
  font-size: 14px;
}

.order-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.order-items {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 15px;
}

.order-item {
  display: flex;
  gap: 15px;
  padding: 10px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
}

.item-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.item-info {
  flex: 1;
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.item-tag {
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
}

.risk-indicator {
  font-size: 12px;
  font-weight: bold;
}

.item-name {
  font-size: 14px;
  color: #333;
  margin: 0 0 5px 0;
}

.item-price {
  font-size: 14px;
  color: #ff7f24;
  font-weight: bold;
  margin: 0;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.order-total {
  font-size: 16px;
  color: #ff7f24;
  font-weight: bold;
}

.order-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.pay-btn {
  background: #ff7f24;
  color: white;
}

.pay-btn:hover {
  background: #ff6a00;
}

.cancel-btn {
  background: #f0f0f0;
  color: #666;
}

.cancel-btn:hover {
  background: #e0e0e0;
}

.detail-btn {
  background: transparent;
  border: 1px solid #ff7f24;
  color: #ff7f24;
}

.detail-btn:hover {
  background: #fff6ee;
}

/* 空订单状态 */
.empty-orders {
  text-align: center;
  padding: 40px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 50px;
  margin-bottom: 15px;
  color: #ccc;
}

.empty-orders p {
  color: #666;
}

/* 未登录状态 */
.login-required {
  text-align: center;
  padding: 80px 20px;
  max-width: 500px;
  margin: 0 auto;
}

.login-icon {
  font-size: 80px;
  margin-bottom: 20px;
}

.login-required h2 {
  color: #666;
  margin-bottom: 10px;
}

.login-required p {
  color: #999;
  margin-bottom: 30px;
}

.login-btn {
  background: #ff7f24;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.login-btn:hover {
  background: #ff6a00;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 10px;
    text-align: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .order-main {
    padding: 20px 15px;
  }
  
  .stats-card {
    padding: 20px;
  }
}
</style>