<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import VectorIcon from '@/components/VectorIcon.vue'
import MiniMap from '@/components/MiniMap.vue'
import { UI_ICONS } from '@/constants/ui-icons'
import {
  calcDistance,
  getCurrentLocation,
  type LocationResult,
  type LocationTarget,
} from '@/services/location'

const props = defineProps<{
  modelValue: LocationResult | null
  target?: LocationTarget | null
  placeName?: string
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: LocationResult): void
}>()

const loading = ref(false)
const errorMsg = ref('')
const mapReady = ref(false)

const DEFAULT_CENTER = { latitude: 30.000001, longitude: 120.000001 }

function isValidCoord(lat: number, lng: number): boolean {
  return Math.abs(lat) > 0.0001 && Math.abs(lng) > 0.0001
}

const hasTarget = computed(() => {
  if (!props.target) {
    return false
  }
  return isValidCoord(props.target.latitude, props.target.longitude)
})

const distanceInfo = computed(() => {
  if (!props.modelValue || !hasTarget.value || !props.target) {
    return null
  }
  const distance = calcDistance(
    props.modelValue.latitude,
    props.modelValue.longitude,
    props.target.latitude,
    props.target.longitude,
  )
  return {
    distance,
    inside: distance <= props.target.radius,
    radius: props.target.radius,
  }
})

const statusText = computed(() => {
  if (!props.modelValue) {
    return { label: '正在获取位置…', color: '#999' }
  }
  if (!distanceInfo.value) {
    return { label: '已获取当前位置', color: '#1677ff' }
  }
  if (distanceInfo.value.inside) {
    return { label: '在打卡范围内', color: '#22c55e' }
  }
  return {
    label: `距签到点 ${Math.round(distanceInfo.value.distance)}m（需 ≤${distanceInfo.value.radius}m）`,
    color: '#ef4444',
  }
})

const mapCenter = computed(() => {
  if (hasTarget.value && props.target) {
    return {
      latitude: props.target.latitude,
      longitude: props.target.longitude,
    }
  }
  if (props.modelValue) {
    return {
      latitude: props.modelValue.latitude,
      longitude: props.modelValue.longitude,
    }
  }
  return DEFAULT_CENTER
})

const mapScale = computed(() => {
  const radius = props.target?.radius ?? 100
  if (radius <= 50) return 17
  if (radius <= 120) return 16
  if (radius <= 300) return 15
  return 14
})

