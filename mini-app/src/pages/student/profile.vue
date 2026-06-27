<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import StatusTag from '@/components/StatusTag.vue'
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

const profile = ref<StudentProfile | null>(null)
const growth = ref<GrowthSummary>({
  checkedInDays: 0,
  normalCount: 0,
  appealSuccessRate: '0%',
  streakDays: 0,
})

const activationStatus = computed(() => (profile.value?.activationState === 'activated' ? 'normal' : 'pending'))

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

onShow(async () => {
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
    <view class="profile-page__hero">
      <text class="profile-page__title">我的</text>
      <text class="profile-page__subtitle">{{ profile ? `${profile.realName} · ${profile.className}` : '暂无个人信息' }}</text>
    </view>

    <view v-if="!profile" class="profile-page__card">
      <text class="profile-page__section-title">暂无个人信息</text>
      <text class="profile-page__value">请检查登录状态、网络或后端服务。</text>
    </view>

    <view v-else class="profile-page__card">
      <view class="profile-page__row">
        <text class="profile-page__label">激活状态</text>
        <StatusTag :status="activationStatus" />
      </view>
      <view class="profile-page__row">
        <text class="profile-page__label">学号</text>
        <text class="profile-page__value">{{ profile.studentNo }}</text>
      </view>
      <view class="profile-page__row">
        <text class="profile-page__label">手机号</text>
        <text class="profile-page__value">{{ profile.phone }}</text>
      </view>
      <view class="profile-page__row">
        <text class="profile-page__label">辅导员</text>
        <text class="profile-page__value">{{ profile.counselor }}</text>
      </view>
    </view>

    <view class="profile-page__card">
      <text class="profile-page__section-title">成长概览</text>
      <view class="profile-page__stats">
        <view class="profile-page__stat">
          <text class="profile-page__stat-value">{{ growth.checkedInDays }}</text>
          <text class="profile-page__stat-label">累计打卡天数</text>
        </view>
        <view class="profile-page__stat">
          <text class="profile-page__stat-value">{{ growth.normalCount }}</text>
          <text class="profile-page__stat-label">正常记录</text>
        </view>
        <view class="profile-page__stat">
          <text class="profile-page__stat-value">{{ growth.appealSuccessRate }}</text>
          <text class="profile-page__stat-label">申诉通过率</text>
        </view>
        <view class="profile-page__stat">
          <text class="profile-page__stat-value">{{ growth.streakDays }}</text>
          <text class="profile-page__stat-label">连续完成</text>
        </view>
      </view>
    </view>

    <view class="profile-page__card profile-page__privacy">
      <text class="profile-page__section-title">隐私设置</text>
      <text class="profile-page__value">{{ profile?.privacyEntryText || '暂无隐私设置说明' }}</text>
    </view>

    <view class="profile-page__card profile-page__actions">
      <button class="profile-page__logout" @click="handleLogout">退出登录</button>
    </view>
    <view class="tab-page__safe-bottom"></view>
  </scroll-view>
  <StudentTabBar active="profile" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.profile-page {
  background: $page-bg;
}

.profile-page__hero {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding: 112rpx 28rpx 34rpx;
  background: $mobile-gradient;
}

.profile-page__title,
.profile-page__subtitle {
  color: #ffffff;
}

.profile-page__title {
  font-size: 48rpx;
  font-weight: 700;
}

.profile-page__subtitle {
  font-size: 28rpx;
  opacity: 0.95;
}

.profile-page__card {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin: 24rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.08);
}

.profile-page__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20rpx;
}

.profile-page__label {
  color: $text-secondary;
  font-size: 26rpx;
}

.profile-page__value {
  color: $text-primary;
  font-size: 28rpx;
  text-align: right;
}

.profile-page__section-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.profile-page__stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx;
}

.profile-page__stat {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  padding: 24rpx;
  border-radius: 22rpx;
  background: rgba($primary, 0.05);
}

.profile-page__stat-value {
  color: $text-primary;
  font-size: 40rpx;
  font-weight: 700;
}

.profile-page__stat-label {
  color: $text-secondary;
  font-size: 24rpx;
}

.profile-page__privacy {
  margin-bottom: 0;
}

.profile-page__actions {
  margin-bottom: 0;
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
</style>
