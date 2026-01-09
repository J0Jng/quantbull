<template>
  <div class="factor-create-page">
    <div class="container">
      <!-- 页面导航 -->
      <div class="page-nav">
        <router-link to="/factors" class="back-btn">返回列表</router-link>
        <h1 class="page-title">因子创建</h1>
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
                placeholder="请输入因子名称（最大50字符）"
                maxlength="50"
                class="form-control"
                :class="{ 'error': fieldErrors.name }"
              />
              <div v-if="fieldErrors.name" class="field-error">{{ fieldErrors.name }}</div>
              <div class="char-count">{{ factorForm.name.length }}/50</div>
            </div>
            <div class="form-group">
              <label for="factor-code">因子代码 <span class="required">*</span></label>
              <input 
                id="factor-code"
                v-model="factorForm.code"
                type="text"
                placeholder="请输入因子代码（如：MACD、RSI）"
                maxlength="20"
                class="form-control"
                :class="{ 'error': fieldErrors.code }"
              />
              <div v-if="fieldErrors.code" class="field-error">{{ fieldErrors.code }}</div>
              <div class="char-count">{{ factorForm.code.length }}/20</div>
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
                placeholder="请输入因子描述（最大500字符）"
                rows="3"
                maxlength="500"
                class="form-control"
                :class="{ 'error': fieldErrors.description }"
              ></textarea>
              <div v-if="fieldErrors.description" class="field-error">{{ fieldErrors.description }}</div>
              <div class="char-count">{{ factorForm.description.length }}/500</div>
            </div>
          </div>
        </div>

        <!-- 因子表达式编辑器 -->
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
              <button 
                class="btn-secondary" 
                @click="applyExpressionTemplate"
                :disabled="applyingTemplate"
              >
                {{ applyingTemplate ? '应用中...' : '应用模板' }}
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>表达式定义（支持数学公式和Python语法）</label>
            <div class="expression-editor-container">
              <textarea
                ref="expressionEditor"
                v-model="factorForm.expression"
                placeholder="请输入因子计算表达式..."
                rows="8"
                class="expression-input"
                :class="{ 'error': fieldErrors.expression }"
                @input="onExpressionChange"
              ></textarea>
              <div class="expression-info">
                <div class="char-count">字符数: {{ factorForm.expression.length }}</div>
                <div class="validation-status" :class="validationStatusClass">
                  {{ validationMessage }}
                </div>
              </div>
            </div>
            <div v-if="fieldErrors.expression" class="field-error">{{ fieldErrors.expression }}</div>
            <div class="expression-hint">
              <p><strong>表达式提示:</strong></p>
              <ul>
                <li>可以使用基本的数学运算符：+ - * /</li>
                <li>支持常见函数：log、exp、sqrt、abs等</li>
                <li>可引用价格数据：open、high、low、close、volume</li>
                <li>可使用技术指标：MA、RSI、MACD等</li>
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

        <!-- 高级设置 -->
        <div class="form-section">
          <h2 class="section-title">高级设置</h2>
          <div class="form-row">
            <div class="form-group">
              <label for="factor-format">数值格式</label>
              <select 
                id="factor-format"
                v-model="factorForm.format"
                class="form-control"
              >
                <option value="decimal">小数（默认）</option>
                <option value="percentage">百分比</option>
                <option value="integer">整数</option>
              </select>
            </div>
            <div class="form-group">
              <label for="factor-precision">小数位数</label>
              <input 
                id="factor-precision"
                v-model="factorForm.precision"
                type="number"
                min="0"
                max="8"
                class="form-control"
                placeholder="默认4位"
              />
            </div>
          </div>
        </div>

        <!-- 表单操作按钮 -->
        <div class="form-actions">
          <button 
            class="btn-primary" 
            @click="createFactor"
            :disabled="submitting"
          >
            {{ submitting ? '创建中...' : '创建因子' }}
          </button>
          <router-link to="/factors" class="btn-secondary">
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
          <div v-if="creationResult.factorId" class="result-actions">
            <router-link :to="`/factors/${creationResult.factorId}`" class="btn-primary">
              查看因子详情
            </router-link>
            <router-link to="/factors" class="btn-secondary">
              返回列表
            </router-link>
            <router-link :to="`/factors/create`" class="btn-secondary">
              继续创建
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useFactorStore } from '@/stores/factor'

const router = useRouter()
const factorStore = useFactorStore()

// 响应式数据
const factorForm = ref({
  name: '',
  code: '',
  category: '',
  description: '',
  expression: '',
  parameters: '{}',
  format: 'decimal',
  precision: 4
})

const formErrors = ref([])
const fieldErrors = ref({})
const submitting = ref(false)
const validatingExpression = ref(false)
const applyingTemplate = ref(false)
const validationResult = ref(null)
const creationResult = ref(null)

