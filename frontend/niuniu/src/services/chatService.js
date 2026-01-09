// AI聊天API服务
class ChatService {
  constructor() {
    this.baseURL = '/api/ai'
  }

  // 发送聊天消息
  async sendChat(message, systemPrompt = null, model = null, temperature = 0.7, maxTokens = 1000) {
    try {
      const response = await fetch(`${this.baseURL}/api/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          system_prompt: systemPrompt,
          model,
          temperature,
          max_tokens: maxTokens
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`)
      }

      const data = await response.json()
      
      // 验证响应格式
      if (!data.content || !data.model) {
        throw new Error('Invalid response format from AI service')
      }

      return {
        success: true,
        content: data.content,
        model: data.model,
        tokensUsed: data.tokens_used || null,
        finishReason: data.finish_reason || null
      }
    } catch (error) {
      console.error('Chat API Error:', error)
      return {
        success: false,
        error: error.message,
        content: '抱歉，AI服务暂时无法响应。请检查网络连接或稍后再试。'
      }
    }
  }

  // 检查API健康状况
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseURL}/health`)
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`)
      }
      return { success: true, status: 'online' }
    } catch (error) {
      console.error('Health check error:', error)
      return { success: false, status: 'offline', error: error.message }
    }
  }

  // 模型路由推荐
  async getRecommendedModel(taskType, message) {
    try {
      const response = await fetch(`${this.baseURL}/api/ai/model/route`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_type: taskType,
          message
        })
      })

      if (!response.ok) {
        throw new Error(`Model routing error: ${response.status}`)
      }

      const data = await response.json()
      return {
        success: true,
        recommendedModel: data.recommended_model,
        reason: data.reason
      }
    } catch (error) {
      console.error('Model routing error:', error)
      return { success: false, error: error.message }
    }
  }

  // 生成投资策略代码
  async generateStrategy(description, includeRiskControl = true) {
    try {
      const response = await fetch(`${this.baseURL}/api/ai/generate/strategy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_description: description,
          include_risk_control: includeRiskControl,
          framework: 'backtrader'
        })
      })

      if (!response.ok) {
        throw new Error(`Strategy generation error: ${response.status}`)
      }

      const data = await response.json()
      return {
        success: true,
        strategyCode: data.strategy_code,
        explanation: data.explanation,
        model: data.model
      }
    } catch (error) {
      console.error('Strategy generation error:', error)
      return { success: false, error: error.message }
    }
  }

  // 新闻解读生成
  async generateNewsAnalysis(newsFlash, stockCode = null) {
    try {
      const response = await fetch(`${this.baseURL}/api/ai/generate/news`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          news_flash: newsFlash,
          stock_code: stockCode,
          target_length: 300
        })
      })

      if (!response.ok) {
        throw new Error(`News generation error: ${response.status}`)
      }

      const data = await response.json()
      return {
        success: true,
        newsContent: data.news_content,
        model: data.model,
        wordCount: data.word_count
      }
    } catch (error) {
      console.error('News generation error:', error)
      return { success: false, error: error.message }
    }
  }
}

// 创建单例实例
const chatService = new ChatService()

export default chatService