import http, { handleRequest } from './http'

export const getLhbStocks = async ({ tradeDate, page, pageSize, refresh } = {}) => {
  return handleRequest(() =>
    http.get('/lhb/stocks', {
      params: {
        trade_date: tradeDate,
        page,
        page_size: pageSize,
        refresh
      }
    })
  )
}

export const getLhbSummary = async ({ days, endTradeDate, page, pageSize, refresh } = {}) => {
  return handleRequest(() =>
    http.get('/lhb/stocks/summary', {
      params: {
        days,
        end_trade_date: endTradeDate,
        page,
        page_size: pageSize,
        refresh
      }
    })
  )
}