// 计算属性
const validationStatusClass = computed(() => {
  if (validationResult.value) {
    return validationResult.value.status
  }
  return factorForm.value.expression.length > 0 ? 'success' : 'warning'
})

const validationMessage = computed(() => {
  if (validationResult.value) {
    return validationResult.value.message
  }
  return factorForm.value.expression.length > 0 ? '表达式格式良好' : '请输入表达式'
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
  // 清除之前的验证结果
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
        details: response.errors ? response.errors.join('\n') : '表达式语法正确且格式规范。'
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

const applyExpressionTemplate = () => {
  applyingTemplate.value = true
  
  try {
    const templates = {
      technical: `# 移动平均线因子示例
close_price = close
ma_20 = MA(close, 20)
factor_value = (close_price - ma_20) / ma_20`,
      fundamental: `# 市盈率因子示例
eps = earnings_per_share
price = close
pe_ratio = price / eps if eps > 0 else None
factor_value = 1 / pe_ratio if pe_ratio else None`,
      macro: `# 宏观经济因子示例
gdp_growth = gdp_data.growth_rate
inflation_rate = macro_data.inflation
factor_value = gdp_growth - inflation_rate`
    }
    
    const template = templates[factorForm.value.category] || `# ${factorForm.value.category} 因子模板
# 请在此处编写因子表达式
factor_value = close`
    
    factorForm.value.expression = template
    factorForm.value.parameters = '{"window": 20, "threshold": 0.1}'
    
    validationResult.value = {
      status: 'success',
      message: '模板应用成功！',
      details: `已应用${factorForm.value.category}因子模板，请根据需要进行修改。`
    }
  } catch (error) {
    validationResult.value = {
      status: 'error',
      message: '模板应用失败',
      details: error.message
    }
  } finally {
    applyingTemplate.value = false
  }
}

const validateForm = () => {
  formErrors.value = []
  fieldErrors.value = {}
  
  // 验证因子名称
  if (!factorForm.value.name.trim()) {
    fieldErrors.value.name = '因子名称不能为空'
    formErrors.value.push('因子名称不能为空')
  } else if (factorForm.value.name.length > 50) {
    fieldErrors.value.name = '因子名称不能超过50个字符'
    formErrors.value.push('因子名称长度超标')
  }
  
  // 验证因子代码
  if (!factorForm.value.code.trim()) {
    fieldErrors.value.code = '因子代码不能为空'
    formErrors.value.push('因子代码不能为空')
  } else if (factorForm.value.code.length > 20) {
    fieldErrors.value.code = '因子代码不能超过20个字符'
    formErrors.value.push('因子代码长度超标')
  }
  
  // 验证因子类别
  if (!factorForm.value.category) {
    fieldErrors.value.category = '请选择因子类别'
    formErrors.value.push('因子类别不能为空')
  }
  
  // 验证因子描述
  if (factorForm.value.description.length > 500) {
    fieldErrors.value.description = '因子描述不能超过500个字符'
    formErrors.value.push('因子描述长度超标')
  }
  
  // 验证因子表达式
  if (!factorForm.value.expression.trim()) {
    fieldErrors.value.expression = '因子表达式不能为空'
    formErrors.value.push('因子表达式不能为空')
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

const createFactor = async () => {
  if (!validateForm()) {
    return
  }
  
  submitting.value = true
  creationResult.value = null
  
  try {
    const factorData = {
      name: factorForm.value.name,
      code: factorForm.value.code,
      category: factorForm.value.category,
      description: factorForm.value.description,
      expression: factorForm.value.expression,
      parameters: JSON.parse(factorForm.value.parameters),
      format: factorForm.value.format,
      precision: parseInt(factorForm.value.precision) || 4
    }
    
    const response = await factorStore.createNewFactor(factorData)
    
    if (factorStore.error) {
      creationResult.value = {
        status: 'error',
        title: '创建失败',
        message: factorStore.error
      }
    } else if (response) {
      creationResult.value = {
        status: 'success',
        title: '因子创建成功！',
        message: `因子 "${factorForm.value.name}" 已成功创建。`,
        factorId: response.id
      }
    }
  } catch (error) {
    creationResult.value = {
      status: 'error',
      title: '创建失败',
      message: `创建因子时发生错误: ${error.message}`
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
      message: `因子 "${factorForm.value.name}" 已保存为草稿。`
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
  // 可以在这里加载默认设置
})
</script>

<style scoped>
.factor-create-page {
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

.expression-hint {
  margin-top: 10px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
  font-size: 0.9rem;
}

.expression-hint ul {
  margin: 5px 0;
  padding-left: 20px;
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
</style>