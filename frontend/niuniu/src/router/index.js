import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated, getCurrentUser } from '@/services/authService'
import HomePage from '@/components/HomePage.vue'
import ShopPage from '@/views/ShopPage.vue'
import QuantAnalysisTool from '@/views/QuantAnalysisTool.vue'
import BacktestDetailPage from '@/views/BacktestDetailPage.vue'
import NewsDetailPage from '@/views/NewsDetailPage.vue'
import CompanyResearchPage from '@/views/CompanyResearchPage.vue'
import CompanyResearchDetail from '@/views/CompanyResearchDetail.vue'
import ResearchDetailPage from '@/views/ResearchDetailPage.vue'
import UserProfile from '@/views/UserProfile.vue'
import FinanceChannelPage from '@/views/FinanceChannelPage.vue'
import DailyInsightPage from '@/views/DailyInsightPage.vue'
import FundRankingPage from '@/views/FundRankingPage.vue'
import StockDataPage from '@/views/StockDataPage.vue'
import GoodsDetail from '@/views/GoodsDetail.vue'
import CartPage from '@/views/CartPage.vue'
import OrderPage from '@/views/OrderPage.vue'
import AboutPage from '@/views/AboutPage.vue'
import ContactPage from '@/views/ContactPage.vue'
import NewsListPage from '@/views/NewsListPage.vue'
import StrategyListPage from '@/views/StrategyListPage.vue'
import StrategyCreatePage from '@/views/StrategyCreatePage.vue'
import StrategyDetailPage from '@/views/StrategyDetailPage.vue'
import StrategyEditPage from '@/views/StrategyEditPage.vue'
import AdminUsersPage from '@/views/AdminUsersPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/shop',
    name: 'Shop',
    component: ShopPage
  },
  {
    path: '/shop/cart',
    name: 'Cart',
    component: CartPage
  },
  {
    path: '/shop/orders',
    name: 'Orders',
    component: OrderPage
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
    path: '/quant-analysis',
    name: 'QuantAnalysis',
    component: QuantAnalysisTool
  },
  {
    path: '/backtests/:id',
    name: 'BacktestDetail',
    component: BacktestDetailPage,
    props: true,
    meta: { title: '回测详情' }
  },
  {
    path: '/news-list',
    name: 'NewsList',
    component: NewsListPage
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
    component: FinanceChannelPage
  },
  {
    path: '/daily-insight',
    name: 'DailyInsight',
    component: DailyInsightPage
  },
  {
    path: '/fund-ranking',
    name: 'FundRanking',
    component: FundRankingPage
  },
  {
    path: '/stock-data',
    name: 'StockData',
    component: StockDataPage
  },
  {
    path: '/shop/goods-detail/:id',
    name: 'GoodsDetail',
    component: GoodsDetail,
    props: true
  },
  // 策略管理路由
  {
    path: '/strategies',
    name: 'StrategyList',
    component: StrategyListPage,
    meta: { title: '策略管理' }
  },
  {
    path: '/strategies/create',
    name: 'StrategyCreate',
    component: StrategyCreatePage,
    meta: { title: '创建策略' }
  },
  {
    path: '/strategies/:id',
    name: 'StrategyDetail',
    component: StrategyDetailPage,
    props: true,
    meta: { title: '策略详情' }
  },
  {
    path: '/strategies/:id/edit',
    name: 'StrategyEdit',
    component: StrategyEditPage,
    props: true,
    meta: { title: '编辑策略' }
  },
  // 因子管理路由
  {
    path: '/factors',
    name: 'FactorList',
    component: () => import('@/views/FactorListPage.vue'),
    meta: { title: '因子管理' }
  },
  {
    path: '/factors/create',
    name: 'FactorCreate',
    component: () => import('@/views/FactorCreatePage.vue'),
    meta: { title: '创建因子' }
  },
  {
    path: '/factors/:id',
    name: 'FactorDetail',
    component: () => import('@/views/FactorDetailPage.vue'),
    props: true,
    meta: { title: '因子详情' }
  },
  {
    path: '/factors/:id/edit',
    name: 'FactorEdit',
    component: () => import('@/views/FactorEditPage.vue'),
    props: true,
    meta: { title: '编辑因子' }
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
  const title = to.meta.title || '量化牛牛'
  document.title = `${title} - 量化牛牛`
  
  // 白名单路由（不需要登录）
  const publicRoutes = ['/', '/Home', '/about', '/contact']
  const isPublic = publicRoutes.includes(to.path) || to.name === 'Home'
  
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