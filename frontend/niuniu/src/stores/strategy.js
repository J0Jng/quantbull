import { defineStore } from 'pinia'
import { 
  getStrategies, 
  getStrategy, 
  createStrategy, 
  updateStrategy, 
  deleteStrategy,
  validateStrategyCode,
  getStrategyBacktests,
  runBacktest,
  generateStrategyTemplate
} from '@/services/strategyService'

export const useStrategyStore = defineStore('strategy', {
  state: () => ({
    strategies: [],
    currentStrategy: null,
    backtests: [],
    loading: false,
    error: null,
    validationResult: null
  }),

  actions: {
    // 获取回测模型列表
    async fetchStrategies(params = {}) {
      this.loading = true
      this.error = null
      
      try {
        const response = await getStrategies(params)
        if (response.success) {
          this.strategies = response.data
        } else {
          throw new Error(response.message)
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    // 获取回测模型详情
    async fetchStrategy(id) {
      this.loading = true
      this.error = null
      this.currentStrategy = null
      
      try {
        const response = await getStrategy(id)
        if (response.success) {
          this.currentStrategy = response.data
        } else {
          throw new Error(response.message)
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    // 创建回测模型
    async createNewStrategy(strategyData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await createStrategy(strategyData)
        if (response.success) {
          this.strategies.unshift(response.data)
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

    // 更新回测模型
    async updateExistingStrategy(id, updateData) {
      this.loading = true
      this.error = null
      
      try {
        const response = await updateStrategy(id, updateData)
        if (response.success) {
          // 更新列表中的回测模型
          const index = this.strategies.findIndex(s => s.id === id)
          if (index !== -1) {
            this.strategies[index] = response.data
          }
          
          // 更新当前回测模型
          if (this.currentStrategy && this.currentStrategy.id === id) {
            this.currentStrategy = response.data
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

    // 删除回测模型
    async removeStrategy(id) {
      this.loading = true
      this.error = null
      
      try {
        const response = await deleteStrategy(id)
        if (response.success) {
          // 从列表中删除
          this.strategies = this.strategies.filter(s => s.id !== id)
          
          // 如果当前回测模型是被删除的回测模型，清空currentStrategy
          if (this.currentStrategy?.id === id) {
            this.currentStrategy = null
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

    // 验证回测模型代码
    async validateCode(code) {
      this.validationResult = null
      
      try {
        const response = await validateStrategyCode(code)
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

    // 获取回测模型回测历史
    async fetchBacktests(strategyId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await getStrategyBacktests(strategyId)
        if (response.success) {
          this.backtests = response.data
        } else {
          throw new Error(response.message)
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },

    // 运行回测
    async runStrategyBacktest(strategyId, backtestParams) {
      this.loading = true
      this.error = null
      
      try {
        const response = await runBacktest(strategyId, backtestParams)
        if (response.success) {
          // 添加回测记录
          this.backtests.unshift(response.data)
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

    // 生成回测模型模板
    async generateTemplate(templateType) {
      this.loading = true
      this.error = null
      
      try {
        const response = await generateStrategyTemplate(templateType)
        if (response.success) {
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

    // 清除当前回测模型
    clearCurrentStrategy() {
      this.currentStrategy = null
    },

    // 清除错误
    clearError() {
      this.error = null
    }
  },

  getters: {
    // 获取活跃回测模型
    activeStrategies: (state) => {
      return state.strategies.filter(s => s.status === 'active')
    },

    // 获取非活跃回测模型
    inactiveStrategies: (state) => {
      return state.strategies.filter(s => s.status === 'inactive')
    },

    // 获取回测模型详情
    getStrategyById: (state) => (id) => {
      return state.strategies.find(s => s.id === id)
    },

    // 获取最新回测结果
    latestBacktest: (state) => {
      return state.backtests.length > 0 ? state.backtests[0] : null
    }
  }
})