const mapMarkers = computed(() => {
  if (!hasTarget.value || !props.target) {
    return []
  }
  return [
    {
      id: 1,
      latitude: props.target.latitude,
      longitude: props.target.longitude,
      title: props.placeName || '签到地点',
      width: 28,
      height: 36,
      callout: {
        content: props.placeName || '签到地点',
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
  if (!hasTarget.value || !props.target) {
    return []
  }
  return [
    {
      latitude: props.target.latitude,
      longitude: props.target.longitude,
      radius: props.target.radius,
      color: '#1677ff55',
      fillColor: '#1677ff22',
      strokeWidth: 2,
    },
  ]
})

const rangeLabel = computed(() => {
  if (!hasTarget.value || !props.target) {
    return '当前位置'
  }
  return `打卡范围（${props.target.radius}米）`
})

async function handlePick() {
  loading.value = true
  errorMsg.value = ''

  try {
    const location = await getCurrentLocation()
    emit('update:modelValue', location)
    uni.showToast({ title: '定位成功', icon: 'success' })
  } catch {
    errorMsg.value = '定位失败，请检查定位权限是否开启'
    uni.showToast({ title: '请开启定位权限', icon: 'none' })
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  if (!props.modelValue) {
    await handlePick()
  }
  mapReady.value = true
})
</script>

<template>
  <view class="location-card">
    <view class="location-card__map-wrap">
      <MiniMap
        v-if="mapReady"
        class="location-card__map"
        :latitude="mapCenter.latitude"
        :longitude="mapCenter.longitude"
        :scale="mapScale"
        :markers="mapMarkers"
        :circles="mapCircles"
      />
      <view v-else class="location-card__map-loading">正在加载地图…</view>
      <view class="location-card__legend">
        <view class="location-card__legend-dot" />
        <text class="location-card__legend-text">{{ rangeLabel }}</text>
      </view>
      <view v-if="placeName && hasTarget" class="location-card__place-tag">
        <text>{{ placeName }}</text>
      </view>
    </view>

    <view class="location-card__info">
      <text class="location-card__label">当前位置</text>
      <text v-if="modelValue" class="location-card__coords">
        经度 {{ modelValue.longitude.toFixed(6) }} / 纬度 {{ modelValue.latitude.toFixed(6) }}
      </text>
      <text v-if="modelValue?.accuracy" class="location-card__accuracy">
        精度 ±{{ modelValue.accuracy.toFixed(0) }}m
      </text>
      <text v-if="errorMsg" class="location-card__error">{{ errorMsg }}</text>
      <text v-if="!modelValue && !errorMsg" class="location-card__hint">正在获取 GPS 位置…</text>
    </view>

    <view class="location-card__status">
      <view v-if="distanceInfo" :class="['location-card__badge', distanceInfo.inside ? 'badge-ok' : 'badge-far']">
        <view v-if="distanceInfo.inside" class="location-card__badge-row">
          <VectorIcon :src="UI_ICONS.check" size="24rpx" />
          <text>在打卡范围内</text>
        </view>
        <view v-else class="location-card__badge-row">
          <VectorIcon :src="UI_ICONS.close" size="24rpx" />
          <text>超出 {{ Math.round(distanceInfo.distance - distanceInfo.radius) }}m</text>
        </view>
      </view>
      <text v-else class="location-card__status-text" :style="{ color: statusText.color }">
        {{ statusText.label }}
      </text>
    </view>

    <button class="location-card__button" :loading="loading" @click="handlePick">
      {{ modelValue ? '重新定位' : '获取定位' }}
    </button>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.location-card {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.location-card__map-wrap {
  position: relative;
  overflow: hidden;
  border-radius: 24rpx;
  border: 2rpx solid rgba($primary, 0.12);
  background: #eef5ff;
}

.location-card__map {
  width: 100%;
  height: 480rpx;
}

.location-card__map-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 480rpx;
  color: #667085;
  font-size: 24rpx;
  background: #eef5ff;
}

.location-card__legend {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 8rpx 20rpx rgba(15, 23, 42, 0.08);
}

.location-card__legend-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: $primary;
}

.location-card__legend-text {
  font-size: 22rpx;
  color: $text-primary;
}

.location-card__place-tag {
  position: absolute;
  left: 50%;
  bottom: 36rpx;
  transform: translateX(-50%);
  padding: 10rpx 24rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8rpx 20rpx rgba(15, 23, 42, 0.1);
  font-size: 26rpx;
  font-weight: 700;
  color: $text-primary;
}

.location-card__info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  padding: 0 4rpx;
}

.location-card__label {
  color: $text-secondary;
  font-size: 22rpx;
}

.location-card__coords {
  color: $text-primary;
  font-size: 26rpx;
  font-weight: 600;
}

.location-card__accuracy {
  color: $text-secondary;
  font-size: 22rpx;
}

.location-card__error {
  color: #ef4444;
  font-size: 24rpx;
}

.location-card__hint {
  color: $text-secondary;
  font-size: 24rpx;
}

.location-card__status {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 0 4rpx;
}

.location-card__badge {
  display: inline-flex;
  align-items: center;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.location-card__badge-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.badge-ok {
  background: #dcfce7;
  color: #16a34a;
}

.badge-far {
  background: #fef2f2;
  color: #dc2626;
}

.location-card__status-text {
  font-size: 22rpx;
}

.location-card__button {
  margin: 0;
  padding: 0 24rpx;
  height: 72rpx;
  line-height: 72rpx;
  border: none;
  border-radius: 999rpx;
  background: $primary;
  font-size: 24rpx;
  color: #fff;
}
</style>
