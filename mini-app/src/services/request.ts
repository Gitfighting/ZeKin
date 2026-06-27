export const API_BASE_URL = 'http://192.168.165.19:8000/api'
const AUTH_STORAGE_KEYS = ['access_token', 'student_auth_user', 'student_profile', 'user_profile']

function logRequest(step: string, detail: Record<string, unknown>) {
  console.info(`[register-flow] 网络层 ${step}`, detail)
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
  const isRegister = options.url === '/auth/register'

  return new Promise((resolve, reject) => {
    if (!token && !isAuthEndpoint(options.url)) {
      reject(redirectToLogin())
      return
    }

    if (isRegister) {
      logRequest('uni.request 发出', {
        method: options.method ?? 'GET',
        url: fullUrl,
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
        if (isRegister) {
          logRequest('uni.request 响应', {
            statusCode: response.statusCode,
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
        if (isRegister) {
          logRequest('uni.request fail', { error })
        }
        reject(error)
      },
    })
  })
}
