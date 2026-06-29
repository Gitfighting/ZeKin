<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import { refreshStudentUnreadMessageCount } from '@/composables/useStudentUnreadMessages'
import { useStudentPageHeroLayout } from '@/composables/useStudentPageHeroLayout'
import VectorIcon from '@/components/VectorIcon.vue'
import { UI_ICONS } from '@/constants/ui-icons'
import { logInfo, showError } from '@/services/feedback'
import {
  enrichMessageWithTask,
  getStudentMessageDetail,
  isCheckinReminderMessage,
  resolveCheckinTaskByTitle,
  type MessageItem,
} from '@/services/student'

const MESSAGE_PREVIEW_KEY = 'student_message_preview'

const { brandBarStyle, heroContentStyle, backButtonStyle, navRightStyle } = useStudentPageHeroLayout()

const pageSlogan = '以知铸魂，以勤立身'

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
    <view class="student-page-header-block">
      <view class="student-page-hero">
        <view class="student-page-hero__visual">
          <view class="student-page-hero__bg-window">
            <image class="student-page-hero__bg" src="/static/home.png" mode="widthFix" />
          </view>
        </view>

        <view class="message-detail-page__nav-bar" :style="brandBarStyle">
          <view
            class="message-detail-page__back"
            :style="backButtonStyle"
            aria-label="返回"
            @click="handleBack"
          ></view>
          <view class="message-detail-page__nav-spacer" :style="navRightStyle"></view>
        </view>

        <view class="student-page-hero__content" :style="heroContentStyle">
          <text class="student-page-hero__title">消息</text>
          <text class="student-page-hero__slogan">{{ pageSlogan }}</text>
        </view>
      </view>

      <view v-if="loading" class="message-detail-page__overlap student-page-overlap-card">
        <view class="message-detail-page__overlap-inner message-detail-page__overlap-inner--state">
          <text class="message-detail-page__state-text">消息加载中...</text>
        </view>
      </view>

      <view v-else-if="message" class="message-detail-page__overlap student-page-overlap-card">
        <view class="message-detail-page__overlap-inner">
          <view class="message-detail-page__header">
            <view class="message-detail-page__icon" aria-hidden="true">
              <VectorIcon :src="UI_ICONS.bell" size="40rpx" />
            </view>
            <view class="message-detail-page__header-main">
              <text class="message-detail-page__card-title">{{ displayTaskName }}</text>
              <text class="message-detail-page__badge">{{ badgeLabel }}</text>
            </view>
          </view>

          <view class="message-detail-page__info-list">
            <view class="message-detail-page__info-row">
              <VectorIcon class="message-detail-page__info-icon" :src="UI_ICONS.records" size="28rpx" />
              <text class="message-detail-page__info-label">任务名称</text>
              <text class="message-detail-page__info-value">{{ displayTaskName }}</text>
            </view>
            <view class="message-detail-page__info-row">
              <VectorIcon class="message-detail-page__info-icon" :src="UI_ICONS.classes" size="28rpx" />
              <text class="message-detail-page__info-label">课群名称</text>
              <text class="message-detail-page__info-value">{{ displayGroupName }}</text>
            </view>
            <view class="message-detail-page__info-row">
              <VectorIcon class="message-detail-page__info-icon" :src="UI_ICONS.clock" size="28rpx" />
              <text class="message-detail-page__info-label">发送时间</text>
              <text class="message-detail-page__info-value">{{ displaySendTime }}</text>
            </view>
          </view>

          <view class="message-detail-page__delivered">
            <VectorIcon class="message-detail-page__delivered-icon" :src="UI_ICONS.check" size="28rpx" />
            <text>{{ message.read ? '已读' : '系统已送达' }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="student-page-content-sheet message-detail-page__sheet">
      <template v-if="message && !loading">
        <view class="message-detail-page__card">
          <view class="message-detail-page__section-head">
            <view class="message-detail-page__section-icon" aria-hidden="true">
              <VectorIcon :src="UI_ICONS.document" size="32rpx" />
            </view>
            <text class="message-detail-page__section-title">任务说明</text>
          </view>

          <text class="message-detail-page__content">{{ displayTaskDescription }}</text>

          <view v-if="showCheckinAction" class="message-detail-page__detail-list">
            <view v-if="message.checkinMethods" class="message-detail-page__detail-row">
              <VectorIcon class="message-detail-page__detail-icon" :src="UI_ICONS.checkin" size="28rpx" />
              <view class="message-detail-page__detail-body">
                <text class="message-detail-page__detail-label">签到方式</text>
                <text class="message-detail-page__detail-value">{{ message.checkinMethods }}</text>
              </view>
            </view>
            <view v-if="message.checkinLocation" class="message-detail-page__detail-row">
              <VectorIcon class="message-detail-page__detail-icon" :src="UI_ICONS.location" size="28rpx" />
              <view class="message-detail-page__detail-body">
                <text class="message-detail-page__detail-label">签到地点</text>
                <text class="message-detail-page__detail-value">{{ message.checkinLocation }}</text>
              </view>
            </view>
            <view v-if="message.timeWindow" class="message-detail-page__detail-row">
              <VectorIcon class="message-detail-page__detail-icon" :src="UI_ICONS.clock" size="28rpx" />
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

      <view v-else-if="!loading" class="message-detail-page__card message-detail-page__card--state">
        <text class="message-detail-page__state-text">消息不存在或已失效</text>
      </view>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.message-detail-page {
  min-height: 100vh;
  background: $page-bg;
}

.message-detail-page__nav-bar {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24rpx 0 32rpx;
  box-sizing: border-box;
}

.message-detail-page__back {
  position: relative;
  flex-shrink: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.28);
  box-shadow: 0 4rpx 16rpx rgba(15, 60, 120, 0.12);

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20rpx;
    height: 20rpx;
    margin-top: -11rpx;
    margin-left: -5rpx;
    border-left: 4rpx solid #fff;
    border-bottom: 4rpx solid #fff;
    transform: rotate(45deg);
  }
}

.message-detail-page__nav-spacer {
  flex-shrink: 0;
}

.message-detail-page__overlap-inner {
  padding: 8rpx 24rpx 24rpx;
}

.message-detail-page__overlap-inner--state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 152rpx;
}

.message-detail-page__sheet {
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
}

.message-detail-page__card {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin: 0 24rpx 20rpx;
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
  flex-shrink: 0;
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

<style lang="scss">
@use '@/styles/student-page-hero.scss';
</style>
