<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { getSceneLocationPresets, type LocationPresetScene } from '@/constants/location-presets'
import MiniMap from '@/components/MiniMap.vue'
import { isAmapConfigured } from '@/config/amap'
import { regeocodeAmapPlace, searchAmapPlaces, type AmapPlaceSuggestion } from '@/services/amap'
import { getCurrentLocation } from '@/services/location'

export interface TeacherLocationValue {
  placeName: string
  longitude: number
  latitude: number
  radius: number
}

const props = defineProps<{
  modelValue: TeacherLocationValue
  scene?: LocationPresetScene
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: TeacherLocationValue): void
}>()

type PickMode = 'preset' | 'custom'

const pickMode = ref<PickMode>('preset')
const searchKeyword = ref('')
const searching = ref(false)
const searchResults = ref<AmapPlaceSuggestion[]>([])
const locating = ref(false)
const activePresetKey = ref('')

const presets = computed(() => getSceneLocationPresets(props.scene ?? 'class'))

const hasValidCoords = computed(() =>
  Math.abs(props.modelValue.latitude) > 0.0001 && Math.abs(props.modelValue.longitude) > 0.0001,
)

const mapCenter = computed(() => {
  if (hasValidCoords.value) {
    return {
      latitude: props.modelValue.latitude,
      longitude: props.modelValue.longitude,
    }
  }
  return { latitude: 30.27415, longitude: 120.15515 }
})

const mapMarkers = computed(() => {
  if (!hasValidCoords.value) {
    return []
  }
  return [
    {
      id: 1,
      latitude: props.modelValue.latitude,
      longitude: props.modelValue.longitude,
      title: props.modelValue.placeName || '签到地点',
      width: 28,
      height: 36,
      callout: {
        content: props.modelValue.placeName || '签到地点',
        display: 'BYCLICK',
        padding: 8,
        borderRadius: 8,
        fontSize: 12,
        color: '#1f2937',
        bgColor: '#ffffff',
      },
    },
  ]
})

const mapCircles = computed(() => {
  if (!hasValidCoords.value) {
    return []
  }
  return [
    {
      latitude: props.modelValue.latitude,
      longitude: props.modelValue.longitude,
      radius: props.modelValue.radius,
      color: '#1677ff55',
      fillColor: '#1677ff22',
      strokeWidth: 2,
    },
  ]
})

function patchValue(partial: Partial<TeacherLocationValue>) {
  emit('update:modelValue', { ...props.modelValue, ...partial })
}

function applyPreset(preset: ReturnType<typeof getSceneLocationPresets>[number]) {
  pickMode.value = 'preset'
  activePresetKey.value = preset.key
  patchValue({
    placeName: preset.placeName,
    radius: preset.radius,
  })
}

async function confirmCoords(longitude: number, latitude: number, placeName?: string) {
  let name = placeName?.trim() || props.modelValue.placeName
  if (!name) {
    try {
      name = await regeocodeAmapPlace(longitude, latitude)
    } catch {
      name = '自定义签到点'
    }
  }
  patchValue({ longitude, latitude, placeName: name })
}

async function handleSearch() {
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    searchResults.value = []
    return
  }
  searching.value = true
  try {
    searchResults.value = await searchAmapPlaces(keyword)
    if (searchResults.value.length === 0) {
      uni.showToast({ title: '未找到相关地点', icon: 'none' })
    }
  } catch (error) {
    searchResults.value = []
    uni.showToast({
      title: error instanceof Error ? error.message : '搜索失败',
      icon: 'none',
    })
  } finally {
    searching.value = false
  }
}

async function selectSearchResult(item: AmapPlaceSuggestion) {
  pickMode.value = 'custom'
  activePresetKey.value = ''
  searchResults.value = []
  searchKeyword.value = item.name
  await confirmCoords(item.longitude, item.latitude, item.name)
}

async function handleMapTap(detail: { latitude?: number; longitude?: number }) {
  const latitude = detail?.latitude
  const longitude = detail?.longitude
  if (typeof latitude !== 'number' || typeof longitude !== 'number') {
    return
  }
  pickMode.value = 'custom'
  activePresetKey.value = ''
  await confirmCoords(longitude, latitude)
}

