<script setup lang="ts">
import { ref, watch } from 'vue'

import GestureGridPicker from '@/components/GestureGridPicker.vue'
import VectorIcon from '@/components/VectorIcon.vue'
import {
  GESTURE_PRESETS,
  normalizePatternId,
  patternDisplayLabel,
  sequenceToPatternId,
} from '@/constants/gesture-patterns'
import { UI_ICONS } from '@/constants/ui-icons'
import { showError } from '@/services/feedback'

const props = defineProps<{
  visible: boolean
  modelValue?: string
}>()

const emit = defineEmits<{
  (event: 'update:visible', value: boolean): void
  (event: 'update:modelValue', value: string): void
  (event: 'confirm', value: string): void
}>()

const draftPattern = ref('')
const gridRef = ref<InstanceType<typeof GestureGridPicker> | null>(null)
const canvasId = `gestureCanvas_${Math.random().toString(36).slice(2, 9)}`

watch(
  () => props.visible,
  (open) => {
    if (!open) {
      return
    }
    draftPattern.value = normalizePatternId(props.modelValue) || sequenceToPatternId(GESTURE_PRESETS[0].sequence)
  },
)

function close() {
  emit('update:visible', false)
}

function applyPreset(sequence: number[]) {
  draftPattern.value = sequenceToPatternId(sequence)
  gridRef.value?.setSequence([...sequence])
}

function confirm() {
  const pattern = normalizePatternId(draftPattern.value)
  if (pattern.length < 3) {
    showError('请至少连接 3 个点')
    return
  }
  emit('update:modelValue', pattern)
  emit('confirm', pattern)
  close()
}
</script>

<template>
  <view v-if="visible" class="gesture-modal-mask" @click="close">
    <view class="gesture-modal-sheet" @click.stop>
      <view class="gesture-modal-header">
        <text class="gesture-modal-title">设置手势图案</text>
        <view class="gesture-modal-close" @click="close">
          <VectorIcon :src="UI_ICONS.close" size="32rpx" />
        </view>
      </view>

      <view class="gesture-modal-body">
        <text class="gesture-modal-subtitle">典型九宫格一笔画，学生签到需按相同轨迹绘制</text>

        <view class="gesture-modal-presets">
          <text class="gesture-modal-presets__label">常用图案</text>
          <view class="gesture-modal-presets__chips">
            <view
              v-for="preset in GESTURE_PRESETS"
              :key="preset.id"
              class="gesture-modal-preset"
              :class="{ 'gesture-modal-preset--active': draftPattern === sequenceToPatternId(preset.sequence) }"
              @click="applyPreset(preset.sequence)"
            >
              {{ preset.label }}
            </view>
          </view>
        </view>

        <GestureGridPicker
          ref="gridRef"
          v-model="draftPattern"
          :canvas-id="canvasId"
        />

        <text class="gesture-modal-current">当前：{{ patternDisplayLabel(draftPattern) }}</text>
      </view>

      <view class="gesture-modal-footer">
        <view class="gesture-modal-btn gesture-modal-btn--ghost" @click="close">取消</view>
        <view class="gesture-modal-btn" @click="confirm">确定</view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.gesture-modal-mask {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  background: rgba(15, 23, 42, 0.45);
}

.gesture-modal-sheet {
  display: flex;
  width: 100%;
  max-height: 88vh;
  flex-direction: column;
  border-radius: 28rpx 28rpx 0 0;
  background: #fff;
}

.gesture-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 32rpx 12rpx;
}

.gesture-modal-title {
  color: $text-primary;
  font-size: 34rpx;
  font-weight: 700;
}

.gesture-modal-close {
  display: flex;
  width: 56rpx;
  height: 56rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f5f8ff;
}

.gesture-modal-body {
  padding: 0 32rpx 24rpx;
}

.gesture-modal-subtitle {
  display: block;
  margin-bottom: 20rpx;
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.5;
}

.gesture-modal-presets {
  margin-bottom: 20rpx;
}

.gesture-modal-presets__label {
  display: block;
  margin-bottom: 12rpx;
  color: $text-secondary;
  font-size: 24rpx;
  font-weight: 600;
}

.gesture-modal-presets__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.gesture-modal-preset {
  padding: 10rpx 22rpx;
  border: 1rpx solid rgba(15, 23, 42, 0.08);
  border-radius: 999rpx;
  background: #f7faff;
  color: $text-secondary;
  font-size: 24rpx;
}

.gesture-modal-preset--active {
  border-color: rgba($primary, 0.35);
  background: rgba($primary, 0.1);
  color: $primary;
  font-weight: 600;
}

.gesture-modal-current {
  display: block;
  margin-top: 16rpx;
  color: $text-secondary;
  font-size: 24rpx;
  text-align: center;
}

.gesture-modal-footer {
  display: flex;
  gap: 16rpx;
  padding: 16rpx 32rpx calc(16rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid rgba(15, 23, 42, 0.06);
}

.gesture-modal-btn {
  display: flex;
  flex: 1;
  height: 88rpx;
  align-items: center;
  justify-content: center;
  border-radius: 999rpx;
  background: $primary;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
}

.gesture-modal-btn--ghost {
  background: #fff;
  border: 2rpx solid rgba($primary, 0.25);
  color: $primary;
}
</style>
