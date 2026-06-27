<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import StatusTag from '@/components/StatusTag.vue'
import StudentTabBar from '@/components/StudentTabBar.vue'
import { refreshStudentUnreadMessageCount } from '@/composables/useStudentUnreadMessages'
import { logInfo, showError } from '@/services/feedback'
import { getStudentMessages, type MessageItem } from '@/services/student'

const messages = ref<MessageItem[]>([])
const unreadCount = ref(0)

const tagStatusMap: Record<MessageItem['type'], 'normal' | 'in-progress' | 'pending'> = {
  reminder: 'pending',
  teacher_feedback: 'in-progress',
  appeal_result: 'normal',
}

const labelMap: Record<MessageItem['type'], string> = {
  reminder: '消息提醒',
  teacher_feedback: '教师消息',
  appeal_result: '消息结果',
}

const subtitleText = computed(() => {
  if (unreadCount.value > 0) {
    return `${unreadCount.value} 条未读消息 · 打卡提醒、教师反馈与申诉通知`
  }
  return '查看打卡提醒、教师反馈与申诉相关消息'
})

function openMessage(item: MessageItem) {
  if (typeof uni !== 'undefined') {
    uni.setStorageSync('student_message_preview', JSON.stringify(item))
  }
  uni.navigateTo({
    url: `/pages/student/message-detail?id=${item.id}`,
  })
}

onShow(async () => {
  try {
    const result = await getStudentMessages()
    messages.value = result.messages
    unreadCount.value = result.unreadCount
    await refreshStudentUnreadMessageCount()
    logInfo('学生消息加载成功', {
      count: messages.value.length,
      unreadCount: unreadCount.value,
    })
  } catch (error) {
    messages.value = []
    unreadCount.value = 0
    showError(error, '消息加载失败')
  }
})
</script>

<template>
  <view class="student-tab-page">
    <scroll-view scroll-y class="messages-page student-tab-page__scroll">
      <view class="messages-page__hero">
        <view class="messages-page__hero-bg-box" aria-hidden="true">
          <image class="messages-page__hero-bg" src="/static/student-home-hero.png" mode="aspectFill" />
        </view>
        <view class="messages-page__hero-mask" aria-hidden="true"></view>
        <view class="messages-page__hero-content">
          <view class="messages-page__title-row">
            <text class="messages-page__title">消息</text>
            <view v-if="unreadCount > 0" class="messages-page__unread-pill">
              <text>{{ unreadCount }} 条未读</text>
            </view>
          </view>
          <text class="messages-page__subtitle">{{ subtitleText }}</text>
        </view>
      </view>

      <view class="messages-page__list">
        <view
          v-for="item in messages"
          :key="item.id"
          class="messages-page__card"
          :class="{ 'messages-page__card--unread': !item.read }"
          @click="openMessage(item)"
        >
          <view class="messages-page__card-header">
            <view class="messages-page__title-group">
              <view v-if="!item.read" class="messages-page__dot" aria-hidden="true"></view>
              <text class="messages-page__card-title">{{ item.title }}</text>
            </view>
            <StatusTag :status="tagStatusMap[item.type]" />
          </view>
          <text class="messages-page__card-type">{{ labelMap[item.type] }}</text>
          <text class="messages-page__card-content">{{ item.content }}</text>
          <text class="messages-page__card-time">{{ item.time }}</text>
        </view>
        <view v-if="messages.length === 0" class="messages-page__empty">
          <text class="messages-page__empty-icon">💬</text>
          <text>暂无消息</text>
        </view>
      </view>
      <view class="tab-page__safe-bottom"></view>
    </scroll-view>
    <StudentTabBar active="messages" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.messages-page {
  background: #f5f8fc;
}

.messages-page__hero {
  position: relative;
  height: 360rpx;
  overflow: hidden;
}

.messages-page__hero-bg-box {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 175%;
}

.messages-page__hero-bg {
  width: 100%;
  height: 100%;
}

.messages-page__hero-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(15, 120, 255, 0.08) 0%, rgba(15, 120, 255, 0.42) 100%);
}

.messages-page__hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding: 112rpx 32rpx 48rpx;
}

.messages-page__title-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.messages-page__title,
.messages-page__subtitle {
  color: #ffffff;
}

.messages-page__title {
  font-size: 48rpx;
  font-weight: 700;
}

.messages-page__unread-pill {
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.22);
}

.messages-page__unread-pill text {
  color: #fff;
  font-size: 24rpx;
  font-weight: 600;
}

.messages-page__subtitle {
  max-width: 620rpx;
  font-size: 26rpx;
  line-height: 1.55;
  opacity: 0.96;
}

.messages-page__list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  padding: 24rpx;
  margin-top: -24rpx;
}

.messages-page__card {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 12rpx 36rpx rgba(15, 107, 214, 0.07);
}

.messages-page__card--unread {
  border: 2rpx solid rgba($primary, 0.12);
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
}

.messages-page__card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.messages-page__title-group {
  display: flex;
  align-items: center;
  gap: 12rpx;
  min-width: 0;
}

.messages-page__dot {
  width: 14rpx;
  height: 14rpx;
  flex-shrink: 0;
  border-radius: 50%;
  background: #ff4d4f;
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  padding: 64rpx 32rpx;
  border-radius: 24rpx;
  background: $card-bg;
  color: $text-secondary;
  font-size: 26rpx;
  text-align: center;
}

.messages-page__empty-icon {
  font-size: 56rpx;
}

.tab-page__safe-bottom {
  height: $tab-bar-safe-bottom;
}
</style>
