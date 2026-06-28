<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import {
  createBeijingDatePickerState,
  rebuildBeijingDatePickerColumn,
  resolveMinTaskDate,
} from '@/utils/beijing-date-picker'
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

const visible = ref(false)
const minBound = computed(() => resolveMinTaskDate(props.minDate))
const maxBound = computed(() => props.maxDate || formatBeijingDateAfterYears(5))

const draftState = ref(
  createBeijingDatePickerState(props.modelValue, minBound.value, maxBound.value),
)

const displayDate = computed(() => {
  if (props.modelValue) {
    return props.modelValue
  }
  return draftState.value.displayDate
})

function syncDraft(value?: string) {
  draftState.value = createBeijingDatePickerState(value, minBound.value, maxBound.value)
}

watch(
  () => [props.modelValue, minBound.value, maxBound.value] as const,
  ([value]) => {
    syncDraft(value)
  },
)

function openPicker() {
  syncDraft(props.modelValue)
  visible.value = true
}

function closePicker() {
  visible.value = false
}

function onDraftPick(event: { detail: { value: number[] } }) {
  const newIndexes = event.detail.value
  const oldIndexes = draftState.value.indexes
  let changedColumn = -1

  for (let index = 0; index < newIndexes.length; index += 1) {
    if (newIndexes[index] !== oldIndexes[index]) {
      changedColumn = index
      break
    }
  }

  if (changedColumn >= 0) {
    draftState.value = rebuildBeijingDatePickerColumn(
      draftState.value,
      minBound.value,
      maxBound.value,
      changedColumn,
      newIndexes[changedColumn] ?? 0,
    )
  }
}

function confirmPicker() {
  const next = draftState.value.displayDate
  emit('update:modelValue', next)
  emit('change', next)
  closePicker()
}
</script>

<template>
  <view class="theme-date-picker">
    <view class="theme-date-picker__trigger" @click="openPicker">
      <slot>
        <view class="theme-date-picker__box">
          <text>{{ displayDate }}</text>
        </view>
      </slot>
    </view>

    <view v-if="visible" class="theme-date-picker__mask" @click="closePicker" />
    <view v-if="visible" class="theme-date-picker__sheet">
      <view class="theme-date-picker__header">
        <text class="theme-date-picker__action theme-date-picker__action--cancel" @click="closePicker">取消</text>
        <text class="theme-date-picker__action theme-date-picker__action--confirm" @click="confirmPicker">确定</text>
      </view>

      <picker-view
        class="theme-date-picker__view"
        :value="draftState.indexes"
        indicator-style="height: 80rpx; border-top: 1rpx solid rgba(22, 119, 255, 0.12); border-bottom: 1rpx solid rgba(22, 119, 255, 0.12);"
        @change="onDraftPick"
      >
        <picker-view-column v-for="(column, columnIndex) in draftState.range" :key="columnIndex">
          <view
            v-for="(item, itemIndex) in column"
            :key="`${columnIndex}-${itemIndex}`"
            class="theme-date-picker__item"
          >
            {{ item }}
          </view>
        </picker-view-column>
      </picker-view>
    </view>
  </view>
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

.theme-date-picker__mask {
  position: fixed;
  inset: 0;
  z-index: 1200;
  background: rgba(16, 24, 40, 0.45);
}

.theme-date-picker__sheet {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 1201;
  padding-bottom: env(safe-area-inset-bottom);
  border-radius: 28rpx 28rpx 0 0;
  background: $card-bg;
  box-shadow: 0 -12rpx 40rpx rgba(15, 107, 214, 0.12);
}

.theme-date-picker__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  border-bottom: 1rpx solid $border-light;
}

.theme-date-picker__action {
  font-size: 30rpx;
  line-height: 1.4;
}

.theme-date-picker__action--cancel {
  color: $text-secondary;
}

.theme-date-picker__action--confirm {
  color: $primary;
  font-weight: 700;
}

.theme-date-picker__view {
  width: 100%;
  height: 420rpx;
}

.theme-date-picker__item {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80rpx;
  color: $text-primary;
  font-size: 32rpx;
  font-weight: 600;
}

</style>
