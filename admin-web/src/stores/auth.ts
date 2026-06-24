import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

const TOKEN_KEY = 'access_token'
const USER_KEY = 'admin_user'

export interface AdminUser {
  id: number
  displayName: string
  role: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) ?? '')
  const user = ref<AdminUser | null>(
    (() => {
      const raw = localStorage.getItem(USER_KEY)
      return raw ? (JSON.parse(raw) as AdminUser) : null
    })(),
  )

  const isAuthenticated = computed(() => Boolean(token.value))

  const login = (account: string) => {
    token.value = 'mock-admin-token'
    user.value = {
      id: 1,
      displayName: account || '系统管理员',
      role: '校级管理员',
    }
    localStorage.setItem(TOKEN_KEY, token.value)
    localStorage.setItem(USER_KEY, JSON.stringify(user.value))
  }

  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
  }
})
