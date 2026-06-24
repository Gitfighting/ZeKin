<script setup lang="ts">
import { computed, ref } from 'vue'

import type { TeacherGroupDetail } from '@/services/teacher'

const detail = ref<TeacherGroupDetail>({
  group: {
    id: 1,
    name: '思政一班',
    studentCount: 42,
    recentTaskCount: 8,
    courseName: '马克思主义原理',
  },
  stats: {
    attendanceRate: 91,
    exceptionRate: 7,
    pendingReviewCount: 3,
  },
  students: [
    { id: 1, name: '李明', status: 'submitted' },
    { id: 2, name: '张悦', status: 'pending_review' },
    { id: 3, name: '王辰', status: 'missing' },
  ],
  tasks: [
    {
      id: 101,
      title: '思政一班晨检',
      status: 'in_progress',
      groupName: '思政一班',
      templateName: '晨检模板',
      taskType: 'attendance',
      startsAt: '08:00',
      endsAt: '08:20',
      completionRate: 87,
      pendingReviewCount: 2,
      exceptionCount: 3,
    },
    {
      id: 104,
      title: '晚点名',
      status: 'ended',
      groupName: '思政一班',
      templateName: '晚点名模板',
      taskType: 'photo',
      startsAt: '21:00',
      endsAt: '21:30',
      completionRate: 98,
      pendingReviewCount: 0,
      exceptionCount: 1,
    },
  ],
})

const quickStats = computed(() => [
  { label: '到课率', value: `${detail.value.stats.attendanceRate}%` },
  { label: '异常率', value: `${detail.value.stats.exceptionRate}%` },
  { label: '待审核', value: `${detail.value.stats.pendingReviewCount}` },
])

function openTask(id: number) {
  if (typeof uni === 'undefined') {
    return
  }

  uni.navigateTo({ url: `/pages/teacher/task-detail?id=${id}` })
}
</script>

<template>
  <view class="teacher-page">
    <view class="hero-card">
      <text class="page-title">{{ detail.group.name }}</text>
      <text class="page-subtitle">{{ detail.group.courseName }} · {{ detail.group.studentCount }} 名学生</text>
      <view class="stats-grid">
        <view v-for="item in quickStats" :key="item.label" class="stat-card">
          <text class="stat-value">{{ item.value }}</text>
          <text class="stat-label">{{ item.label }}</text>
        </view>
      </view>
    </view>

    <view class="section-card">
      <text class="section-title">学生列表</text>
      <view v-for="student in detail.students" :key="student.id" class="row-card">
        <text class="row-title">{{ student.name }}</text>
        <text class="row-status">{{ student.status }}</text>
      </view>
    </view>

    <view class="section-card">
      <text class="section-title">班级任务</text>
      <view v-for="task in detail.tasks" :key="task.id" class="row-card" @click="openTask(task.id)">
        <view>
          <text class="row-title">{{ task.title }}</text>
          <text class="row-subtitle">{{ task.startsAt }} - {{ task.endsAt }}</text>
        </view>
        <text class="row-status">{{ task.status }}</text>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.teacher-page {
  min-height: 100vh;
  padding: 24rpx;
  background: $page-bg;
}

.hero-card,
.section-card {
  padding: 24rpx;
  border-radius: 22rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.hero-card {
  background: linear-gradient(180deg, #1677ff 0%, #53b1fd 100%);
  color: #fff;
}

.page-title,
.section-title,
.row-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
}

.page-subtitle,
.row-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.5;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12rpx;
  margin-top: 18rpx;
}

.stat-card {
  padding: 18rpx;
  border-radius: 18rpx;
  background: rgba(255, 255, 255, 0.16);
}

.stat-value {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
}

.stat-label {
  display: block;
  margin-top: 8rpx;
  font-size: 20rpx;
}

.section-card {
  margin-top: 20rpx;
}

.row-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  padding: 20rpx 0;
  border-bottom: 1rpx solid rgba(102, 112, 133, 0.12);
}

.row-card:last-child {
  border-bottom: 0;
}

.row-title {
  color: $text-primary;
}

.row-subtitle {
  color: $text-secondary;
}

.row-status {
  font-size: 22rpx;
  color: $primary;
}
</style>
