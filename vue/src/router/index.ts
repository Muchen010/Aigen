import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import { authStore } from '../store/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../views/Chat.vue'),
      meta: {
        requiresAuth: true
      }
    }
  ]
})

// 路由守卫，检查是否需要登录
router.beforeEach((to, from, next) => {
  console.log('路由守卫触发，当前路径:', from.path, '目标路径:', to.path);
  console.log('目标路径需要认证:', to.matched.some(record => record.meta.requiresAuth));
  console.log('当前登录状态:', authStore.getIsLoggedIn());
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查用户是否已登录
    if (authStore.getIsLoggedIn()) {
      console.log('用户已登录，允许访问');
      next()
    } else {
      // 未登录，重定向到登录页
      console.log('用户未登录，重定向到登录页');
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    }
  } else {
    console.log('目标路径不需要认证，允许访问');
    next()
  }
})

export default router
