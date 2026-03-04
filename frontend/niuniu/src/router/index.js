import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated, getCurrentUser } from '@/services/authService'
import HomePage from '@/components/HomePage.vue'
import QuantAnalysisTool from '@/views/QuantAnalysisTool.vue'
import BacktestDetailPage from '@/views/BacktestDetailPage.vue'
import NewsDetailPage from '@/views/NewsDetailPage.vue'
import CompanyResearchPage from '@/views/CompanyResearchPage.vue'
import CompanyResearchDetail from '@/views/CompanyResearchDetail.vue'
import ResearchDetailPage from '@/views/ResearchDetailPage.vue'
import UserProfile from '@/views/UserProfile.vue'
import FinanceChannelPage from '@/views/FinanceChannelPage.vue'
import DailyInsightPage from '@/views/DailyInsightPage.vue'
import StockDataPage from '@/views/StockDataPage.vue'
import FundSourcePage from '@/views/FundSourcePage.vue'
import FinancialReportPage from '@/views/FinancialReportPage.vue'
import DragonTigerListPage from '@/views/DragonTigerListPage.vue'
import ProfitForecastPage from '@/views/ProfitForecastPage.vue'
import AboutPage from '@/views/AboutPage.vue'
import ContactPage from '@/views/ContactPage.vue'
import JoinPage from '@/views/JoinPage.vue'
import PartnersPage from '@/views/PartnersPage.vue'
import StrategyListPage from '@/views/StrategyListPage.vue'
import StrategyCreatePage from '@/views/StrategyCreatePage.vue'
import StrategyDetailPage from '@/views/StrategyDetailPage.vue'
import StrategyEditPage from '@/views/StrategyEditPage.vue'
import AdminUsersPage from '@/views/AdminUsersPage.vue'
import NiuModelPage from '@/views/NiuModelPage.vue'
import ComplianceNoticePage from '@/views/ComplianceNoticePage.vue'
import DisclaimerPage from '@/views/DisclaimerPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/home'
  },
  {
    path: '/disclaimer',
    name: 'Disclaimer',
    component: DisclaimerPage,
    meta: { title: '网站申明' }
  },
  {
    path: '/home',
    name: 'MainHome',
    component: HomePage,
    meta: { title: '首页' }
  },
  {
    path: '/shop',
    name: 'Shop',
    component: ComplianceNoticePage,
    meta: { title: '脑科学研究室' }
  },
  {
    path: '/shop/cart',
    name: 'Cart',
    redirect: '/shop',
    meta: { title: '脑科学研究室' }
  },
  {
    path: '/shop/orders',
    name: 'Orders',
    redirect: '/shop',
    meta: { title: '脑科学研究室' }
  },
  {
    path: '/about',
    name: 'About',
    component: AboutPage,
    meta: { title: '关于我们' }
  },
  {
    path: '/contact',
    name: 'Contact',
    component: ContactPage,
    meta: { title: '联系我们' }
  },
  {
    path: '/join',
    name: 'Join',
    component: JoinPage,
    meta: { title: '加入我们' }
  },
  {
    path: '/partners',
    name: 'Partners',
    component: PartnersPage,
    meta: { title: '战略合作单位' }
  },
  {
    path: '/quant-analysis',
    name: 'QuantAnalysis',
    component: QuantAnalysisTool
  },
  {
    path: '/niu-model',
    name: 'NiuModel',
    component: NiuModelPage,
    meta: { title: '脑科学技术研究中心' }
  },
  {
    path: '/backtests/:id',
    name: 'BacktestDetail',
    component: BacktestDetailPage,
    props: true,
    meta: { title: '回测详情' }
  },
  {
    path: '/news-detail/:id',
    name: 'NewsDetail',
    component: NewsDetailPage,
    props: true
  },
  {
    path: '/company-research',
    name: 'CompanyResearch',
    component: CompanyResearchPage
  },
  {
    path: '/company-research/:id',
    name: 'CompanyResearchDetail',
    component: CompanyResearchDetail,
    props: true
  },
  {
    path: '/company-research/research-detail/:id',
    name: 'ResearchDetail',
    component: ResearchDetailPage
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: UserProfile
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: AdminUsersPage,
    meta: { title: '用户管理' }
  },
  {
    path: '/finance-channel',
    name: 'FinanceChannel',
    component: FinanceChannelPage,
    meta: { title: '宏微观数据' }
  },
  {
    path: '/daily-insight',
    name: 'DailyInsight',
    component: DailyInsightPage,
    meta: { title: '每日数据模拟分析' }
  },
  {
    path: '/stock-data',
    name: 'StockData',
    component: StockDataPage
  },
  {
    path: '/fund-source',
    name: 'FundSource',
    component: FundSourcePage
  },
  {
    path: '/financial-report',
    name: 'FinancialReport',
    component: FinancialReportPage,
    meta: { title: '财报' }
  },
  {
    path: '/dragon-tiger-list',
    name: 'DragonTigerList',
    component: DragonTigerListPage,
    meta: { title: '龙虎榜' }
  },
  {
    path: '/profit-forecast',
    name: 'ProfitForecast',
    component: ProfitForecastPage,
    meta: { title: '盈利预测' }
  },
  {
    path: '/shop/goods-detail/:id',
    name: 'GoodsDetail',
    redirect: '/shop',
    props: true,
    meta: { title: '脑科学研究室' }
  },
  // 回测模型管理路由
  {
    path: '/strategies',
    name: 'StrategyList',
    component: StrategyListPage,
    meta: { title: '回测模型管理' }
  },
  {
    path: '/strategies/create',
    name: 'StrategyCreate',
    component: StrategyCreatePage,
    meta: { title: '创建回测模型' }
  },
  {
    path: '/strategies/:id',
    name: 'StrategyDetail',
    component: StrategyDetailPage,
    props: true,
    meta: { title: '回测模型详情' }
  },
  {
    path: '/strategies/:id/edit',
    name: 'StrategyEdit',
    component: StrategyEditPage,
    props: true,
    meta: { title: '编辑回测模型' }
  },
  // 模拟参数管理路由
  {
    path: '/factors',
    name: 'FactorList',
    component: () => import('@/views/FactorListPage.vue'),
    meta: { title: '模拟参数管理' }
  },
  {
    path: '/factors/create',
    name: 'FactorCreate',
    component: () => import('@/views/FactorCreatePage.vue'),
    meta: { title: '创建模拟参数' }
  },
  {
    path: '/factors/:id',
    name: 'FactorDetail',
    component: () => import('@/views/FactorDetailPage.vue'),
    props: true,
    meta: { title: '模拟参数详情' }
  },
  {
    path: '/factors/:id/edit',
    name: 'FactorEdit',
    component: () => import('@/views/FactorEditPage.vue'),
    props: true,
    meta: { title: '编辑模拟参数' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 设置页面标题 + 鉴权守卫
router.beforeEach(async (to, from, next) => {
  const title = to.meta.title || '脑科学研究室'
  document.title = `${title} - 深脑纪元·数据模拟实验室`
  
  // 检查是否已同意网站申明
  const hasAgreedDisclaimer = localStorage.getItem('disclaimer_agreed') === 'true'
  if (!hasAgreedDisclaimer && to.path !== '/disclaimer') {
    next('/disclaimer')
    return
  }

  // 白名单路由（不需要登录）
  const publicRoutes = ['/', '/disclaimer', '/Home', '/home', '/about', '/contact', '/shop']
  const isPublic = publicRoutes.includes(to.path) || to.name === 'Home' || to.name === 'Disclaimer'

  // 如果不是公开页面且未登录，触发登录弹窗并阻止导航
  if (!isPublic && !isAuthenticated()) {
    const result = await getCurrentUser()
    if (result.success) {
      localStorage.setItem('session_active', 'true')
      next()
      return
    }
    // 触发全局登录弹窗事件
    window.dispatchEvent(new CustomEvent('auth:required'))
    // 重定向到首页
    next('/')
    return
  }
  
  next()
})

export default router