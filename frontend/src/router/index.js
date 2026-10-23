import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getUserInfo } from '@/utils/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/manager/home' },
    {
      path: '/manager',
      name: 'Layout',
      component: () => import('@/Layouts/Layout.vue'),
      children: [
        { path: 'home', name: 'Home', component: () => import('@/views/Home.vue') },
        { path: 'lab', name: 'Lab', meta: { roles: ['admin'] }, component: () => import('@/views/Lab.vue') },
        { path: 'profile', name: 'Profile', component: () => import('@/views/Profile.vue') },
        { path: 'password', name: 'Password', component: () => import('@/views/Password.vue') },
        { path: 'user', name: 'User', meta: { roles: ['admin'] }, component: () => import('@/views/User.vue') },
        { path: 'equipment', name: 'Equipment', meta: { roles: ['admin'] }, component: () => import('@/views/Equipment.vue') },
        { path: 'lablist', name: 'LabList', component: () => import('@/views/LabList.vue') },
        { path: 'lab-equipment', name: 'LabEquipment', component: () => import('@/views/LabEquipment.vue') },
        { path: 'my-reservation', name: 'MyReservation', component: () => import('@/views/MyReservation.vue') },
        { path: 'audit-reservation', name: 'AuditReservation', meta: { roles: ['admin'] }, component: () => import('@/views/AuditReservation.vue') },
        { path: 'ai-chat', name: 'AIChat', component: () => import('@/views/AIChat.vue') }
      ]
    },
    { path: '/login', name: 'Login', component: () => import('@/views/login.vue') },
    { path: '/register', name: 'Register', component: () => import('@/views/Register.vue') }
  ]
})

// 路由守卫：验证 token
router.beforeEach((to, from) => {
  const token = getToken()

  if (to.path === '/login' || to.path === '/register') {
    return true
  }
  if (!token) return '/login'
  if (to.meta.roles && !to.meta.roles.includes(getUserInfo()?.role)) return '/manager/home'
  return true
})

export default router
