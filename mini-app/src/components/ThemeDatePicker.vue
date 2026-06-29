<script setup lang="ts">
import { computed } from 'vue'

import { resolveMinTaskDate } from '@/utils/beijing-date-picker'
import { formatBeijingDateAfterYears } from '@/utils/datetime'

const props = defineProps<{
  modelValue: string
  minDate?: string
  maxDate?: string
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
  (event: 'change', value: string): void
}>()

const minBound = computed(() => resolveMinTaskDate(props.minDate))
const maxBound = computed(() => props.maxDate || formatBeijingDateAfterYears(5))

const pickerValue = computed(() => {
  const raw = props.modelValue?.trim()
  const match = raw?.match(/^(\d{4}-\d{2}-\d{2})/)
  if (match?.[1]) {
    return match[1]
  }
  return minBound.value
})

const displayDate = computed(() => pickerValue.value)

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
    class="theme-date-picker"
    mode="date"
    :value="pickerValue"
    :start="minBound"
    :end="maxBound"
    @change="onPick"
  >
    <view class="theme-date-picker__trigger">
      <slot>
        <view class="theme-date-picker__box">
          <text>{{ displayDate }}</text>
        </view>
      </slot>
    </view>
  </picker>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.theme-date-picker {
  flex: 1;
}

.theme-date-picker__trigger {
  flex: 1;
}

.theme-date-picker__box {
  display: flex;
  flex: 1;
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
