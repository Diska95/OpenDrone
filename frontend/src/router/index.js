import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', component: () => import('@/views/Home.vue'), meta: { public: true } },
  { path: '/login', component: () => import('@/views/auth/Login.vue'), meta: { public: true } },
  { path: '/register', component: () => import('@/views/auth/Register.vue'), meta: { public: true } },
  { path: '/projects', component: () => import('@/views/marketplace/ProjectList.vue'), meta: { public: true } },
  { path: '/projects/new', component: () => import('@/views/marketplace/ProjectCreate.vue'), meta: { requiresDesigner: true } },
  { path: '/projects/:slug/edit', component: () => import('@/views/marketplace/ProjectCreate.vue'), meta: { requiresDesigner: true } },
  { path: '/my-projects', component: () => import('@/views/marketplace/MyProjects.vue'), meta: { requiresDesigner: true } },
  { path: '/admin', component: () => import('@/views/admin/AdminDashboard.vue'), meta: { requiresAdmin: true } },
  { path: '/admin/projects', component: () => import('@/views/admin/AdminProjects.vue'), meta: { requiresAdmin: true } },
  { path: '/admin/users', component: () => import('@/views/admin/AdminUsers.vue'), meta: { requiresAdmin: true } },
  { path: '/admin/orders', component: () => import('@/views/admin/AdminOrders.vue'), meta: { requiresAdmin: true } },
  { path: '/projects/:slug', component: () => import('@/views/marketplace/ProjectDetail.vue'), meta: { public: true } },
  { path: '/orders', component: () => import('@/views/orders/OrderList.vue') },
  { path: '/orders/:id', component: () => import('@/views/orders/OrderDetail.vue') },
  { path: '/checkout/:projectSlug', component: () => import('@/views/orders/Checkout.vue') },
  { path: '/dashboard', component: () => import('@/views/dashboard/Dashboard.vue') },
  { path: '/profile', component: () => import('@/views/profile/Profile.vue') },
  // Catch-all: previene schermo nero quando si naviga a una URL non esistente
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.user && auth.accessToken) {
    await auth.fetchMe()
  }
  if (!to.meta.public && !auth.isAuthenticated) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresDesigner && !auth.isDesigner) {
    return { path: '/dashboard' }
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { path: '/dashboard' }
  }
  // Admin viene rediretto da /dashboard a /admin (interfaccia dedicata)
  if (to.path === '/dashboard' && auth.isAdmin) {
    return { path: '/admin' }
  }
})

export default router
