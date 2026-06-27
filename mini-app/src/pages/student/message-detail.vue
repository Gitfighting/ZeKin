<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import { refreshStudentUnreadMessageCount } from '@/composables/useStudentUnreadMessages'
import { logInfo, showError } from '@/services/feedback'
import {
  enrichMessageWithTask,
  getStudentMessageDetail,
  isCheckinReminderMessage,
  resolveCheckinTaskByTitle,
  type MessageItem,
} from '@/services/student'

const MESSAGE_PREVIEW_KEY = 'student_message_preview'

const message = ref<MessageItem | null>(null)
const loading = ref(true)
const checkinTaskId = ref<string>()
const navigating = ref(false)

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

const showCheckinAction = computed(() => message.value && isCheckinReminderMessage(message.value))

const badgeLabel = computed(() => {
  if (!message.value) {
    return ''
  }
  if (message.value.type === 'appeal_result') {
    return '申诉结果'
  }
  if (message.value.type === 'teacher_feedback') {
    return '教师消息'
  }
  if (isCheckinReminderMessage(message.value)) {
    return '教师消息'
  }
  return '系统通知'
})

const displayTaskName = computed(() => message.value?.taskName ?? message.value?.title ?? '—')
const displayGroupName = computed(() => message.value?.groupName || '—')
const displaySendTime = computed(() => message.value?.time ?? '—')
const displayTaskDescription = computed(
  () => message.value?.taskDescription ?? message.value?.content ?? '暂无任务说明',
)

async function resolveCheckinTask() {
  if (!message.value || !isCheckinReminderMessage(message.value)) {
    checkinTaskId.value = undefined
    return
  }
  try {
    const task = await resolveCheckinTaskByTitle(message.value.title)
    checkinTaskId.value = task?.id
  } catch {
    checkinTaskId.value = undefined
  }
}

async function handleGoCheckin() {
  if (!message.value || navigating.value) {
    return
  }
  navigating.value = true
  try {
    const task = checkinTaskId.value
      ? { id: checkinTaskId.value }
      : await resolveCheckinTaskByTitle(message.value.title)
    if (task?.id) {
      checkinTaskId.value = task.id
      uni.navigateTo({ url: `/pages/student/checkin-submit?id=${task.id}` })
      return
    }
    uni.showToast({ title: '未找到对应打卡任务', icon: 'none' })
    uni.switchTab({ url: '/pages/student/tasks' })
  } catch (error) {
    showError(error, '跳转签到失败')
  } finally {
    navigating.value = false
  }
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
    message.value = await enrichMessageWithTask(message.value)
    logInfo('学生消息详情加载成功', { messageId: id, read: message.value.read })
    try {
      await refreshStudentUnreadMessageCount()
    } catch {
      // 未读角标刷新失败不影响详情展示
    }
  } catch (error) {
    if (!message.value) {
      showError(error, '消息详情加载失败')
    } else {
      message.value = await enrichMessageWithTask(message.value)
    }
  } finally {
    if (message.value) {
      await resolveCheckinTask()
    }
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
            <view class="message-detail-page__icon" aria-hidden="true">
              <text class="message-detail-page__icon-text">🔔</text>
            </view>
            <view class="message-detail-page__header-main">
              <text class="message-detail-page__card-title">{{ displayTaskName }}</text>
              <text class="message-detail-page__badge">{{ badgeLabel }}</text>
            </view>
          </view>

          <view class="message-detail-page__info-list">
            <view class="message-detail-page__info-row">
              <text class="message-detail-page__info-icon">📋</text>
              <text class="message-detail-page__info-label">任务名称</text>
              <text class="message-detail-page__info-value">{{ displayTaskName }}</text>
            </view>
            <view class="message-detail-page__info-row">
              <text class="message-detail-page__info-icon">👥</text>
              <text class="message-detail-page__info-label">课群名称</text>
              <text class="message-detail-page__info-value">{{ displayGroupName }}</text>
            </view>
            <view class="message-detail-page__info-row">
              <text class="message-detail-page__info-icon">🕒</text>
              <text class="message-detail-page__info-label">发送时间</text>
              <text class="message-detail-page__info-value">{{ displaySendTime }}</text>
            </view>
          </view>

          <view class="message-detail-page__delivered">
            <text class="message-detail-page__delivered-icon">✓</text>
            <text>{{ message.read ? '已读' : '系统已送达' }}</text>
          </view>
        </view>

        <view class="message-detail-page__card">
          <view class="message-detail-page__section-head">
            <view class="message-detail-page__section-icon" aria-hidden="true">
              <text class="message-detail-page__section-icon-text">📝</text>
            </view>
            <text class="message-detail-page__section-title">任务说明</text>
          </view>

          <text class="message-detail-page__content">{{ displayTaskDescription }}</text>

          <view v-if="showCheckinAction" class="message-detail-page__detail-list">
            <view v-if="message.checkinMethods" class="message-detail-page__detail-row">
              <text class="message-detail-page__detail-icon">📍</text>
              <view class="message-detail-page__detail-body">
                <text class="message-detail-page__detail-label">签到方式</text>
                <text class="message-detail-page__detail-value">{{ message.checkinMethods }}</text>
              </view>
            </view>
            <view v-if="message.checkinLocation" class="message-detail-page__detail-row">
              <text class="message-detail-page__detail-icon">📌</text>
              <view class="message-detail-page__detail-body">
                <text class="message-detail-page__detail-label">签到地点</text>
                <text class="message-detail-page__detail-value">{{ message.checkinLocation }}</text>
              </view>
            </view>
            <view v-if="message.timeWindow" class="message-detail-page__detail-row">
              <text class="message-detail-page__detail-icon">⏰</text>
              <view class="message-detail-page__detail-body">
                <text class="message-detail-page__detail-label">签到时间</text>
                <text class="message-detail-page__detail-value">{{ message.timeWindow }}</text>
              </view>
            </view>
          </view>

          <button
            v-if="showCheckinAction"
            class="message-detail-page__checkin-btn"
            :loading="navigating"
            :disabled="navigating"
            @click="handleGoCheckin"
          >
            去签到
          </button>
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
  gap: 20rpx;
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
  gap: 20rpx;
}

