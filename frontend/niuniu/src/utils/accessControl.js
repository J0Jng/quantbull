/**
 * 每日内参访问控制工具
 */

/**
 * 检查当前是否可以访问今天的报告
 * 规则：只有当天 16:00 之后才能访问今天的报告
 */
export const canAccessTodayReport = () => {
  const now = new Date()
  const hours = now.getHours()
  const minutes = now.getMinutes()
  
  // 16:00 = 16 * 60 = 960分钟
  // 当前时间 = hours * 60 + minutes
  const currentMinutes = hours * 60 + minutes
  const cutoffMinutes = 16 * 60 // 16:00
  
  return currentMinutes >= cutoffMinutes
}

/**
 * 获取今天的日期字符串 (YYYY-MM-DD)
 */
export const getTodayString = () => {
  const today = new Date()
  return today.toISOString().split('T')[0]
}

/**
 * 获取昨天的日期字符串 (YYYY-MM-DD)
 */
export const getYesterdayString = () => {
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  return yesterday.toISOString().split('T')[0]
}

/**
 * 获取访问拒绝提示信息
 */
export const getAccessDeniedMessage = () => {
  return '今日投资方案需在当天 16:00 后查看，请查阅历史报告'
}

/**
 * 检查给定日期是否为今天
 */
export const isToday = (dateStr) => {
  if (!dateStr) return false
  return dateStr === getTodayString()
}
