import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { loginAdmin } from '../api/admin'

const TOKEN_KEY = 'access_token'
const USER_KEY = 'admin_user'

export interface AdminUser {
  id: number
  displayName: string
  role: string
}

const readStoredUser = (): AdminUser | null => {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null

  try {
    const parsed = JSON.parse(raw) as Partial<AdminUser>
    if (
      typeof parsed.id === 'number' &&
      typeof parsed.displayName === 'string' &&
      typeof parsed.role === 'string'
    ) {
      return {
        id: parsed.id,
        displayName: parsed.displayName,
        role: parsed.role,
      }
    }
  } catch {
    localStorage.removeItem(USER_KEY)
  }

  return null
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) ?? '')
  const user = ref<AdminUser | null>(readStoredUser())

  const isAuthenticated = computed(() => Boolean(token.value))

  const login = async (account: string, password: string) => {
    const session = await loginAdmin(account, password)

    token.value = session.access_token
    user.value = {
      id: session.user.id,
      displayName: session.user.display_name || account || '系统管理员',
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