.message-detail-page__icon {
  display: flex;
  width: 72rpx;
  height: 72rpx;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 20rpx;
  background: linear-gradient(135deg, #1677ff 0%, #38b6ff 100%);
}

.message-detail-page__icon-text {
  font-size: 34rpx;
}

.message-detail-page__header-main {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 12rpx;
}

.message-detail-page__card-title {
  color: $text-primary;
  font-size: 34rpx;
  font-weight: 700;
  line-height: 1.45;
}

.message-detail-page__badge {
  align-self: flex-start;
  padding: 6rpx 18rpx;
  border-radius: 999rpx;
  background: #eaf4ff;
  color: $primary;
  font-size: 22rpx;
}

.message-detail-page__info-list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  padding-top: 8rpx;
}

.message-detail-page__info-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.message-detail-page__info-icon {
  width: 36rpx;
  flex-shrink: 0;
  font-size: 24rpx;
  text-align: center;
}

.message-detail-page__info-label {
  width: 128rpx;
  flex-shrink: 0;
  color: $text-secondary;
  font-size: 26rpx;
}

.message-detail-page__info-value {
  flex: 1;
  min-width: 0;
  color: $text-primary;
  font-size: 26rpx;
  text-align: right;
}

.message-detail-page__delivered {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8rpx;
  padding-top: 8rpx;
  color: $text-muted;
  font-size: 22rpx;
}

.message-detail-page__delivered-icon {
  display: inline-flex;
  width: 28rpx;
  height: 28rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #eef2f6;
  color: $text-secondary;
  font-size: 18rpx;
}

.message-detail-page__section-head {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.message-detail-page__section-icon {
  display: flex;
  width: 56rpx;
  height: 56rpx;
  align-items: center;
  justify-content: center;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #1677ff 0%, #38b6ff 100%);
}

.message-detail-page__section-icon-text {
  font-size: 28rpx;
}

.message-detail-page__section-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.message-detail-page__content {
  color: $text-secondary;
  font-size: 28rpx;
  line-height: 1.75;
  white-space: pre-wrap;
}

.message-detail-page__detail-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding-top: 8rpx;
}

.message-detail-page__detail-row {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
}

.message-detail-page__detail-icon {
  width: 40rpx;
  flex-shrink: 0;
  font-size: 28rpx;
  line-height: 1.4;
}

.message-detail-page__detail-body {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 6rpx;
}

.message-detail-page__detail-label {
  color: $text-secondary;
  font-size: 24rpx;
}

.message-detail-page__detail-value {
  color: $text-primary;
  font-size: 28rpx;
  line-height: 1.5;
}

.message-detail-page__state-text {
  color: $text-secondary;
  font-size: 28rpx;
  text-align: center;
}

.message-detail-page__checkin-btn {
  width: 100%;
  margin-top: 8rpx;
  border: none;
  border-radius: 999rpx;
  background: $primary;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  line-height: 2.4;
}
</style>
