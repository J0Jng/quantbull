<template>
  <div class="contact-page">
    <section class="hero">
      <div class="container">
        <p class="hero-tag">联系我们</p>
        <h1 class="hero-title">联系方式</h1>
      </div>
    </section>

    <section class="content">
      <div class="container">
        <div class="content-card">
          <div class="contact-item">
            <span class="label">邮箱</span>
            <span class="value">490479476@qq.com</span>
          </div>
          <div class="contact-item">
            <span class="label">QQ</span>
            <span class="value">490479476</span>
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
.contact-page {
  min-height: 100vh;
  background: #f9fafc;
  color: #333;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
}

.hero {
  background: linear-gradient(135deg, #fff2e6 0%, #ffffff 55%, #eef5ff 100%);
  padding: 60px 0 45px;
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
  font-size: 30px;
  margin: 0 0 10px;
  font-weight: 700;
  color: #1d1d1f;
  font-family: 'Microsoft YaHei', sans-serif;
}

.hero-subtitle {
  font-size: 15px;
  color: #555;
  line-height: 1.7;
}

.content {
  padding: 35px 0 10px;
}

.content-card {
  background: #fff;
  border-radius: 12px;
  padding: 26px 28px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
}

.contact-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.contact-item:last-child {
  border-bottom: none;
}

.label {
  font-size: 14px;
  color: #666;
}

.value {
  font-size: 14px;
  color: #1d1d1f;
  font-weight: 600;
}

@media (max-width: 768px) {
  .hero {
    padding: 45px 0 35px;
  }

  .hero-title {
    font-size: 24px;
  }

  .content-card {
    padding: 22px;
  }
}
</style>
