<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { ref } from 'vue'

import StatusTag from '@/components/StatusTag.vue'
import { logInfo, showError } from '@/services/feedback'
import { getStudentMessages, type MessageItem } from '@/services/student'

const messages = ref<MessageItem[]>([])

const tagStatusMap: Record<MessageItem['type'], 'normal' | 'in-progress' | 'pending'> = {
  reminder: 'pending',
  teacher_feedback: 'in-progress',
  appeal_result: 'normal',
}

const labelMap: Record<MessageItem['type'], string> = {
  reminder: '提醒',
  teacher_feedback: '反馈',
  appeal_result: '结果',
}

onShow(async () => {
  try {
    messages.value = await getStudentMessages()
    logInfo('学生消息加载成功', { count: messages.value.length })
  } catch (error) {
    messages.value = []
    showError(error, '消息加载失败')
  }
})
</script>

<template>
  <scroll-view scroll-y class="messages-page">
    <view class="messages-page__hero">
      <text class="messages-page__title">消息</text>
      <text class="messages-page__subtitle">任务提醒、辅导员反馈与申诉进度都在这里</text>
    </view>

    <view class="messages-page__list">
      <view v-for="item in messages" :key="item.id" class="messages-page__card">
        <view class="messages-page__card-header">
          <text class="messages-page__card-title">{{ item.title }}</text>
          <StatusTag :status="tagStatusMap[item.type]" />
        </view>
        <text class="messages-page__card-type">{{ labelMap[item.type] }}</text>
        <text class="messages-page__card-content">{{ item.content }}</text>
        <text class="messages-page__card-time">{{ item.time }}</text>
      </view>
      <view v-if="messages.length === 0" class="messages-page__empty">
        <text>暂无消息</text>
      </view>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.messages-page {
  min-height: 100vh;
  background: $page-bg;
}

.messages-page__hero {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding: 112rpx 28rpx 34rpx;
  background: $mobile-gradient;
}

.messages-page__title,
.messages-page__subtitle {
  color: #ffffff;
}

.messages-page__title {
  font-size: 48rpx;
  font-weight: 700;
}

.messages-page__subtitle {
  font-size: 28rpx;
  opacity: 0.95;
}

.messages-page__list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  padding: 24rpx;
}

.messages-page__card {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.08);
}

.messages-page__card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.messages-page__card-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.messages-page__card-type,
.messages-page__card-time {
  color: $text-secondary;
  font-size: 24rpx;
}

.messages-page__card-content {
  color: $text-primary;
  font-size: 28rpx;
  line-height: 1.6;
}

.messages-page__empty {
  padding: 32rpx;
  border-radius: 24rpx;
  background: $card-bg;
  color: $text-secondary;
  font-size: 26rpx;
  text-align: center;
}
</style>
