export type LocationPresetScene = 'class' | 'dorm' | 'internship'

export interface LocationPreset {
  key: string
  placeName: string
  hint: string
  radius: number
}

export const SCENE_LOCATION_PRESETS: Record<LocationPresetScene, LocationPreset[]> = {
  class: [
    { key: 'class-a', placeName: '教学楼A区', hint: '课堂默认签到点', radius: 300 },
    { key: 'class-b', placeName: '实验楼签到点', hint: '实验课常用', radius: 250 },
  ],
  dorm: [
    { key: 'dorm-3', placeName: '3号宿舍楼', hint: '查寝默认签到点', radius: 200 },
    { key: 'dorm-5', placeName: '5号宿舍楼', hint: '查寝备用点', radius: 200 },
  ],
  internship: [
    { key: 'intern-company', placeName: '实习单位门口', hint: '实习打卡默认点', radius: 500 },
    { key: 'intern-office', placeName: '实习办公区', hint: '办公区签到', radius: 300 },
  ],
}

export function getSceneLocationPresets(scene: LocationPresetScene): LocationPreset[] {
  return SCENE_LOCATION_PRESETS[scene] ?? SCENE_LOCATION_PRESETS.class
}
