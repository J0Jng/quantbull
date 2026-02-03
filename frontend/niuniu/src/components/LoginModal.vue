<template>
  <!-- 登录弹窗 -->
  <div class="login-modal" v-show="showLoginModal">
    <div class="login-box">
      <span class="close-login" @click="closeLoginModal">&times;</span>
      <div class="login-title">量化牛牛 - {{ isRegisterMode ? '注册' : '登录' }}</div>
      <div class="error-tips" v-show="errorVisible">{{ errorMessage }}</div>
      <div class="success-tips" v-show="successVisible">{{ successMessage }}</div>
      <form class="login-form" @submit.prevent>
        <input v-model="loginForm.username" type="text" placeholder="请输入账号" />
        <input v-model="loginForm.password" type="password" placeholder="请输入密码" minlength="6" />
        <input v-if="isRegisterMode" v-model="loginForm.confirmPassword" type="password" placeholder="请确认密码" minlength="6" />
        <input v-if="isRegisterMode" v-model="loginForm.phone" type="tel" placeholder="请输入手机号（必填）" />
        <input v-if="isRegisterMode" v-model="loginForm.email" type="email" placeholder="请输入邮箱（可选）" />
        <button v-if="!isRegisterMode" type="button" class="login-btn" @click="submitLogin" :disabled="loginLoading">
          {{ loginLoading ? '登录中...' : '登录' }}
        </button>
        <button v-else type="button" class="login-btn register-btn" @click="submitRegister" :disabled="loginLoading">
          {{ loginLoading ? '注册中...' : '注册' }}
        </button>
      </form>
      <div class="login-switch">
        <span v-if="!isRegisterMode">
          还没有账号？<a href="#" @click.prevent="switchToRegister">立即注册</a>
        </span>
        <span v-else>
          已有账号？<a href="#" @click.prevent="switchToLogin">返回登录</a>
        </span>
      </div>
    </div>
  </div>

  <!-- 动态风险提示弹窗 -->
  <div class="risk-modal" v-show="showRiskTip">
    <div class="risk-box">
      <div class="risk-icon">⚠️</div>
      <div class="risk-title">风险提示</div>
      <div class="risk-content">
        <p>尊敬的用户，您正在登录量化牛牛交易平台。投资有风险，入市需谨慎。请注意：</p>
        <ul>
          <li>量化交易可能面临市场风险、流动性风险等</li>
          <li>过去业绩不代表未来表现</li>
          <li>请根据自身风险承受能力合理配置资产</li>
          <li>建议您详细了解产品风险收益特征</li>
        </ul>
      </div>
      <button class="risk-confirm-btn" @click="confirmRiskTip">我已阅读并了解风险</button>
    </div>
  </div>
</template>

<script setup>
import { useAuth } from '@/composables/useAuth'

const {
  showLoginModal,
  showRiskTip,
  loginForm,
  isRegisterMode,
  loginLoading,
  errorMessage,
  errorVisible,
  successMessage,
  successVisible,
  closeLoginModal,
  switchToRegister,
  switchToLogin,
  submitLogin,
  submitRegister,
  confirmRiskTip
} = useAuth()
</script>

<style scoped>
/* 登录弹窗样式 */
.login-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.login-box {
  width: 90%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  padding: 30px;
  position: relative;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.close-login {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 24px;
  color: #ff7f24;
  cursor: pointer;
}

.login-title {
  font-size: 22px;
  color: #ff7f24;
  text-align: center;
  margin-bottom: 20px;
  font-weight: bold;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.login-form input {
  padding: 12px 15px;
  border: 1px solid #ffb380;
  border-radius: 6px;
  font-size: 14px;
}

.login-form input:focus {
  outline: none;
  border-color: #ff7f24;
}

.login-btn {
  background-color: #ff7f24;
  color: white;
  border: none;
  padding: 12px 0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.2s;
}

.login-btn:hover {
  background-color: #ff6a00;
}

.login-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.login-btn.register-btn {
  background-color: #4CAF50;
}

.login-btn.register-btn:hover {
  background-color: #45a049;
}

.login-switch {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 15px;
}

.login-switch a {
  color: #ff7f24;
  text-decoration: none;
  font-weight: bold;
}

.login-switch a:hover {
  text-decoration: underline;
}

.login-tips {
  text-align: center;
  font-size: 13px;
  color: #999;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.error-tips {
  color: #ff4500;
  text-align: center;
  margin-bottom: 10px;
  padding: 8px;
  background-color: #fff0f0;
  border-radius: 4px;
}

.success-tips {
  color: #4CAF50;
  text-align: center;
  margin-bottom: 10px;
  padding: 8px;
  background-color: #f0fff0;
  border-radius: 4px;
}

/* 动态风险提示样式 */
.risk-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10000;
}

.risk-box {
  width: 90%;
  max-width: 500px;
  background: white;
  border-radius: 10px;
  padding: 30px;
  text-align: center;
}

.risk-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.risk-title {
  font-size: 24px;
  color: #ff7f24;
  margin-bottom: 20px;
  font-weight: bold;
}

.risk-content {
  text-align: left;
  color: #666;
  margin-bottom: 20px;
  line-height: 1.8;
}

.risk-content ul {
  padding-left: 20px;
  margin-top: 10px;
}

.risk-content li {
  margin-bottom: 8px;
}

.risk-confirm-btn {
  background-color: #ff7f24;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}

.risk-confirm-btn:hover {
  background-color: #ff6a00;
}
</style>
