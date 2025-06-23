//src/router/index.js
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("../views/HomePage.vue"),
    },
    {
      path: "/faq",
      name: "faq",
      component: () => import("../views/FaqPage.vue"),
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/LoginPage.vue"),
    },
    {
      path: "/logout",
      name: "logout",
      component: () => import("../views/LogoutPage.vue"),
    },
    {
      path: '/createtournament',
      name: 'CreateTournament',
      component: () => import('../components/CreateTournament.vue'),
      meta: { requiresAuth: true },
    }
  ],
});
export default router;
