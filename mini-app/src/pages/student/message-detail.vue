<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

import StatusTag from '@/components/StatusTag.vue'
import { refreshStudentUnreadMessageCount } from '@/composables/useStudentUnreadMessages'
import { logInfo, showError } from '@/services/feedback'
import { getStudentMessageDetail, type MessageItem } from '@/services/student'

const MESSAGE_PREVIEW_KEY = 'student_message_preview'

const message = ref<MessageItem | null>(null)
const loading = ref(true)

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

function resolveMessageId(raw: unknown): string | undefined {
  if (raw === undefined || raw === null || raw === '') {
    return undefined
  }
  return String(raw)
}

function readPreview(id: string): MessageItem | null {
  if (typeof uni === 'undefined') {
    return null
  }
  try {
    const cached = uni.getStorageSync(MESSAGE_PREVIEW_KEY)
    if (!cached) {
      return null
    }
    const item = JSON.parse(String(cached)) as MessageItem
    return item.id === id ? item : null
  } catch {
    return null
  }
}

function handleBack() {
  uni.navigateBack({ delta: 1 })
}

async function loadMessage(id?: string) {
  loading.value = true
  message.value = id ? readPreview(id) : null

  if (!id) {
    loading.value = false
    uni.showToast({ title: '缺少消息编号', icon: 'none' })
    return
  }

  try {
    message.value = await getStudentMessageDetail(id)
    logInfo('学生消息详情加载成功', { messageId: id, read: message.value.read })
    try {
      await refreshStudentUnreadMessageCount()
    } catch {
      // 未读角标刷新失败不影响详情展示
    }
  } catch (error) {
    if (!message.value) {
      showError(error, '消息详情加载失败')
    }
  } finally {
    loading.value = false
  }
}

onLoad((options) => {
  void loadMessage(resolveMessageId(options?.id))
})
</script>

<template>
  <scroll-view scroll-y class="message-detail-page">
    <view class="message-detail-page__hero">
      <view class="message-detail-page__hero-bg-box" aria-hidden="true">
        <image class="message-detail-page__hero-bg" src="/static/student-home-hero.png" mode="aspectFill" />
      </view>
      <view class="message-detail-page__hero-mask" aria-hidden="true"></view>
      <view class="message-detail-page__nav" @click="handleBack">
        <text class="message-detail-page__nav-back">‹</text>
      </view>
      <view class="message-detail-page__hero-content">
        <text class="message-detail-page__title">消息</text>
        <text class="message-detail-page__subtitle">消息详情</text>
      </view>
    </view>

    <view class="message-detail-page__body">
      <view v-if="loading" class="message-detail-page__card message-detail-page__card--state">
        <text class="message-detail-page__state-text">消息加载中...</text>
      </view>

      <template v-else-if="message">
        <view class="message-detail-page__card">
          <view class="message-detail-page__header">
            <text class="message-detail-page__card-title">{{ message.title }}</text>
            <StatusTag :status="tagStatusMap[message.type]" />
          </view>
          <view class="message-detail-page__meta-row">
            <text class="message-detail-page__meta-label">消息类型</text>
            <text class="message-detail-page__meta-value">{{ labelMap[message.type] }}</text>
          </view>
          <view class="message-detail-page__meta-row">
            <text class="message-detail-page__meta-label">消息时间</text>
            <text class="message-detail-page__meta-value">{{ message.time }}</text>
          </view>
          <view class="message-detail-page__meta-row">
            <text class="message-detail-page__meta-label">阅读状态</text>
            <text class="message-detail-page__meta-value">{{ message.read ? '已读' : '未读' }}</text>
          </view>
        </view>

        <view class="message-detail-page__card">
          <text class="message-detail-page__section-title">消息内容</text>
          <text class="message-detail-page__content">{{ message.content || '暂无消息正文' }}</text>
        </view>
      </template>

      <view v-else class="message-detail-page__card message-detail-page__card--state">
        <text class="message-detail-page__state-text">消息不存在或已失效</text>
      </view>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.message-detail-page {
  min-height: 100vh;
  background: #f5f8fc;
}

.message-detail-page__hero {
  position: relative;
  height: 360rpx;
  overflow: hidden;
}

.message-detail-page__hero-bg-box {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 175%;
}

.message-detail-page__hero-bg {
  width: 100%;
  height: 100%;
}

.message-detail-page__hero-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(15, 120, 255, 0.08) 0%, rgba(15, 120, 255, 0.42) 100%);
}

.message-detail-page__nav {
  position: absolute;
  top: 88rpx;
  left: 24rpx;
  z-index: 3;
  display: flex;
  width: 64rpx;
  height: 64rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
}

.message-detail-page__nav-back {
  color: #fff;
  font-size: 48rpx;
  font-weight: 300;
  line-height: 1;
}

.message-detail-page__hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding: 140rpx 32rpx 48rpx;
}

.message-detail-page__title,
.message-detail-page__subtitle {
  color: #fff;
}

.message-detail-page__title {
  font-size: 48rpx;
  font-weight: 700;
}

.message-detail-page__subtitle {
  font-size: 26rpx;
  line-height: 1.55;
  opacity: 0.96;
}

.message-detail-page__body {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding: 0 24rpx 48rpx;
  margin-top: -24rpx;
}

.message-detail-page__card {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  padding: 32rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 12rpx 36rpx rgba(15, 107, 214, 0.07);
}

.message-detail-page__card--state {
  align-items: center;
  padding: 64rpx 32rpx;
}

.message-detail-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16rpx;
}

.message-detail-page__card-title {
  flex: 1;
  min-width: 0;
  color: $text-primary;
  font-size: 34rpx;
  font-weight: 700;
  line-height: 1.4;
}

.message-detail-page__meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24rpx;
  padding-top: 8rpx;
}

.message-detail-page__meta-label {
  flex-shrink: 0;
  color: $text-secondary;
  font-size: 26rpx;
}

.message-detail-page__meta-value {
  color: $text-primary;
  font-size: 26rpx;
  text-align: right;
}

.message-detail-page__section-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.message-detail-page__content {
  color: $text-primary;
  font-size: 30rpx;
  line-height: 1.75;
  white-space: pre-wrap;
}

.message-detail-page__state-text {
  color: $text-secondary;
  font-size: 28rpx;
  text-align: center;
}
</style>
