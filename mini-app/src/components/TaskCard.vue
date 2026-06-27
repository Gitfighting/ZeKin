<script setup lang="ts">
import { computed } from 'vue'

import type { StudentTask } from '@/services/student'

const props = defineProps<{
  task: StudentTask
}>()

const emit = defineEmits<{
  (event: 'action', task: StudentTask): void
  (event: 'click', task: StudentTask): void
}>()

type TaskTone = 'blue' | 'green' | 'orange' | 'purple'

function inferCategory(task: StudentTask): { label: string; tone: TaskTone; icon: string } {
  const haystack = `${task.title}${task.type}${task.description}`
  if (/宿舍|查寝|晚间/.test(haystack)) {
    return { label: '日常任务', tone: 'blue', icon: '🏠' }
  }
  if (/课堂|课程|上课/.test(haystack)) {
    return { label: '课堂类', tone: 'green', icon: '🎓' }
  }
  if (/实习|实践|校外/.test(haystack)) {
    return { label: '实习类', tone: 'orange', icon: '💼' }
  }
  if (/活动|班团|会议/.test(haystack)) {
    return { label: '活动类', tone: 'purple', icon: '👥' }
  }
  return { label: task.type || '打卡任务', tone: 'blue', icon: '📋' }
}

const category = computed(() => inferCategory(props.task))

const statusInfo = computed(() => {
  switch (props.task.status) {
    case 'in-progress':
      return { label: '待完成', tone: 'pending' as const }
    case 'pending':
      return {
        label: props.task.attachmentRule.required ? '待提交' : '待完成',
        tone: 'pending' as const,
      }
    case 'normal':
      return { label: '已完成', tone: 'done' as const }
    case 'ended':
      return { label: '已结束', tone: 'ended' as const }
    case 'exception':
      return { label: '异常', tone: 'exception' as const }
    default:
      return { label: '待完成', tone: 'pending' as const }
  }
})

const requirementsText = computed(() => {
  if (props.task.requirements.length) {
    return props.task.requirements.slice(0, 3).join('+')
  }
  return '按任务要求'
})

const isPrimaryAction = computed(() =>
  ['in-progress', 'pending', 'exception'].includes(props.task.status),
)
</script>

<template>
  <view class="task-card" @click="emit('click', task)">
    <view class="task-card__icon" :class="`task-card__icon--${category.tone}`">
      <text class="task-card__icon-text">{{ category.icon }}</text>
    </view>

    <view class="task-card__body">
      <view class="task-card__header">
        <view class="task-card__title-group">
          <text class="task-card__title">{{ task.title }}</text>
          <text class="task-card__tag" :class="`task-card__tag--${category.tone}`">{{ category.label }}</text>
        </view>
        <text class="task-card__status" :class="`task-card__status--${statusInfo.tone}`">
          {{ statusInfo.label }}
        </text>
      </view>

      <view class="task-card__meta">
        <text class="task-card__meta-icon">🕐</text>
        <text class="task-card__meta-text">{{ task.timeWindow }}</text>
      </view>
      <view class="task-card__meta">
        <text class="task-card__meta-icon">📍</text>
        <text class="task-card__meta-text">{{ requirementsText }}</text>
      </view>

      <view class="task-card__footer">
        <button
          class="task-card__action"
          :class="{ 'task-card__action--primary': isPrimaryAction, 'task-card__action--outline': !isPrimaryAction }"
          @click.stop="emit('action', task)"
        >
          {{ task.actionText }}
        </button>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.task-card {
  display: flex;
  gap: 20rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 12rpx 36rpx rgba(15, 107, 214, 0.07);
}

.task-card__icon {
  display: flex;
  width: 88rpx;
  height: 88rpx;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 20rpx;
}

.task-card__icon--blue {
  background: linear-gradient(135deg, #3b9bff 0%, #1677ff 100%);
}

.task-card__icon--green {
  background: linear-gradient(135deg, #34d399 0%, #20c55a 100%);
}

.task-card__icon--orange {
  background: linear-gradient(135deg, #ffb347 0%, #ff9f1a 100%);
}

.task-card__icon--purple {
  background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
}

.task-card__icon-text {
  font-size: 40rpx;
  line-height: 1;
}

.task-card__body {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 12rpx;
}

.task-card__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12rpx;
}

.task-card__title-group {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-wrap: wrap;
  align-items: center;
  gap: 10rpx;
}

.task-card__title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.35;
}

.task-card__tag {
  flex-shrink: 0;
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.task-card__tag--blue {
  background: rgba($primary, 0.1);
  color: $primary;
}

.task-card__tag--green {
  background: rgba($success, 0.12);
  color: $success;
}

.task-card__tag--orange {
  background: rgba($warning, 0.14);
  color: $warning;
}

.task-card__tag--purple {
  background: rgba(#7c3aed, 0.12);
  color: #7c3aed;
}

.task-card__status {
  flex-shrink: 0;
  font-size: 24rpx;
  font-weight: 600;
  white-space: nowrap;
}

.task-card__status--pending {
  color: $warning;
}

.task-card__status--done {
  color: $success;
}

.task-card__status--ended {
  color: $text-muted;
}

.task-card__status--exception {
  color: $danger;
}

.task-card__meta {
  display: flex;
  align-items: flex-start;
  gap: 8rpx;
}

.task-card__meta-icon {
  flex-shrink: 0;
  font-size: 22rpx;
  line-height: 1.5;
}

.task-card__meta-text {
  flex: 1;
  min-width: 0;
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.5;
}

.task-card__footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 4rpx;
}

.task-card__action {
  margin: 0;
  padding: 0 28rpx;
  height: 64rpx;
  line-height: 64rpx;
  border-radius: 999rpx;
  font-size: 26rpx;
  font-weight: 600;
}

.task-card__action--primary {
  border: none;
  background: $primary;
  color: #fff;
}

.task-card__action--outline {
  border: 2rpx solid rgba($primary, 0.35);
  background: #fff;
  color: $primary;
}
</style>
