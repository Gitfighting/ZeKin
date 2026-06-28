/** 高德 Web 服务 Key，用于地点搜索与逆地理编码。请在 .env 中配置 VITE_AMAP_WEB_KEY */
export const AMAP_WEB_KEY = import.meta.env.VITE_AMAP_WEB_KEY ?? ''

export const AMAP_REST_BASE = 'https://restapi.amap.com/v3'

export function isAmapConfigured(): boolean {
  return AMAP_WEB_KEY.trim().length > 0
}
