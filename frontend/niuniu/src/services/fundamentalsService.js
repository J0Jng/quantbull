import http, { handleRequest } from './http';

/**
 * 获取行业排名
 * @param {string} month - 月份 YYYY-MM，不传则使用最近月
 * @param {boolean} autoCalculate - 如果数据库没有数据，是否自动计算
 * @returns {Promise}
 */
export const getIndustryRank = async (month = null, autoCalculate = false) => {
  return handleRequest(() =>
    http.get('/fundamentals/industry/rank', {
      params: { month, auto_calculate: autoCalculate }
    })
  );
};

/**
 * 批量获取股票基本面数据
 * @param {Array} codes - 股票代码列表
 * @param {string} tradeDate - 交易日期 YYYYMMDD
 * @returns {Promise}
 */
export const getFundamentalsBatch = async (codes, tradeDate = null) => {
  return handleRequest(() =>
    http.post('/fundamentals/batch', { codes, trade_date: tradeDate })
  );
};

/**
 * 获取舆情评分
 * @param {Array} codes - 股票代码列表
 * @param {string} startDate - 开始日期 YYYYMMDD
 * @param {string} endDate - 结束日期 YYYYMMDD
 * @returns {Promise}
 */
export const getSentimentScores = async (codes, startDate, endDate) => {
  return handleRequest(() =>
    http.post('/fundamentals/sentiment/score', { codes, start_date: startDate, end_date: endDate })
  );
};

/**
 * 获取热度评分
 * @param {Array} codes - 股票代码列表
 * @param {string} startDate - 开始日期 YYYYMMDD
 * @param {string} endDate - 结束日期 YYYYMMDD
 * @returns {Promise}
 */
export const getHotScores = async (codes, startDate, endDate) => {
  return handleRequest(() =>
    http.post('/fundamentals/hot/score', { codes, start_date: startDate, end_date: endDate })
  );
};
