import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  
  // 风险等级定义
  const riskLevels = {
    low: { label: '低风险', color: '#52c41a' },
    medium: { label: '中风险', color: '#faad14' },
    high: { label: '高风险', color: '#ff4d4f' }
  }
  
  // 产品类型风险映射
  const productTypeRisk = {
    'factor': riskLevels.medium,
    'strategy': riskLevels.high,
    'fund': riskLevels.high,
    'advisor': riskLevels.medium,
    'course': riskLevels.low,
    'book': riskLevels.low,
    'talent': riskLevels.medium
  }

  // 获取已下线功能商品总数
  const totalItems = computed(() => items.value.length)

  // 计算总金额
  const totalAmount = computed(() => {
    return items.value.reduce((total, item) => {
      const price = parseFloat(item.price.replace(/[^0-9.]/g, '')) || 0
      return total + price
    }, 0)
  })

  // 检查是否有高风险产品
  const hasHighRiskProducts = computed(() => {
    return items.value.some(item => item.riskLevel === 'high')
  })

  // 添加商品到已下线功能
  const addToCart = (product) => {
    const existingItem = items.value.find(item => 
      item.id === product.id && item.type === product.type
    )
    
    if (existingItem) {
      // 如果商品已存在，更新数量（如果需要支持多数量）
      existingItem.quantity += product.quantity || 1
    } else {
      // 添加新商品
      items.value.push({
        ...product,
        quantity: product.quantity || 1,
        riskLevel: productTypeRisk[product.type]?.label || riskLevels.medium.label,
        riskColor: productTypeRisk[product.type]?.color || riskLevels.medium.color,
        addedAt: new Date().toISOString()
      })
    }
  }

  // 从已下线功能移除商品
  const removeFromCart = (productId, productType) => {
    const index = items.value.findIndex(item => 
      item.id === productId && item.type === productType
    )
    
    if (index !== -1) {
      items.value.splice(index, 1)
      return true
    }
    return false
  }

  // 清空已下线功能
  const clearCart = () => {
    items.value = []
  }

  // 更新商品数量
  const updateQuantity = (productId, productType, quantity) => {
    const item = items.value.find(item => 
      item.id === productId && item.type === productType
    )
    
    if (item && quantity > 0) {
      item.quantity = quantity
    } else if (item && quantity <= 0) {
      removeFromCart(productId, productType)
    }
  }

  // 检查用户是否可以购买高风险产品
  const canPurchaseHighRiskProducts = () => {
    const isLoggedIn = localStorage.getItem('quantLogin') === '123'
    const isQualifiedInvestor = localStorage.getItem('qualifiedInvestor') === 'certified'
    return isLoggedIn && (hasHighRiskProducts.value ? isQualifiedInvestor : true)
  }

  // 获取格式化总金额
  const formattedTotalAmount = computed(() => {
    return `¥${totalAmount.value.toLocaleString('zh-CN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`
  })

  return {
    items,
    totalItems,
    totalAmount,
    formattedTotalAmount,
    hasHighRiskProducts,
    riskLevels,
    addToCart,
    removeFromCart,
    clearCart,
    updateQuantity,
    canPurchaseHighRiskProducts
  }
})