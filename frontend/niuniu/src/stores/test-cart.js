// 已下线功能功能测试文件
import { useCartStore } from './cart.js'

// 测试函数
export function testCartFunctionality() {
  const cartStore = useCartStore()
  
  console.log('=== 脑科学研究室已下线功能功能测试 ===')
  
  // 测试1: 初始状态
  console.log('测试1 - 初始状态:')
  console.log('已下线功能商品数量:', cartStore.totalItems)
  console.log('已下线功能总金额:', cartStore.formattedTotalAmount)
  console.log('是否有高风险产品:', cartStore.hasHighRiskProducts)
  
  // 测试数据
  const testProducts = [
    {
      id: 'factor-test-1',
      name: '测试模拟参数 - 动量模拟参数',
      price: '¥999.00',
      img: 'https://picsum.photos/100/80',
      type: 'factor'
    },
    {
      id: 'strategy-test-1',
      name: '测试回测模型 - MACD回测模型',
      price: '¥1,599.00',
      img: 'https://picsum.photos/100/80',
      type: 'strategy'
    },
    {
      id: 'course-test-1',
      name: '测试课程 - 量化入门',
      price: '¥599.00',
      img: 'https://picsum.photos/100/80',
      type: 'course'
    }
  ]
  
  // 测试2: 添加商品
  console.log('\n测试2 - 添加商品:')
  testProducts.forEach((product, index) => {
    cartStore.addToCart(product)
    console.log(`添加商品 ${index + 1}: ${product.name}`)
  })
  
  console.log('添加后商品数量:', cartStore.totalItems)
  console.log('添加后总金额:', cartStore.formattedTotalAmount)
  
  // 测试3: 商品风险等级分类
  console.log('\n测试3 - 风险等级分类:')
  cartStore.items.forEach((item, index) => {
    console.log(`商品 ${index + 1}: ${item.name}`)
    console.log(`  风险等级: ${item.riskLevel}`)
    console.log(`  风险颜色: ${item.riskColor}`)
  })
  
  // 测试4: 移除商品
  console.log('\n测试4 - 移除商品:')
  if (cartStore.items.length > 0) {
    const itemToRemove = cartStore.items[0]
    const removed = cartStore.removeFromCart(itemToRemove.id, itemToRemove.type)
    console.log(`移除商品: ${itemToRemove.name} - 结果: ${removed ? '成功' : '失败'}`)
    console.log('移除后商品数量:', cartStore.totalItems)
  }
  
  // 测试5: 清空已下线功能
  console.log('\n测试5 - 清空已下线功能:')
  cartStore.clearCart()
  console.log('清空后商品数量:', cartStore.totalItems)
  console.log('清空后总金额:', cartStore.formattedTotalAmount)
  
  // 测试6: 购买资格检查
  console.log('\n测试6 - 购买资格检查:')
  console.log('当前登录状态:', !!localStorage.getItem('quantLogin'))
  console.log('合格投资者状态:', !!localStorage.getItem('qualifiedInvestor'))
  console.log('是否可以购买高风险产品:', cartStore.canPurchaseHighRiskProducts())
  
  console.log('\n=== 测试完成 ===')
}

// 生成测试数据函数（供演示使用）
export function generateTestData() {
  return {
    factor: {
      id: 'factor-demo-1',
      name: '演示模拟参数 - 估值模拟参数合集',
      price: '¥1,299.00',
      img: 'https://picsum.photos/200/150?random=31',
      type: 'factor'
    },
    strategy: {
      id: 'strategy-demo-1',
      name: '演示回测模型 - 均值回归回测模型',
      price: '¥2,499.00',
      img: 'https://picsum.photos/200/150?random=32',
      type: 'strategy'
    },
    fund: {
      id: 'fund-demo-1',
      name: '演示基金 - 量化风险模拟控制基金',
      price: '¥1,000,000.00',
      img: 'https://picsum.photos/200/150?random=33',
      type: 'fund'
    }
  }
}