<template>
  <footer class="footer">
    <div class="footer-container">
      <!-- 顶部分隔线 -->
      <div class="footer-divider"></div>
      
      <!-- 四栏主要内容区域 -->
      <div class="footer-content">
        <!-- 关于 -->
        <div class="footer-column">
          <h3 class="column-title">关于</h3>
          <div class="link-list">
            <router-link to="/about" class="footer-link">关于我们</router-link>
            <router-link to="/contact" class="footer-link">联系我们</router-link>
            <router-link to="/join" class="footer-link">加入我们</router-link>
            <router-link to="/partners" class="footer-link">战略合作单位</router-link>
          </div>
        </div>

        <!-- 帮助 -->
        <div class="footer-column">
          <h3 class="column-title">帮助</h3>
          <div class="link-list">
            <a href="/faq" class="footer-link">常见问题</a>
          </div>
        </div>

        <!-- 友情链接 -->
        <div class="footer-column">
          <h3 class="column-title">友情链接</h3>
          <div class="link-list">
            <a href="https://www.csc.com.cn/" target="_blank" rel="noopener noreferrer" class="footer-link">中信建投</a>
            <a href="https://www.ubquant.com/" target="_blank" rel="noopener noreferrer" class="footer-link">九坤投资</a>
            <a href="http://www.ronginvest.com/" target="_blank" rel="noopener noreferrer" class="footer-link">榕树投资</a>
            <a href="http://www.wk-investment.com/" target="_blank" rel="noopener noreferrer" class="footer-link">悟空投资</a>
            <a href="#" class="footer-link">深泛联投资</a>
          </div>
        </div>

        <!-- 关注我们 -->
        <div class="footer-column">
          <h3 class="column-title">关注我们</h3>
          <div class="link-list">
            <a href="https://zhuanlan.zhihu.com" class="footer-link blue-link">知乎专栏</a>
            <a href="https://xueqiu.com" class="footer-link blue-link">雪球</a>
          </div>
          <!-- 二维码区域 -->
          <div class="qrcode-section">
            <div class="qrcode-placeholder">
              <div class="qrcode-image">二维码</div>
              <span class="qrcode-text">微信公众号</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部版权区域 -->
      <div class="footer-bottom">
        <div class="compliance-notice">
          <span class="warning-icon">⚠️</span>
          <p class="warning-text">投资有风险，入市需谨慎。以上内容仅供参考，不构成投资建议。请遵循国家法律法规进行投资。</p>
        </div>
        
        <div class="copyright-area">
          <div class="legal-notes">
            <span>量化牛牛（北京）科技有限公司</span>
            <span class="separator">|</span>
            <span>营业执照：91110108MA01XXXXXX</span>
            <span class="separator">|</span>
            <span>备案号：京ICP备XXXXXXX号</span>
          </div>
          <div class="copyright-text">
            © 2025 量化牛牛 版权所有
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup>
// 这是一个独立的页脚组件，可以直接在其他页面中使用
import { ref, onMounted } from 'vue'

// 组件逻辑（如果需要的话）
const currentYear = ref(new Date().getFullYear())

onMounted(() => {
  // 可以添加一些初始化逻辑
})
</script>

<style scoped>
.footer {
  background: #ffffff; /* 白色背景 */
  color: #333333;
  margin-top: 40px;
  border-top: 1px solid #f0f0f0;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 顶部分隔线 */
.footer-divider {
  height: 1px;
  background: #e0e0e0;
}

/* 四栏主要内容区域 */
.footer-content {
  display: flex;
  gap: 60px;
  padding: 40px 0 30px;
}

/* 四栏基础样式 */
.footer-column {
  flex: 1;
  min-width: 0;
}

.column-title {
  color: #333333;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
  font-family: 'Microsoft YaHei', sans-serif;
}

.link-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-link {
  color: #666666;
  text-decoration: none;
  font-size: 14px;
  font-family: 'Microsoft YaHei', sans-serif;
  transition: color 0.3s ease;
}

.footer-link:hover {
  color: #ff7f24;
}

.blue-link {
  color: #007bff;
}

.blue-link:hover {
  color: #0056b3;
}

/* 二维码区域 */
.qrcode-section {
  margin-top: 20px;
}

.qrcode-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.qrcode-image {
  width: 80px;
  height: 80px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666666;
  font-size: 12px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
}

.qrcode-text {
  font-size: 12px;
  color: #666666;
  font-family: 'Microsoft YaHei', sans-serif;
}

/* 底部版权区域 */
.footer-bottom {
  padding: 20px 0;
  border-top: 1px solid #e0e0e0;
}

.compliance-notice {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 15px;
  padding: 12px;
  background: #fff8f0;
  border-radius: 4px;
  border: 1px solid #ffd591;
}

.warning-icon {
  font-size: 18px;
  flex-shrink: 0;
  margin-top: 1px;
}

.warning-text {
  font-size: 12px;
  line-height: 1.4;
  color: #d46b08;
  margin: 0;
  font-family: 'Microsoft YaHei', sans-serif;
}

.copyright-area {
  text-align: center;
}

.legal-notes {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 12px;
  color: #666666;
  font-family: 'Microsoft YaHei', sans-serif;
}

.separator {
  color: #cccccc;
}

.copyright-text {
  font-size: 11px;
  color: #999999;
  font-family: 'Microsoft YaHei', sans-serif;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .footer-content {
    gap: 40px;
  }
}

@media (max-width: 768px) {
  .footer-container {
    padding: 0 15px;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 30px;
    padding: 30px 0 20px;
  }
  
  .link-list {
    gap: 10px;
  }
  
  .legal-notes {
    flex-direction: column;
    gap: 4px;
  }
  
  .separator {
    display: none;
  }
}

@media (max-width: 480px) {
  .footer-content {
    gap: 20px;
  }
  
  .qrcode-image {
    width: 60px;
    height: 60px;
  }
  
  .qrcode-text {
    font-size: 11px;
  }
}
</style>