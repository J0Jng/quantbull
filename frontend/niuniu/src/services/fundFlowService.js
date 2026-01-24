/**
 * 资金流向服务
 * 对接后端 /api/fundflow/* 接口
 */
import http, { handleRequest } from './http'

export const getMarketFundFlow = async (params = {}) => {
  return handleRequest(() => http.get('/fundflow/market', { params }))
}

export const getSectorFundFlow = async (params = {}) => {
  return handleRequest(() => http.get('/fundflow/sectors', { params }))
}

export const getStockFundFlow = async (params = {}) => {
  return handleRequest(() => http.get('/fundflow/stocks', { params }))
}
