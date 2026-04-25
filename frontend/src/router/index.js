import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../components/HomePage.vue'
import SearchPage from '../components/SearchPage.vue'
import RankPage from '../components/RankPage.vue'
import HotBooksPage from '../components/HotBooksPage.vue'
import BookDetail from '../components/BookDetail.vue'
import UserProfile from '../components/UserProfile.vue'
import Bookshelf from '../components/Bookshelf.vue'
import AdminLogin from '../components/AdminLogin.vue'
import AdminPanel from '../components/AdminPanel.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HotBooksPage
  },
  {
    path: '/search',
    name: 'search',
    component: SearchPage
  },
  {
    path: '/rank',
    name: 'rank',
    component: RankPage
  },
  {
    path: '/smart',
    name: 'smart',
    component: HomePage
  },
  {
    path: '/hot',
    name: 'hot',
    component: HotBooksPage
  },
  {
    path: '/:bookId',
    name: 'bookDetail',
    component: BookDetail,
    props: true
  },
  {
    path: '/profile',
    name: 'profile',
    component: UserProfile
  },
  {
    path: '/bookshelf',
    name: 'bookshelf',
    component: Bookshelf
  },
  {
    path: '/admin/login',
    name: 'adminLogin',
    component: AdminLogin
  },
  {
    path: '/admin/panel',
    name: 'adminPanel',
    component: AdminPanel
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
