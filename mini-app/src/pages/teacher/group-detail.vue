<script setup lang="ts">
import { computed, ref } from 'vue'

import type { TeacherGroupDetail } from '@/services/teacher'

const detail = ref<TeacherGroupDetail>({
  group: {
    id: 0,
    name: '班级详情',
    studentCount: 0,
    recentTaskCount: 0,
    courseName: '',
  },
  stats: {
    attendanceRate: 0,
    exceptionRate: 0,
    pendingReviewCount: 0,
  },
  students: [],
  tasks: [],
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
      <text v-if="detail.students.length === 0" class="empty-line">暂无学生详情数据</text>
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
      <text v-if="detail.tasks.length === 0" class="empty-line">暂无班级任务数据</text>
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

.empty-line {
  display: block;
  padding: 20rpx 0 0;
  color: $text-secondary;
  font-size: 24rpx;
}
</style>
