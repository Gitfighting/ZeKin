const DEFAULT_API_BASE_URL = 'http://192.168.165.19:8000/api'

/** 勿用 typeof import.meta 判断，微信小程序编译会错误注入 require('url') */
export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL

const AUTH_STORAGE_KEYS = ['access_token', 'student_auth_user', 'student_profile', 'user_profile']

function shouldTraceRequest(url: string): boolean {
  return url.includes('/student/groups') || url === '/auth/register'
}

function logRequest(step: string, detail: Record<string, unknown>) {
  console.info(`[AI思政] 网络层 ${step}`, detail)
}

if (typeof console !== 'undefined') {
  console.info('[AI思政] API 基址已加载', { API_BASE_URL })
}

export class AuthRequiredError extends Error {
  silent = true

  constructor(message = '未登录') {
    super(message)
    this.name = 'AuthRequiredError'
  }
}

function isAuthEndpoint(url: string): boolean {
  return url.startsWith('/auth/')
}

function clearLoginState() {
  AUTH_STORAGE_KEYS.forEach((key) => {
    uni.removeStorageSync(key)
  })
}

function redirectToLogin(): AuthRequiredError {
  clearLoginState()
  uni.reLaunch({ url: '/pages/auth/login' })
  return new AuthRequiredError()
}

export function request<T>(options: UniApp.RequestOptions): Promise<T> {
  const token = uni.getStorageSync('access_token')
  const fullUrl = `${API_BASE_URL}${options.url}`
  const trace = shouldTraceRequest(options.url ?? '')

  return new Promise((resolve, reject) => {
    if (!token && !isAuthEndpoint(options.url ?? '')) {
      reject(redirectToLogin())
      return
    }

    if (trace) {
      logRequest('请求发出', {
        method: options.method ?? 'GET',
        url: fullUrl,
        apiBase: API_BASE_URL,
        path: options.url,
        hasToken: Boolean(token),
      })
    }

    uni.request({
      ...options,
      url: fullUrl,
      header: {
        ...(options.header ?? {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success: (response) => {
        if (trace) {
          logRequest('响应收到', {
            statusCode: response.statusCode,
            path: options.url,
            data: response.data,
          })
        }

        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(response.data as T)
          return
        }
        if (response.statusCode === 401 || response.statusCode === 403) {
          reject(redirectToLogin())
          return
        }
        reject(response)
      },
      fail: (error) => {
        if (trace) {
          logRequest('请求失败', { path: options.url, url: fullUrl, error })
        }
        reject(error)
      },
    })
  })
}
