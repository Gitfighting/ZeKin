<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import StudentTabBar from '@/components/StudentTabBar.vue'
import { refreshStudentUnreadMessageCount } from '@/composables/useStudentUnreadMessages'
import { clearLoginState } from '@/services/auth'
import { logInfo, showError } from '@/services/feedback'
import {
  getGrowthSummary,
  getStudentProfile,
  type GrowthSummary,
  type StudentProfile,
} from '@/services/student'

interface ProfileMenuItem {
  key: string
  label: string
  icon: string
  action: 'settings'
}

const profile = ref<StudentProfile | null>(null)
const growth = ref<GrowthSummary>({
  checkedInDays: 0,
  normalCount: 0,
  appealSuccessRate: '0%',
  streakDays: 0,
})

const brandBarStyle = ref<Record<string, string>>({
  top: '48px',
  height: '32px',
})

const pageTopStyle = ref<Record<string, string>>({
  height: '112rpx',
})

const menuItems: ProfileMenuItem[] = [
  { key: 'settings', label: '设置', icon: '/static/profile-icons/settings.svg', action: 'settings' },
]

const growthStats = computed(() => {
  const total = growth.value.checkedInDays
  const normal = growth.value.normalCount
  const completionRate = total > 0 ? `${Math.min(100, Math.round((normal / total) * 100))}%` : '0%'
  const score = normal * 32 + total * 12
  const badges = normal > 0 ? Math.max(1, Math.floor(normal / 6)) : 0

  return [
    { key: 'days', label: '打卡天数', value: `${total}天`, icon: '/static/profile-icons/stat-checkin.svg' },
    { key: 'course', label: '课程完成', value: completionRate, icon: '/static/profile-icons/stat-course.svg' },
    { key: 'score', label: '综合积分', value: `${score}分`, icon: '/static/profile-icons/stat-score.svg' },
    { key: 'badge', label: '荣誉徽章', value: `${badges}枚`, icon: '/static/profile-icons/stat-badge.svg' },
  ]
})

function syncBrandLayout() {
  if (typeof uni === 'undefined') {
    return
  }

  try {
    const menuButton = uni.getMenuButtonBoundingClientRect()
    brandBarStyle.value = {
      top: `${menuButton.top}px`,
      height: `${menuButton.height}px`,
    }
    pageTopStyle.value = {
      height: `${menuButton.bottom + 12}px`,
    }
  } catch {
    // 非小程序环境保留默认占位
  }
}

function finishLogout() {
  clearLoginState()
  logInfo('学生退出登录成功')
  uni.reLaunch({ url: '/pages/auth/login' })
}

function handleLogout() {
  uni.showModal({
    title: '退出登录',
    content: '确认退出当前账号？',
    confirmText: '退出',
    success: (result: { confirm?: boolean }) => {
      if (result.confirm) {
        finishLogout()
      }
    },
  })
}

function openSettings() {
  uni.showActionSheet({
    itemList: ['隐私说明', '退出登录'],
    success: (result) => {
      if (result.tapIndex === 0) {
        uni.showModal({
          title: '隐私说明',
          content: profile.value?.privacyEntryText || '查看定位与照片使用说明',
          showCancel: false,
        })
        return
      }
      if (result.tapIndex === 1) {
        handleLogout()
      }
    },
  })
}

function openQrCode() {
  uni.showToast({ title: '二维码功能开发中', icon: 'none' })
}

function openGrowthOverview() {
  uni.navigateTo({ url: '/pages/student/records' })
}

function openMenuItem(item: ProfileMenuItem) {
  if (item.action === 'settings') {
    openSettings()
  }
}

