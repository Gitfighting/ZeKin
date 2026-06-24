import { defineStore } from 'pinia'

import {
  activateStudent,
  clearAuthSession,
  login as loginService,
  persistAuthSession,
  readStoredSession,
  type ActivateStudentPayload,
  type AuthSession,
  type AuthUser,
  type LoginPayload,
} from '@/services/auth'
import { getStudentProfile, type StudentProfile } from '@/services/student'

const PROFILE_KEY = 'student_profile'

interface UserState {
  session: AuthSession | null
  profile: StudentProfile | null
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    session: readStoredSession(),
    profile: (uni.getStorageSync(PROFILE_KEY) as StudentProfile | undefined) ?? null,
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.session?.accessToken),
    displayName: (state) => state.session?.user.displayName ?? state.profile?.realName ?? '同学',
    currentUser: (state): AuthUser | null => state.session?.user ?? null,
  },
  actions: {
    hydrate() {
      this.session = readStoredSession()
      this.profile = (uni.getStorageSync(PROFILE_KEY) as StudentProfile | undefined) ?? null
    },
    setSession(session: AuthSession) {
      this.session = session
      persistAuthSession(session)
    },
    setProfile(profile: StudentProfile) {
      this.profile = profile
      uni.setStorageSync(PROFILE_KEY, profile)
    },
    async login(payload: LoginPayload) {
      const session = await loginService(payload)
      this.setSession(session)
      return session
    },
    async activate(payload: ActivateStudentPayload) {
      const session = await activateStudent(payload)
      this.setSession(session)
      return session
    },
    async refreshProfile() {
      const profile = await getStudentProfile()
      this.setProfile(profile)
      return profile
    },
    logout() {
      this.session = null
      this.profile = null
      clearAuthSession()
      uni.removeStorageSync(PROFILE_KEY)
    },
  },
})
