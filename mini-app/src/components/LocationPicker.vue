<script setup lang="ts">
import { computed, ref } from 'vue'

import {
  calcDistance,
  getCurrentLocation,
  type LocationResult,
  type LocationTarget,
} from '@/services/location'

const props = defineProps<{
  modelValue: LocationResult | null
  target?: LocationTarget | null
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: LocationResult): void
}>()

const loading = ref(false)
const errorMsg = ref('')

const distanceInfo = computed(() => {
  if (!props.modelValue || !props.target) {
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
    return { label: '暂未定位', color: '#999' }
  }
  if (!distanceInfo.value) {
    return { label: '已获取坐标', color: '#1677ff' }
  }
  if (distanceInfo.value.inside) {
    return { label: '在打卡范围内', color: '#22c55e' }
  }
  return {
    label: `距目标 ${Math.round(distanceInfo.value.distance)}m (需 ≤${distanceInfo.value.radius}m)`,
    color: '#ef4444',
  }
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
</script>

<template>
  <view class="location-card">
    <view class="location-card__info">
      <text class="location-card__label">当前位置</text>
      <text v-if="modelValue" class="location-card__coords">
        经度 {{ modelValue.longitude.toFixed(6) }} / 纬度 {{ modelValue.latitude.toFixed(6) }}
      </text>
      <text v-if="modelValue?.accuracy" class="location-card__accuracy">
        精度 ±{{ modelValue.accuracy.toFixed(0) }}m
      </text>
      <text v-if="errorMsg" class="location-card__error">{{ errorMsg }}</text>
      <text v-if="!modelValue && !errorMsg" class="location-card__hint">点击下方按钮获取当前 GPS 位置</text>
    </view>

    <view class="location-card__status">
      <view v-if="distanceInfo" :class="['location-card__badge', distanceInfo.inside ? 'badge-ok' : 'badge-far']">
        <text v-if="distanceInfo.inside">✓ 范围内</text>
        <text v-else>✗ 超出 {{ Math.round(distanceInfo.distance - distanceInfo.radius) }}m</text>
      </view>
      <text v-else class="location-card__status-text">{{ statusText.label }}</text>
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
  padding: 28rpx;
  border-radius: 24rpx;
  background: #f8fbff;
  border: 2rpx solid rgba($primary, 0.08);
}

.location-card__info {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
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
}

.location-card__badge {
  display: inline-flex;
  align-items: center;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 600;
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
  color: $text-secondary;
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
}
</style>