onShow(async () => {
  syncBrandLayout()
  void refreshStudentUnreadMessageCount()
  try {
    const [profileResponse, growthResponse] = await Promise.all([getStudentProfile(), getGrowthSummary()])
    profile.value = profileResponse
    growth.value = growthResponse
    logInfo('学生个人中心加载成功', {
      studentNo: profileResponse.studentNo,
    })
  } catch (error) {
    profile.value = null
    growth.value = {
      checkedInDays: 0,
      normalCount: 0,
      appealSuccessRate: '0%',
      streakDays: 0,
    }
    showError(error, '个人信息加载失败')
  }
})
</script>

<template>
  <view class="student-tab-page">
    <scroll-view scroll-y class="profile-page student-tab-page__scroll">
      <view class="profile-page__brand-bar" :style="brandBarStyle">
        <text class="profile-page__brand">知勤</text>
      </view>

      <view class="profile-page__top-spacer" :style="pageTopStyle"></view>

      <view class="profile-page__identity">
        <view class="profile-page__identity-main">
          <view class="profile-page__avatar-wrap">
            <image
              class="profile-page__avatar"
              src="/static/man-blue-daily.png"
              mode="aspectFill"
            />
          </view>

          <view class="profile-page__identity-info">
            <view class="profile-page__name-row">
              <text class="profile-page__name">{{ profile?.realName || '同学' }}</text>
              <text class="profile-page__role-tag">学生</text>
            </view>
            <text class="profile-page__class">{{ profile?.className || '暂无班级信息' }}</text>
            <text class="profile-page__student-no">学号：{{ profile?.studentNo || '--' }}</text>
          </view>
        </view>

        <view class="profile-page__qr-entry" @click="openQrCode">
          <image class="profile-page__qr-icon" src="/static/profile-icons/qrcode.svg" mode="aspectFit" />
          <text class="profile-page__qr-text">我的二维码 ›</text>
        </view>
      </view>

      <view class="profile-page__growth-card">
        <view class="profile-page__growth-head">
          <view class="profile-page__growth-copy">
            <text class="profile-page__growth-title">成长档案概览</text>
            <text class="profile-page__growth-subtitle">记录每一次成长，见证更好的自己</text>
          </view>
          <view class="profile-page__growth-action" @click="openGrowthOverview">
            <text>查看 ›</text>
          </view>
        </view>

        <view class="profile-page__growth-stats">
          <view
            v-for="item in growthStats"
            :key="item.key"
            class="profile-page__growth-stat"
          >
            <image class="profile-page__growth-stat-icon" :src="item.icon" mode="aspectFit" />
            <text class="profile-page__growth-stat-label">{{ item.label }}</text>
            <text class="profile-page__growth-stat-value">{{ item.value }}</text>
          </view>
        </view>
      </view>

      <view class="profile-page__menu-card">
        <view
          v-for="item in menuItems"
          :key="item.key"
          class="profile-page__menu-item"
          @click="openMenuItem(item)"
        >
          <image class="profile-page__menu-icon" :src="item.icon" mode="aspectFit" />
          <text class="profile-page__menu-label">{{ item.label }}</text>
          <text class="profile-page__menu-arrow">›</text>
        </view>
      </view>

      <button class="profile-page__logout profile-page__logout--hidden" @click="handleLogout">退出登录</button>

      <view class="tab-page__safe-bottom"></view>
    </scroll-view>
    <StudentTabBar active="profile" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.profile-page {
  background: linear-gradient(180deg, #f3f8ff 0%, $page-bg 280rpx, $page-bg 100%);
}

.profile-page__brand-bar {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  padding-left: 32rpx;
  box-sizing: border-box;
}

.profile-page__top-spacer {
  flex-shrink: 0;
}

.profile-page__brand {
  font-size: 42rpx;
  font-weight: 700;
  color: $text-primary;
  line-height: 1;
}

.profile-page__identity {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  margin: 12rpx 24rpx 24rpx;
  padding: 28rpx 24rpx;
  overflow: hidden;
  border-radius: 28rpx;
  background: linear-gradient(135deg, #eef6ff 0%, #f8fbff 52%, #edf4ff 100%);
  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.08);
}

.profile-page__identity::after {
  content: '';
  position: absolute;
  top: -40rpx;
  right: -20rpx;
  width: 180rpx;
  height: 180rpx;
  border-radius: 50%;
  background: rgba(89, 179, 255, 0.12);
}

.profile-page__identity-main {
  display: flex;
  min-width: 0;
  flex: 1;
  align-items: center;
  gap: 20rpx;
}

.profile-page__avatar-wrap {
  width: 112rpx;
  height: 112rpx;
  flex-shrink: 0;
  overflow: hidden;
  border: 4rpx solid rgba(255, 255, 255, 0.92);
  border-radius: 50%;
  background: #fff;
}

.profile-page__avatar {
  width: 100%;
  height: 100%;
}

.profile-page__identity-info {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 8rpx;
}

.profile-page__name-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.profile-page__name {
  color: $text-primary;
  font-size: 36rpx;
  font-weight: 700;
}

.profile-page__role-tag {
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  background: rgba($primary, 0.12);
  color: $primary;
  font-size: 22rpx;
  font-weight: 600;
}

.profile-page__class,
.profile-page__student-no {
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.5;
}

.profile-page__qr-entry {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  flex-shrink: 0;
}

.profile-page__qr-icon {
  width: 40rpx;
  height: 40rpx;
}

.profile-page__qr-text {
  color: $text-secondary;
  font-size: 22rpx;
  white-space: nowrap;
}

.profile-page__growth-card {
  margin: 0 24rpx 24rpx;
  padding: 28rpx 24rpx;
  border-radius: 28rpx;
  background: linear-gradient(135deg, #1677ff 0%, #2ea8ff 100%);
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.18);
}

.profile-page__growth-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.profile-page__growth-copy {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.profile-page__growth-title {
  color: #fff;
  font-size: 34rpx;
  font-weight: 700;
}

.profile-page__growth-subtitle {
  color: rgba(255, 255, 255, 0.88);
  font-size: 24rpx;
  line-height: 1.5;
}

.profile-page__growth-action {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 56rpx;
  padding: 0 22rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  font-size: 24rpx;
  font-weight: 600;
}

.profile-page__growth-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12rpx;
}

.profile-page__growth-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding-top: 8rpx;
}

