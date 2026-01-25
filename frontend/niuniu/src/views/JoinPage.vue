<template>
  <div class="join-page">
    <div class="back-home-container">
      <router-link to="/" class="back-home-btn">
        &lt; 返回主页面
      </router-link>
    </div>
    <section class="hero">
      <div class="container">
        <p class="hero-tag">加入我们</p>
        <h1 class="hero-title">人才招聘</h1>
      </div>
    </section>

    <section class="content">
      <div class="container">
        <div class="content-card">
          <p>虚位以待，期待您的加入！</p>
          <p>请发送简历至: @qq.com</p>
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
.join-page {
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

.content-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  margin-bottom: 30px;
}

.content-card p {
  line-height: 1.8;
  color: #4b5563;
  margin-bottom: 20px;
  font-size: 16px;
  text-align: justify;
}
</style>
