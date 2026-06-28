/** 微信开发者工具中 map 原生组件易触发 addListener 渲染层错误，改用占位 UI */
export function isWeixinDevtools(): boolean {
  // #ifdef MP-WEIXIN
  try {
    const system = uni.getSystemInfoSync()
    return system.platform === 'devtools'
  } catch {
    return false
  }
  // #endif
  return false
}

export function shouldUseNativeMap(): boolean {
  // #ifdef H5
  return true
  // #endif

  // #ifdef MP-WEIXIN
  return !isWeixinDevtools()
  // #endif

  return false
}

export function isValidMapCoord(latitude: number, longitude: number): boolean {
  return (
    Number.isFinite(latitude)
    && Number.isFinite(longitude)
    && Math.abs(latitude) <= 90
    && Math.abs(longitude) <= 180
    && (Math.abs(latitude) > 0.0001 || Math.abs(longitude) > 0.0001)
  )
}
