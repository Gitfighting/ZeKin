<script setup lang="ts">
import { onMounted, ref } from 'vue'

import TeacherTabBar from './components/TeacherTabBar.vue'
import { getTeacherDashboard, type TeacherDashboard } from '@/services/teacher'

const dashboard = ref<TeacherDashboard>({
  todayTasks: 3,
  exceptions: 6,
  pendingReviews: 4,
  quickCreateCount: 2,
})

const shortcuts = [
  { title: '快捷创建', value: '模板建任务', path: '/pages/teacher/task-create' },
  { title: '异常处理', value: '查看待审', path: '/pages/teacher/exceptions' },
  { title: '任务总览', value: '进行中任务', path: '/pages/teacher/tasks' },
]

async function loadDashboard() {
  if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
    return
  }

  try {
    dashboard.value = await getTeacherDashboard()
  } catch {
    // Keep the shell useful even when the backend lane is not ready.
  }
}

function openPage(path: string) {
  if (typeof uni === 'undefined') {
    return
  }

  uni.navigateTo({ url: path })
}

onMounted(loadDashboard)
</script>

<template>
  <view class="teacher-page">
    <view class="hero-card">
      <text class="eyebrow">教师工作台</text>
      <text class="hero-title">今天先把签到任务发出去，再把异常闭环收回来。</text>
      <view class="hero-metrics">
        <view class="metric-card">
          <text class="metric-value">{{ dashboard.todayTasks }}</text>
          <text class="metric-label">今日任务</text>
        </view>
        <view class="metric-card">
          <text class="metric-value">{{ dashboard.exceptions }}</text>
          <text class="metric-label">异常</text>
        </view>
        <view class="metric-card">
          <text class="metric-value">{{ dashboard.pendingReviews }}</text>
          <text class="metric-label">待审核</text>
        </view>
        <view class="metric-card">
          <text class="metric-value">{{ dashboard.quickCreateCount }}</text>
          <text class="metric-label">快捷创建</text>
        </view>
      </view>
    </view>

    <view class="section">
      <view class="section-header">
        <text class="section-title">常用入口</text>
        <text class="section-meta">适合课前 30 秒完成</text>
      </view>
      <view class="shortcut-list">
        <view
          v-for="shortcut in shortcuts"
          :key="shortcut.title"
          class="shortcut-card"
          @click="openPage(shortcut.path)"
        >
          <view>
            <text class="shortcut-title">{{ shortcut.title }}</text>
            <text class="shortcut-subtitle">{{ shortcut.value }}</text>
          </view>
          <text class="shortcut-arrow">></text>
        </view>
      </view>
    </view>

    <view class="section compact-grid">
      <view class="info-panel">
        <text class="info-title">本日提醒</text>
        <text class="info-line">1 个班级还没创建晨检</text>
        <text class="info-line">4 条异常等你复核</text>
      </view>
      <view class="info-panel">
        <text class="info-title">发布建议</text>
        <text class="info-line">优先用课堂考勤模板</text>
        <text class="info-line">高级规则默认折叠</text>
      </view>
    </view>

    <TeacherTabBar active="home" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.teacher-page {
  min-height: 100vh;
  padding: 28rpx 24rpx 180rpx;
  background: $page-bg;
}

.hero-card {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $mobile-gradient;
  color: #fff;
  box-shadow: 0 24rpx 48rpx rgba(22, 119, 255, 0.16);
}

.eyebrow {
  font-size: 22rpx;
  opacity: 0.88;
}

.hero-title {
  font-size: 40rpx;
  line-height: 1.35;
  font-weight: 700;
}

.hero-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx;
}

.metric-card {
  padding: 20rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.16);
  backdrop-filter: blur(8rpx);
}

.metric-value {
  display: block;
  font-size: 40rpx;
  font-weight: 700;
}

.metric-label {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
}

.section {
  margin-top: 24rpx;
}

.section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 700;
  color: $text-primary;
}

.section-meta {
  font-size: 22rpx;
  color: $text-secondary;
}

.shortcut-list {
  display: grid;
  gap: 16rpx;
}

.shortcut-card,
.info-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
  border-radius: 20rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.shortcut-title,
.info-title {
  display: block;
  font-size: 28rpx;
  font-weight: 700;
  color: $text-primary;
}

.shortcut-subtitle,
.info-line {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.5;
  color: $text-secondary;
}

.shortcut-arrow {
  font-size: 32rpx;
  color: $primary;
}

.compact-grid {
  display: grid;
  gap: 16rpx;
}
</style>
