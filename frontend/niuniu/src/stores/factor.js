import { defineStore } from 'pinia'
import { 
  getFactors, 
  getFactor, 
  createFactor, 
  updateFactor, 
  deleteFactor,
  calculateFactor,
  validateFactorExpression
} from '@/services/factorService'

export const useFactorStore = defineStore('factor', {
  state: () => ({
    factors: [],
    total: 0,
    currentFactor: null,
    calculationResults: [],
    loading: false,
    error: null,
    validationResult: null,
    pagination: {
      page: 1,
      pageSize: 20
    },
    filters: {
      category: '',
      search: ''
    }
  }),

  actions: {
    // 获取模拟参数列表（支持分页和过滤）
    async fetchFactors(params = {}) {
      this.loading = true
      this.error = null
      
      try {
        // 合并过滤条件和分页
        const queryParams = {
          limit: params.limit ?? this.pagination.pageSize,
          offset: params.offset ?? (this.pagination.page - 1) * this.pagination.pageSize,
          ...(this.filters.category && { category: this.filters.category }),
          ...(this.filters.search && { search: this.filters.search }),
          ...params
        }
        
        const response = await getFactors(queryParams)
        if (response.success) {
          // 后端响应格式: { code, message, data: { total, factors } }
          // handleRequest 包装后: { success, data: { code, message, data: { total, factors } } }
          const responseData = response.data?.data || response.data || {}
          this.factors = responseData.factors || []
          this.total = responseData.total || 0
          return { factors: this.factors, total: this.total }
        } else {
          throw new Error(response.message)
        }
      } catch (error) {
        this.error = error.message
        return null
      } finally {
        this.loading = false
      }
    },

    // 设置过滤条件
    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
      this.pagination.page = 1 // 重置到第一页
    },

    // 设置分页
    setPagination(pagination) {
      this.pagination = { ...this.pagination, ...pagination }
    },

    // 获取模拟参数详情
    async fetchFactor(id) {
      this.loading = true
      this.error = null
      this.currentFactor = null
      
      try {
        const response = await getFactor(id)
        if (response.success) {
          // 后端响应格式: { code, message, data: {...} }
          this.currentFactor = response.data?.data || response.data
        } else {
          throw new Error(response.message)
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    // 创建模拟参数
    async createNewFactor(factorData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await createFactor(factorData)
        if (response.success) {
          // 后端响应格式: { code, message, data: {...} }
          const newFactor = response.data?.data || response.data
          this.factors.unshift(newFactor)
          return newFactor
        } else {
          throw new Error(response.message)
        }
      } catch (error) {
        this.error = error.message
        return null
      } finally {
        this.loading = false
      }
    },

    // 更新模拟参数
    async updateExistingFactor(id, updateData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await updateFactor(id, updateData)
        if (response.success) {
          // 后端响应格式: { code, message, data: {...} }
          const updatedFactor = response.data?.data || response.data
          
          // 更新列表中的模拟参数
          const index = this.factors.findIndex(f => f.id === id)
          if (index !== -1) {
            this.factors[index] = updatedFactor
          }
          
          // 更新当前模拟参数
          if (this.currentFactor && this.currentFactor.id === id) {
            this.currentFactor = updatedFactor
          }
          
          return updatedFactor
        } else {
          throw new Error(response.message)
        }
      } catch (error) {
        this.error = error.message
        return null
      } finally {
        this.loading = false
      }
    },

    // 删除模拟参数
    async removeFactor(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await deleteFactor(id)
        if (response.success) {
          // 从列表中删除
          this.factors = this.factors.filter(f => f.id !== id)
          
          // 如果当前模拟参数是被删除的模拟参数，清空currentFactor
          if (this.currentFactor?.id === id) {
            this.currentFactor = null
          }
        } else {
          throw new Error(response.message)
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    // 计算模拟参数值
    async calculateFactorValue(factorId, calculationParams = {}) {
      this.loading = true
      this.error = null
      
      try {
        // 直接传递完整参数，不再拆分 factorId
        const response = await calculateFactor(calculationParams)
        if (response.success) {
          // 后端响应格式: { code, message, data: {...} }
          const result = response.data?.data || response.data
          // 添加计算结果记录
          this.calculationResults.unshift(result)
          return result
        } else {
          throw new Error(response.message)
        }
      } catch (error) {
        this.error = error.message
        return null
      } finally {
        this.loading = false
      }
    },

    // 验证模拟参数表达式
    async validateExpression(expression) {
      this.validationResult = null
      
      try {
        const response = await validateFactorExpression(expression)
        // 后端响应格式: { code, message, data: { valid, expression, errors, warnings, suggested_fix } }
        if (response.success) {
          const data = response.data?.data || response.data
          this.validationResult = {
            success: data.valid,
            valid: data.valid,
            errors: data.errors || [],
            warnings: data.warnings || [],
            suggested_fix: data.suggested_fix,
            message: data.valid ? '表达式验证通过' : '表达式验证失败'
          }
        } else {
          this.validationResult = {
            success: false,
            valid: false,
            message: response.message || '验证失败',
            errors: [response.message]
          }
        }
        return this.validationResult
      } catch (error) {
        this.validationResult = {
          success: false,
          valid: false,
          message: '验证服务错误: ' + error.message,
          errors: [error.message]
        }
        return this.validationResult
      }
    },

    // 清除当前模拟参数
    clearCurrentFactor() {
      this.currentFactor = null
    },

    // 清除错误
    clearError() {
      this.error = null
    }
  },

  getters: {
    // 按类别获取模拟参数
    factorsByCategory: (state) => (category) => {
      if (category === 'all') return state.factors
      return state.factors.filter(f => f.category === category)
    },

    // 获取技术指标模拟参数
    technicalFactors: (state) => {
      return state.factors.filter(f => f.category === 'technical')
    },

    // 获取基本面模拟参数
    fundamentalFactors: (state) => {
      return state.factors.filter(f => f.category === 'fundamental')
    },

    // 获取宏观模拟参数
    macroFactors: (state) => {
      return state.factors.filter(f => f.category === 'macro')
    },

    // 获取模拟参数详情
    getFactorById: (state) => (id) => {
      return state.factors.find(f => f.id === id)
    },

    // 获取最新计算结果
    latestCalculation: (state) => {
      return state.calculationResults.length > 0 ? state.calculationResults[0] : null
    }
  }
})