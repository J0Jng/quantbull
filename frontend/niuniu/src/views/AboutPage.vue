<template>
  <div class="about-page">
    <section class="hero">
      <div class="container">
        <p class="hero-tag">公司介绍</p>
        <h1 class="hero-title">广州深脑纪元全脑科技有限公司</h1>
        <p class="hero-subtitle">
          以脑机接口为核心引擎，融合金融科技、量化投资与机器学习，构建跨学科创新生态。
        </p>
      </div>
    </section>

    <section class="content">
      <div class="container">
        <div class="content-card">
          <p>
            广州深脑纪元全脑科技有限公司是一家致力于探索人类智慧前沿的脑科学公司，以脑机接口技术为核心引擎，深度融合金融科技、量化投资与机器学习等前沿领域，构建起一个跨学科、多维度的创新生态系统。
          </p>
          <p>
            公司核心团队汇聚了来自全球顶尖学府与研究机构的脑科学专家、算法工程师及金融领域资深从业者。我们坚信，大脑作为宇宙间最复杂的系统，其运作机制蕴含着无限的潜能与智慧，而解码这些信号，不仅能够深刻改变医疗健康领域，更能为人工智能的发展提供全新的范式与灵感。
          </p>
          <p>
            在核心技术布局上，我们专注于非侵入式脑机接口技术的研发与应用。通过自主研发的高精度脑电采集设备与核心算法，我们能够实现对大脑活动的实时、精准监测与解析。这一技术突破，为我们打开了理解人类认知、情绪与决策过程的大门，为后续在多个领域的深度应用奠定了坚实基础。
          </p>
        </div>

        <div class="content-card">
          <h2>“量化牛牛”平台定位</h2>
          <p>
            “量化牛牛”作为公司旗下的量化投资专业平台与技术创新中心，是脑科学与金融科技深度融合的典范。我们创新性地将脑机接口技术与机器学习算法引入量化投资领域，开创了“神经金融学”与“智能量化”的全新赛道。
          </p>
          <p>
            在“量化牛牛”，我们不仅关注市场数据的波动，更深入探究市场参与者——投资者的群体心理与决策机制。通过分析交易过程中的脑电活动，我们能够更敏锐地捕捉市场情绪的微妙变化，理解风险决策背后的神经基础，从而构建更具前瞻性与稳健性的量化交易模型。
          </p>
          <p>
            我们的机器学习团队致力于开发能够模拟和增强人类认知能力的智能算法。这些算法不仅能够处理海量的金融数据，更能够学习和理解人类的决策模式，为量化投资提供强大的策略支持与风险控制能力。我们正在构建一个“人机协同”的智能投研平台，让机器的算力与人类的智慧在投资决策中实现最优互补。
          </p>
        </div>

        <div class="content-card">
          <h2>使命与愿景</h2>
          <p>
            展望未来，广州深脑纪元全脑科技有限公司将继续秉持“探索大脑，智启未来”的使命，深耕脑机接口技术，不断拓展其在金融科技、医疗健康、人机交互等领域的应用边界。
          </p>
          <p>
            我们致力于成为全球脑科学领域的创新引领者，用科技的力量解锁人类智慧的无限潜能，为社会创造更大的价值。
          </p>
          <p>
            “量化牛牛”将作为我们连接金融世界的重要窗口，持续输出基于前沿脑科学的量化投资解决方案，与投资者共同驾驭市场风浪，创造长期价值。
          </p>
        </div>

        <div class="highlight-grid">
          <div class="highlight-item">
            <h3>脑机接口</h3>
            <p>非侵入式高精度脑电采集与解析，实时监测大脑活动。</p>
          </div>
          <div class="highlight-item">
            <h3>神经金融学</h3>
            <p>洞察投资者群体心理与风险决策的神经基础。</p>
          </div>
          <div class="highlight-item">
            <h3>智能量化</h3>
            <p>机器学习增强投研效率与风险控制能力。</p>
          </div>
        </div>
      </div>
    </section>

    <FooterComponent />
  </div>
</template>

<script setup>
import FooterComponent from '@/components/FooterComponent.vue'
</script>

<style scoped>
.about-page {
  min-height: 100vh;
  background: #f9fafc;
  color: #333;
}

.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero {
  background: linear-gradient(135deg, #fff2e6 0%, #ffffff 55%, #eef5ff 100%);
  padding: 60px 0 50px;
  border-bottom: 1px solid #f0f0f0;
}

.hero-tag {
  display: inline-block;
  font-size: 12px;
  letter-spacing: 1px;
  color: #ff7f24;
  background: #fff4ec;
  padding: 6px 12px;
  border-radius: 20px;
  margin-bottom: 16px;
}

.hero-title {
  font-size: 32px;
  margin: 0 0 12px;
  font-weight: 700;
  color: #1d1d1f;
  font-family: 'Microsoft YaHei', sans-serif;
}

.hero-subtitle {
  font-size: 16px;
  color: #555;
  line-height: 1.7;
  max-width: 720px;
}

.content {
  padding: 40px 0 10px;
}

.content-card {
  background: #fff;
  border-radius: 12px;
  padding: 26px 28px;
  margin-bottom: 24px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
}

.content-card h2 {
  font-size: 20px;
  margin-bottom: 14px;
  color: #1f2a44;
}

.content-card p {
  font-size: 14px;
  line-height: 1.9;
  color: #555;
  margin-bottom: 12px;
}

.content-card p:last-child {
  margin-bottom: 0;
}

.highlight-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin: 30px 0 40px;
}

.highlight-item {
  background: #ffffff;
  border: 1px solid #f0f0f0;
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.04);
}

.highlight-item h3 {
  font-size: 16px;
  margin-bottom: 8px;
  color: #ff7f24;
}

.highlight-item p {
  font-size: 13px;
  color: #666;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .hero {
    padding: 45px 0 35px;
  }

  .hero-title {
    font-size: 26px;
  }

  .content-card {
    padding: 22px;
  }
}
</style>
