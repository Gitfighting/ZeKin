<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import StudentTabBar from '@/components/StudentTabBar.vue'
import { refreshStudentUnreadMessageCount } from '@/composables/useStudentUnreadMessages'
import { logInfo, showError } from '@/services/feedback'
import { getStudentMessages, type MessageItem } from '@/services/student'

type MessageFilter = 'all' | 'unread' | 'system' | 'teacher'
type MessageTone = 'blue' | 'orange'

const filterTabs: { key: MessageFilter; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'unread', label: '未读' },
  { key: 'system', label: '系统消息' },
  { key: 'teacher', label: '教师消息' },
]

const messages = ref<MessageItem[]>([])
const unreadCount = ref(0)
const activeFilter = ref<MessageFilter>('all')

function isTaskPublishMessage(item: MessageItem): boolean {
  return Boolean(item.checkinMethods || item.timeWindow)
}

function isTeacherMessage(item: MessageItem): boolean {
  if (isTaskPublishMessage(item)) {
    return false
  }
  const text = `${item.title}${item.content}`
  return item.type === 'teacher_feedback' || /老师|教师|反馈/.test(text)
}

function isSystemMessage(item: MessageItem): boolean {
  return !isTeacherMessage(item)
}

function messageIcon(item: MessageItem): { icon: string; tone: MessageTone } {
  if (item.type === 'teacher_feedback') {
    return { icon: '👨‍🏫', tone: 'blue' }
  }
  if (item.type === 'appeal_result') {
    return { icon: '📋', tone: 'blue' }
  }
  if (/异常|申诉/.test(`${item.title}${item.content}`)) {
    return { icon: '⚠️', tone: 'orange' }
  }
  if (/系统|维护|通知/.test(`${item.title}${item.content}`)) {
    return { icon: '🔔', tone: 'blue' }
  }
  return { icon: '📅', tone: 'blue' }
}

function messageCategory(item: MessageItem): string {
  if (isTeacherMessage(item)) {
    return '教师消息'
  }
  if (item.type === 'appeal_result') {
    return '申诉结果'
  }
  if (/异常/.test(`${item.title}${item.content}`)) {
    return '异常提醒'
  }
  if (/系统|维护/.test(`${item.title}${item.content}`)) {
    return '系统通知'
  }
  return '打卡提醒'
}

function matchFilter(item: MessageItem, filter: MessageFilter): boolean {
  if (filter === 'all') {
    return true
  }
  if (filter === 'unread') {
    return !item.read
  }
  if (filter === 'teacher') {
    return isTeacherMessage(item)
  }
  return isSystemMessage(item)
}

const visibleMessages = computed(() =>
  messages.value.filter((item) => matchFilter(item, activeFilter.value)),
)

const subtitleText = computed(() => {
  if (unreadCount.value > 0) {
    return `${unreadCount.value} 条未读消息 · 打卡提醒、教师反馈与申诉通知`
  }
  return '查看打卡提醒、教师反馈与申诉相关消息'
})

function displayTime(time: string): string {
  const match = time.match(/(\d{2}:\d{2})$/)
  return match?.[1] ?? time
}

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

      <view class="messages-page__panel">
        <view class="messages-page__tabs">
          <view
            v-for="tab in filterTabs"
            :key="tab.key"
            class="messages-page__tab"
            :class="{ 'messages-page__tab--active': activeFilter === tab.key }"
            @click="activeFilter = tab.key"
          >
            <text>{{ tab.label }}</text>
          </view>
        </view>
      </view>

      <view class="messages-page__list">
        <view
          v-for="item in visibleMessages"
          :key="item.id"
          class="messages-page__card"
          :class="{ 'messages-page__card--unread': !item.read }"
          @click="openMessage(item)"
        >
          <view
            class="messages-page__icon"
            :class="`messages-page__icon--${messageIcon(item).tone}`"
          >
            <text class="messages-page__icon-text">{{ messageIcon(item).icon }}</text>
          </view>

          <view class="messages-page__body">
            <view class="messages-page__header">
              <view class="messages-page__title-group">
                <text class="messages-page__card-title">{{ item.title }}</text>
                <text
                  class="messages-page__tag"
                  :class="`messages-page__tag--${messageIcon(item).tone}`"
                >
                  {{ messageCategory(item) }}
                </text>
              </view>
              <view class="messages-page__status-wrap">
                <text class="messages-page__card-time">{{ displayTime(item.time) }}</text>
                <view v-if="!item.read" class="messages-page__dot" aria-hidden="true"></view>
              </view>
            </view>

            <view class="messages-page__meta">
              <template v-if="item.checkinMethods || item.timeWindow">
                <view v-if="item.checkinMethods" class="messages-page__meta-line">
                  <text class="messages-page__meta-label">打卡方式</text>
                  <text class="messages-page__meta-text">{{ item.checkinMethods }}</text>
                </view>
                <view v-if="item.timeWindow" class="messages-page__meta-line">
                  <text class="messages-page__meta-label">打卡时间</text>
                  <text class="messages-page__meta-text">{{ item.timeWindow }}</text>
                </view>
              </template>
              <view v-else class="messages-page__meta-line">
                <text class="messages-page__meta-icon">💬</text>
                <text class="messages-page__meta-text">{{ item.content }}</text>
              </view>
            </view>
          </view>
        </view>

        <view v-if="visibleMessages.length === 0" class="messages-page__empty">
          <text class="messages-page__empty-icon">💬</text>
          <text>暂无{{ filterTabs.find((tab) => tab.key === activeFilter)?.label }}消息</text>
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

