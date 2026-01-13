<template>
  <div class="strategy-edit-page">
    <div class="container">
      <!-- 页面导航 -->
      <div class="page-nav">
        <router-link :to="`/strategies/${strategyId}`" class="back-btn">返回详情</router-link>
        <h1 class="page-title">编辑策略</h1>
      </div>

      <!-- 表单验证错误 -->
      <div v-if="formErrors.length > 0" class="validation-errors">
        <h3>请修正以下错误:</h3>
        <ul>
          <li v-for="error in formErrors" :key="error">{{ error }}</li>
        </ul>
      </div>

      <!-- 策略基本信息编辑 -->
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

      <!-- 策略状态编辑 -->
      <div class="form-section">
        <h2 class="section-title">策略状态</h2>
        <div class="form-row">
          <div class="form-group">
            <label>状态:</label>
            <div class="status-options">
              <label class="status-option">
                <input 
                  type="radio" 
                  v-model="strategyForm.status" 
                  value="draft" 
                  class="status-input"
                />
                <span class="status-label">草稿</span>
              </label>
              <label class="status-option">
                <input 
                  type="radio" 
                  v-model="strategyForm.status" 
                  value="active" 
                  class="status-input"
                />
                <span class="status-label">活跃</span>
              </label>
              <label class="status-option">
                <input 
                  type="radio" 
                  v-model="strategyForm.status" 
                  value="archived" 
                  class="status-input"
                />
                <span class="status-label">已归档</span>
              </label>
            </div>
          </div>
        </div>
      </div>

      <!-- 策略代码编辑 -->
      <div class="form-section">
        <div class="section-header">
          <h2 class="section-title">策略代码 <span class="required">*</span></h2>
          <div class="code-actions">
            <button 
              class="btn-secondary" 
              @click="validateCode"
              :disabled="!strategyForm.code || validatingCode"
            >
              {{ validatingCode ? '验证中...' : '验证代码' }}
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
        <div v-if="validationResult" class="validation-result" :class="validationResult.status">
          <div class="validation-header">
            <span class="validation-icon">
              {{ validationResult.status === 'success' ? '✓' : '✗' }}
            </span>
            <span class="validation-title">
              {{ validationResult.status === 'success' ? '验证通过' : '验证失败' }}
            </span>
          </div>
          <div class="validation-message">{{ validationResult.message }}</div>
          <div v-if="validationResult.details" class="validation-details">
            <pre>{{ validationResult.details }}</pre>
          </div>
        </div>
      </div>

      <!-- 策略参数编辑 -->
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
          @click="saveStrategyUpdate"
          :disabled="submitting"
        >
          {{ submitting ? '更新中...' : '更新策略' }}
        </button>
        <router-link :to="`/strategies`" class="btn-secondary">
          取消
        </router-link>
      </div>

      <!-- 更新结果提示 -->
      <div v-if="updateResult" class="update-result" :class="updateResult.status">
        <div class="result-icon">
          {{ updateResult.status === 'success' ? '✓' : '✗' }}
        </div>
        <div class="result-content">
          <h3>{{ updateResult.title }}</h3>
          <p>{{ updateResult.message }}</p>
          <div class="result-actions">
            <router-link :to="`/strategies`" class="btn-primary">
              查看策略详情
            </router-link>
            <router-link to="/strategies" class="btn-secondary">
              返回列表
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  getStrategy, 
  updateStrategy, 
  validateStrategyCode 
} from '@/services/strategyService'

const route = useRoute()
const router = useRouter()

// 从路由获取策略ID
const strategyId = ref(route.params.id)

// 响应式数据
const strategyForm = ref({
  name: '',
  description: '',
  code: '',
  parameters: '{}',
  status: 'active'
})

const formErrors = ref([])
const fieldErrors = ref({})
const submitting = ref(false)
const validatingCode = ref(false)
const validationResult = ref(null)
const updateResult = ref(null)

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
  return validationResult.value && validationResult.value.status === 'error'
})

const validationStatusClass = computed(() => {
  if (validationResult.value) {
    return validationResult.value.status
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
  if (validationResult.value) {
    validationResult.value = null
  }
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
        status: data.valid ? 'success' : 'error',
        message: data.message || '代码验证通过',
        errors: data.errors || [],
        warnings: data.warnings || [],
        details: data.details || ''
      }
    } else {
      validationResult.value = {
        valid: false,
        status: 'error',
        message: response.message || '代码验证失败',
        errors: ['服务返回错误'],
        warnings: [],
        details: ''
      }
    }
  } catch (error) {
    validationResult.value = {
      valid: false,
      status: 'error',
      message: '验证服务暂时不可用',
      errors: [error.message || '网络错误'],
      warnings: [],
      details: ''
    }
  } finally {
    validatingCode.value = false
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
  
  return formErrors.value.length === 0
}

const saveStrategyUpdate = async () => {
  if (!validateForm()) {
    return
  }
  
  submitting.value = true
  updateResult.value = null
  
  try {
    const updateData = {
      name: strategyForm.value.name,
      description: strategyForm.value.description,
      code: strategyForm.value.code,
      parameters: JSON.parse(strategyForm.value.parameters),
      status: strategyForm.value.status
    }
    
    const response = await updateStrategy(strategyId.value, updateData)
    
    if (response.success) {
      updateResult.value = {
        status: 'success',
        title: '策略更新成功！',
        message: `策略 "${strategyForm.value.name}" 已成功更新。`
      }
      
      // 2秒后跳转到详情页
      setTimeout(() => {
        router.push(`/strategies`)
      }, 2000)
    } else {
      updateResult.value = {
        status: 'error',
        title: '更新失败',
        message: response.message || '更新策略失败'
      }
    }
  } catch (error) {
    updateResult.value = {
      status: 'error',
      title: '更新失败',
      message: `更新策略时发生错误: ${error.message}`
    }
  } finally {
    submitting.value = false
  }
}

// 生命周期
onMounted(() => {
  // 模拟加载策略数据
  fetchStrategyData()
})

const fetchStrategyData = async () => {
  try {
    const response = await getStrategy(strategyId.value)
    
    if (response.success) {
      const data = response.data?.data || response.data || {}
      strategyForm.value = {
        name: data.name || '',
        description: data.description || '',
        code: data.code || '',
        parameters: JSON.stringify(data.parameters || {}, null, 2),
        status: data.status || 'draft'
      }
    } else {
      console.error('获取策略数据失败:', response.message)
    }
  } catch (error) {
    console.error('获取策略数据失败:', error)
  }
}
</script>

<style scoped>
.strategy-edit-page {
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

.status-options {
  display: flex;
  gap: 20px;
  margin-top: 8px;
}

.status-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.status-input {
  width: 18px;
  height: 18px;
}

.status-label {
  font-size: 1rem;
}

.code-actions {
  display: flex;
  gap: 10px;
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

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.update-result {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
}

.update-result.success {
  background: #e8f5e8;
  border: 1px solid #4caf50;
}

.update-result.error {
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