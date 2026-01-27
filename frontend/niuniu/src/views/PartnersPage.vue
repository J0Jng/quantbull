<template>
  <div class="partners-page">
    <div class="back-home-container">
      <router-link to="/" class="back-home-btn">
        &lt; 返回主页面
      </router-link>
    </div>
    <section class="hero">
      <div class="container">
        <p class="hero-tag">战略合作单位</p>
        <h1 class="hero-title">合作伙伴</h1>
      </div>
    </section>

    <section class="content">
      <div class="container">
        <div class="partners-grid">
          <a 
            v-for="(partner, index) in partners" 
            :key="index"
            :href="partner.url"
            target="_blank"
            rel="noopener noreferrer"
            class="partner-card"
          >
            <div class="partner-info">
              <h3 class="partner-name">{{ partner.name }}</h3>
              <span class="visit-text">访问官网 &rarr;</span>
            </div>
          </a>
        </div>
      </div>
    </section>

    <FooterComponent />
  </div>
</template>

<script setup>
import FooterComponent from '@/components/FooterComponent.vue'

const partners = [
  { name: '中信建投', url: 'https://www.csc108.com/' },
  { name: '九坤投资', url: 'https://www.ubiquant.com/website/about' },
  { name: '榕树投资', url: 'https://www.rongshutz.com/' },
  { name: '悟空投资', url: 'https://www.wukongtz.com/' },
  { name: '深泛联投资', url: 'http://www.cashchina.cn/gywm' }, // 官网待确认
]
</script>

<style scoped>
.partners-page {
  min-height: 100vh;
  background-color: #f5f7fa;
  position: relative;
}

.back-home-container {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 100;
}

.back-home-btn {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.9);
  color: #333;
  text-decoration: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.back-home-btn:hover {
  background-color: #fff;
  color: #ff7f24;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.hero {
  background: linear-gradient(135deg, #1f2937, #111827);
  color: #ffffff;
  padding: 80px 0;
  text-align: center;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero-tag {
  color: #ff7f24;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  letter-spacing: 1px;
}

.hero-title {
  font-size: 42px;
  font-weight: bold;
  margin: 0;
  line-height: 1.2;
}

.content {
  padding: 40px 0 80px;
}

.partners-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.partner-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  text-decoration: none;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.partner-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.partner-info {
  text-align: center;
}

.partner-name {
  color: #1f2937;
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 10px 0;
  transition: color 0.3s ease;
}

.partner-card:hover .partner-name {
  color: #ff7f24;
}

.visit-text {
  color: #9ca3af;
  font-size: 14px;
  transition: color 0.3s ease;
}

.partner-card:hover .visit-text {
  color: #ff7f24;
}
</style>
