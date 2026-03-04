<template>
  <div class="disclaimer-page">
    <section class="hero">
      <div class="container">
        <p class="hero-tag">合规与权益</p>
        <h1 class="hero-title">网站申明</h1>
        <p class="hero-subtitle">
          请您在首次登陆「深脑纪元·数据模拟实验室」前，认真阅读并充分理解以下服务及权利义务说明。
        </p>
      </div>
    </section>

    <section class="content-section">
      <div class="container">
        <div class="content-card">
          <p class="greeting">尊敬的客户：</p>
          <div class="scroll-content">
            <p>欢迎进入「深脑纪元·数据模拟实验室」，为保障您的合法权益，助您了解「深脑纪元·数据模拟实验室」为您提供的服务内容及您使用该服务的权利和义务，在您首次登陆「深脑纪元·数据模拟实验室」前，请您认真阅读、充分理解以下内容。</p>
            
            <p>「深脑纪元·数据模拟实验室」系广州深脑纪元全脑科技有限公司出品。我司将逐步拥有该网站功能板块的「网站著作权」「网站登记证书」「商标权」等；网站所使用的相关数据系公开数据，不产生任何商业运用。</p>
            
            <p>「深脑纪元·数据模拟实验室」受网站功能板块自身限制，其功能仅用于查看行情数据，以及针对行情数据的记录及统计等，并不能改变或影响交易数据，更无法预知交易结果。在您的投资操作中，本网站功能板块绝不能替代您的个人决策，因此所产生的任何投资盈亏结果，均与本网站功能板块无关。</p>

            <p class="highlight">具体而言，我们不提供如下服务：</p>
            <ul>
              <li>不提供涉及具体证券投资品种的投资分析意见；</li>
              <li>不预测具体证券投资品种的价格走势；</li>
              <li>不提供具体证券投资品种选择建议；</li>
              <li>不提供具体证券投资品种的买卖时机建议；</li>
              <li>不提供其他证券投资分析、预测或者建议。</li>
            </ul>

            <p>我司主营网站功能板块开发，不具备「证券投资咨询资格」，因此不提供任何形式的「证券投资咨询服务」，其中包括但不限于不推荐股票、不指导买卖操作、不代客理财等。同时，我司员工入职不要求具有「证券从业资格」，任何员工与您进行的所有沟通内容，仅限于「深脑纪元·数据模拟实验室」网站的基本使用及与网站使用相关的问题解答。</p>

            <p>我司员工入职起，即与我司签订法律承诺书，承诺不为任何用户提供任何形式的「证券投资咨询服务」，其中包括但不限于不推荐股票、不指导买卖操作、不代客理财等。如您与我司工作人员沟通中发现有违规现象，或因此而产生的任何结果，我司不负有必然关联责任，请您及时取证并向我司及相关部门举报该员工行为，过程中，我司将全面配合。在「深脑纪元·数据模拟实验室」网站内呈现的各类文章、音频、视频，包括但不限于用户投稿、用户交流、及脑科研究中心及深脑纪元员工所发表的任何文字、截图及音频视频等，无论与产品使用是否相关，均不代表我司观点或立场，更不构成任何形式上的投资建议，因此而产生的任何结果，我司不负有必然关联责任。</p>

            <p>「深脑纪元·数据模拟实验室」网站，仅为数据的汇总和历史数据的统计，所提供的一切文字、数据等仅作为用户学习之用和公司研究之用，不构成任何的投资建议，同时，所有历史数据统计结果，不代表未来数据变化或股价走向。用户不应据此进行操作，若发生据此操作行为所造成的任何风险和后果均由用户自行负责。软件中涉及文字与真实数据之区分，而不具有其字面本身含义及更广泛的任何其他含义，更不具有映射涨跌之意图。</p>

            <p>在您使用「深脑纪元·数据模拟实验室」网站的过程中，如因网络故障、服务器故障及交易所等各种不可抗力，以及网站程序自身错误等原因，而导致部分或全部行情数据、数据统计结果及数据呈现结果等出现错误，对此，我司承诺一旦发现包括但不限于上述问题时，会努力整改，但对此而产生的任何结果，我司不负有必然关联责任，我司网站仅做研究和数据模拟使用。</p>
          </div>
          
          <div class="actions">
            <button class="agree-btn" @click="handleAgree">我已阅读并知晓</button>
          </div>
        </div>
      </div>
    </section>
    
    <FooterComponent />
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import FooterComponent from '@/components/FooterComponent.vue'

const router = useRouter()

const handleAgree = () => {
  localStorage.setItem('disclaimer_agreed', 'true')
  router.push('/home')
}
</script>

<style scoped>
.disclaimer-page {
  min-height: 100vh;
  background: #f9fafc;
  color: #333;
  position: relative;
  display: flex;
  flex-direction: column;
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
  text-align: center;
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
  margin: 0 0 16px;
  font-weight: 700;
  color: #1d1d1f;
  font-family: 'Microsoft YaHei', sans-serif;
}

.hero-subtitle {
  font-size: 16px;
  color: #555;
  line-height: 1.7;
  max-width: 720px;
  margin: 0 auto;
}

.content-section {
  padding: 40px 0 60px;
  flex: 1;
}

.content-card {
  background: #fff;
  border-radius: 12px;
  padding: 40px 48px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  max-width: 900px;
  margin: 0 auto;
}

.greeting {
  font-weight: 600;
  margin-bottom: 20px;
  color: #1f2a44;
  font-size: 18px;
}

.scroll-content {
  color: #555;
  line-height: 1.9;
  font-size: 15px;
  max-height: 50vh;
  overflow-y: auto;
  padding-right: 15px;
  margin-bottom: 30px;
}

.scroll-content p {
  margin-bottom: 16px;
  text-align: justify;
}

.scroll-content .highlight {
  font-weight: 600;
  color: #1f2a44;
  margin-top: 24px;
  margin-bottom: 12px;
  text-align: left;
}

.scroll-content ul {
  margin-bottom: 24px;
  padding-left: 20px;
  list-style-type: none;
}

.scroll-content li {
  margin-bottom: 10px;
  position: relative;
  padding-left: 18px;
}

.scroll-content li::before {
  content: "•";
  color: #ff7f24;
  font-weight: bold;
  position: absolute;
  left: 0;
  top: -1px;
}

/* 自定义滚动条样式 */
.scroll-content::-webkit-scrollbar {
  width: 6px;
}

.scroll-content::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.scroll-content::-webkit-scrollbar-track {
  background-color: #f5f7fa;
  border-radius: 3px;
}

.actions {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.agree-btn {
  background-color: #ff7f24;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 12px 36px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(255, 127, 36, 0.3);
}

.agree-btn:hover {
  background-color: #ff6a00;
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(255, 127, 36, 0.4);
}

@media (max-width: 768px) {
  .hero {
    padding: 45px 0 35px;
  }

  .hero-title {
    font-size: 26px;
  }

  .content-card {
    padding: 24px 20px;
  }
}
</style>
