import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/components/HomePage.vue'
import ShopPage from '@/views/ShopPage.vue'
import QuantAnalysisTool from '@/views/QuantAnalysisTool.vue'
import NewsDetailPage from '@/views/NewsDetailPage.vue'
import CompanyResearchPage from '@/views/CompanyResearchPage.vue'
import UserProfile from '@/views/UserProfile.vue'
import FinanceChannelPage from '@/views/FinanceChannelPage.vue'
import DailyInsightPage from '@/views/DailyInsightPage.vue'
import FundRankingPage from '@/views/FundRankingPage.vue'
import StockDataPage from '@/views/StockDataPage.vue'
import GoodsDetail from '@/views/GoodsDetail.vue'
import CartPage from '@/views/CartPage.vue'
import OrderPage from '@/views/OrderPage.vue'

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
    path: '/news-detail',
    name: 'NewsDetail',
    component: NewsDetailPage
  },
  {
    path: '/company-research',
    name: 'CompanyResearch',
    component: CompanyResearchPage
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
    path: '/goods-detail',
    name: 'GoodsDetail',
    component: GoodsDetail
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router