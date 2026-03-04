import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useOrderStore = defineStore('order', () => {
  // 模拟实验记录数据
  const orders = ref([
    {
      id: 'ORD-20251224-001',
      date: '2025-12-24',
      status: '已完成',
      items: [
        {
          id: 'FACT-001',
          type: 'factor',
          name: '动量模拟参数回测模型',
          price: 299.00,
          riskLevel: '中风险',
          riskColor: '#faad14',
          img: '/1.png'
        }
      ],
      totalAmount: 299.00,
      paymentMethod: '支付宝',
      deliveryInfo: '电子邮箱: user@example.com'
    }
  ])

  // 计算属性
  const totalOrders = computed(() => orders.value.length)
  
  const totalAmount = computed(() => {
    return orders.value.reduce((sum, order) => sum + order.totalAmount, 0)
  })

  const formattedTotalAmount = computed(() => {
    return `¥${totalAmount.value.toFixed(2)}`
  })

  // 方法
  const getOrderById = (id) => {
    return orders.value.find(order => order.id === id)
  }

  return {
    orders,
    totalOrders,
    totalAmount,
    formattedTotalAmount,
    getOrderById
  }
})