import { request } from '@/services/request'
import type { ApiResponse, LoginResponse, UserType } from '@/services/types'

const TOKEN_KEY = 'access_token'
const USER_KEY = 'student_auth_user'

export interface AuthUser {
  id: number
  userType: UserType
  displayName: string
  studentNo?: string
  phone?: string
  className?: string | null
  activated: boolean
}

export interface AuthSession {
  accessToken: string
  user: AuthUser
}

export interface LoginPayload {
  account: string
  password: string
  userType?: UserType
}

export interface ActivateStudentPayload {
  name: string
  studentNo: string
  phone: string
  code: string
  password: string
  confirmPassword?: string
}

interface LegacyLoginResponse {
  token?: string
  access_token?: string
  user?: {
    id: number
    role?: UserType
    user_type?: UserType
    real_name?: string
    display_name?: string
    username?: string
    class_name?: string | null
    phone?: string
  }
}

function normalizeUser(user: LegacyLoginResponse['user'] | LoginResponse['user'] | undefined): AuthUser {
  return {
    id: user?.id ?? 0,
    userType: user?.user_type ?? user?.role ?? 'student',
    displayName: user?.display_name ?? user?.real_name ?? user?.username ?? '同学',
    className: user?.class_name ?? null,
    phone: user?.phone,
    activated: true,
  }
}

function normalizeSession(payload: LoginResponse | LegacyLoginResponse): AuthSession {
  return {
    accessToken: payload.access_token ?? payload.token ?? '',
    user: normalizeUser(payload.user),
  }
}

function unwrap<T>(response: ApiResponse<T> | T): T {
  if (typeof response === 'object' && response !== null && 'data' in response) {
    return (response as ApiResponse<T>).data
  }
  return response as T
}

export function persistAuthSession(session: AuthSession) {
  uni.setStorageSync(TOKEN_KEY, session.accessToken)
  uni.setStorageSync(USER_KEY, session.user)
}

export function readStoredSession(): AuthSession | null {
  const accessToken = uni.getStorageSync(TOKEN_KEY) as string
  const user = uni.getStorageSync(USER_KEY) as AuthUser | undefined

  if (!accessToken || !user) {
    return null
  }

  return {
    accessToken,
    user,
  }
}

export function clearAuthSession() {
  uni.removeStorageSync(TOKEN_KEY)
  uni.removeStorageSync(USER_KEY)
}

export function clearLoginState() {
  clearAuthSession()
  uni.removeStorageSync('student_profile')
  uni.removeStorageSync('user_profile')
}

export async function login(payload: LoginPayload): Promise<AuthSession> {
  const data: Record<string, string> = {
    account: payload.account,
    username: payload.account,
    password: payload.password,
  }
  if (payload.userType) {
    data.user_type = payload.userType
  }

  const response = await request<ApiResponse<LoginResponse | LegacyLoginResponse>>({
    url: '/auth/login',
    method: 'POST',
    data,
  })

  const session = normalizeSession(unwrap(response))
  persistAuthSession(session)
  return session
}

export async function activateStudent(payload: ActivateStudentPayload): Promise<AuthSession> {
  const response = await request<ApiResponse<LoginResponse | LegacyLoginResponse>>({
    url: '/auth/student/activate',
    method: 'POST',
    data: {
      name: payload.name,
      student_no: payload.studentNo,
      phone: payload.phone,
      code: payload.code,
      password: payload.password,
    },
  })

  const session = normalizeSession(unwrap(response))
  persistAuthSession(session)
  return session
}
