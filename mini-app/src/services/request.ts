const API_BASE_URL = 'http://localhost:8000/api'

export function request<T>(options: UniApp.RequestOptions): Promise<T> {
  const token = uni.getStorageSync('access_token')

  return new Promise((resolve, reject) => {
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
        reject(response)
      },
      fail: reject,
    })
  })
}
