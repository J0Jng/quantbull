/**
 * 服务模块统一导出
 */

// 基础 HTTP 客户端
export { default as http, handleRequest } from './http'

// 认证服务
export * from './authService'

// 回测模型服务
export * from './strategyService'

// 模拟参数服务  
export * from './factorService'

// 回测服务
export * from './backtestService'

// 每日报告服务
export * from './dailyReportService'

// 研报服务
export * from './reportService'

// 市场数据服务
export * from './marketService'

// 资金流向服务
export * from './fundFlowService'

// AI 服务
export * from './aiService'

// 商品服务
export * from './productService'
