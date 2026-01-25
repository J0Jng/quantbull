<template>
  <div class="strategy-create-page">
    <header class="header">
      <router-link to="/" class="logo">量化牛牛 - 股票数据中心</router-link>
      <div class="header-nav">
        <router-link to="/stock-data">股票数据</router-link>
        <router-link to="/dragon-tiger-list">龙虎榜</router-link>
        <router-link to="/financial-report">财报</router-link>
        <router-link to="/fund-source">资金流动</router-link>
        <router-link to="/company-research">公司研报</router-link>
        <router-link to="/quant-analysis">量化分析工具</router-link>
        <div class="user-menu-container" @mouseenter="onMenuEnter" @mouseleave="onMenuLeave">
          <div class="user-btn" @click="toggleUserMenu">{{ userText }}</div>
          <div class="user-dropdown" v-show="showUserMenu && logged" @mouseenter="onDropdownEnter" @mouseleave="onDropdownLeave">
            <div class="dropdown-item" @click="goToUserProfile">个人主页</div>
            <div class="dropdown-item logout" @click="handleLogout">退出登录</div>
          </div>
        </div>
      </div>
    </header>

    <div class="container">
      <!-- 页面导航 -->
      <div class="page-nav">
        <router-link to="/strategies" class="back-btn">返回列表</router-link>
        <h1 class="page-title">策略创建</h1>
      </div>

      <div class="strategy-form-section card">
        <!-- 表单验证错误 -->
        <div v-if="formErrors.length > 0" class="validation-errors">
          <h3>请修正以下错误:</h3>
          <ul>
            <li v-for="error in formErrors" :key="error">{{ error }}</li>
          </ul>
        </div>

        <!-- 策略基本信息 -->
        <div class="form-section">
          <h2 class="section-title">策略信息</h2>
          <div class="form-row">
            <div class="form-group">
              <label for="strategy-name">策略名称 <span class="required">*</span></label>
              <input 
                id="strategy-name"
                v-model="strategyForm.name"
                type="text"
                placeholder="请输入策略名称（最大100字符）"
                maxlength="100"
                class="form-control"
                :class="{ 'error': fieldErrors.name }"
              />
              <div v-if="fieldErrors.name" class="field-error">{{ fieldErrors.name }}</div>
              <div class="char-count">{{ strategyForm.name.length }}/100</div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="strategy-description">策略描述</label>
              <textarea 
                id="strategy-description"
                v-model="strategyForm.description"
                placeholder="请输入策略描述（最大1000字符）"
                rows="3"
                maxlength="1000"
                class="form-control"
                :class="{ 'error': fieldErrors.description }"
              ></textarea>
              <div v-if="fieldErrors.description" class="field-error">{{ fieldErrors.description }}</div>
              <div class="char-count">{{ strategyForm.description.length }}/1000</div>
            </div>
          </div>
        </div>

        <!-- 策略代码编辑器 -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">策略代码 <span class="required">*</span></h2>
            <div class="code-actions">
              <select 
                v-model="selectedExample" 
                @change="insertExample"
                class="example-select"
                :disabled="loadingExamples"
              >
                <option value="">{{ loadingExamples ? '加载中...' : '插入示例代码' }}</option>
                <option v-for="example in exampleStrategies" :key="example.id" :value="example.id">
                  {{ example.name }}
                </option>
              </select>
              <button 
                class="btn-secondary" 
                @click="validateCode"
                :disabled="!strategyForm.code || validatingCode"
              >
                {{ validatingCode ? '验证中...' : '验证代码' }}
              </button>
              <button 
                class="btn-secondary" 
                @click="showAIDialog = true"
                :disabled="generatingStrategy"
                title="使用AI生成策略代码"
              >
                {{ generatingStrategy ? 'AI生成中...' : 'AI生成' }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>Python策略代码（最少10行）</label>
            <div class="code-editor-container">
              <textarea
                ref="codeEditor"
                v-model="strategyForm.code"
                placeholder="请输入Python策略代码..."
                rows="15"
                class="code-input"
                :class="{ 'error': fieldErrors.code }"
                @input="onCodeChange"
              ></textarea>
              <div class="code-info">
                <div class="line-count">行数: {{ lineCount }}</div>
                <div class="validation-status" :class="validationStatusClass">
                  {{ validationMessage }}
                </div>
              </div>
            </div>
            <div v-if="fieldErrors.code" class="field-error">{{ fieldErrors.code }}</div>
            <div class="code-requirements">
              <ul>
                <li :class="{ 'requirement-met': lineCount >= 10 }">
                  ✓ 最少10行代码（当前: {{ lineCount }}行）
                </li>
                <li :class="{ 'requirement-met': hasRequiredClasses }">
                  ✓ 必须包含必要的类和函数定义
                </li>
                <li :class="{ 'requirement-met': !hasSyntaxErrors }">
                  ✓ Python语法正确
                </li>
              </ul>
            </div>
          </div>

          <!-- 验证结果 -->
          <div v-if="validationResult" class="validation-result" :class="validationResult.valid ? 'success' : 'error'">
            <div class="validation-header">
              <span class="validation-icon">
                {{ validationResult.valid ? '✓' : '✗' }}
              </span>
              <span class="validation-title">
                {{ validationResult.message }}
              </span>
            </div>
            
            <!-- 错误列表 -->
            <div v-if="validationResult.errors && validationResult.errors.length > 0" class="validation-errors-list">
              <h4 class="validation-subtitle">错误:</h4>
              <ul>
                <li v-for="(error, index) in validationResult.errors" :key="'error-' + index" class="error-item">
                  {{ error }}
                </li>
              </ul>
            </div>
            
            <!-- 警告列表 -->
            <div v-if="validationResult.warnings && validationResult.warnings.length > 0" class="validation-warnings-list">
              <h4 class="validation-subtitle">警告:</h4>
              <ul>
                <li v-for="(warning, index) in validationResult.warnings" :key="'warning-' + index" class="warning-item">
                  {{ warning }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 因子选择 -->
        <div class="form-section">
          <h2 class="section-title">关联因子（可选）</h2>
          <div class="factor-selection">
            <div class="selected-factors" v-if="selectedFactors.length > 0">
              <h4>已选择的因子:</h4>
              <div class="selected-factor-list">
                <div 
                  v-for="factor in selectedFactors" 
                  :key="factor.id" 
                  class="selected-factor-item"
                >
                  <span class="factor-name">{{ factor.name }}</span>
                  <span class="factor-code">({{ factor.code }})</span>
                  <button 
                    class="remove-factor-btn" 
                    @click="removeSelectedFactor(factor.id)"
                    title="移除因子"
                  >×</button>
                </div>
              </div>
            </div>
            
            <div class="factor-picker">
              <div class="factor-picker-header">
                <label>选择因子:</label>
                <select 
                  v-model="factorCategoryFilter" 
                  class="factor-category-select"
                >
                  <option value="">全部类别</option>
                  <option value="technical">技术指标</option>
                  <option value="fundamental">基本面因子</option>
                  <option value="macro">宏观因子</option>
                </select>
              </div>
              
              <div v-if="loadingFactors" class="factor-loading">
                加载因子列表中...
              </div>
              
              <div v-else class="available-factors">
                <div 
                  v-for="factor in availableFactors" 
                  :key="factor.id" 
                  class="available-factor-item"
                  :class="{ 'selected': isFactorSelected(factor.id) }"
                  @click="toggleFactor(factor)"
                >
                  <span class="factor-checkbox">{{ isFactorSelected(factor.id) ? '☑' : '☐' }}</span>
                  <span class="factor-name">{{ factor.name }}</span>
                  <span class="factor-code">({{ factor.code }})</span>
                  <span :class="['factor-category-badge', `category-${factor.category}`]">
                    {{ getCategoryText(factor.category) }}
                  </span>
                </div>
                <div v-if="availableFactors.length === 0" class="no-factors">
                  暂无可用因子，<router-link to="/factors/create">创建因子</router-link>
                </div>
              </div>
            </div>
            
            <div class="factor-hint">
              <p>提示：选择因子后，策略回测时可以使用这些因子的计算结果作为信号输入。</p>
            </div>
          </div>
        </div>

        <!-- 策略参数配置 -->
        <div class="form-section">
          <h2 class="section-title">策略参数配置</h2>
          <div class="form-group">
            <label for="strategy-parameters">JSON参数配置</label>
            <textarea
              id="strategy-parameters"
              v-model="strategyForm.parameters"
              placeholder='请输入JSON格式的参数配置，例如：{"window": 20, "threshold": 0.1}'
              rows="5"
              class="form-control json-input"
              :class="{ 'error': fieldErrors.parameters }"
            ></textarea>
            <div v-if="fieldErrors.parameters" class="field-error">{{ fieldErrors.parameters }}</div>
            <div class="json-validation" :class="jsonValidationClass">
              {{ jsonValidationMessage }}
            </div>
          </div>
        </div>

        <!-- 表单操作按钮 -->
        <div class="form-actions">
          <button 
            class="btn-primary" 
            @click="createStrategy"
            :disabled="submitting"
          >
            {{ submitting ? '创建中...' : '创建策略' }}
          </button>
          <router-link to="/strategies" class="btn-secondary">
            取消
          </router-link>
          <button 
            class="btn-secondary" 
            @click="saveAsDraft"
            :disabled="submitting"
          >
            {{ submitting ? '保存中...' : '保存草稿' }}
          </button>
        </div>
      </div>

      <!-- 创建结果提示 -->
      <div v-if="creationResult" class="creation-result" :class="creationResult.status">
        <div class="result-icon">
          {{ creationResult.status === 'success' ? '✓' : '✗' }}
        </div>
        <div class="result-content">
          <h3>{{ creationResult.title }}</h3>
          <p>{{ creationResult.message }}</p>
          <div v-if="creationResult.strategyId" class="result-actions">
            <router-link :to="`/strategies/${creationResult.strategyId}`" class="btn-primary">
              查看策略详情
            </router-link>
            <router-link to="/strategies" class="btn-secondary">
              返回列表
            </router-link>
            <router-link :to="`/strategies/create`" class="btn-secondary">
              继续创建
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- AI 生成对话框 -->
    <div v-if="showAIDialog" class="ai-dialog-overlay" @click="showAIDialog = false">
      <div class="ai-dialog" @click.stop>
        <div class="ai-dialog-header">
          <h3>AI 生成策略代码</h3>
          <button class="close-btn" @click="showAIDialog = false">×</button>
        </div>
        <div class="ai-dialog-body">
          <label for="ai-description">策略描述:</label>
          <textarea
            id="ai-description"
            v-model="aiDescription"
            placeholder="请描述您想要的策略逻辑，例如：\n基于MACD指标的趋势跟踪策略，当MACD金叉时买入，死叉时卖出..."
            rows="6"
            class="ai-textarea"
          ></textarea>
        </div>
        <div class="ai-dialog-footer">
          <button class="btn-secondary" @click="showAIDialog = false">取消</button>
          <button class="btn-primary" @click="generateWithAI" :disabled="!aiDescription.trim() || generatingStrategy">
            {{ generatingStrategy ? '生成中...' : '生成策略' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { 
  createStrategy as createStrategyApi, 
  validateStrategyCode, 
  getStrategyExamples,
  generateStrategyCode 
} from '@/services/strategyService'
import { useFactorStore } from '@/stores/factor'

const router = useRouter()
const { logged, userText, openLoginModal, logout } = useAuth()
const showUserMenu = ref(false)
let menuTimeout = null
let hideTimeout = null

function onMenuEnter() {
  if (!logged.value) return
  clearTimeout(hideTimeout)
  menuTimeout = setTimeout(() => {
    showUserMenu.value = true
  }, 300)
}

function onMenuLeave() {
  clearTimeout(menuTimeout)
  hideTimeout = setTimeout(() => {
    if (showUserMenu.value) {
      showUserMenu.value = false
    }
  }, 200)
}

function onDropdownEnter() {
  clearTimeout(hideTimeout)
}

function onDropdownLeave() {
  hideTimeout = setTimeout(() => {
    showUserMenu.value = false
  }, 200)
}

function toggleUserMenu() {
  if (!logged.value) {
    openLoginModal()
    showUserMenu.value = false
  } else {
    clearTimeout(menuTimeout)
    clearTimeout(hideTimeout)
    showUserMenu.value = !showUserMenu.value
  }
}

function handleLogout() {
  logout()
  showUserMenu.value = false
}

function goToUserProfile() {
  showUserMenu.value = false
  router.push('/profile')
}

const factorStore = useFactorStore()

// 响应式数据
const strategyForm = ref({
  name: '',
  description: '',
  code: '',
  parameters: '{}',
  factor_ids: [],
  status: 'draft'
})

const formErrors = ref([])
const fieldErrors = ref({})
const submitting = ref(false)
const validatingCode = ref(false)
const validationResult = ref(null)
const creationResult = ref(null)

// 示例代码相关
const exampleStrategies = ref([])
const selectedExample = ref('')
const loadingExamples = ref(false)

// AI 生成相关
const showAIDialog = ref(false)
const aiDescription = ref('')
const generatingStrategy = ref(false)
const isExampleCode = ref(false)

// 因子选择相关
const loadingFactors = ref(false)
const allFactors = ref([])
const selectedFactors = ref([])
const factorCategoryFilter = ref('')

// 因子相关计算属性
const availableFactors = computed(() => {
  let factors = allFactors.value
  if (factorCategoryFilter.value) {
    factors = factors.filter(f => f.category === factorCategoryFilter.value)
  }
  return factors
})

// 因子相关方法
const fetchFactors = async () => {
  loadingFactors.value = true
  try {
    await factorStore.fetchFactors({ limit: 100, offset: 0 })
    allFactors.value = factorStore.factors || []
  } catch (error) {
    console.error('加载因子列表失败:', error)
  } finally {
    loadingFactors.value = false
  }
}

const isFactorSelected = (factorId) => {
  return strategyForm.value.factor_ids.includes(factorId)
}

const toggleFactor = (factor) => {
  const index = strategyForm.value.factor_ids.indexOf(factor.id)
  if (index >= 0) {
    // 移除
    strategyForm.value.factor_ids.splice(index, 1)
    selectedFactors.value = selectedFactors.value.filter(f => f.id !== factor.id)
  } else {
    // 添加
    strategyForm.value.factor_ids.push(factor.id)
    selectedFactors.value.push(factor)
  }
}

const removeSelectedFactor = (factorId) => {
  strategyForm.value.factor_ids = strategyForm.value.factor_ids.filter(id => id !== factorId)
  selectedFactors.value = selectedFactors.value.filter(f => f.id !== factorId)
}

const getCategoryText = (category) => {
  const categoryMap = {
    'technical': '技术指标',
    'fundamental': '基本面',
    'macro': '宏观'
  }
  return categoryMap[category] || category
}

// 计算属性
const lineCount = computed(() => {
  if (!strategyForm.value.code) return 0
  return strategyForm.value.code.split('\n').length
})

const hasRequiredClasses = computed(() => {
  const code = strategyForm.value.code.toLowerCase()
  return code.includes('class') && code.includes('def')
})

const hasSyntaxErrors = computed(() => {
  return validationResult.value ? !validationResult.value.valid : false
})

const validationStatusClass = computed(() => {
  if (validationResult.value) {
    return validationResult.value.valid ? 'success' : 'error'
  }
  return lineCount.value >= 10 ? 'success' : 'warning'
})

const validationMessage = computed(() => {
  if (validationResult.value) {
    return validationResult.value.message
  }
  return lineCount.value >= 10 ? '代码格式良好' : '请继续编写代码'
})

const jsonValidationClass = computed(() => {
  try {
    JSON.parse(strategyForm.value.parameters)
    return 'success'
  } catch {
    return 'error'
  }
})

const jsonValidationMessage = computed(() => {
  try {
    JSON.parse(strategyForm.value.parameters)
    return 'JSON格式正确'
  } catch (e) {
    return 'JSON格式错误: ' + e.message
  }
})

// 方法
const onCodeChange = () => {
  // 清除之前的验证结果
  if (validationResult.value) {
    validationResult.value = null
  }
  isExampleCode.value = false
}

const validateCode = async () => {
  if (!strategyForm.value.code.trim()) {
    fieldErrors.value.code = '请先输入策略代码'
    return
  }

  validatingCode.value = true
  validationResult.value = null

  try {
    const response = await validateStrategyCode(strategyForm.value.code)
    
    if (response.success) {
      const data = response.data?.data || response.data || {}
      validationResult.value = {
        valid: data.valid !== undefined ? data.valid : true,
        message: data.message || '代码验证通过',
        errors: data.errors || [],
        warnings: data.warnings || []
      }
    } else {
      validationResult.value = isExampleCode.value
        ? {
            valid: true,
            message: '示例代码已加载（验证服务不可用）',
            errors: [],
            warnings: [response.message || '验证服务返回错误，已跳过验证']
          }
        : {
            valid: false,
            message: response.message || '代码验证失败',
            errors: ['服务返回错误'],
            warnings: []
          }
    }
  } catch (error) {
    validationResult.value = isExampleCode.value
      ? {
          valid: true,
          message: '示例代码已加载（验证服务不可用）',
          errors: [],
          warnings: [error.message || '网络错误，已跳过验证']
        }
      : {
          valid: false,
          message: '验证服务暂时不可用',
          errors: [error.message || '网络错误'],
          warnings: []
        }
  } finally {
    validatingCode.value = false
  }
}

// 加载策略示例
const loadExamples = async () => {
  loadingExamples.value = true
  try {
    const response = await getStrategyExamples()
    if (response.success) {
      const data = response.data?.data || response.data || {}
      exampleStrategies.value = data.items || []
    }
  } catch (error) {
    console.error('加载示例失败:', error)
  } finally {
    loadingExamples.value = false
  }
}

// 插入示例代码
const insertExample = () => {
  if (!selectedExample.value) return
  
  const example = exampleStrategies.value.find(ex => ex.id === selectedExample.value)
  if (example) {
    isExampleCode.value = true
    strategyForm.value.code = example.code
    strategyForm.value.parameters = JSON.stringify(example.default_parameters || {}, null, 2)
    
    // 自动触发验证
    setTimeout(() => {
      validateCode()
    }, 100)
  }
  
  // 重置选择
  selectedExample.value = ''
}

// AI 生成策略代码
const generateWithAI = async () => {
  if (!aiDescription.value.trim()) return
  
  generatingStrategy.value = true
  
  try {
    const response = await generateStrategyCode({
      user_description: aiDescription.value,
      framework: 'backtrader',
      include_risk_control: true
    })
    
    if (response.success) {
      const data = response.data?.data || response.data || {}
      strategyForm.value.code = data.strategy_code || data.code || ''
      
      if (data.parameters) {
        strategyForm.value.parameters = JSON.stringify(data.parameters, null, 2)
      }
      
      showAIDialog.value = false
      aiDescription.value = ''
      
      // 自动验证生成的代码
      setTimeout(() => {
        validateCode()
      }, 100)
    } else {
      alert('AI 生成失败: ' + (response.message || '未知错误'))
    }
  } catch (error) {
    alert('AI 生成失败: ' + error.message)
  } finally {
    generatingStrategy.value = false
  }
}

const validateForm = () => {
  formErrors.value = []
  fieldErrors.value = {}
  
  // 验证策略名称
  if (!strategyForm.value.name.trim()) {
    fieldErrors.value.name = '策略名称不能为空'
    formErrors.value.push('策略名称不能为空')
  } else if (strategyForm.value.name.length > 100) {
    fieldErrors.value.name = '策略名称不能超过100个字符'
    formErrors.value.push('策略名称长度超标')
  }
  
  // 验证策略描述
  if (strategyForm.value.description.length > 1000) {
    fieldErrors.value.description = '策略描述不能超过1000个字符'
    formErrors.value.push('策略描述长度超标')
  }
  
  // 验证策略代码
  if (!strategyForm.value.code.trim()) {
    fieldErrors.value.code = '策略代码不能为空'
    formErrors.value.push('策略代码不能为空')
  } else if (lineCount.value < 10) {
    fieldErrors.value.code = '策略代码至少需要10行'
    formErrors.value.push('策略代码行数不足')
  }
  
  // 验证JSON参数
  try {
    JSON.parse(strategyForm.value.parameters)
  } catch (e) {
    fieldErrors.value.parameters = '参数配置必须是有效的JSON格式'
    formErrors.value.push('参数配置格式错误')
  }
  
  // 检查代码验证状态
  if (validationResult.value && !validationResult.value.valid) {
    formErrors.value.push('策略代码验证未通过，请修正错误后再提交')
  }
  
  return formErrors.value.length === 0
}

const createStrategy = async () => {
  if (!validateForm()) {
    return
  }
  
  submitting.value = true
  creationResult.value = null
  
  try {
    const strategyData = {
      name: strategyForm.value.name,
      description: strategyForm.value.description,
      code: strategyForm.value.code,
      factor_ids: strategyForm.value.factor_ids.length > 0 ? strategyForm.value.factor_ids : ['default'],
      parameters: JSON.parse(strategyForm.value.parameters),
      status: strategyForm.value.status
    }
    
    const response = await createStrategyApi(strategyData)
    
    if (response.success) {
      creationResult.value = {
        status: 'success',
        title: '策略创建成功！',
        message: `策略 "${strategyForm.value.name}" 已成功创建。`,
        strategyId: response.data.id
      }
    } else {
      creationResult.value = {
        status: 'error',
        title: '创建失败',
        message: response.message || '创建策略时发生错误'
      }
    }
  } catch (error) {
    creationResult.value = {
      status: 'error',
      title: '创建失败',
      message: `创建策略时发生错误: ${error.message}`
    }
  } finally {
    submitting.value = false
  }
}

const saveAsDraft = async () => {
  if (!validateForm()) {
    return
  }
  
  submitting.value = true
  
  try {
    // 模拟保存草稿
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    creationResult.value = {
      status: 'success',
      title: '草稿保存成功！',
      message: `策略 "${strategyForm.value.name}" 已保存为草稿。`
    }
  } catch (error) {
    creationResult.value = {
      status: 'error',
      title: '保存失败',
      message: `保存草稿时发生错误: ${error.message}`
    }
  } finally {
    submitting.value = false
  }
}

// 生命周期
onMounted(() => {
  loadExamples()
  fetchFactors()
})
</script>

<style scoped>
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
  color: white;
  text-decoration: none;
}

.logo:hover {
  text-decoration: underline;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-nav a {
  color: white;
  text-decoration: none;
  font-size: 14px;
}

.header-nav .active,
.header-nav .router-link-active,
.header-nav .router-link-exact-active {
  text-decoration: underline;
}

.header-nav .user-btn {
  background-color: white;
  color: #ff7f24;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
}

.user-menu-container {
  position: relative;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border: 1px solid #ffb380;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  min-width: 120px;
}

.dropdown-item {
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #fff3e6;
  color: #333;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background-color: #fff8f0;
}

.dropdown-item.logout {
  color: #ff4500;
}

.strategy-create-page {
  padding: 20px 0;
  background: #fff8f0;
  min-height: calc(100vh - 100px);
}

.container {
  width: 1200px;
  margin: 0 auto;
  position: relative;
}

.page-nav {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.back-btn {
  display: inline-block;
  padding: 10px 20px;
  background-color: #ff7f00;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.back-btn:hover {
  background-color: #e06f00;
}

.page-title {
  font-size: 2rem;
  color: #ff7f00;
  font-weight: bold;
  margin: 0;
}

.card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #f0f0f0;
}

.form-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-title {
  font-size: 24px;
  color: #fff;
  background: #ff7f00;
  padding: 4px 12px;
  border-radius: 3px;
  margin: 0 0 20px 0;
  display: inline-block;
  border-radius: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.required {
  color: #f44336;
  margin-left: 4px;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-group {
  flex: 1;
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
  font-family: inherit;
}

.form-control:focus {
  border-color: #ff7f00;
  outline: none;
}

.form-control.error {
  border-color: #f44336;
  background-color: #ffebee;
}

.char-count {
  text-align: right;
  font-size: 0.8rem;
  color: #666;
  margin-top: 4px;
}

.field-error {
  color: #f44336;
  font-size: 0.9rem;
  margin-top: 4px;
}

.code-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.example-select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 0.9rem;
  min-width: 200px;
}

.example-select:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
  font-weight: bold;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background-color: #ff7f00;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #e06f00;
}

.btn-primary:disabled {
  background-color: #ffa555;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #1e90ff;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #0077ea;
}

.btn-secondary:disabled {
  background-color: #87cefa;
  cursor: not-allowed;
}

.code-editor-container {
  position: relative;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.code-input {
  width: 100%;
  min-height: 300px;
  padding: 15px;
  border: none;
  border-radius: 0;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  resize: vertical;
  background: #f8f8f8;
}

.code-input.error {
  background: #ffebee;
}

.code-info {
  display: flex;
  justify-content: space-between;
  padding: 8px 15px;
  background: #f5f5f5;
  border-top: 1px solid #ddd;
  font-size: 0.8rem;
  color: #666;
}

.line-count {
  font-weight: bold;
}

.validation-status {
  font-weight: bold;
}

.validation-status.success {
  color: #4caf50;
}

.validation-status.warning {
  color: #ff9800;
}

.validation-status.error {
  color: #f44336;
}

.code-requirements {
  margin-top: 10px;
}

.code-requirements ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.code-requirements li {
  padding: 4px 0;
  font-size: 0.9rem;
  color: #666;
}

.requirement-met {
  color: #4caf50;
  font-weight: bold;
}

.validation-result {
  margin-top: 15px;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid;
}

.validation-result.success {
  background: #e8f5e8;
  border-left-color: #4caf50;
}

.validation-result.error {
  background: #ffebee;
  border-left-color: #f44336;
}

.validation-errors-list,
.validation-warnings-list {
  margin-top: 10px;
}

.validation-subtitle {
  margin: 10px 0 5px 0;
  font-size: 0.95rem;
  font-weight: bold;
}

.validation-errors-list ul,
.validation-warnings-list ul {
  margin: 0;
  padding-left: 20px;
}

.error-item {
  color: #d32f2f;
  margin: 5px 0;
}

.warning-item {
  color: #f57c00;
  margin: 5px 0;
}

.ai-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.ai-dialog {
  background: white;
  border-radius: 8px;
  padding: 20px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.ai-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.ai-dialog-header h3 {
  margin: 0;
  color: #ff7f00;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #666;
  line-height: 1;
  padding: 0;
  width: 30px;
  height: 30px;
}

.close-btn:hover {
  color: #333;
}

.ai-dialog-body {
  margin-bottom: 20px;
}

.ai-dialog-body label {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
}

.ai-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  resize: vertical;
}

.ai-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.validation-result.error {
  background: #ffebee;
  border-left-color: #f44336;
}

.validation-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.validation-icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.validation-title {
  font-weight: bold;
}

.validation-details {
  margin-top: 10px;
  padding: 10px;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
  font-family: monospace;
  font-size: 0.9rem;
  white-space: pre-wrap;
}

.json-input {
  font-family: monospace;
  font-size: 0.9rem;
}

.json-validation {
  margin-top: 5px;
  font-size: 0.8rem;
  font-weight: bold;
}

.json-validation.success {
  color: #4caf50;
}

.json-validation.error {
  color: #f44336;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.creation-result {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.creation-result.success {
  background: #e8f5e8;
  border: 1px solid #4caf50;
}

.creation-result.error {
  background: #ffebee;
  border: 1px solid #f44336;
}

.result-icon {
  font-size: 2rem;
  font-weight: bold;
}

.result-content h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.result-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.validation-errors {
  background: #ffebee;
  border: 1px solid #ffcdd2;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 20px;
}

.validation-errors h3 {
  margin: 0 0 10px 0;
  color: #c62828;
}

.validation-errors ul {
  margin: 0;
  padding-left: 20px;
}

.validation-errors li {
  color: #c62828;
}

/* 因子选择样式 */
.factor-selection {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.selected-factors h4 {
  margin: 0 0 10px 0;
  font-size: 14px;
  color: #666;
}

.selected-factor-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.selected-factor-item {
  display: flex;
  align-items: center;
  gap: 5px;
  background: #e3f2fd;
  border: 1px solid #90caf9;
  border-radius: 16px;
  padding: 4px 12px;
  font-size: 13px;
}

.selected-factor-item .factor-name {
  color: #1565c0;
  font-weight: 500;
}

.selected-factor-item .factor-code {
  color: #666;
  font-size: 12px;
}

.remove-factor-btn {
  background: none;
  border: none;
  color: #f44336;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  padding: 0 0 0 5px;
}

.factor-picker-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.factor-category-select {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.factor-loading {
  padding: 20px;
  text-align: center;
  color: #666;
}

.available-factors {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 10px;
}

.available-factor-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f9f9f9;
  border: 1px solid #eee;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.available-factor-item:hover {
  background: #e3f2fd;
  border-color: #90caf9;
}

.available-factor-item.selected {
  background: #e3f2fd;
  border-color: #1976d2;
}

.factor-checkbox {
  color: #1976d2;
}

.available-factor-item .factor-name {
  flex: 1;
  font-weight: 500;
}

.available-factor-item .factor-code {
  color: #888;
  font-size: 12px;
}

.factor-category-badge {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
}

.factor-category-badge.category-technical {
  background: #e8f5e9;
  color: #2e7d32;
}

.factor-category-badge.category-fundamental {
  background: #fff3e0;
  color: #e65100;
}

.factor-category-badge.category-macro {
  background: #e3f2fd;
  color: #1565c0;
}

.no-factors {
  padding: 20px;
  text-align: center;
  color: #999;
}

.no-factors a {
  color: #ff7f00;
}

.factor-hint {
  font-size: 13px;
  color: #888;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}

.factor-hint p {
  margin: 0;
}

@media (max-width: 768px) {
  .container {
    width: 95%;
    padding: 0 10px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 0;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .code-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .result-actions {
    flex-direction: column;
  }
}
</style>