import { createRouter, createWebHistory } from "vue-router";
import DashView from "../views/DashView.vue";
import ListView from "../views/ListView.vue";
import GraphView from "../views/GraphView.vue";
import HistoryView from "../views/HistoryView.vue";
import ProfileView from "../views/ProfileView.vue";
import LogoutView from "../views/LogoutView.vue";
import LoginView from "../views/LoginView.vue";
import AboutView from "../views/AboutView.vue";
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
  // /settings was a live authenticated route rendering the Vue CLI welcome
  // page: it printed the signed-in user's name, email and admin flag as bare
  // <h1>s above links to the vue-cli docs. Nothing in the app linked to it.
  // Removed along with the view and HelloWorld; a real settings screen can
  // reclaim the path.
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
    path: "/about",
    name: "about",
    component: AboutView,
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