.profile-page__growth-stat:not(:last-child) {
  border-right: 1rpx solid rgba(255, 255, 255, 0.18);
}

.profile-page__growth-stat-icon {
  width: 32rpx;
  height: 32rpx;
}

.profile-page__growth-stat-label {
  color: rgba(255, 255, 255, 0.82);
  font-size: 22rpx;
  text-align: center;
}

.profile-page__growth-stat-value {
  color: #fff;
  font-size: 28rpx;
  font-weight: 700;
  text-align: center;
}

.profile-page__menu-card {
  margin: 0 24rpx;
  padding: 8rpx 0;
  border-radius: 28rpx;
  background: $card-bg;
  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.08);
}

.profile-page__menu-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx 28rpx;
}

.profile-page__menu-item:not(:last-child) {
  border-bottom: 1rpx solid rgba(15, 23, 42, 0.06);
}

.profile-page__menu-icon {
  width: 48rpx;
  height: 48rpx;
  flex-shrink: 0;
}

.profile-page__menu-label {
  flex: 1;
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 600;
}

.profile-page__menu-arrow {
  color: $text-muted;
  font-size: 34rpx;
  line-height: 1;
}

.tab-page__safe-bottom {
  height: $tab-bar-safe-bottom;
}

.profile-page__logout {
  width: 100%;
  border: 0;
  border-radius: 999rpx;
  background: #fff1f0;
  color: #d92d20;
  font-size: 28rpx;
  font-weight: 700;
}

.profile-page__logout--hidden {
  position: absolute;
  left: -9999px;
  width: 1px;
  height: 1px;
  overflow: hidden;
  opacity: 0;
}
</style>
