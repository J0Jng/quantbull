<template>
  <div class="compliance-page">
    <div class="compliance-card">
      <h1>脑科学研究室</h1>
      <div class="strategy-list">
        <div class="strategy-item">
          <h2>指数增强策略</h2>
          <p>通过构建一个极度分散的股票组合，以较小的误差跟踪特定的市场指数，并根据量化策略优化选股，每日动态调整，力求在长期能够跑赢对标指数、产生超额收益。</p>
        </div>
        <div class="strategy-item">
          <h2>CTA策略</h2>
          <p>同时监控并跟踪商品期货市场的高流动性期货合约，在维持头寸分散的基础上，利用商品价格波动的厚尾效应，力争在趋势行情中获利，在震荡行情中止损。</p>
        </div>
        <div class="strategy-item">
          <h2>量化对冲策略</h2>
          <p>通过量化因子叠加形成策略组合对全市场股票进行分散投资形成股票多头组合，同时使用风险对冲工具（股指期货、融券、指数互换等）将大盘风险、行业风险对冲，承担一定的对冲成本，赚取逐日积累的超额收益。</p>
        </div>
        <div class="strategy-item">
          <h2>量化多空策略</h2>
          <p>在仓位分散的基础上，通过量化策略投资于股票，同时动态地使用股指期货进行对冲，力求在风险可控的同时更好地赚取超额收益。</p>
        </div>
        <div class="strategy-item">
          <h2>股票优选策略</h2>
          <p>通过量化多策略叠加构建因子组合，对个股的预期超额收益进行预测，由此筛选出不同期限下一篮子优质的股票，在长期中追求绝对收益，并通过保持分散度降低组合风险。</p>
        </div>
      </div>
      <div class="action-row">
        <router-link to="/home" class="back-btn">返回主界面</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.compliance-page {
  min-height: 100vh;
  background: #fff8f0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.compliance-card {
  width: 100%;
  max-width: 760px;
  background: #fff;
  border: 1px solid #ffd591;
  border-radius: 10px;
  padding: 28px;
}

.compliance-card h1 {
  margin: 0 0 10px;
  color: #333;
}

.strategy-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.strategy-item {
  background: #fff7e6;
  border: 1px solid #ffd591;
  border-radius: 6px;
  padding: 10px;
}

.strategy-item h2 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #8c4b00;
}

.strategy-item p {
  margin: 0;
  color: #333;
  line-height: 1.7;
}

.action-row {
  margin-top: 16px;
}

.back-btn {
  display: inline-block;
  padding: 8px 14px;
  border-radius: 6px;
  border: 1px solid #ffd591;
  background: #fff7e6;
  color: #8c4b00;
  text-decoration: none;
}

.back-btn:hover {
  background: #ffeacc;
}
</style>
