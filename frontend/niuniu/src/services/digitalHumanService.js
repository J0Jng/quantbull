import http from './http'

// 数字人视频生成服务
class DigitalHumanService {
  // 生成数字人视频
  async generateVideo(text, durationLimit = 40, voiceStyle = 'professional') {
    try {
      console.log('开始生成数字人视频:', { text, durationLimit, voiceStyle })
      
      const response = await http.post('/ai/digital-human/generate', {
        text,
        duration_limit: durationLimit,
        voice_style: voiceStyle
      })

      const data = response?.data ?? response
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
      const response = await http.get(`/ai/digital-human/status/${taskId}`)
      const data = response?.data ?? response
      
      return {
        success: true,
        status: data.status || 'completed',
        videoUrl: data.video_url || `/api/ai/digital-human/video/${taskId}`
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
      investment_advice: '请生成专业操作指引，强调风险提示，避免具体个股推荐，用通俗易懂的语言解释投资逻辑。',
      education: '请生成金融投资教育内容，讲解基础概念或投资方法，语言简洁明了。'
    }

    let selectedPrompt = videoPrompts.market_analysis
    
    if (prompt.includes('建议') || prompt.includes('投资') || prompt.includes('回测模型')) {
      selectedPrompt = videoPrompts.investment_advice
    } else if (prompt.includes('教育') || prompt.includes('学习') || prompt.includes('基础')) {
      selectedPrompt = videoPrompts.education
    }

    return `${selectedPrompt} 原始问题：${prompt}`
  }

  // 验证文本内容是否符合金融监管要求
  validateFinancialContent(text) {
    const restrictedWords = [
      '保证收益', '稳赚不赔', '绝对赚钱', '100%模拟数据波动验证',
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