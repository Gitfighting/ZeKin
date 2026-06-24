<script setup lang="ts">
import { computed, ref } from 'vue'

import { getCurrentLocation, type LocationResult } from '@/services/location'

const props = defineProps<{
  modelValue: LocationResult | null
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: LocationResult): void
}>()

const loading = ref(false)

const locationText = computed(() => {
  if (!props.modelValue) {
    return '暂未获取定位'
  }

  return `经度 ${props.modelValue.longitude.toFixed(6)} / 纬度 ${props.modelValue.latitude.toFixed(6)}`
})

async function handlePick() {
  loading.value = true

  try {
    const location = await getCurrentLocation()
    emit('update:modelValue', location)
    uni.showToast({
      title: '定位成功',
      icon: 'success',
    })
  } catch {
    uni.showToast({
      title: '请开启定位权限',
      icon: 'none',
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <view class="location-card">
    <view class="location-card__content">
      <text class="location-card__label">当前位置</text>
      <text class="location-card__value">{{ locationText }}</text>
    </view>
    <button class="location-card__button" type="primary" :loading="loading" @click="handlePick">
      {{ modelValue ? '重新定位' : '获取定位' }}
    </button>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.location-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: #f8fbff;
  border: 2rpx solid rgba($primary, 0.08);
}

.location-card__content {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 12rpx;
}

.location-card__label {
  color: $text-secondary;
  font-size: 24rpx;
}

.location-card__value {
  color: $text-primary;
  font-size: 26rpx;
  line-height: 1.5;
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
