import { createRouter, createWebHistory } from 'vue-router'
import DashView from '../views/DashView.vue'
import ListView from '../views/ListView.vue'
import GraphView from '../views/GraphView.vue'
import HistoryView from '../views/HistoryView.vue'
import ProfileView from '../views/ProfileView.vue'
import SettingsView from '../views/SettingsView.vue'
import LogoutView from '../views/LogoutView.vue'
import LoginView from '../views/LoginView.vue'
import FourView from '../views/FourView.vue'

const routes = [
  {
    path: '/',
    name: 'dash',
    component: DashView,
    meta: { requiresAuth: true },
  },
  {
    path: '/list',
    name: 'list',
    component: ListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/graphs',
    name: 'graphs',
    component: GraphView,
    meta: { requiresAuth: true },
  },
  {
    path: '/history',
    name: 'history',
    component: HistoryView,
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView,
    meta: { requiresAuth: true },
  },
  {
    path: '/logout',
    name: 'logout',
    component: LogoutView,
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  { 
    path: '/:catchAll(.*)', 
    component: FourView,
    name: 'NotFound'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Global navigation guard
router.beforeEach((to, from, next) => {
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    // Check if the user is authenticated (e.g., by checking the presence of a token)
    const isAuthenticated = localStorage.getItem('authToken');

    if (!isAuthenticated) {
      // Redirect to the login page if not authenticated
      next('/login');
    } else {
      // Continue to the requested route if authenticated
      next();
    }
  } else {
    // No authentication required, continue to the requested route
    next();
  }
});

export default router
