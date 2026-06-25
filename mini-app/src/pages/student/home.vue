<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { ref } from 'vue'

import TaskCard from '@/components/TaskCard.vue'
import { logInfo, showError } from '@/services/feedback'
import {
  getStudentDashboard,
  type QuickEntry,
  type StudentDashboard,
  type StudentTask,
} from '@/services/student'

const dashboard = ref<StudentDashboard>({
  greeting: '同学，你好',
  pendingCount: 0,
  upcomingDeadline: '暂无待办任务',
  exceptionCount: 0,
  alerts: [],
  quickEntries: [
    { label: '今日任务', path: '/pages/student/tasks' },
    { label: '打卡记录', path: '/pages/student/records' },
    { label: '异常申诉', path: '/pages/student/appeal' },
    { label: '个人中心', path: '/pages/student/profile' },
  ],
  focusTasks: [],
})

function openQuickEntry(entry: QuickEntry) {
  if (entry.path.includes('/pages/student/home') || entry.path.includes('/pages/student/tasks') || entry.path.includes('/pages/student/messages') || entry.path.includes('/pages/student/profile')) {
    uni.switchTab({
      url: entry.path,
    })
    return
  }

  uni.navigateTo({
    url: entry.path,
  })
}

function openTask(task: StudentTask) {
  uni.navigateTo({
    url: `/pages/student/task-detail?id=${task.id}`,
  })
}

onShow(async () => {
  try {
    dashboard.value = await getStudentDashboard()
    logInfo('学生首页数据加载成功', {
      pendingCount: dashboard.value.pendingCount,
      exceptionCount: dashboard.value.exceptionCount,
    })
  } catch (error) {
    dashboard.value = {
      ...dashboard.value,
      pendingCount: 0,
      upcomingDeadline: '加载失败',
      exceptionCount: 0,
      alerts: [],
      focusTasks: [],
    }
    showError(error, '首页数据加载失败')
  }
})
</script>

<template>
  <scroll-view scroll-y class="student-page">
    <view class="student-page__hero">
      <text class="student-page__greeting">{{ dashboard.greeting }}</text>
      <text class="student-page__headline">今日待打卡 {{ dashboard.pendingCount }} 项</text>
      <text class="student-page__subhead">即将截止：{{ dashboard.upcomingDeadline }}</text>
    </view>

    <view class="student-page__panel student-page__stats">
      <view class="student-page__stat">
        <text class="student-page__stat-label">今日待打卡</text>
        <text class="student-page__stat-value">{{ dashboard.pendingCount }}</text>
      </view>
      <view class="student-page__stat">
        <text class="student-page__stat-label">即将截止</text>
        <text class="student-page__stat-value student-page__stat-value--small">{{ dashboard.upcomingDeadline }}</text>
      </view>
      <view class="student-page__stat">
        <text class="student-page__stat-label">异常提醒</text>
        <text class="student-page__stat-value">{{ dashboard.exceptionCount }}</text>
      </view>
    </view>

    <view class="student-page__panel">
      <view class="student-page__section-header">
        <text class="student-page__section-title">快捷入口</text>
      </view>
      <view class="student-page__quick-grid">
        <view
          v-for="entry in dashboard.quickEntries"
          :key="entry.label"
          class="student-page__quick-item"
          @click="openQuickEntry(entry)"
        >
          <text class="student-page__quick-label">{{ entry.label }}</text>
          <text v-if="entry.badge" class="student-page__quick-badge">{{ entry.badge }}</text>
        </view>
      </view>
    </view>

    <view class="student-page__panel">
      <view class="student-page__section-header">
        <text class="student-page__section-title">异常提醒</text>
      </view>
      <view class="student-page__alerts">
        <text v-for="item in dashboard.alerts" :key="item" class="student-page__alert-item">
          {{ item }}
        </text>
        <text v-if="dashboard.alerts.length === 0" class="student-page__empty">暂无异常提醒</text>
      </view>
    </view>

    <view class="student-page__panel student-page__tasks">
      <view class="student-page__section-header">
        <text class="student-page__section-title">即将截止</text>
      </view>
      <TaskCard v-for="task in dashboard.focusTasks" :key="task.id" :task="task" @action="openTask" @click="openTask" />
      <text v-if="dashboard.focusTasks.length === 0" class="student-page__empty">暂无即将截止任务</text>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.student-page {
  min-height: 100vh;
  background: $page-bg;
}

.student-page__hero {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding: 112rpx 28rpx 34rpx;
  background: $mobile-gradient;
}

.student-page__greeting,
.student-page__headline,
.student-page__subhead {
  color: #ffffff;
}

.student-page__greeting {
  font-size: 26rpx;
  opacity: 0.9;
}

.student-page__headline {
  font-size: 48rpx;
  font-weight: 700;
}

.student-page__subhead {
  font-size: 28rpx;
  opacity: 0.95;
}

.student-page__panel {
  margin: 0 24rpx 24rpx;
  padding: 28rpx;
  border-radius: 28rpx;
  background: $card-bg;
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.08);
}

.student-page__stats {
  margin-top: -40rpx;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16rpx;
}

.student-page__stat {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 14rpx;
  padding: 24rpx;
  border-radius: 24rpx;
  background: rgba($primary, 0.05);
}

.student-page__stat-label {
  color: $text-secondary;
  font-size: 24rpx;
}

.student-page__stat-value {
  color: $text-primary;
  font-size: 42rpx;
  font-weight: 700;
  line-height: 1.3;
}

.student-page__stat-value--small {
  font-size: 24rpx;
}

.student-page__section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.student-page__section-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.student-page__quick-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16rpx;
}

.student-page__quick-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 108rpx;
  padding: 0 24rpx;
  border-radius: 24rpx;
  background: #f8fbff;
  border: 2rpx solid rgba($primary, 0.08);
}

.student-page__quick-label {
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 600;
}

.student-page__quick-badge {
  min-width: 40rpx;
  height: 40rpx;
  line-height: 40rpx;
  border-radius: 999rpx;
  background: $primary;
  color: #ffffff;
  text-align: center;
  font-size: 24rpx;
}

.student-page__alerts,
.student-page__tasks {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
}

.student-page__alert-item {
  padding: 20rpx 24rpx;
  border-radius: 22rpx;
  background: rgba($warning, 0.1);
  color: $text-primary;
  font-size: 26rpx;
  line-height: 1.5;
}

.student-page__empty {
  color: $text-secondary;
  font-size: 26rpx;
  line-height: 1.6;
}
</style>
