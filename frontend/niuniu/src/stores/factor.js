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
    currentFactor: null,
    calculationResults: [],
    loading: false,
    error: null,
    validationResult: null
  }),

  actions: {
    // 获取因子列表
    async fetchFactors(params = {}) {
      this.loading = true
      this.error = null
      
      try {
        const response = await getFactors(params)
        if (response.success) {
          this.factors = response.data
        } else {
          throw new Error(response.message)
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    // 获取因子详情
    async fetchFactor(id) {
      this.loading = true
      this.error = null
      this.currentFactor = null
      
      try {
        const response = await getFactor(id)
        if (response.success) {
          this.currentFactor = response.data
        } else {
          throw new Error(response.message)
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    // 创建因子
    async createNewFactor(factorData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await createFactor(factorData)
        if (response.success) {
          this.factors.unshift(response.data)
          return response.data
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

    // 更新因子
    async updateExistingFactor(id, updateData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await updateFactor(id, updateData)
        if (response.success) {
          // 更新列表中的因子
          const index = this.factors.findIndex(f => f.id === id)
          if (index !== -1) {
            this.factors[index] = response.data
          }
          
          // 更新当前因子
          if (this.currentFactor && this.currentFactor.id === id) {
            this.currentFactor = response.data
          }
          
          return response.data
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

    // 删除因子
    async removeFactor(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await deleteFactor(id)
        if (response.success) {
          // 从列表中删除
          this.factors = this.factors.filter(f => f.id !== id)
          
          // 如果当前因子是被删除的因子，清空currentFactor
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

    // 计算因子值
    async calculateFactorValue(factorId, calculationParams = {}) {
      this.loading = true
      this.error = null
      
      try {
        const response = await calculateFactor(factorId, calculationParams)
        if (response.success) {
          // 添加计算结果记录
          this.calculationResults.unshift(response.data)
          return response.data
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

    // 验证因子表达式
    async validateExpression(expression) {
      this.validationResult = null
      
      try {
        const response = await validateFactorExpression(expression)
        this.validationResult = response
        return response
      } catch (error) {
        this.validationResult = {
          success: false,
          message: '验证服务错误: ' + error.message
        }
        return this.validationResult
      }
    },

    // 清除当前因子
    clearCurrentFactor() {
      this.currentFactor = null
    },

    // 清除错误
    clearError() {
      this.error = null
    }
  },

  getters: {
    // 按类别获取因子
    factorsByCategory: (state) => (category) => {
      if (category === 'all') return state.factors
      return state.factors.filter(f => f.category === category)
    },

    // 获取技术指标因子
    technicalFactors: (state) => {
      return state.factors.filter(f => f.category === 'technical')
    },

    // 获取基本面因子
    fundamentalFactors: (state) => {
      return state.factors.filter(f => f.category === 'fundamental')
    },

    // 获取宏观因子
    macroFactors: (state) => {
      return state.factors.filter(f => f.category === 'macro')
    },

    // 获取因子详情
    getFactorById: (state) => (id) => {
      return state.factors.find(f => f.id === id)
    },

    // 获取最新计算结果
    latestCalculation: (state) => {
      return state.calculationResults.length > 0 ? state.calculationResults[0] : null
    }
  }
})