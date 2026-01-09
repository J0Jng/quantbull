// 数字人视频生成服务
class DigitalHumanService {
  constructor() {
    this.baseURL = '/api/ai'
  }

  // 生成数字人视频
  async generateVideo(text, durationLimit = 40, voiceStyle = 'professional') {
    try {
      console.log('开始生成数字人视频:', { text, durationLimit, voiceStyle })
      
      const response = await fetch(`${this.baseURL}/api/ai/digital-human/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          duration_limit: durationLimit,
          voice_style: voiceStyle
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP Error: ${response.status}`)
      }

      const data = await response.json()
      console.log('数字人视频生成响应:', data)
      
      // 验证响应格式
      if (!data.task_id || !data.status) {
        throw new Error('Invalid response format from digital human service')
      }

      return {
        success: true,
        taskId: data.task_id,
        videoUrl: data.video_url,
        estimatedDuration: data.estimated_duration,
        status: data.status
      }
    } catch (error) {
      console.error('Digital Human API Error:', error)
      return {
        success: false,
        error: error.message,
        message: '抱歉，数字人视频生成服务暂时无法响应。请稍后再试。'
      }
    }
  }

  // 检查任务状态
  async checkTaskStatus(taskId) {
    try {
      // 注意：这里需要根据实际API调整，假设有检查状态的接口
      // 目前使用轮询模拟
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      return {
        success: true,
        status: 'completed',
        videoUrl: `/api/ai/api/ai/digital-human/video/${taskId}`
      }
    } catch (error) {
      console.error('Task status check error:', error)
      return { success: false, error: error.message }
    }
  }

  // 生成适合视频口播的金融内容
  generateFinancialContent(prompt) {
    const videoPrompts = {
      market_analysis: '请生成一段适合视频口播的市场分析内容，包含当前市场热点、投资机会和风险提示，语言生动易懂，适合视频表达。',
      investment_advice: '请生成专业投资建议，强调风险提示，避免具体个股推荐，用通俗易懂的语言解释投资逻辑。',
      education: '请生成金融投资教育内容，讲解基础概念或投资方法，语言简洁明了。'
    }

    let selectedPrompt = videoPrompts.market_analysis
    
    if (prompt.includes('建议') || prompt.includes('投资') || prompt.includes('策略')) {
      selectedPrompt = videoPrompts.investment_advice
    } else if (prompt.includes('教育') || prompt.includes('学习') || prompt.includes('基础')) {
      selectedPrompt = videoPrompts.education
    }

    return `${selectedPrompt} 原始问题：${prompt}`
  }

  // 验证文本内容是否符合金融监管要求
  validateFinancialContent(text) {
    const restrictedWords = [
      '保证收益', '稳赚不赔', '绝对赚钱', '100%获利',
      '内幕消息', '独家渠道', '马上买入', '立即投资'
    ]

    const hasRestrictedContent = restrictedWords.some(word => 
      text.toLowerCase().includes(word.toLowerCase())
    )

    return {
      isValid: !hasRestrictedContent,
      issues: hasRestrictedContent ? ['内容包含违规承诺收益表述'] : []
    }
  }
}

// 创建单例实例
const digitalHumanService = new DigitalHumanService()

export default digitalHumanService