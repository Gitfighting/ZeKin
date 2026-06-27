<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { ref } from 'vue'

import { logInfo, showError } from '@/services/feedback'
import { getTeacherRiskStudents, type TeacherRiskStudent } from '@/services/teacher'

const loading = ref(false)
const students = ref<TeacherRiskStudent[]>([])

function riskReason(student: TeacherRiskStudent) {
  return `连续 ${student.missCount} 次未签到`
}

function avatarText(name: string) {
  return name.trim().slice(-2) || '学'
}

async function loadStudents() {
  loading.value = true
  try {
    students.value = await getTeacherRiskStudents()
    logInfo('风险学生列表加载成功', { count: students.value.length })
  } catch (error) {
    students.value = []
    showError(error, '风险学生列表加载失败')
  } finally {
    loading.value = false
  }
}

onShow(() => {
  void loadStudents()
})
</script>

<template>
  <view class="risk-page">
    <view class="risk-page__head">
      <text class="risk-page__title">风险学生列表</text>
      <text class="risk-page__subtitle">按未签到次数从高到低排序</text>
    </view>

    <view v-if="loading" class="risk-page__empty">加载中...</view>
    <view v-else-if="students.length === 0" class="risk-page__empty">暂无风险学生</view>
    <view v-else class="risk-page__list">
      <view v-for="(student, index) in students" :key="`${student.id}-${index}`" class="risk-item">
        <view class="risk-item__avatar">
          <text>{{ avatarText(student.name) }}</text>
        </view>
        <view class="risk-item__body">
          <text class="risk-item__name">{{ student.name }}</text>
          <text class="risk-item__group">{{ student.groupName }}</text>
          <text class="risk-item__reason">{{ riskReason(student) }}</text>
        </view>
        <view class="risk-item__count">
          <text class="risk-item__count-value">{{ student.missCount }}</text>
          <text class="risk-item__count-label">次未签</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.risk-page {
  min-height: 100vh;
  padding: 24rpx 24rpx calc(24rpx + env(safe-area-inset-bottom));
  background: $page-bg;
  box-sizing: border-box;
}

.risk-page__head {
  margin-bottom: 24rpx;
}

.risk-page__title {
  display: block;
  color: $text-primary;
  font-size: 36rpx;
  font-weight: 700;
}

.risk-page__subtitle {
  display: block;
  margin-top: 8rpx;
  color: $text-secondary;
  font-size: 24rpx;
}

.risk-page__list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.risk-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 24rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.risk-item__avatar {
  display: flex;
  width: 80rpx;
  height: 80rpx;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba($warning, 0.14);
  color: $warning;
  font-size: 26rpx;
  font-weight: 700;
}

.risk-item__body {
  flex: 1;
  min-width: 0;
}

.risk-item__name {
  display: block;
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 700;
}

.risk-item__group {
  display: block;
  margin-top: 6rpx;
  color: $text-secondary;
  font-size: 24rpx;
}

.risk-item__reason {
  display: block;
  margin-top: 6rpx;
  color: $warning;
  font-size: 24rpx;
}

.risk-item__count {
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}

.risk-item__count-value {
  color: $danger;
  font-size: 34rpx;
  font-weight: 700;
  line-height: 1;
}

.risk-item__count-label {
  color: $text-muted;
  font-size: 20rpx;
}

.risk-page__empty {
  padding: 80rpx 24rpx;
  color: $text-secondary;
  font-size: 26rpx;
  text-align: center;
}
</style>