async function handleChooseOnMap() {
  if (typeof uni.chooseLocation !== 'function') {
    uni.showToast({ title: '当前环境不支持地图选点', icon: 'none' })
    return
  }
  try {
    const result = await new Promise<UniApp.ChooseLocationSuccess>((resolve, reject) => {
      uni.chooseLocation({
        keyword: searchKeyword.value.trim() || props.modelValue.placeName,
        success: resolve,
        fail: reject,
      })
    })
    pickMode.value = 'custom'
    activePresetKey.value = ''
    await confirmCoords(result.longitude, result.latitude, result.name || result.address)
  } catch {
    uni.showToast({ title: '已取消选点', icon: 'none' })
  }
}

async function handleLocateCurrent() {
  locating.value = true
  try {
    const location = await getCurrentLocation()
    pickMode.value = 'custom'
    activePresetKey.value = ''
    await confirmCoords(location.longitude, location.latitude)
    uni.showToast({ title: '已定位到当前位置', icon: 'success' })
  } catch {
    uni.showToast({ title: '定位失败，请检查权限', icon: 'none' })
  } finally {
    locating.value = false
  }
}

function handleRadiusInput(event: { detail?: { value?: string } }) {
  const radius = Number(event.detail?.value ?? 0)
  patchValue({ radius: Number.isFinite(radius) && radius > 0 ? radius : 300 })
}

watch(
  () => props.scene,
  (scene) => {
    const first = getSceneLocationPresets(scene ?? 'class')[0]
    if (first && !hasValidCoords.value && !props.modelValue.placeName) {
      applyPreset(first)
    }
  },
  { immediate: true },
)
</script>

