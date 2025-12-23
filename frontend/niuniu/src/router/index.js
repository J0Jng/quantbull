import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/components/HomePage.vue'
import ShopPage from '@/views/ShopPage.vue'
import QuantAnalysisTool from '@/views/QuantAnalysisTool.vue'
import NewsDetailPage from '@/views/NewsDetailPage.vue'
import CompanyResearchPage from '@/views/CompanyResearchPage.vue'
import UserProfile from '@/views/UserProfile.vue'
import FinanceChannelPage from '@/views/FinanceChannelPage.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router