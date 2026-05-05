import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => !!accessToken.value)
  const isDesigner = computed(() => user.value?.roles?.includes('designer'))
  const isPrintNode = computed(() => user.value?.roles?.includes('print_node'))
  const isAssemblyCenter = computed(() => user.value?.roles?.includes('assembly_center'))
  const isAdmin = computed(() => user.value?.roles?.includes('admin') || user.value?.is_staff)

  async function login(email, password) {
    const { data } = await authApi.login(email, password)
    user.value = data.user
    accessToken.value = data.access
    refreshToken.value = data.refresh
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    return data.user
  }

  async function register(formData) {
    const { data } = await authApi.register(formData)
    user.value = data.user
    accessToken.value = data.access
    refreshToken.value = data.refresh
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    return data.user
  }

  async function loginWithGoogle({ credential, role }) {
    const { data } = await authApi.googleAuth({ credential, role })
    user.value = data.user
    accessToken.value = data.access
    refreshToken.value = data.refresh
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    return { user: data.user, created: data.created }
  }

  async function logout() {
    if (refreshToken.value) {
      try { await authApi.logout(refreshToken.value) } catch {}
    }
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function fetchMe() {
    if (!accessToken.value) return
    try {
      const { data } = await authApi.getMe()
      user.value = data
    } catch {
      await logout()
    }
  }

  return { user, accessToken, refreshToken, isAuthenticated, isDesigner, isPrintNode, isAssemblyCenter, isAdmin, login, register, loginWithGoogle, logout, fetchMe }
})
