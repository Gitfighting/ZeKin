import { AMAP_REST_BASE, AMAP_WEB_KEY, isAmapConfigured } from '@/config/amap'

export interface AmapPlaceSuggestion {
  id: string
  name: string
  address: string
  longitude: number
  latitude: number
}

interface AmapApiLocation {
  lng: string
  lat: string
}

function parseLocation(value?: string | AmapApiLocation): { longitude: number; latitude: number } | null {
  if (!value) {
    return null
  }
  if (typeof value === 'object') {
    const longitude = Number(value.lng)
    const latitude = Number(value.lat)
    if (Number.isFinite(longitude) && Number.isFinite(latitude)) {
      return { longitude, latitude }
    }
    return null
  }
  const [lng, lat] = value.split(',').map(Number)
  if (!Number.isFinite(lng) || !Number.isFinite(lat)) {
    return null
  }
  return { longitude: lng, latitude: lat }
}

async function amapGet<T>(path: string, params: Record<string, string>): Promise<T> {
  const query = new URLSearchParams({ key: AMAP_WEB_KEY, ...params })
  const url = `${AMAP_REST_BASE}${path}?${query.toString()}`
  const response = await uni.request({ url, method: 'GET' })
  if (response.statusCode !== 200 || !response.data) {
    throw new Error('高德地图服务请求失败')
  }
  return response.data as T
}

export async function searchAmapPlaces(keyword: string): Promise<AmapPlaceSuggestion[]> {
  const trimmed = keyword.trim()
  if (!trimmed) {
    return []
  }
  if (!isAmapConfigured()) {
    throw new Error('未配置高德地图 Key，请联系管理员配置 VITE_AMAP_WEB_KEY')
  }

  const data = await amapGet<{
    status: string
    tips?: Array<{
      id?: string
      name?: string
      address?: string
      district?: string
      location?: string | AmapApiLocation
    }>
  }>('/assistant/inputtips', {
    keywords: trimmed,
    datatype: 'all',
  })

  if (data.status !== '1' || !Array.isArray(data.tips)) {
    return []
  }

  return data.tips
    .map((tip, index) => {
      const coords = parseLocation(tip.location)
      if (!coords) {
        return null
      }
      return {
        id: tip.id || `${index}-${tip.name ?? 'place'}`,
        name: tip.name?.trim() || trimmed,
        address: [tip.district, tip.address].filter(Boolean).join(' '),
        longitude: coords.longitude,
        latitude: coords.latitude,
      }
    })
    .filter((item): item is AmapPlaceSuggestion => item !== null)
}

export async function regeocodeAmapPlace(longitude: number, latitude: number): Promise<string> {
  if (!isAmapConfigured()) {
    return `${longitude.toFixed(6)}, ${latitude.toFixed(6)}`
  }

  const data = await amapGet<{
    status: string
    regeocode?: { formatted_address?: string }
  }>('/geocode/regeo', {
    location: `${longitude},${latitude}`,
    extensions: 'base',
  })

  if (data.status !== '1') {
    return `${longitude.toFixed(6)}, ${latitude.toFixed(6)}`
  }
  return data.regeocode?.formatted_address?.trim() || `${longitude.toFixed(6)}, ${latitude.toFixed(6)}`
}
