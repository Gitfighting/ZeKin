import { request, API_BASE_URL } from '@/services/request'
import type { ApiResponse, LoginResponse, UserType } from '@/services/types'
import { logInfo, logError } from '@/services/feedback'

const TOKEN_KEY = 'access_token'
const USER_KEY = 'student_auth_user'
const REMEMBER_LOGIN_KEY = 'auth_remember_login'
const SAVED_ACCOUNT_KEY = 'auth_saved_account'
const SAVED_PASSWORD_KEY = 'auth_saved_password'

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

export interface RegisterPayload {
  account: string
  phone: string
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

export function redirectToHome(userType: UserType) {
  if (userType === 'teacher') {
    uni.reLaunch({ url: '/pages/teacher/home' })
    return
  }
  uni.switchTab({ url: '/pages/student/home' })
}

/** 启动时若本地仍有 token，直接进入首页，避免每次编译/刷新都要登录 */
export function tryRestoreSession(): AuthSession | null {
  const session = readStoredSession()
  if (!session?.accessToken) {
    return null
  }
  redirectToHome(session.user.userType)
  return session
}

export interface SavedLoginDraft {
  remember: boolean
  account: string
  password: string
}

export function loadLoginDraft(): SavedLoginDraft {
  const rememberFlag = uni.getStorageSync(REMEMBER_LOGIN_KEY)
  const account = (uni.getStorageSync(SAVED_ACCOUNT_KEY) as string) || ''
  const password = (uni.getStorageSync(SAVED_PASSWORD_KEY) as string) || ''
  const remember =
    rememberFlag !== false &&
    rememberFlag !== 'false' &&
    Boolean(account)
  return { remember, account, password }
}

export function saveLoginDraft(payload: LoginPayload, remember: boolean) {
  uni.setStorageSync(REMEMBER_LOGIN_KEY, remember)
  if (!remember) {
    uni.removeStorageSync(SAVED_ACCOUNT_KEY)
    uni.removeStorageSync(SAVED_PASSWORD_KEY)
    return
  }
  uni.setStorageSync(SAVED_ACCOUNT_KEY, payload.account)
  uni.setStorageSync(SAVED_PASSWORD_KEY, payload.password)
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

export async function registerAccount(payload: RegisterPayload): Promise<AuthSession> {
  const body = {
    account: payload.account.trim(),
    phone: payload.phone.trim(),
    password: payload.password,
  }
  logInfo('[register-flow] API层 发起 POST /auth/register', {
    url: `${API_BASE_URL}/auth/register`,
    account: body.account,
    phone: body.phone,
    passwordLen: body.password.length,
  })

  try {
    const response = await request<ApiResponse<LoginResponse | LegacyLoginResponse>>({
      url: '/auth/register',
      method: 'POST',
      data: body,
    })

    logInfo('[register-flow] API层 收到成功响应', response)
    const session = normalizeSession(unwrap(response))
    persistAuthSession(session)
    logInfo('[register-flow] API层 会话已写入本地存储', {
      userId: session.user.id,
      userType: session.user.userType,
    })
    return session
  } catch (error) {
    const statusCode =
      typeof error === 'object' && error !== null && 'statusCode' in error
        ? (error as { statusCode?: number }).statusCode
        : undefined
    if (statusCode === 404) {
      logError(
        '[register-flow] API层 404：后端未部署 /api/auth/register，请重启 backend 并确认 openapi 含该路由',
        error,
      )
    } else {
      logError('[register-flow] API层 请求失败', error)
    }
    throw error
  }
}
