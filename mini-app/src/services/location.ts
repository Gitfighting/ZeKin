export interface LocationResult {
  longitude: number
  latitude: number
}

export function getCurrentLocation(): Promise<LocationResult> {
  return new Promise((resolve, reject) => {
    uni.getLocation({
      type: 'gcj02',
      success: ({ longitude, latitude }) => {
        resolve({
          longitude,
          latitude,
        })
      },
      fail: reject,
    })
  })
}
