/**
 * 基金排行榜服务
 * 对接后端 /api/funds/* 接口（经 api-gateway 透传到 data-service）
 * 支持本地缓存，每天早上 8 点后缓存失效自动刷新
 */
import http, { handleRequest } from './http'

const CACHE_KEY_PREFIX = 'fund_ranking_cache_'
const CACHE_VERSION = 'v1'

/**
 * 获取今天早上 8 点的时间戳
 */
function getTodayRefreshTime() {
  const now = new Date()
  return new Date(now.getFullYear(), now.getMonth(), now.getDate(), 8, 0, 0, 0).getTime()
}

/**
 * 判断缓存是否仍然有效
 * 规则：当前时间 >= 今天 8 点时，缓存必须在今天 8 点之后写入；
 *       当前时间 < 今天 8 点时，缓存必须在昨天 8 点之后写入。
 */
function isCacheValid(cachedAt) {
  const now = Date.now()
  const todayRefresh = getTodayRefreshTime()
  if (now >= todayRefresh) {
    return cachedAt >= todayRefresh
  } else {
    const yesterdayRefresh = todayRefresh - 24 * 60 * 60 * 1000
    return cachedAt >= yesterdayRefresh
  }
}

/**
 * 根据请求参数生成缓存键
 */
function getCacheKey(params) {
  const keyParams = {
    fund_type: params.fund_type || '',
    return_sign: params.return_sign || '',
    sort_by: params.sort_by || 'default',
    keyword: params.keyword || '',
    page: params.page || 1,
    page_size: params.page_size || 50
  }
  return `${CACHE_KEY_PREFIX}${CACHE_VERSION}_public_${JSON.stringify(keyParams)}`
}

/**
 * 从 localStorage 读取缓存，若已过期则删除并返回 null
 */
function readCache(key) {
  try {
    const raw = localStorage.getItem(key)
    if (!raw) return null
    const { data, cachedAt } = JSON.parse(raw)
    if (!isCacheValid(cachedAt)) {
      localStorage.removeItem(key)
      return null
    }
    return data
  } catch {
    return null
  }
}

/**
 * 向 localStorage 写入缓存
 */
function writeCache(key, data) {
  try {
    localStorage.setItem(key, JSON.stringify({ data, cachedAt: Date.now() }))
  } catch (e) {
    // localStorage 空间不足时忽略
    console.warn('[fundRankingService] 缓存写入失败:', e)
  }
}

/**
 * 清空所有基金排行榜缓存（供定时刷新使用）
 */
export function clearFundRankingCache() {
  const keys = Object.keys(localStorage).filter(k => k.startsWith(CACHE_KEY_PREFIX))
  keys.forEach(k => localStorage.removeItem(k))
}

export const getPublicFundRanking = async (params = {}) => {
  // 强制刷新时跳过缓存读取
  if (!params.refresh) {
    const cacheKey = getCacheKey(params)
    const cached = readCache(cacheKey)
    if (cached) {
      return cached
    }
  }

  const result = await handleRequest(() => http.get('/funds/public/ranking', { params }))

  // 请求成功且初始业务代码为 0 时才写入缓存
  if (result?.success && result.data?.code === 0) {
    const cacheKey = getCacheKey(params)
    writeCache(cacheKey, result)
  }

  return result
}

export const getPrivateFundRanking = async (params = {}) => {
  return handleRequest(() => http.get('/funds/private/ranking', { params }))
}
