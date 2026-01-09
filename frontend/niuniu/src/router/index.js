import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/components/HomePage.vue'
import ShopPage from '@/views/ShopPage.vue'
import QuantAnalysisTool from '@/views/QuantAnalysisTool.vue'
import NewsDetailPage from '@/views/NewsDetailPage.vue'
import CompanyResearchPage from '@/views/CompanyResearchPage.vue'
import ResearchDetailPage from '@/views/ResearchDetailPage.vue'
import UserProfile from '@/views/UserProfile.vue'
import FinanceChannelPage from '@/views/FinanceChannelPage.vue'
import DailyInsightPage from '@/views/DailyInsightPage.vue'
import FundRankingPage from '@/views/FundRankingPage.vue'
import StockDataPage from '@/views/StockDataPage.vue'
import GoodsDetail from '@/views/GoodsDetail.vue'
import CartPage from '@/views/CartPage.vue'
import OrderPage from '@/views/OrderPage.vue'
import NewsListPage from '@/views/NewsListPage.vue'
import StrategyListPage from '@/views/StrategyListPage.vue'
import StrategyCreatePage from '@/views/StrategyCreatePage.vue'
import StrategyDetailPage from '@/views/StrategyDetailPage.vue'
import StrategyEditPage from '@/views/StrategyEditPage.vue'

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
    path: '/quant-analysis',
    name: 'QuantAnalysis',
    component: QuantAnalysisTool
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

// 设置页面标题
router.beforeEach((to, from, next) => {
  const title = to.meta.title || '量化牛牛'
  document.title = `${title} - 量化牛牛`
  next()
})

export default router