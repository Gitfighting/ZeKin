<script setup lang="ts">
import StatusTag from '@/components/StatusTag.vue'
import type { StudentTask } from '@/services/student'

defineProps<{
  task: StudentTask
}>()

const emit = defineEmits<{
  (event: 'action', task: StudentTask): void
  (event: 'click', task: StudentTask): void
}>()
</script>

<template>
  <view class="task-card" @click="emit('click', task)">
    <view class="task-card__header">
      <view class="task-card__title-group">
        <text class="task-card__type">{{ task.type }}</text>
        <text class="task-card__title">{{ task.title }}</text>
      </view>
      <StatusTag :status="task.status" />
    </view>

    <text class="task-card__description">{{ task.description }}</text>

    <view class="task-card__meta">
      <text class="task-card__deadline">截止时间：{{ task.deadline }}</text>
      <button class="task-card__action" type="primary" @click.stop="emit('action', task)">
        {{ task.actionText }}
      </button>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.task-card {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.08);
}

.task-card__header,
.task-card__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18rpx;
}

.task-card__title-group {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  min-width: 0;
}

.task-card__type {
  color: $primary;
  font-size: 24rpx;
  font-weight: 600;
}

.task-card__title {
  color: $text-primary;
  font-size: 34rpx;
  font-weight: 700;
}

.task-card__description,
.task-card__deadline {
  color: $text-secondary;
  font-size: 26rpx;
  line-height: 1.5;
}

.task-card__action {
  margin: 0;
  padding: 0 28rpx;
  height: 72rpx;
  line-height: 72rpx;
  border: none;
  border-radius: 999rpx;
  background: $primary;
  font-size: 26rpx;
  font-weight: 600;
}
</style>
