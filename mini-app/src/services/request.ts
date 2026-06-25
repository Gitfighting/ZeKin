const API_BASE_URL = 'http://localhost:8000/api'
const AUTH_STORAGE_KEYS = ['access_token', 'student_auth_user', 'student_profile', 'user_profile']

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

  return new Promise((resolve, reject) => {
    if (!token && !isAuthEndpoint(options.url)) {
      reject(redirectToLogin())
      return
    }

    uni.request({
      ...options,
      url: `${API_BASE_URL}${options.url}`,
      header: {
        ...(options.header ?? {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success: (response) => {
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
      fail: reject,
    })
  })
}
