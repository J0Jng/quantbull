/**
 * 基金排行榜服务
 * 对接后端 /api/funds/* 接口（经 api-gateway 透传到 data-service）
 */
import http, { handleRequest } from './http'

export const getPublicFundRanking = async (params = {}) => {
  return handleRequest(() => http.get('/funds/public/ranking', { params }))
}

export const getPrivateFundRanking = async (params = {}) => {
  return handleRequest(() => http.get('/funds/private/ranking', { params }))
}
