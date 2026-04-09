import { createRouter, createWebHistory } from "vue-router";
import DashView from "../views/DashView.vue";
import ListView from "../views/ListView.vue";
import GraphView from "../views/GraphView.vue";
import HistoryView from "../views/HistoryView.vue";
import ProfileView from "../views/ProfileView.vue";
import SettingsView from "../views/SettingsView.vue";
import LogoutView from "../views/LogoutView.vue";
import LoginView from "../views/LoginView.vue";
import FourView from "../views/FourView.vue";
import { useUserStore } from "@/stores/user";

const routes = [
  {
    path: "/",
    name: "dash",
    component: DashView,
    meta: { requiresAuth: true },
  },
  {
    path: "/list",
    name: "list",
    component: ListView,
    meta: { requiresAuth: true },
  },
  {
    path: "/graphs",
    name: "graphs",
    component: GraphView,
    meta: { requiresAuth: true },
  },
  {
    path: "/history",
    name: "history",
    component: HistoryView,
    meta: { requiresAuth: true },
  },
  {
    path: "/settings",
    name: "settings",
    component: SettingsView,
    meta: { requiresAuth: true },
  },
  {
    path: "/profile",
    name: "profile",
    component: ProfileView,
    meta: { requiresAuth: true },
  },
  {
    path: "/logout",
    name: "logout",
    component: LogoutView,
    meta: { requiresAuth: true },
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  {
    path: "/:catchAll(.*)",
    component: FourView,
    name: "NotFound",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Global navigation guard
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    const userstore = useUserStore();
    if (!userstore.isLoggedIn) {
      next("/login");
    } else {
      next();
    }
  } else {
    next();
  }
});

// Add a global beforeEach guard
router.beforeEach((to, from, next) => {
  const isPageReload = sessionStorage.getItem("isPageReload");
  sessionStorage.removeItem("isPageReload");

  if (isPageReload && to.fullPath !== "/") {
    next("/");
  } else {
    next();
  }
});

// Set a flag to detect page reload
window.addEventListener("beforeunload", () => {
  sessionStorage.setItem("isPageReload", "true");
});

export default router;