.messages-page__panel {
  position: relative;
  z-index: 3;
  margin: -36rpx 24rpx 0;
  padding: 8rpx 24rpx 0;
  border-radius: 28rpx 28rpx 24rpx 24rpx;
  background: #fff;
  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.08);
}

.messages-page__tabs {
  display: flex;
  border-bottom: 1rpx solid rgba(15, 23, 42, 0.06);
}

.messages-page__tab {
  position: relative;
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  height: 88rpx;
  color: $text-secondary;
  font-size: 26rpx;
  font-weight: 500;
}

.messages-page__tab--active {
  color: $primary;
  font-weight: 700;
}

.messages-page__tab--active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 48rpx;
  height: 6rpx;
  border-radius: 999rpx;
  background: $primary;
  transform: translateX(-50%);
}

.messages-page__list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding: 24rpx;
}

.messages-page__card {
  display: flex;
  gap: 20rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 12rpx 36rpx rgba(15, 107, 214, 0.07);
}

.messages-page__card--unread {
  border: 2rpx solid rgba($primary, 0.12);
  background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
}

.messages-page__icon {
  display: flex;
  width: 88rpx;
  height: 88rpx;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 20rpx;
}

.messages-page__icon--blue {
  background: linear-gradient(135deg, #3b9bff 0%, $primary 100%);
}

.messages-page__icon--orange {
  background: linear-gradient(135deg, #ffb347 0%, $warning 100%);
}

.messages-page__icon-text {
  font-size: 40rpx;
  line-height: 1;
}

.messages-page__body {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 12rpx;
}

.messages-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12rpx;
}

.messages-page__title-group {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-wrap: wrap;
  align-items: center;
  gap: 10rpx;
}

.messages-page__card-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.35;
}

.messages-page__tag {
  flex-shrink: 0;
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 600;
}

.messages-page__tag--blue {
  background: rgba($primary, 0.1);
  color: $primary;
}

.messages-page__tag--orange {
  background: rgba($warning, 0.14);
  color: $warning;
}

.messages-page__status-wrap {
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  align-items: flex-end;
  gap: 10rpx;
}

.messages-page__card-time {
  color: $text-muted;
  font-size: 24rpx;
  white-space: nowrap;
}

.messages-page__dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: #ff4d4f;
}

.messages-page__meta {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.messages-page__meta-line {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
}

.messages-page__meta-label {
  flex-shrink: 0;
  width: 112rpx;
  color: $text-muted;
  font-size: 24rpx;
  line-height: 1.5;
}

.messages-page__meta-icon {
  flex-shrink: 0;
  font-size: 22rpx;
  line-height: 1.5;
}

.messages-page__meta-text {
  display: -webkit-box;
  overflow: hidden;
  flex: 1;
  min-width: 0;
  color: $text-secondary;
  font-size: 26rpx;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
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
  box-shadow: 0 12rpx 36rpx rgba(15, 107, 214, 0.07);
}

.messages-page__empty-icon {
  font-size: 56rpx;
}

.tab-page__safe-bottom {
  height: $tab-bar-safe-bottom;
}
</style>
