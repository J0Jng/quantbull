/**
 * 商品服务
 * 对接后端 /api/products/* 接口
 */
import http, { handleRequest } from './http'

/**
 * 商品类型枚举
 */
export const ProductType = {
  FACTOR: 'factor',
  STRATEGY: 'strategy',
  FUND: 'fund',
  ADVISOR: 'advisor',
  COURSE: 'course',
  BOOK: 'book',
  TALENT: 'talent',
  BANK: 'bank',
  INSURANCE: 'insurance'
}

/**
 * 商品类型名称映射
 */
export const ProductTypeName = {
  factor: '模拟参数',
  strategy: '回测模型',
  fund: '基金',
  advisor: '投顾',
  course: '课程',
  book: '书籍',
  talent: '人才',
  bank: '银行产品',
  insurance: '保险产品'
}

/**
 * 获取商品列表
 * GET /api/products
 * @param {Object} params - 查询参数
 * @param {string} [params.type] - 商品类型过滤
 * @param {boolean} [params.include_inactive] - 是否包含下架商品（仅管理员）
 * @param {number} [params.limit] - 每页数量，默认 100
 * @param {number} [params.offset] - 偏移量，默认 0
 */
export const getProducts = async (params = {}) => {
  const result = await handleRequest(() => 
    http.get('/products', { params })
  )
  
  // 后端返回格式: {code: 0, message: "ok", data: [...]}
  if (result.success && result.data?.data) {
    return { success: true, data: result.data.data }
  }
  return result
}

/**
 * 获取单个商品详情
 * GET /api/products/{productId}
 * @param {string} productId - 商品ID
 */
export const getProduct = async (productId) => {
  const result = await handleRequest(() => 
    http.get(`/products/${productId}`)
  )
  
  if (result.success && result.data?.data) {
    return { success: true, data: result.data.data }
  }
  return result
}

/**
 * 创建商品（仅管理员）
 * POST /api/products
 * @param {Object} productData - 商品数据
 * @param {string} productData.type - 商品类型
 * @param {string} productData.name - 商品名称
 * @param {number} productData.price - 价格
 * @param {number} [productData.original_price] - 原价
 * @param {string} [productData.img] - 图片URL
 * @param {string} [productData.description] - 描述
 * @param {string} [productData.duration] - 课时/时长
 * @param {string} [productData.target_audience] - 适合人群
 * @param {string} [productData.learning_method] - 学习方式
 * @param {string} [productData.start_time] - 开课时间
 * @param {string} [productData.instructor] - 讲师信息
 * @param {string} [productData.outline] - 课程大纲（JSON字符串）
 * @param {string} [productData.detail_content] - 详细介绍
 * @param {string} [productData.faq] - 常见问题（JSON字符串）
 * @param {boolean} [productData.is_active] - 是否上架，默认 true
 */
export const createProduct = async (productData) => {
  const result = await handleRequest(() => 
    http.post('/products', productData)
  )
  
  if (result.success && result.data?.data) {
    return { success: true, data: result.data.data }
  }
  return result
}

/**
 * 更新商品（仅管理员）
 * PATCH /api/products/{productId}
 * @param {string} productId - 商品ID
 * @param {Object} updateData - 更新数据（部分更新）
 */
export const updateProduct = async (productId, updateData) => {
  const result = await handleRequest(() => 
    http.patch(`/products/${productId}`, updateData)
  )
  
  if (result.success && result.data?.data) {
    return { success: true, data: result.data.data }
  }
  return result
}

/**
 * 删除商品（仅管理员，软删除）
 * DELETE /api/products/{productId}
 * @param {string} productId - 商品ID
 */
export const deleteProduct = async (productId) => {
  const result = await handleRequest(() => 
    http.delete(`/products/${productId}`)
  )
  
  if (result.success && result.data?.data) {
    return { success: true, data: result.data.data }
  }
  return result
}

/**
 * 按类型获取商品
 * @param {string} type - 商品类型
 * @param {Object} [options] - 其他选项
 */
export const getProductsByType = async (type, options = {}) => {
  return getProducts({ type, ...options })
}

/**
 * 格式化价格显示
 * @param {number} price - 价格
 * @returns {string} 格式化后的价格字符串
 */
export const formatPrice = (price) => {
  if (typeof price !== 'number') return '¥0.00'
  return `¥${price.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}
