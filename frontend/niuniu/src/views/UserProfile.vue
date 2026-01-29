<template>
  <div class="user-profile">
    <!-- 头部 -->
    <div class="header">
      <div class="logo" @click="goHome">个人主页</div>
      <div class="header-opt">
        <a href="#">我的订单</a>
        <a href="#">购物车</a>
        <div class="user-menu-container">
          <div class="user-btn">已登录</div>
        </div>
      </div>
    </div>

    <!-- 个人主页内容 -->
    <div class="profile-container">
      <div class="profile-card">
        <h1 class="profile-title">个人信息中心</h1>
        
        <!-- 基本信息 -->
        <div class="info-section">
          <h2 class="section-title">基本信息</h2>
          <div class="info-grid">
            <div class="info-item">
              <label>昵称</label>
              <div class="info-value">{{ currentUser || '--' }}</div>
            </div>
            <div class="info-item">
              <label>注册时间</label>
              <div class="info-value">{{ userCreatedAtDisplay }}</div>
            </div>
          </div>
        </div>

        <!-- 账户状态 -->
        <div class="status-section">
          <h2 class="section-title">账户状态</h2>
          <div class="status-grid">
            <div class="status-item">
              <span class="status-icon">💰</span>
              <div class="status-info">
                <div class="status-label">账户余额</div>
                <div class="status-value">¥0.00</div>
              </div>
            </div>
            <div class="status-item">
              <span class="status-icon">🔑</span>
              <div class="status-info">
                <div class="status-label">AI Token 余额</div>
                <div class="status-value">{{ tokenBalanceDisplay }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 合格投资者认证 -->
        <div class="investor-section" v-if="!isQualifiedInvestor">
          <h2 class="section-title">合格投资者认证</h2>
          <div class="investor-card">
            <div class="investor-info">
              <div class="investor-icon">🔒</div>
              <div class="investor-text">
                <h3>认证合格投资者</h3>
                <p>完成认证后，您将能访问专属基金等高风险投资产品</p>
                <ul>
                  <li>查看高价值基金产品</li>
                  <li>参与私募投资机会</li>
                  <li>获取专业投资咨询</li>
                </ul>
              </div>
            </div>
            <button class="investor-btn" @click="startInvestorCertification">开始认证</button>
          </div>
        </div>

        <!-- 已认证投资者 -->
        <div class="investor-section" v-else>
          <h2 class="section-title">合格投资者认证</h2>
          <div class="certified-card">
            <div class="certified-icon">✅</div>
            <div class="certified-content">
              <h3>认证成功</h3>
              <p>您已完成合格投资者认证，可以访问所有投资产品</p>
              <div class="certification-tags" v-if="investorTags.length">
                <span class="certification-tag" v-for="(tag, index) in investorTags" :key="index">{{ tag }}</span>
              </div>
              <div class="certification-info">
                <span>认证时间：{{ investorCertifiedAtDisplay }}</span>
                <span>认证等级：合格投资者</span>
              </div>
              <button class="logout-cert-btn" @click="logoutCertification">退出认证</button>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-section">
          <button class="action-btn secondary" v-if="isAdmin" @click="goAdminUsers">用户管理</button>
          <button class="action-btn secondary" @click="goHome">返回首页</button>
        </div>
      </div>
    </div>

    <!-- 合格投资者认证弹窗 -->
    <div class="certification-modal" v-show="showCertification">
      <div class="modal-content">
        <div class="modal-header">
          <h2>合格投资者认证</h2>
          <span class="close-btn" @click="closeCertification">&times;</span>
        </div>
        <div class="modal-body">
          <div class="certification-step">
            <h3>基本信息确认</h3>
            <form class="certification-form">
              <div class="form-group">
                <label>真实姓名</label>
                <input type="text" v-model="certForm.realName" placeholder="请输入真实姓名（选填）">
              </div>
              <div class="form-group">
                <label>身份证号码</label>
                <input type="text" v-model="certForm.idCard" placeholder="请输入身份证号码（选填）">
              </div>
              <div class="form-group">
                <label>风险承受能力评估</label>
                <select v-model="certForm.riskLevel">
                  <option value="">请选择风险承受能力</option>
                  <option value="conservative">保守型</option>
                  <option value="moderate">稳健型</option>
                  <option value="aggressive">进取型</option>
                </select>
              </div>
            </form>
          </div>

          <div class="certification-step">
            <h3>资产情况</h3>
            <div class="asset-info">
              <p>根据《证券期货投资者适当性管理办法》，合格投资者需满足以下条件之一：</p>
              <ul>
                <li>金融资产不低于300万元</li>
                <li>最近3年个人年均收入不低于50万元</li>
                <li>具有2年以上投资经验</li>
              </ul>
              <div class="asset-options">
                <label><input type="radio" v-model="certForm.assetType" value="financial">金融资产 ≥ 300万元</label>
                <label><input type="radio" v-model="certForm.assetType" value="income">年收入 ≥ 50万元</label>
                <label><input type="radio" v-model="certForm.assetType" value="experience">投资经验 ≥ 2年</label>
              </div>
            </div>
          </div>

          <div class="certification-step">
            <h3>风险确认</h3>
            <div class="risk-confirm">
              <p>请仔细阅读并确认以下风险提示：</p>
              <div class="risk-content">
                <p>• 投资有风险，入市需谨慎</p>
                <p>• 过往业绩不代表未来表现</p>
                <p>• 高风险产品可能导致本金损失</p>
                <p>• 请根据自身情况合理配置资产</p>
              </div>
              <label class="confirm-checkbox">
                <input type="checkbox" v-model="certForm.riskConfirmed">
                我已阅读并理解上述风险提示
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeCertification">取消</button>
          <button class="btn-submit" @click="submitCertification">提交认证</button>
        </div>
      </div>
    </div>

    <!-- 统一页脚 -->
    <FooterComponent />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import FooterComponent from '@/components/FooterComponent.vue'
import { getTokenBalance, isAuthenticated } from '@/services/authService'
import { submitInvestorCertification, getInvestorStatus, revokeInvestorCertification } from '@/services/investorService'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { isAdmin, initAuth, isQualifiedInvestor, currentUser, currentUserEmail, currentUserPhone, currentUserCreatedAt } = useAuth()
const showCertification = ref(false)
const tokenBalance = ref(null)
const tokenLoading = ref(false)
const tokenError = ref('')
const investorTags = ref([])
const investorCertifiedAt = ref(null)

// 在页面加载时检查认证状态
onMounted(async () => {
  const authed = await initAuth()
  loadTokenBalance()
  if (authed || isAuthenticated()) {
    loadInvestorStatus()
  }
})

const certForm = ref({
  realName: '',
  idCard: '',
  riskLevel: '',
  assetType: '',
  riskConfirmed: false
})

function goHome() {
  router.push('/')
}

function goAdminUsers() {
  router.push('/admin/users')
}

function goBack() {
  router.push('/shop')
}

function editProfile() {
  alert('个人信息编辑功能开发中...')
}

function startInvestorCertification() {
  showCertification.value = true
  // 重置表单
  certForm.value = {
    realName: '',
    idCard: '',
    riskLevel: '',
    assetType: '',
    riskConfirmed: false
  }
}

async function loadInvestorStatus() {
  try {
    const result = await getInvestorStatus()
    if (result.success) {
      const data = result.data?.data || result.data || {}
      isQualifiedInvestor.value = !!data.qualified_investor
      investorTags.value = Array.isArray(data.tags) ? data.tags : []
      investorCertifiedAt.value = data.certified_at || null
      if (data.qualified_investor) {
        localStorage.setItem('qualifiedInvestor', 'certified')
      } else {
        localStorage.removeItem('qualifiedInvestor')
      }
    }
  } catch (err) {
    console.warn('Failed to load investor status:', err)
  }
}

// 加载 AI Token 余额
async function loadTokenBalance() {
  tokenLoading.value = true
  tokenError.value = ''
  try {
    const result = await getTokenBalance()
    if (result.success) {
      const data = result.data?.data || result.data || {}
      const balance = data.ai_tokens ?? data.balance ?? data.tokens ?? null
      tokenBalance.value = balance !== null ? Number(balance) : null
    } else {
      tokenError.value = result.message || '获取失败'
    }
  } catch (err) {
    tokenError.value = err.message || '获取失败'
  } finally {
    tokenLoading.value = false
  }
}

const tokenBalanceDisplay = computed(() => {
  if (tokenLoading.value) return '加载中...'
  if (tokenError.value) return '获取失败'
  if (tokenBalance.value === null || Number.isNaN(tokenBalance.value)) return '--'
  return `${tokenBalance.value}`
})

const investorCertifiedAtDisplay = computed(() => {
  if (!investorCertifiedAt.value) return '--'
  const date = new Date(investorCertifiedAt.value)
  if (Number.isNaN(date.getTime())) return '--'
  return date.toLocaleString('zh-CN')
})

const userCreatedAtDisplay = computed(() => {
  if (!currentUserCreatedAt.value) return '--'
  const date = new Date(currentUserCreatedAt.value)
  if (Number.isNaN(date.getTime())) return '--'
  return date.toLocaleString('zh-CN')
})

function closeCertification() {
  showCertification.value = false
}

async function submitCertification() {
  if (!certForm.value.riskConfirmed) {
    alert('请确认风险提示')
    return
  }
  
  // 检查必填字段是否为空（姓名/身份证不再强制）
  if (!certForm.value.riskLevel || !certForm.value.assetType) {
    alert('请填写完整的认证信息')
    return
  }
  
  try {
    const payload = {
      real_name: certForm.value.realName?.trim() || null,
      id_card: certForm.value.idCard?.trim() || null,
      risk_level: certForm.value.riskLevel,
      asset_type: certForm.value.assetType,
      risk_confirmed: certForm.value.riskConfirmed
    }
    const result = await submitInvestorCertification(payload)
    if (result.success) {
      const data = result.data?.data || result.data || {}
      isQualifiedInvestor.value = !!data.qualified_investor
      investorTags.value = Array.isArray(data.tags) ? data.tags : []
      investorCertifiedAt.value = data.certified_at || null
      showCertification.value = false
      if (data.qualified_investor) {
        localStorage.setItem('qualifiedInvestor', 'certified')
      }
      window.dispatchEvent(new Event('investorCertificationChanged'))
      alert('合格投资者认证成功！您现在可以访问基金和投顾产品了。')
    } else {
      alert(result.message || '认证失败，请稍后重试')
    }
  } catch (err) {
    alert(err.message || '认证失败，请稍后重试')
  }
}

async function logoutCertification() {
  if (!confirm('确定要退出合格投资者认证吗？退出后将无法访问基金和投顾产品。')) {
    return
  }

  try {
    const result = await revokeInvestorCertification()
    if (result.success) {
      const data = result.data?.data || result.data || {}
      isQualifiedInvestor.value = !!data.qualified_investor
      investorTags.value = Array.isArray(data.tags) ? data.tags : []
      investorCertifiedAt.value = data.certified_at || null
      localStorage.removeItem('qualifiedInvestor')
      window.dispatchEvent(new Event('investorCertificationChanged'))
      alert('已成功退出合格投资者认证。')
    } else {
      alert(result.message || '退出失败，请稍后重试')
    }
  } catch (err) {
    alert(err.message || '退出失败，请稍后重试')
  }
}
</script>

<style scoped>
.user-profile {
  min-height: 100vh;
  background-color: #fff8f0;
}

/* 头部样式复用 */
.header {
  background-color: #ff7f24;
  padding: 12px 20px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 99;
}

.logo {
  font-size: 22px;
  font-weight: bold;
  color: #ffffff;
  cursor: pointer;
}

.header-opt {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-opt a {
  color: white;
  text-decoration: none;
  font-size: 14px;
}

.user-btn {
  background-color: white;
  color: #ff7f24;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

/* 个人主页内容 */
.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 30px 20px;
}

.profile-card {
  background: white;
  border-radius: 10px;
  padding: 30px;
  border: 2px solid #ffb380;
  box-shadow: 0 4px 12px rgba(255, 127, 36, 0.1);
}

.profile-title {
  font-size: 28px;
  color: #ff7f24;
  text-align: center;
  margin-bottom: 30px;
  font-weight: bold;
}

.section-title {
  font-size: 20px;
  color: #ffffff;
  border-left: 4px solid #ffffff;
  padding-left: 10px;
  margin: 25px 0 15px;
}

/* 基本信息样式 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-item label {
  font-weight: bold;
  color: #666;
  font-size: 14px;
}

.info-value {
  font-size: 16px;
  color: white;
  padding: 8px 12px;
  background: #ff7f24;
  border-radius: 4px;
  border: 1px solid #ff9933;
}

/* 状态信息样式 */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: linear-gradient(135deg, #fff8f0, #ffe8d6);
  border-radius: 8px;
  border: 1px solid #ffb380;
}

.status-icon {
  font-size: 24px;
}

.status-info {
  display: flex;
  flex-direction: column;
}

.status-label {
  font-size: 14px;
  color: #666;
}

.status-value {
  font-size: 18px;
  color: #ff7f24;
  font-weight: bold;
}

/* 投资者认证样式 */
.investor-card, .certified-card {
  background: linear-gradient(135deg, #ff7f24, #ff9933);
  color: white;
  padding: 25px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.investor-info {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 15px;
}

.investor-icon, .certified-icon {
  font-size: 40px;
}

.investor-text h3, .certified-content h3 {
  margin-bottom: 10px;
  font-size: 20px;
}

.investor-text ul {
  margin: 10px 0;
  padding-left: 20px;
}

.investor-text li {
  margin-bottom: 5px;
}

.investor-btn {
  background: white;
  color: #ff7f24;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.investor-btn:hover {
  background: #f0f0f0;
  transform: translateY(-2px);
}

/* 已认证样式 */
.certified-content {
  text-align: center;
}

.certification-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin: 12px 0 8px;
}

.certification-tag {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: #fff;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
}

.certification-info {
  margin-top: 15px;
  font-size: 14px;
  opacity: 0.9;
}

.certification-info span {
  display: block;
  margin: 5px 0;
}

.logout-cert-btn {
  background: white;
  color: #ff7f24;
  border: 1px solid #ff7f24;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 15px;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.3s;
}

.logout-cert-btn:hover {
  background: #ffe6cc;
  transform: translateY(-2px);
}

/* 操作按钮 */
.action-section {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  justify-content: center;
}

.action-btn {
  padding: 12px 25px;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn.primary {
  background: #ff7f24;
  color: white;
}

.action-btn.secondary {
  background: white;
  color: #ff7f24;
  border: 2px solid #ff7f24;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 127, 36, 0.2);
}

/* 认证弹窗样式 */
.certification-modal {
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

.modal-content {
  width: 90%;
  max-width: 500px;
  background: white;
  border-radius: 10px;
  overflow: hidden;
}

.modal-header {
  background: #ff7f24;
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-btn {
  font-size: 24px;
  cursor: pointer;
}

.modal-body {
  padding: 25px;
  max-height: 400px;
  overflow-y: auto;
}

.certification-step h3 {
  color: #ff7f24;
  margin-bottom: 15px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.asset-info ul {
  margin: 10px 0;
  padding-left: 20px;
}

.asset-options label {
  display: block;
  margin: 10px 0;
}

.risk-content p {
  margin: 8px 0;
  color: #666;
}

.confirm-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 15px;
}

.modal-footer {
  padding: 15px 25px;
  background: #f8f8f8;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.modal-footer button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-cancel { background: #ccc; color: #333; }
.btn-prev { background: #ffb380; color: white; }
.btn-next, .btn-submit { background: #ff7f24; color: white; }

@media (max-width: 768px) {
  .profile-container {
    padding: 15px;
  }
  
  .profile-card {
    padding: 20px;
  }
  
  .info-grid, .status-grid {
    grid-template-columns: 1fr;
  }
  
  .action-section {
    flex-direction: column;
  }
}
</style>
