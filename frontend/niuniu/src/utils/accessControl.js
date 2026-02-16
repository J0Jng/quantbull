/**
 * 每日内参访问控制工具
 */

/**
 * 检查当前是否可以访问今天的报告
 * 规则：当日内参在次日 03:00 生成，当天不可访问
 */
export const canAccessTodayReport = () => {
  return false
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
  return '当日内参在次日 03:00 生成，请查阅历史报告'
}

/**
 * 检查给定日期是否为今天
 */
export const isToday = (dateStr) => {
  if (!dateStr) return false
  return dateStr === getTodayString()
}
