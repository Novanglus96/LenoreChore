import { createRouter, createWebHistory } from 'vue-router'
import DashView from '../views/DashView.vue'
import ListView from '../views/ListView.vue'
import GraphView from '../views/GraphView.vue'
import HistoryView from '../views/HistoryView.vue'
import ProfileView from '../views/ProfileView.vue'
import SettingsView from '../views/SettingsView.vue'
import LogoutView from '../views/LogoutView.vue'
import LoginView from '../views/LoginView.vue'

const routes = [
  {
    path: '/',
    name: 'dash',
    component: DashView
  },
  {
    path: '/list',
    name: 'list',
    component: ListView
  },
  {
    path: '/graphs',
    name: 'graphs',
    component: GraphView
  },
  {
    path: '/history',
    name: 'history',
    component: HistoryView
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView
  },
  {
    path: '/logout',
    name: 'logout',
    component: LogoutView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
