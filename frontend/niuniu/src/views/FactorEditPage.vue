<template>
  <div class="factor-edit-page">
    <div class="container">
      <!-- 页面导航 -->
      <div class="page-nav">
        <router-link :to="`/factors/${factorId}`" class="back-btn">返回详情</router-link>
        <h1 class="page-title">编辑因子</h1>
      </div>

      <div class="factor-form-section card">
        <!-- 表单验证错误 -->
        <div v-if="formErrors.length > 0" class="validation-errors">
          <h3>请修正以下错误:</h3>
          <ul>
            <li v-for="error in formErrors" :key="error">{{ error }}</li>
          </ul>
        </div>

        <!-- 因子基本信息 -->
        <div class="form-section">
          <h2 class="section-title">因子信息</h2>
          <div class="form-row">
            <div class="form-group">
              <label for="factor-name">因子名称 <span class="required">*</span></label>
              <input 
                id="factor-name"
                v-model="factorForm.name"
                type="text"
                placeholder="请输入因子名称（最大100字符）"
                maxlength="100"
                class="form-control"
                :class="{ 'error': fieldErrors.name }"
              />
              <div v-if="fieldErrors.name" class="field-error">{{ fieldErrors.name }}</div>
              <div class="char-count">{{ factorForm.name.length }}/100</div>
            </div>
            <div class="form-group">
              <label for="factor-code">因子代码 <span class="required">*</span></label>
              <input 
                id="factor-code"
                v-model="factorForm.code"
                type="text"
                placeholder="请输入因子代码（如：RSI, MACD等）"
                maxlength="50"
                class="form-control"
                :class="{ 'error': fieldErrors.code }"
              />
              <div v-if="fieldErrors.code" class="field-error">{{ fieldErrors.code }}</div>
              <div class="char-count">{{ factorForm.code.length }}/50</div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="factor-category">因子类别 <span class="required">*</span></label>
              <select 
                id="factor-category"
                v-model="factorForm.category"
                class="form-control"
                :class="{ 'error': fieldErrors.category }"
              >
                <option value="">请选择类别</option>
                <option value="technical">技术指标</option>
                <option value="fundamental">基本面因子</option>
                <option value="macro">宏观因子</option>
              </select>
              <div v-if="fieldErrors.category" class="field-error">{{ fieldErrors.category }}</div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="factor-description">因子描述</label>
              <textarea 
                id="factor-description"
                v-model="factorForm.description"
                placeholder="请输入因子描述（最大1000字符）"
                rows="3"
                maxlength="1000"
                class="form-control"
                :class="{ 'error': fieldErrors.description }"
              ></textarea>
              <div v-if="fieldErrors.description" class="field-error">{{ fieldErrors.description }}</div>
              <div class="char-count">{{ factorForm.description.length }}/1000</div>
            </div>
          </div>
        </div>

        <!-- 因子表达式编辑区域 -->
        <div class="form-section">
          <div class="section-header">
            <h2 class="section-title">因子表达式 <span class="required">*</span></h2>
            <div class="expression-actions">
              <button 
                class="btn-secondary" 
                @click="validateExpression"
                :disabled="!factorForm.expression || validatingExpression"
              >
                {{ validatingExpression ? '验证中...' : '验证表达式' }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>因子表达式（数学公式或Python函数）</label>
            <div class="expression-editor-container">
              <textarea
                ref="expressionEditor"
                v-model="factorForm.expression"
                placeholder="请输入因子表达式，例如：(close - open) / volume * 100"
                rows="8"
                class="expression-input"
                :class="{ 'error': fieldErrors.expression }"
                @input="onExpressionChange"
              ></textarea>
              <div class="expression-info">
                <div class="line-count">字符数: {{ expressionLength }}</div>
                <div class="validation-status" :class="validationStatusClass">
                  {{ validationMessage }}
                </div>
              </div>
            </div>
            <div v-if="fieldErrors.expression" class="field-error">{{ fieldErrors.expression }}</div>
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

        <!-- 因子参数配置 -->
        <div class="form-section">
          <h2 class="section-title">因子参数配置</h2>
          <div class="form-group">
            <label for="factor-parameters">JSON参数配置</label>
            <textarea
              id="factor-parameters"
              v-model="factorForm.parameters"
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
            @click="updateFactor"
            :disabled="submitting"
          >
            {{ submitting ? '更新中...' : '更新因子' }}
          </button>
          <router-link :to="`/factors/${factorId}`" class="btn-secondary">
            取消
          </router-link>
        </div>
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
            <router-link :to="`/factors/${factorId}`" class="btn-primary">
              查看因子详情
            </router-link>
            <router-link to="/factors" class="btn-secondary">
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
import { useFactorStore } from '@/stores/factor'

const route = useRoute()
const router = useRouter()
const factorStore = useFactorStore()

const factorId = route.params.id

// 响应式数据
const factorForm = ref({
  name: '',
  code: '',
  category: '',
  description: '',
  expression: '',
  parameters: '{}'
})

const formErrors = ref([])
const fieldErrors = ref({})
const submitting = ref(false)
const validatingExpression = ref(false)
const validationResult = ref(null)
const updateResult = ref(null)

// 计算属性
const expressionLength = computed(() => {
  return factorForm.value.expression.length
})

const validationStatusClass = computed(() => {
  if (validationResult.value) {
    return validationResult.value.status
  }
  return expressionLength.value >= 5 ? 'success' : 'warning'
})

const validationMessage = computed(() => {
  if (validationResult.value) {
    return validationResult.value.message
  }
  return expressionLength.value >= 5 ? '表达式格式良好' : '请继续编写表达式'
})

const jsonValidationClass = computed(() => {
  try {
    JSON.parse(factorForm.value.parameters)
    return 'success'
  } catch {
    return 'error'
  }
})

const jsonValidationMessage = computed(() => {
  try {
    JSON.parse(factorForm.value.parameters)
    return 'JSON格式正确'
  } catch (e) {
    return 'JSON格式错误: ' + e.message
  }
})

// 方法
const onExpressionChange = () => {
  if (validationResult.value) {
    validationResult.value = null
  }
}

const validateExpression = async () => {
  if (!factorForm.value.expression.trim()) {
    fieldErrors.value.expression = '请先输入因子表达式'
    return
  }

  validatingExpression.value = true
  validationResult.value = null

  try {
    const response = await factorStore.validateExpression(factorForm.value.expression)
    
    if (response.success) {
      validationResult.value = {
        status: 'success',
        message: response.message || '表达式验证通过！',
        details: response.errors ? response.errors.join('\n') : '因子表达式语法正确。'
      }
    } else {
      validationResult.value = {
        status: 'error',
        message: response.message || '表达式验证失败',
        details: response.errors ? response.errors.join('\n') : '请检查表达式问题'
      }
    }
  } catch (error) {
    validationResult.value = {
      status: 'error',
      message: '验证服务暂时不可用，请稍后重试',
      details: error.message
    }
  } finally {
    validatingExpression.value = false
  }
}

const validateForm = () => {
  formErrors.value = []
  fieldErrors.value = {}
  
  // 验证因子名称
  if (!factorForm.value.name.trim()) {
    fieldErrors.value.name = '因子名称不能为空'
    formErrors.value.push('因子名称不能为空')
  } else if (factorForm.value.name.length > 100) {
    fieldErrors.value.name = '因子名称不能超过100个字符'
    formErrors.value.push('因子名称长度超标')
  }
  
  // 验证因子代码
  if (!factorForm.value.code.trim()) {
    fieldErrors.value.code = '因子代码不能为空'
    formErrors.value.push('因子代码不能为空')
  } else if (factorForm.value.code.length > 50) {
    fieldErrors.value.code = '因子代码不能超过50个字符'
    formErrors.value.push('因子代码长度超标')
  }
  
  // 验证因子类别
  if (!factorForm.value.category) {
    fieldErrors.value.category = '请选择因子类别'
    formErrors.value.push('因子类别不能为空')
  }
  
  // 验证因子描述
  if (factorForm.value.description.length > 1000) {
    fieldErrors.value.description = '因子描述不能超过1000个字符'
    formErrors.value.push('因子描述长度超标')
  }
  
  // 验证因子表达式
  if (!factorForm.value.expression.trim()) {
    fieldErrors.value.expression = '因子表达式不能为空'
    formErrors.value.push('因子表达式不能为空')
  } else if (expressionLength.value < 5) {
    fieldErrors.value.expression = '因子表达式过于简单'
    formErrors.value.push('因子表达式需要更复杂')
  }
  
  // 验证JSON参数
  try {
    JSON.parse(factorForm.value.parameters)
  } catch (e) {
    fieldErrors.value.parameters = '参数配置必须是有效的JSON格式'
    formErrors.value.push('参数配置格式错误')
  }
  
  return formErrors.value.length === 0
}

const updateFactor = async () => {
  if (!validateForm()) {
    return
  }
  
  submitting.value = true
  updateResult.value = null
  
  try {
    const updateData = {
      name: factorForm.value.name,
      code: factorForm.value.code,
      category: factorForm.value.category,
      description: factorForm.value.description,
      expression: factorForm.value.expression,
      parameters: JSON.parse(factorForm.value.parameters)
    }
    
    const response = await factorStore.updateExistingFactor(factorId, updateData)
    
    if (response) {
      updateResult.value = {
        status: 'success',
        title: '因子更新成功！',
        message: `因子 "${factorForm.value.name}" 已成功更新。`
      }
    } else {
      updateResult.value = {
        status: 'error',
        title: '更新失败',
        message: factorStore.error || '更新因子时发生错误'
      }
    }
  } catch (error) {
    updateResult.value = {
      status: 'error',
      title: '更新失败',
      message: `更新因子时发生错误: ${error.message}`
    }
  } finally {
    submitting.value = false
  }
}

// 加载因子数据
const loadFactorData = async () => {
  try {
    await factorStore.fetchFactor(factorId)
    
    if (factorStore.currentFactor) {
      const factor = factorStore.currentFactor
      factorForm.value = {
        name: factor.name,
        code: factor.code,
        category: factor.category,
        description: factor.description,
        expression: factor.expression,
        parameters: JSON.stringify(factor.parameters || {}, null, 2)
      }
    }
  } catch (error) {
    console.error('加载因子数据失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadFactorData()
})
</script>

<style scoped>
.factor-edit-page {
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

.expression-actions {
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

.expression-editor-container {
  position: relative;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

.expression-input {
  width: 100%;
  min-height: 200px;
  padding: 15px;
  border: none;
  border-radius: 0;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  resize: vertical;
  background: #f8f8f8;
}

.expression-input.error {
  background: #ffebee;
}

.expression-info {
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

.btn-primary {
  display: inline-block;
  padding: 10px 20px;
  background-color: #ff7f00;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: bold;
  transition: background-color 0.3s;
}

.btn-primary:hover {
  background-color: #e06f00;
}

@media (max-width: 768px) {
  .container {
    width: 95%;
    padding: 0 10px;
  }
}
</style>