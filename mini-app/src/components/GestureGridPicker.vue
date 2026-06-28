<script setup lang="ts">
import { getCurrentInstance, nextTick, onMounted, ref, watch } from 'vue'

import {
  patternIdToSequence,
  sequenceToPatternId,
} from '@/constants/gesture-patterns'

const props = withDefaults(
  defineProps<{
    modelValue?: string
    canvasId?: string
    sizeRpx?: number
  }>(),
  {
    modelValue: '',
    canvasId: 'gestureGridCanvas',
    sizeRpx: 560,
  },
)

const emit = defineEmits<{
  (event: 'update:modelValue', value: string): void
  (event: 'change', value: string): void
}>()

const instance = getCurrentInstance()
const componentProxy = instance?.proxy ?? instance
const sequence = ref<number[]>([])
const gridRect = ref({ width: 0, height: 0, left: 0, top: 0 })
const drawing = ref(false)

function dotStyle(index: number) {
  const col = (index - 1) % 3
  const row = Math.floor((index - 1) / 3)
  return {
    left: `${(col / 2) * 100}%`,
    top: `${(row / 2) * 100}%`,
  }
}

function centerPx(index: number, size: number) {
  const col = (index - 1) % 3
  const row = Math.floor((index - 1) / 3)
  return {
    x: (col / 2) * size,
    y: (row / 2) * size,
  }
}

function syncFromModel(value?: string) {
  sequence.value = patternIdToSequence(value)
  void drawLines()
}

function emitSequence() {
  const pattern = sequenceToPatternId(sequence.value)
  emit('update:modelValue', pattern)
  emit('change', pattern)
}

function measureGrid() {
  if (typeof uni === 'undefined') {
    return Promise.resolve()
  }
  return new Promise<void>((resolve) => {
    uni.createSelectorQuery()
      .in(componentProxy as unknown as WechatMiniprogram.Component.TrivialInstance)
      .select('.gesture-grid__board')
      .boundingClientRect((rect) => {
        if (rect && !Array.isArray(rect)) {
          gridRect.value = {
            width: rect.width ?? 0,
            height: rect.height ?? 0,
            left: rect.left ?? 0,
            top: rect.top ?? 0,
          }
        }
        resolve()
      })
      .exec()
  })
}

function hitTest(clientX: number, clientY: number): number | null {
  const { width, height, left, top } = gridRect.value
  if (!width || !height) {
    return null
  }
  const x = clientX - left
  const y = clientY - top
  const threshold = Math.min(width, height) * 0.14

  for (let index = 1; index <= 9; index += 1) {
    const center = centerPx(index, width)
    const distance = Math.hypot(x - center.x, y - center.y)
    if (distance <= threshold) {
      return index
    }
  }
  return null
}

function appendDot(index: number | null) {
  if (!index || sequence.value.includes(index)) {
    return
  }
  sequence.value = [...sequence.value, index]
  emitSequence()
  void drawLines()
}

function touchPoint(event: TouchEvent) {
  const touch = event.changedTouches?.[0] ?? event.touches?.[0]
  if (!touch) {
    return null
  }
  return { x: touch.clientX, y: touch.clientY }
}

async function onTouchStart(event: TouchEvent) {
  drawing.value = true
  await measureGrid()
  const point = touchPoint(event)
  if (!point) {
    return
  }
  appendDot(hitTest(point.x, point.y))
}

async function onTouchMove(event: TouchEvent) {
  if (!drawing.value) {
    return
  }
  const point = touchPoint(event)
  if (!point) {
    return
  }
  appendDot(hitTest(point.x, point.y))
}

function onTouchEnd() {
  drawing.value = false
}

function reset() {
  sequence.value = []
  emitSequence()
  void drawLines()
}

function setSequence(next: number[]) {
  sequence.value = [...next]
  emitSequence()
  void drawLines()
}

async function drawLines() {
  await nextTick()
  if (typeof uni === 'undefined') {
    return
  }
  const ctx = uni.createCanvasContext(
    props.canvasId,
    componentProxy as unknown as WechatMiniprogram.Component.TrivialInstance,
  )
  const size = gridRect.value.width || 280
  ctx.clearRect(0, 0, size, size)
  ctx.setStrokeStyle('#1677ff')
  ctx.setLineWidth(5)
  ctx.setLineCap('round')
  ctx.setLineJoin('round')

  const points = sequence.value.map((index) => centerPx(index, size))
  if (points.length > 1) {
    ctx.beginPath()
    ctx.moveTo(points[0].x, points[0].y)
    for (let i = 1; i < points.length; i += 1) {
      ctx.lineTo(points[i].x, points[i].y)
    }
    ctx.stroke()
  }

  sequence.value.forEach((index) => {
    const center = centerPx(index, size)
    ctx.setFillStyle('#1677ff')
    ctx.beginPath()
    ctx.arc(center.x, center.y, 10, 0, Math.PI * 2)
    ctx.fill()
  })

  ctx.draw()
}

watch(
  () => props.modelValue,
  (value) => {
    const next = patternIdToSequence(value)
    const current = sequenceToPatternId(sequence.value)
    if (sequenceToPatternId(next) !== current) {
      syncFromModel(value)
    }
  },
  { immediate: true },
)

onMounted(async () => {
  await measureGrid()
  syncFromModel(props.modelValue)
})

defineExpose({ reset, setSequence })
</script>

<template>
  <view class="gesture-grid">
    <view
      class="gesture-grid__board"
      :style="{ width: `${sizeRpx}rpx`, height: `${sizeRpx}rpx` }"
      @touchstart.stop.prevent="onTouchStart"
      @touchmove.stop.prevent="onTouchMove"
      @touchend.stop.prevent="onTouchEnd"
      @touchcancel.stop.prevent="onTouchEnd"
    >
      <canvas
        :canvas-id="canvasId"
        :id="canvasId"
        class="gesture-grid__canvas"
        :style="{ width: `${sizeRpx}rpx`, height: `${sizeRpx}rpx` }"
      />
      <view
        v-for="index in 9"
        :key="index"
        class="gesture-grid__dot"
        :class="{ 'gesture-grid__dot--active': sequence.includes(index) }"
        :style="dotStyle(index)"
      >
        <text class="gesture-grid__dot-text">{{ index }}</text>
      </view>
    </view>
    <view class="gesture-grid__actions">
      <text class="gesture-grid__hint">在九宫格上滑动，一笔绘制手势图案</text>
      <text class="gesture-grid__reset" @click="reset">重新绘制</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.gesture-grid {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.gesture-grid__board {
  position: relative;
  touch-action: none;
}

.gesture-grid__canvas {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}

.gesture-grid__dot {
  position: absolute;
  z-index: 2;
  display: flex;
  width: 72rpx;
  height: 72rpx;
  align-items: center;
  justify-content: center;
  border: 4rpx solid rgba($primary, 0.25);
  border-radius: 50%;
  background: #fff;
  transform: translate(-50%, -50%);
  box-shadow: 0 8rpx 20rpx rgba(15, 107, 214, 0.08);
}

.gesture-grid__dot--active {
  border-color: $primary;
  background: rgba($primary, 0.12);
}

.gesture-grid__dot-text {
  color: $primary;
  font-size: 28rpx;
  font-weight: 700;
}

.gesture-grid__actions {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.gesture-grid__hint {
  flex: 1;
  color: $text-secondary;
  font-size: 22rpx;
  line-height: 1.5;
}

.gesture-grid__reset {
  color: $primary;
  font-size: 24rpx;
  font-weight: 600;
}
</style>
