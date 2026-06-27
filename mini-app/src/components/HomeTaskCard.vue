<script setup lang="ts">
import { computed } from 'vue'

import type { StudentTask } from '@/services/student'

const props = withDefaults(
  defineProps<{
    task: StudentTask
    embedded?: boolean
  }>(),
  {
    embedded: false,
  },
)

const emit = defineEmits<{
  (event: 'click', task: StudentTask): void
}>()

const displayTime = computed(() => {
  const match = props.task.timeWindow.match(/(\d{2}:\d{2})\s*$/)
  if (match) {
    return match[1]
  }
  const endMatch = props.task.deadline.match(/(\d{2}:\d{2})/)
  return endMatch?.[1] ?? '--:--'
})

const deadlineText = computed(() => {
  const text = props.task.deadline.replace(/\s*截止\s*$/, '')
  if (text.startsWith('截止时间：') || text.startsWith('截止：')) {
    return text
  }
  return `截止时间：${text}`
})

const statusLabel = computed(() => {
  if (props.task.status === 'normal' || props.task.status === 'ended') {
    return '已完成'
  }
  return '待完成'
})

const statusClass = computed(() =>
  props.task.status === 'normal' || props.task.status === 'ended' ? 'done' : 'pending',
)
</script>

<template>
  <view
    class="home-task-card"
    :class="{ 'home-task-card--embedded': embedded }"
    @click="emit('click', task)"
  >
    <view class="home-task-card__time-col">
      <text class="home-task-card__time">{{ displayTime }}</text>
      <text class="home-task-card__status" :class="`home-task-card__status--${statusClass}`">
        {{ statusLabel }}
      </text>
    </view>

    <view class="home-task-card__divider" aria-hidden="true"></view>

    <view class="home-task-card__body">
      <view class="home-task-card__title-row">
        <text class="home-task-card__title">{{ task.title }}</text>
        <text class="home-task-card__type-tag">{{ task.type }}</text>
      </view>
      <view class="home-task-card__meta-row">
        <text class="home-task-card__meta-icon">📍</text>
        <text class="home-task-card__meta">{{ task.locationName }}</text>
      </view>
      <view class="home-task-card__meta-row">
        <text class="home-task-card__meta-icon">📋</text>
        <text class="home-task-card__meta">{{ task.description }}</text>
      </view>
      <view class="home-task-card__meta-row">
        <text class="home-task-card__meta-icon">⏰</text>
        <text class="home-task-card__meta">{{ deadlineText }}</text>
      </view>
    </view>

    <view class="home-task-card__arrow-btn" aria-hidden="true">
      <text class="home-task-card__arrow">›</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.home-task-card {
  display: flex;
  align-items: stretch;
  padding: 28rpx 20rpx 28rpx 24rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 12rpx 32rpx rgba(15, 107, 214, 0.08);
}

.home-task-card--embedded {
  padding: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.home-task-card__time-col {
  display: flex;
  width: 112rpx;
  flex-shrink: 0;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
}

.home-task-card__time {
  color: $primary;
  font-size: 44rpx;
  font-weight: 700;
  line-height: 1.1;
}

.home-task-card__status {
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 600;
  white-space: nowrap;
}

.home-task-card__status--pending {
  background: rgba($warning, 0.14);
  color: $warning;
}

.home-task-card__status--done {
  background: rgba($success, 0.14);
  color: $success;
}

.home-task-card__divider {
  width: 1rpx;
  flex-shrink: 0;
  align-self: stretch;
  margin: 4rpx 20rpx 4rpx 8rpx;
  background: rgba(15, 23, 42, 0.08);
}

.home-task-card__body {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 10rpx;
}

.home-task-card__title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12rpx;
}

.home-task-card__title {
  flex: 1;
  min-width: 0;
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.home-task-card__type-tag {
  flex-shrink: 0;
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  background: rgba($primary, 0.1);
  color: $primary;
  font-size: 22rpx;
}

.home-task-card__meta-row {
  display: flex;
  align-items: flex-start;
  gap: 8rpx;
}

.home-task-card__meta-icon {
  flex-shrink: 0;
  color: $text-muted;
  font-size: 22rpx;
  line-height: 1.5;
}

.home-task-card__meta {
  flex: 1;
  min-width: 0;
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.5;
}

.home-task-card__arrow-btn {
  display: flex;
  width: 48rpx;
  height: 48rpx;
  flex-shrink: 0;
  align-self: center;
  align-items: center;
  justify-content: center;
  margin-left: 8rpx;
  border-radius: 50%;
  background: #f2f4f7;
}

.home-task-card__arrow {
  color: #98a2b3;
  font-size: 36rpx;
  font-weight: 600;
  line-height: 1;
}
</style>
