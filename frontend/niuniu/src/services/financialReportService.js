import http, { handleRequest } from './http'

export const getYjbb = async ({ period, page, pageSize, market, industry, codes, refresh } = {}) => {
  return handleRequest(() =>
    http.get('/financial-report/yjbb', {
      params: {
        period,
        page,
        page_size: pageSize,
        market,
        industry,
        codes,
        refresh
      }
    })
  )
}

export const getYjkb = async ({ period, page, pageSize, market, industry, codes, refresh } = {}) => {
  return handleRequest(() =>
    http.get('/financial-report/yjkb', {
      params: {
        period,
        page,
        page_size: pageSize,
        market,
        industry,
        codes,
        refresh
      }
    })
  )
}

export const getYjyg = async ({ period, page, pageSize, market, indicator, type, codes, refresh } = {}) => {
  return handleRequest(() =>
    http.get('/financial-report/yjyg', {
      params: {
        period,
        page,
        page_size: pageSize,
        market,
        indicator,
        type,
        codes,
        refresh
      }
    })
  )
}

export const getYysj = async ({ period, page, pageSize, market, codes, refresh } = {}) => {
  return handleRequest(() =>
    http.get('/financial-report/yysj', {
      params: {
        period,
        page,
        page_size: pageSize,
        market,
        codes,
        refresh
      }
    })
  )
}
