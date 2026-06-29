<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: string
  minTime?: string
  maxTime?: string
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
  (event: 'change', value: string): void
}>()

const minBound = computed(() => props.minTime || '00:00')
const maxBound = computed(() => props.maxTime || '23:59')

const pickerValue = computed(() => {
  const raw = props.modelValue?.trim()
  const match = raw?.match(/(\d{2}:\d{2})/)
  if (match?.[1]) {
    return match[1]
  }
  return minBound.value
})

const displayTime = computed(() => pickerValue.value)

function onPick(event: { detail: { value: string } }) {
  const next = event.detail.value
  if (!next) {
    return
  }
  emit('update:modelValue', next)
  emit('change', next)
}
</script>

<template>
  <picker
    class="theme-time-picker"
    mode="time"
    :value="pickerValue"
    :start="minBound"
    :end="maxBound"
    @change="onPick"
  >
    <view class="theme-time-picker__trigger">
      <slot>
        <view class="theme-time-picker__box">
          <text>{{ displayTime }}</text>
        </view>
      </slot>
    </view>
  </picker>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.theme-time-picker {
  flex: 0 0 auto;
}

.theme-time-picker__trigger {
  flex: 0 0 auto;
  width: 160rpx;
}

.theme-time-picker__box {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 80rpx;
  padding: 22rpx 24rpx;
  border-radius: 16rpx;
  background: #f7faff;
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 600;
  box-sizing: border-box;
}
</style>
