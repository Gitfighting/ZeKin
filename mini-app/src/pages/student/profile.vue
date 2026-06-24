<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import StatusTag from '@/components/StatusTag.vue'
import {
  demoGrowthSummary,
  demoStudentProfile,
  getGrowthSummary,
  getStudentProfile,
  type GrowthSummary,
  type StudentProfile,
} from '@/services/student'

const profile = ref<StudentProfile>(demoStudentProfile)
const growth = ref<GrowthSummary>(demoGrowthSummary)

const activationStatus = computed(() => (profile.value.activationState === 'activated' ? 'normal' : 'pending'))

onShow(async () => {
  try {
    const [profileResponse, growthResponse] = await Promise.all([getStudentProfile(), getGrowthSummary()])
    profile.value = profileResponse
    growth.value = growthResponse
  } catch {
    profile.value = demoStudentProfile
    growth.value = demoGrowthSummary
  }
})
</script>

<template>
  <scroll-view scroll-y class="profile-page">
    <view class="profile-page__hero">
      <text class="profile-page__title">我的</text>
      <text class="profile-page__subtitle">{{ profile.realName }} · {{ profile.className }}</text>
    </view>

    <view class="profile-page__card">
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
      <text class="profile-page__value">{{ profile.privacyEntryText }}</text>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.profile-page {
  min-height: 100vh;
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
  margin-bottom: 40rpx;
}
</style>
