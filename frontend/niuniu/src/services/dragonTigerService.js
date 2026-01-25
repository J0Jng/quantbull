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

export const getLhbInstitutionTrades = async ({ tradeDate, page, pageSize, refresh } = {}) => {
  return handleRequest(() =>
    http.get('/lhb/institutions/trades', {
      params: {
        trade_date: tradeDate,
        page,
        page_size: pageSize,
        refresh
      }
    })
  )
}

export const getLhbInstitutionSeatTrack = async ({ days, endTradeDate, page, pageSize, refresh } = {}) => {
  return handleRequest(() =>
    http.get('/lhb/institutions/seats/track', {
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

export const getLhbActiveBrokers = async ({ tradeDate, page, pageSize, refresh } = {}) => {
  return handleRequest(() =>
    http.get('/lhb/brokers/active', {
      params: {
        trade_date: tradeDate,
        page,
        page_size: pageSize,
        refresh
      }
    })
  )
}

export const getLhbBrokerRank = async ({ days, endTradeDate, page, pageSize, refresh } = {}) => {
  return handleRequest(() =>
    http.get('/lhb/brokers/rank', {
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

export const getLhbBrokerOnlistStats = async ({ days, endTradeDate, page, pageSize, refresh } = {}) => {
  return handleRequest(() =>
    http.get('/lhb/brokers/onlist/stats', {
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
