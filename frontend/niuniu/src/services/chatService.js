import http from './http'

// AI聊天API服务
class ChatService {
  // 发送聊天消息
  async sendChat(message, systemPrompt = null, model = null, temperature = 0.7, maxTokens = 1000) {
    try {
      const response = await http.post('/ai/chat', {
        message,
        system_prompt: systemPrompt,
        model,
        temperature,
        max_tokens: maxTokens
      })

      const raw = response
      const payload = raw?.data ?? raw
      const content = payload?.content ?? payload?.message ?? payload?.answer ?? null
      const modelName = payload?.model ?? payload?.used_model ?? null
      if (!content) {
        throw new Error('Invalid response format from AI service')
      }

      return {
        success: true,
        content,
        model: modelName || 'unknown',
        tokensUsed: payload?.tokens_used ?? payload?.usage ?? null,
        finishReason: payload?.finish_reason ?? null
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
      await http.get('/ai/health')
      return { success: true, status: 'online' }
    } catch (error) {
      console.error('Health check error:', error)
      return { success: false, status: 'offline', error: error.message }
    }
  }

  // 模型路由推荐
  async getRecommendedModel(taskType, message) {
    try {
      const response = await http.post('/ai/model/route', {
        task_type: taskType,
        message
      })

      const data = response?.data ?? response
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

  // 生成投资回测模型代码
  async generateStrategy(description, includeRiskControl = true) {
    try {
      const response = await http.post('/ai/generate/strategy', {
        user_description: description,
        include_risk_control: includeRiskControl,
        framework: 'backtrader'
      })

      const data = response?.data ?? response
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
      const response = await http.post('/ai/generate/news', {
        news_flash: newsFlash,
        stock_code: stockCode,
        target_length: 300
      })

      const data = response?.data ?? response
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