<template>
  <view class="teacher-location">
    <view class="teacher-location__mode-tabs">
      <view
        class="teacher-location__mode-tab"
        :class="{ 'teacher-location__mode-tab--active': pickMode === 'preset' }"
        @click="pickMode = 'preset'"
      >
        默认地点
      </view>
      <view
        class="teacher-location__mode-tab"
        :class="{ 'teacher-location__mode-tab--active': pickMode === 'custom' }"
        @click="pickMode = 'custom'"
      >
        自定义地点
      </view>
    </view>

    <view v-if="pickMode === 'preset'" class="teacher-location__presets">
      <view
        v-for="preset in presets"
        :key="preset.key"
        class="teacher-location__preset"
        :class="{ 'teacher-location__preset--active': activePresetKey === preset.key }"
        @click="applyPreset(preset)"
      >
        <text class="teacher-location__preset-name">{{ preset.placeName }}</text>
        <text class="teacher-location__preset-hint">{{ preset.hint }} · {{ preset.radius }}米</text>
      </view>
    </view>

    <view v-else class="teacher-location__search">
      <view class="teacher-location__search-row">
        <input
          v-model="searchKeyword"
          class="teacher-location__search-input"
          placeholder="搜索地点，如：浙江大学紫金港校区"
          confirm-type="search"
          @confirm="handleSearch"
        />
        <view class="teacher-location__search-btn" @click="handleSearch">
          {{ searching ? '搜索中' : '搜索' }}
        </view>
      </view>
      <text v-if="!isAmapConfigured()" class="teacher-location__tip">
        未配置高德 Key 时，请使用下方「地图选点」或「当前位置」确认坐标。
      </text>
      <view v-if="searchResults.length" class="teacher-location__results">
        <view
          v-for="item in searchResults"
          :key="item.id"
          class="teacher-location__result"
          @click="selectSearchResult(item)"
        >
          <text class="teacher-location__result-name">{{ item.name }}</text>
          <text class="teacher-location__result-address">{{ item.address || '高德地图' }}</text>
        </view>
      </view>
    </view>

    <view class="teacher-location__map-wrap">
      <MiniMap
        class="teacher-location__map"
        :latitude="mapCenter.latitude"
        :longitude="mapCenter.longitude"
        :scale="15"
        :markers="mapMarkers"
        :circles="mapCircles"
        enable-tap
        fallback-hint="模拟器不支持原生地图，请用「地图选点」或真机预览"
        @tap="handleMapTap"
      />
      <view class="teacher-location__map-tip">点击地图可调整签到位置（高德坐标系 GCJ-02）</view>
    </view>

    <view class="teacher-location__info">
      <view class="teacher-location__field">
        <text class="teacher-location__label">地点名称</text>
        <input
          :value="modelValue.placeName"
          class="teacher-location__input"
          placeholder="确认位置后自动填充，可手动修改"
          @input="patchValue({ placeName: ($event as any).detail.value })"
        />
      </view>
      <view class="teacher-location__coords">
        <text v-if="hasValidCoords">
          经度 {{ modelValue.longitude.toFixed(6) }} · 纬度 {{ modelValue.latitude.toFixed(6) }}
        </text>
        <text v-else class="teacher-location__coords--empty">请在地图上确认签到位置</text>
      </view>
      <view class="teacher-location__field">
        <text class="teacher-location__label">围栏半径（米）</text>
        <input
          class="teacher-location__input"
          type="number"
          :value="String(modelValue.radius)"
          @input="handleRadiusInput"
        />
      </view>
    </view>

    <view class="teacher-location__actions">
      <button class="teacher-location__btn teacher-location__btn--ghost" @click="handleChooseOnMap">
        地图选点
      </button>
      <button
        class="teacher-location__btn"
        :loading="locating"
        @click="handleLocateCurrent"
      >
        使用当前位置
      </button>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.teacher-location {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.teacher-location__mode-tabs {
  display: flex;
  gap: 16rpx;
}

.teacher-location__mode-tab {
  flex: 1;
  height: 72rpx;
  border-radius: 999rpx;
  background: #f3f6fb;
  color: $text-secondary;
  font-size: 26rpx;
  line-height: 72rpx;
  text-align: center;
}

.teacher-location__mode-tab--active {
  background: rgba($primary, 0.12);
  color: $primary;
  font-weight: 700;
}

.teacher-location__presets {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.teacher-location__preset {
  padding: 20rpx 24rpx;
  border: 2rpx solid rgba(15, 23, 42, 0.08);
  border-radius: 20rpx;
  background: #fff;
}

.teacher-location__preset--active {
  border-color: rgba($primary, 0.45);
  background: rgba($primary, 0.06);
}

.teacher-location__preset-name {
  display: block;
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 700;
}

.teacher-location__preset-hint {
  display: block;
  margin-top: 6rpx;
  color: $text-secondary;
  font-size: 24rpx;
}

.teacher-location__search-row {
  display: flex;
  gap: 12rpx;
}

.teacher-location__search-input {
  flex: 1;
  height: 72rpx;
  padding: 0 24rpx;
  border-radius: 16rpx;
  background: #f3f6fb;
  font-size: 26rpx;
}

.teacher-location__search-btn {
  display: flex;
  width: 128rpx;
  align-items: center;
  justify-content: center;
  border-radius: 16rpx;
  background: $primary;
  color: #fff;
  font-size: 26rpx;
}

.teacher-location__tip {
  color: $text-muted;
  font-size: 22rpx;
  line-height: 1.5;
}

.teacher-location__results {
  display: flex;
  max-height: 280rpx;
  flex-direction: column;
  gap: 8rpx;
  overflow-y: auto;
}

.teacher-location__result {
  padding: 18rpx 20rpx;
  border-radius: 16rpx;
  background: #f8fbff;
}

.teacher-location__result-name {
  display: block;
  color: $text-primary;
  font-size: 26rpx;
  font-weight: 600;
}

.teacher-location__result-address {
  display: block;
  margin-top: 4rpx;
  color: $text-secondary;
  font-size: 22rpx;
}

.teacher-location__map-wrap {
  position: relative;
  overflow: hidden;
  border-radius: 24rpx;
  border: 2rpx solid rgba($primary, 0.12);
}

.teacher-location__map {
  width: 100%;
  height: 420rpx;
}

.teacher-location__map-tip {
  padding: 12rpx 20rpx;
  background: rgba(255, 255, 255, 0.96);
  color: $text-secondary;
  font-size: 22rpx;
  text-align: center;
}

.teacher-location__info {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.teacher-location__field {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.teacher-location__label {
  color: $text-secondary;
  font-size: 24rpx;
}

.teacher-location__input {
  height: 72rpx;
  padding: 0 24rpx;
  border-radius: 16rpx;
  background: #f3f6fb;
  font-size: 26rpx;
}

.teacher-location__coords {
  color: $text-primary;
  font-size: 24rpx;
}

.teacher-location__coords--empty {
  color: #ef4444;
}

.teacher-location__actions {
  display: flex;
  gap: 16rpx;
}

.teacher-location__btn {
  flex: 1;
  margin: 0;
  height: 76rpx;
  line-height: 76rpx;
  border: none;
  border-radius: 999rpx;
  background: $primary;
  color: #fff;
  font-size: 26rpx;
}

.teacher-location__btn--ghost {
  background: rgba($primary, 0.1);
  color: $primary;
}
</style>
