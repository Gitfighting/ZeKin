<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import {
  endTeacherTask,
  getTeacherTaskDetail,
  publishTeacherTask,
  type TeacherTaskDetail,
} from '@/services/teacher'
import { logInfo, showError, showSuccess } from '@/services/feedback'

const detail = ref<TeacherTaskDetail>({
  task: {
    id: 0,
    title: '',
    status: 'not_started',
    groupName: '',
    templateName: '',
    taskType: 'attendance',
    startsAt: '',
    endsAt: '',
    completionRate: 0,
    pendingReviewCount: 0,
    exceptionCount: 0,
    description: '',
    published: false,
  },
  students: [],
  exceptions: [],
})

const completionLabel = computed(() => `${detail.value.task.completionRate}%`)

function currentQuery() {
  const pagesGetter = (globalThis as typeof globalThis & {
    getCurrentPages?: () => Array<{ options?: Record<string, string> }>
  }).getCurrentPages

  if (!pagesGetter) {
    return {}
  }

  const pages = pagesGetter()
  return pages[pages.length - 1]?.options ?? {}
}

async function loadDetail() {
  const id = Number(currentQuery().id || detail.value.task.id)

  if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
    return
  }

  try {
    detail.value = await getTeacherTaskDetail(id)
    logInfo('教师任务详情加载成功', { taskId: id })
  } catch (error) {
    detail.value = {
      ...detail.value,
      students: [],
      exceptions: [],
    }
    showError(error, '任务详情加载失败')
  }
}

async function publishTask() {
  if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
    return
  }

  try {
    detail.value = await publishTeacherTask(detail.value.task.id)
    logInfo('教师任务发布成功', { taskId: detail.value.task.id })
    showSuccess('已发布')
  } catch (error) {
    showError(error, '发布失败')
  }
}

async function endTask() {
  if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
    return
  }

  try {
    detail.value = await endTeacherTask(detail.value.task.id)
    logInfo('教师任务结束成功', { taskId: detail.value.task.id })
    showSuccess('已结束')
  } catch (error) {
    showError(error, '结束失败')
  }
}

function openExceptions() {
  if (typeof uni === 'undefined') {
    return
  }

  uni.navigateTo({ url: '/pages/teacher/exceptions' })
}

onMounted(loadDetail)
</script>

<template>
  <view class="teacher-page">
    <view class="summary-card">
      <text class="page-title">{{ detail.task.title }}</text>
      <text class="page-meta">{{ detail.task.groupName }} · {{ detail.task.startsAt }} - {{ detail.task.endsAt }}</text>
      <view class="stats-row">
        <view class="stat-box">
          <text class="stat-value">{{ completionLabel }}</text>
          <text class="stat-label">完成率</text>
        </view>
        <view class="stat-box">
          <text class="stat-value">{{ detail.task.exceptionCount }}</text>
          <text class="stat-label">异常</text>
        </view>
        <view class="stat-box">
          <text class="stat-value">{{ detail.task.pendingReviewCount }}</text>
          <text class="stat-label">待审核</text>
        </view>
      </view>
      <view class="action-row">
        <view class="secondary-button" @click="publishTask">发布任务</view>
        <view class="primary-button" @click="endTask">结束任务</view>
      </view>
    </view>

    <view class="section-card">
      <text class="section-title">学生列表</text>
      <view v-for="student in detail.students" :key="student.id" class="row-card">
        <view>
          <text class="row-title">{{ student.name }}</text>
          <text class="row-subtitle">{{ student.submittedAt || '未提交' }}</text>
        </view>
        <text class="row-status">{{ student.status }}</text>
      </view>
      <text v-if="detail.students.length === 0" class="empty-line">暂无学生打卡数据</text>
    </view>

    <view class="section-card">
      <view class="section-head">
        <text class="section-title">异常列表</text>
        <text class="section-link" @click="openExceptions">去审核 ></text>
      </view>
      <view v-for="item in detail.exceptions" :key="item.id" class="row-card">
        <view>
          <text class="row-title">{{ item.studentName }}</text>
          <text class="row-subtitle">{{ item.reason }}</text>
        </view>
        <text class="row-status">{{ item.status }}</text>
      </view>
      <text v-if="detail.exceptions.length === 0" class="empty-line">暂无异常记录</text>
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

.summary-card,
.section-card {
  padding: 24rpx;
  border-radius: 22rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.page-title,
.section-title,
.row-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $text-primary;
}

.page-meta,
.stat-label,
.row-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.5;
  color: $text-secondary;
}

.stats-row,
.action-row,
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.stats-row {
  margin-top: 18rpx;
}

.stat-box {
  flex: 1;
  padding: 18rpx;
  border-radius: 18rpx;
  background: $primary-light;
}

.stat-value {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: $primary;
}

.action-row {
  margin-top: 18rpx;
}

.primary-button,
.secondary-button {
  flex: 1;
  padding: 20rpx 0;
  border-radius: 18rpx;
  text-align: center;
  font-size: 24rpx;
}

.primary-button {
  background: $primary;
  color: #fff;
}

.secondary-button {
  background: #eef5ff;
  color: $primary;
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

.row-status,
.section-link {
  font-size: 22rpx;
  color: $primary;
}

.empty-line {
  display: block;
  padding: 24rpx 0 4rpx;
  color: $text-secondary;
  font-size: 24rpx;
}
</style>
