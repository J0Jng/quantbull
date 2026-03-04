<template>
  <div class="niu-model-page">
    <div class="back-home-container">
      <router-link to="/" class="back-home-btn">
        &lt; 返回主页面
      </router-link>
    </div>

    <div class="container">
      <div class="page-nav">
        <h1 class="page-title">脑科学技术研究中心</h1>
      </div>

      <section id="strategy-platform" class="strategy-platform">
        <div class="platform-cards">
          <div class="platform-card orange">
            <h3>模拟参数筛选与分析工具</h3>
            <p>多模拟参数样本筛选、回测实验、数据分析一站式平台</p>
            <router-link to="/quant-analysis">
              <button class="try-btn" style="color:#ff7f00;font-size:14px;border-radius: 100px;">立即体验</button>
            </router-link>
          </div>
          <div class="platform-card blue">
            <h3>回测模型管理工具</h3>
            <p>回测模型管理模块</p>
            <router-link to="/strategies">
              <button class="try-btn" style="color:#1e90ff;font-size:14px;border-radius: 100px;">立即体验</button>
            </router-link>
          </div>
          <div class="platform-card green">
            <h3>模拟参数分析工具</h3>
            <p>实时分析模拟参数，优化配置方案</p>
            <router-link to="/factors">
              <button class="try-btn" style="color:#00b300;font-size:14px;border-radius: 100px;">立即体验</button>
            </router-link>
          </div>
        </div>
      </section>

      <!-- AI智能服务入口（从首页迁移） -->
      <h2 class="section-title">数据分析机器人</h2>
      <section class="ai-service-section">
        <div class="ai-service-cards">
          <!-- 智能新闻解读 -->
          <div class="ai-service-card" @click="openAiModal('news')">
            <div class="ai-icon news-icon">📰</div>
            <h3>快讯文本解读</h3>
            <p>基于输入文本材料生成结构化解读</p>
            <div class="ai-tag">DeepSeek R1</div>
          </div>

          <!-- 回测模型代码生成 -->
          <div class="ai-service-card" @click="openAiModal('strategy')">
            <div class="ai-icon strategy-icon">💡</div>
            <h3>回测模型代码生成</h3>
            <p>数据分析机器人生成Backtrader回测实验模型代码</p>
            <div class="ai-tag">Qwen2.5</div>
          </div>

          <!-- 文本生成摘要 -->
          <div class="ai-service-card" @click="openAiModal('summary')">
            <div class="ai-icon summary-icon">📊</div>
            <h3>文本生成摘要</h3>
            <p>生成结构化研究摘要与分析框架</p>
            <div class="ai-tag">Qwen2.5</div>
          </div>

          <!-- 报告生成 -->
          <div class="ai-service-card" @click="openAiModal('report')">
            <div class="ai-icon report-icon">📈</div>
            <h3>研究报告草稿生成</h3>
            <p>根据输入材料生成结构化报告草稿</p>
            <div class="ai-tag">智能路由</div>
          </div>
        </div>
      </section>

      <!-- AI服务模态框 -->
      <div v-if="showAiModal" class="ai-modal-overlay" @click="hideAiModal">
        <div class="ai-modal-content" @click.stop>
          <div class="ai-modal-header">
            <h3>{{ getAiModalTitle() }}</h3>
            <button class="close-btn" @click="hideAiModal">×</button>
          </div>
          <div class="ai-modal-body">
            <!-- 新闻解读 -->
            <div v-if="activeAiService === 'news'" class="ai-input-section">
              <textarea v-model="newsInput" placeholder="请输入需要解读的信息快讯或文本材料..." rows="4"></textarea>
              <div class="ai-options">
                <label>
                  样本编号：<input v-model="newsStockCode" placeholder="如：000001" type="text">
                </label>
                <button @click="generateNews" class="ai-submit-btn" :disabled="aiLoading">
                  {{ aiLoading ? '生成中...' : '生成解读' }}
                </button>
              </div>
            </div>

            <!-- 回测模型生成 -->
            <div v-if="activeAiService === 'strategy'" class="ai-input-section">
              <textarea v-model="strategyInput" placeholder="请描述您的回测模型实验思路..." rows="4"></textarea>
              <div class="ai-options">
                <label>
                  框架选择：
                  <select v-model="strategyFramework">
                    <option value="backtrader">Backtrader</option>
                    <option value="zipline">Zipline</option>
                  </select>
                </label>
                <button @click="generateStrategy" class="ai-submit-btn" :disabled="aiLoading">
                  {{ aiLoading ? '生成中...' : '生成回测模型' }}
                </button>
              </div>
            </div>

            <!-- 文本生成摘要 -->
            <div v-if="activeAiService === 'summary'" class="ai-input-section">
              <textarea v-model="summaryInput" placeholder="请输入需要摘要的文本材料..." rows="4"></textarea>
              <div class="ai-options">
                <label>
                  摘要类型：
                  <select v-model="summaryType">
                    <option value="structured">结构化</option>
                    <option value="bullet">要点式</option>
                    <option value="paragraph">段落式</option>
                  </select>
                </label>
                <button @click="generateSummary" class="ai-submit-btn" :disabled="aiLoading">
                  {{ aiLoading ? '生成中...' : '生成摘要' }}
                </button>
              </div>
            </div>

            <!-- 研报生成 -->
            <div v-if="activeAiService === 'report'" class="ai-input-section">
              <textarea v-model="reportInput" placeholder="请输入用于生成报告草稿的文本材料..." rows="4"></textarea>
              <div class="ai-options">
                <label>
                  <input type="checkbox" v-model="includeRisks"> 包含风险分析
                </label>
                <button @click="generateReport" class="ai-submit-btn" :disabled="aiLoading">
                  {{ aiLoading ? '生成中...' : '生成报告草稿' }}
                </button>
              </div>
            </div>

            <!-- 结果显示 -->
            <div v-if="aiResult" class="ai-result-section">
              <h4>数据分析机器人生成结果：</h4>
              <div class="ai-disclaimer">{{ AI_DISCLAIMER }}</div>
              <div class="ai-result-content">
                <pre>{{ aiResult }}</pre>
              </div>
              <div class="ai-result-meta">
                <span>使用模型：{{ aiModel }}</span>
                <span>生成时间：{{ new Date().toLocaleTimeString() }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- API状态指示器 -->
      <div class="api-status" :class="apiStatus">
        数据分析机器人服务状态：{{ getApiStatusText() }}
      </div>

      <FooterComponent />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import FooterComponent from '@/components/FooterComponent.vue'
import { generateNewsAnalysis, generateReport as generateReportApi, generateStrategy as generateStrategyApi, generateSummary as generateSummaryApi } from '@/services/aiService'
import chatService from '@/services/chatService'

const AI_DISCLAIMER = '本内容由AI生成，仅供参考，可能存在不准确或遗漏，不代表任何投资建议。请自行核验事实与数据。'

// AI服务相关状态
const showAiModal = ref(false)
const activeAiService = ref('')
const aiResult = ref('')
const aiModel = ref('')
const aiLoading = ref(false)

// 输入数据
const newsInput = ref('')
const newsStockCode = ref('')
const strategyInput = ref('')
const strategyFramework = ref('backtrader')
const summaryInput = ref('')
const summaryType = ref('structured')
const reportInput = ref('')
const includeRisks = ref(true)

// API状态
const apiStatus = ref('checking') // checking, online, offline

// 统一提取 AI 返回数据
const extractPayload = (result) => result?.data?.data || result?.data || {}
const withDisclaimer = (content) => `${AI_DISCLAIMER}\n\n${content || 'AI未返回内容'}`

const openAiModal = (service) => {
  activeAiService.value = service
  showAiModal.value = true
  aiResult.value = ''
}

const hideAiModal = () => {
  showAiModal.value = false
  activeAiService.value = ''
  newsInput.value = ''
  strategyInput.value = ''
  summaryInput.value = ''
  reportInput.value = ''
  aiResult.value = ''
}

const getAiModalTitle = () => {
  const titles = {
    news: '快讯文本解读',
    strategy: '回测模型代码生成',
    summary: '文本生成摘要',
    report: '研究报告草稿生成'
  }
  return titles[activeAiService.value] || '数据分析机器人'
}

const getApiStatusText = () => {
  const statusText = {
    checking: '检查中...',
    online: '服务正常',
    offline: '服务异常'
  }
  return statusText[apiStatus.value] || '未知状态'
}

const generateNews = async () => {
  if (!newsInput.value.trim()) {
    aiResult.value = '请输入新闻内容'
    return
  }

  try {
    aiLoading.value = true
    const result = await generateNewsAnalysis({
      news_flash: newsInput.value,
      stock_code: newsStockCode.value || undefined
    })
    if (result.success) {
      const payload = extractPayload(result)
      const content = payload.news_content || payload.content || '数据分析机器人未返回内容'
      aiResult.value = withDisclaimer(content)
      aiModel.value = payload.model || '未知'
      return
    }
    throw new Error(result.message || '暂无数据')
  } catch (error) {
    aiResult.value = `生成新闻解读失败: ${error.message}`
    aiModel.value = '未知'
  } finally {
    aiLoading.value = false
  }
}

const generateStrategy = async () => {
  if (!strategyInput.value.trim()) {
    aiResult.value = '请输入回测模型描述'
    return
  }

  try {
    aiLoading.value = true
    const result = await generateStrategyApi({
      user_description: strategyInput.value,
      framework: strategyFramework.value
    })
    if (result.success) {
      const payload = extractPayload(result)
      const explanation = payload.explanation || ''
      const code = payload.strategy_code || payload.code || ''
      const content = code && explanation ? `${explanation}\n\n${code}` : (explanation || code || '数据分析机器人未返回内容')
      aiResult.value = withDisclaimer(content)
      aiModel.value = payload.model || '未知'
      return
    }
    throw new Error(result.message || '暂无数据')
  } catch (error) {
    aiResult.value = `生成回测模型失败: ${error.message}`
    aiModel.value = '未知'
  } finally {
    aiLoading.value = false
  }
}

const generateSummary = async () => {
  if (!summaryInput.value.trim()) {
    aiResult.value = '请输入要摘要的内容'
    return
  }

  try {
    aiLoading.value = true
    const result = await generateSummaryApi({
      content: summaryInput.value,
      summary_type: summaryType.value
    })
    if (result.success) {
      const payload = extractPayload(result)
      const content = payload.summary || payload.content || '数据分析机器人未返回内容'
      aiResult.value = withDisclaimer(content)
      aiModel.value = payload.model || '未知'
      return
    }
    throw new Error(result.message || '暂无数据')
  } catch (error) {
    aiResult.value = `生成摘要失败: ${error.message}`
    aiModel.value = '未知'
  } finally {
    aiLoading.value = false
  }
}

const generateReport = async () => {
  if (!reportInput.value.trim()) {
    aiResult.value = '请输入公司信息'
    return
  }

  try {
    aiLoading.value = true
    const result = await generateReportApi({
      company_info: reportInput.value,
      include_risks: includeRisks.value
    })
    if (result.success) {
      const payload = extractPayload(result)
      const content = payload.report_content || payload.content || '数据分析机器人未返回内容'
      aiResult.value = withDisclaimer(content)
      aiModel.value = payload.model || '未知'
      return
    }
    throw new Error(result.message || '暂无数据')
  } catch (error) {
    aiResult.value = `生成报告草稿失败: ${error.message}`
    aiModel.value = '未知'
  } finally {
    aiLoading.value = false
  }
}

const checkApiStatus = async () => {
  apiStatus.value = 'checking'
  try {
    const result = await chatService.checkHealth()
    apiStatus.value = result.success ? 'online' : 'offline'
  } catch {
    apiStatus.value = 'offline'
  }
}

onMounted(() => {
  checkApiStatus()
})
</script>

<style scoped>
.niu-model-page {
  min-height: 100vh;
  background: #fff8f0;
  position: relative;
}

.back-home-container {
  position: absolute;
  top: 20px;
  left: 20px;
  z-index: 100;
}

.back-home-btn {
  display: inline-flex;
  align-items: center;
  padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.9);
  color: #333;
  text-decoration: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
}

.back-home-btn:hover {
  background-color: #fff;
  color: #ff7f24;
  transform: translateY(-1px);
}

.page-nav {
  padding: 80px 0 12px;
}

.page-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 6px;
}

.page-subtitle {
  font-size: 14px;
  color: #666;
}

.ai-disclaimer {
  margin-bottom: 10px;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
  color: #a65300;
  background-color: rgba(255, 127, 0, 0.1);
  border: 1px solid rgba(255, 127, 0, 0.25);
}

@media (max-width: 768px) {
  .page-nav {
    padding-top: 70px;
  }

  .container {
    width: auto;
    padding: 0 12px;
  }

  .platform-cards {
    flex-direction: column;
    gap: 10px;
  }

  .platform-card {
    width: 100%;
  }
}
</style>
