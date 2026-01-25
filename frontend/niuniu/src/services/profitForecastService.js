import http, { handleRequest } from './http'

export const getProfitForecast = async (params = {}) => {
  return handleRequest(() => http.get('/profit-forecast', { params }))
}

export const getProfitForecastScopes = async (params = {}) => {
  return handleRequest(() => http.get('/profit-forecast/scopes', { params }))
}

export default {
  getProfitForecast,
  getProfitForecastScopes
}
