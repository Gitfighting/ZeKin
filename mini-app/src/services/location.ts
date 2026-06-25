export interface LocationResult {
  longitude: number
  latitude: number
}

const LOCATION_SCOPE = 'scope.userLocation'
const LOCATION_PERMISSION_TITLE = '需要定位权限'
const LOCATION_PERMISSION_MESSAGE =
  '打卡需要获取当前位置，用于判断是否在签到范围内。请在设置中允许位置权限。'

function readAuthSetting(): Promise<Record<string, boolean> | null> {
  if (typeof uni.getSetting !== 'function') {
    return Promise.resolve(null)
  }

  return new Promise((resolve) => {
    uni.getSetting({
      success: (result) => {
        resolve((result as UniApp.GetSettingSuccessResult).authSetting ?? null)
      },
      fail: () => {
        resolve(null)
      },
    })
  })
}

function authorizeLocation(): Promise<boolean> {
  if (typeof uni.authorize !== 'function') {
    return Promise.resolve(true)
  }

  return new Promise((resolve) => {
    uni.authorize({
      scope: LOCATION_SCOPE,
      success: () => resolve(true),
      fail: () => resolve(false),
    })
  })
}

function openLocationSetting(): Promise<boolean> {
  if (typeof uni.showModal !== 'function' || typeof uni.openSetting !== 'function') {
    return Promise.resolve(false)
  }

  return new Promise((resolve) => {
    uni.showModal({
      title: LOCATION_PERMISSION_TITLE,
      content: LOCATION_PERMISSION_MESSAGE,
      confirmText: '去设置',
      cancelText: '取消',
      success: (result) => {
        if (!result.confirm) {
          resolve(false)
          return
        }

        uni.openSetting({
          success: (settingResult) => {
            resolve(
              (settingResult as UniApp.OpenSettingSuccessResult).authSetting?.[LOCATION_SCOPE] ===
                true,
            )
          },
          fail: () => resolve(false),
        })
      },
      fail: () => resolve(false),
    })
  })
}

async function ensureLocationPermission(): Promise<void> {
  const authSetting = await readAuthSetting()

  if (authSetting?.[LOCATION_SCOPE] === true) {
    return
  }

  if (authSetting?.[LOCATION_SCOPE] === false) {
    const opened = await openLocationSetting()
    if (!opened) {
      throw new Error('定位权限未开启')
    }
    return
  }

  const authorized = await authorizeLocation()
  if (authorized) {
    return
  }

  const opened = await openLocationSetting()
  if (!opened) {
    throw new Error('定位权限未开启')
  }
}

export function getCurrentLocation(): Promise<LocationResult> {
  return ensureLocationPermission().then(
    () =>
      new Promise((resolve, reject) => {
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
      }),
  )
}
