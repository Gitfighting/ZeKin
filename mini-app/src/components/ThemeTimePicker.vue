<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import {
  createBeijingTimePickerState,
  rebuildBeijingTimePickerColumn,
} from '@/utils/beijing-time-picker'

const props = defineProps<{
  modelValue: string
  minTime?: string
}>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
  (event: 'change', value: string): void
}>()

const visible = ref(false)
const minBound = computed(() => props.minTime || '00:00')

const draftState = ref(createBeijingTimePickerState(props.modelValue, minBound.value))

const displayTime = computed(() => props.modelValue || draftState.value.displayTime)

function syncDraft(value?: string) {
  draftState.value = createBeijingTimePickerState(value, minBound.value)
}

watch(
  () => [props.modelValue, minBound.value] as const,
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
    draftState.value = rebuildBeijingTimePickerColumn(
      draftState.value,
      minBound.value,
      changedColumn,
      newIndexes[changedColumn] ?? 0,
    )
    return
  }

  draftState.value = {
    ...draftState.value,
    indexes: newIndexes,
  }
}

function confirmPicker() {
  const next = draftState.value.displayTime
  emit('update:modelValue', next)
  emit('change', next)
  closePicker()
}
</script>

<template>
  <view class="theme-time-picker">
    <view class="theme-time-picker__trigger" @click="openPicker">
      <slot>
        <view class="theme-time-picker__box">
          <text>{{ displayTime }}</text>
        </view>
      </slot>
    </view>

    <view v-if="visible" class="theme-time-picker__mask" @click="closePicker" />
    <view v-if="visible" class="theme-time-picker__sheet">
      <view class="theme-time-picker__header">
        <text class="theme-time-picker__action theme-time-picker__action--cancel" @click="closePicker">取消</text>
        <text class="theme-time-picker__action theme-time-picker__action--confirm" @click="confirmPicker">确定</text>
      </view>

      <picker-view
        class="theme-time-picker__view"
        :value="draftState.indexes"
        indicator-style="height: 80rpx; border-top: 1rpx solid rgba(22, 119, 255, 0.12); border-bottom: 1rpx solid rgba(22, 119, 255, 0.12);"
        @change="onDraftPick"
      >
        <picker-view-column v-for="(column, columnIndex) in draftState.range" :key="columnIndex">
          <view
            v-for="(item, itemIndex) in column"
            :key="`${columnIndex}-${itemIndex}`"
            class="theme-time-picker__item"
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

.theme-time-picker__mask {
  position: fixed;
  inset: 0;
  z-index: 1200;
  background: rgba(16, 24, 40, 0.45);
}

.theme-time-picker__sheet {
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

.theme-time-picker__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  border-bottom: 1rpx solid $border-light;
}

.theme-time-picker__action {
  font-size: 30rpx;
  line-height: 1.4;
}

.theme-time-picker__action--cancel {
  color: $text-secondary;
}

.theme-time-picker__action--confirm {
  color: $primary;
  font-weight: 700;
}

.theme-time-picker__view {
  width: 100%;
  height: 420rpx;
}

.theme-time-picker__item {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80rpx;
  color: $text-primary;
  font-size: 32rpx;
  font-weight: 600;
}
</style>
