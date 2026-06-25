<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import TeacherTabBar from './components/TeacherTabBar.vue'
import { logInfo, showError } from '@/services/feedback'
import {
  getTeacherTasks,
  type TeacherTask,
  type TeacherTaskStatus,
} from '@/services/teacher'

const statusTabs: Array<{ label: string; value: TeacherTaskStatus }> = [
  { label: '进行中', value: 'in_progress' },
  { label: '未开始', value: 'not_started' },
  { label: '已结束', value: 'ended' },
  { label: '待审核', value: 'pending_review' },
]

const activeStatus = ref<TeacherTaskStatus>('in_progress')
const tasks = ref<TeacherTask[]>([])

const visibleTasks = computed(() =>
  tasks.value.filter((task) => task.status === activeStatus.value),
)

async function loadTasks() {
  if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
    tasks.value = []
    return
  }

  try {
    tasks.value = await getTeacherTasks()
    logInfo('教师任务列表加载成功', { count: tasks.value.length })
  } catch (error) {
    tasks.value = []
    showError(error, '教师任务列表加载失败')
  }
}

function openTask(id: number) {
  if (typeof uni === 'undefined') {
    return
  }

  uni.navigateTo({ url: `/pages/teacher/task-detail?id=${id}` })
}

function createTask() {
  if (typeof uni === 'undefined') {
    return
  }

  uni.navigateTo({ url: '/pages/teacher/task-create' })
}

onMounted(loadTasks)
</script>

<template>
  <view class="teacher-page">
    <view class="page-head">
      <view>
        <text class="page-title">任务列表</text>
        <text class="page-subtitle">按状态切换，先处理发布和复核压力最大的任务。</text>
      </view>
      <view class="create-button" @click="createTask">+ 新建</view>
    </view>

    <view class="tab-row">
      <view
        v-for="tab in statusTabs"
        :key="tab.value"
        :class="['status-tab', { active: tab.value === activeStatus }]"
        @click="activeStatus = tab.value"
      >
        {{ tab.label }}
      </view>
    </view>

    <view class="task-list">
      <view v-for="task in visibleTasks" :key="task.id" class="task-card" @click="openTask(task.id)">
        <view class="task-header">
          <text class="task-title">{{ task.title }}</text>
          <text v-if="task.templateName" class="task-badge">{{ task.templateName }}</text>
        </view>
        <text class="task-meta">{{ task.groupName }} · {{ task.startsAt }} - {{ task.endsAt }}</text>
        <view class="task-stats">
          <text>完成率 {{ task.completionRate }}%</text>
          <text>异常 {{ task.exceptionCount }}</text>
          <text>待审核 {{ task.pendingReviewCount }}</text>
        </view>
      </view>
      <view v-if="visibleTasks.length === 0" class="empty-card">
        <text class="empty-title">当前状态没有任务</text>
        <text class="empty-subtitle">切换到其他状态，或直接创建一个模板任务。</text>
      </view>
    </view>

    <TeacherTabBar active="tasks" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.teacher-page {
  min-height: 100vh;
  padding: 28rpx 24rpx 180rpx;
  background: $page-bg;
}

.page-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16rpx;
}

.page-title {
  display: block;
  font-size: 38rpx;
  font-weight: 700;
  color: $text-primary;
}

.page-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  line-height: 1.5;
  color: $text-secondary;
}

.create-button {
  min-width: 132rpx;
  padding: 18rpx 24rpx;
  border-radius: 18rpx;
  background: $primary;
  color: #fff;
  font-size: 24rpx;
  text-align: center;
}

.tab-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12rpx;
  margin-top: 24rpx;
}

.status-tab {
  padding: 18rpx 12rpx;
  border-radius: 16rpx;
  background: rgba(22, 119, 255, 0.08);
  color: $text-secondary;
  font-size: 24rpx;
  text-align: center;
}

.status-tab.active {
  background: $primary;
  color: #fff;
}

.task-list {
  display: grid;
  gap: 16rpx;
  margin-top: 24rpx;
}

.task-card,
.empty-card {
  padding: 24rpx;
  border-radius: 20rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.task-header,
.task-stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.task-title,
.empty-title {
  font-size: 28rpx;
  font-weight: 700;
  color: $text-primary;
}

.task-badge {
  padding: 8rpx 14rpx;
  border-radius: 999rpx;
  background: $primary-light;
  color: $primary;
  font-size: 20rpx;
}

.task-meta,
.task-stats,
.empty-subtitle {
  display: block;
  margin-top: 12rpx;
  font-size: 22rpx;
  line-height: 1.5;
  color: $text-secondary;
}
</style>
