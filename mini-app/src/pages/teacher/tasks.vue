<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import TeacherTabBar from '@/components/TeacherTabBar.vue'
import { readStoredSession } from '@/services/auth'
import { logInfo, showError } from '@/services/feedback'
import { getTeacherTasks, type TeacherTask } from '@/services/teacher'

type FilterKey = 'all' | 'in_progress' | 'ended' | 'pending_review'

const filterTabs: Array<{ key: FilterKey; label: string; countKey?: 'in_progress' | 'pending_review' }> = [
  { key: 'all', label: '全部' },
  { key: 'in_progress', label: '进行中', countKey: 'in_progress' },
  { key: 'ended', label: '已结束' },
  { key: 'pending_review', label: '待审核', countKey: 'pending_review' },
]

const keyword = ref('')
const activeFilter = ref<FilterKey>('all')
const tasks = ref<TeacherTask[]>([])
const teacherName = ref('老师')

const heroContentStyle = ref<Record<string, string>>({
  paddingTop: '112rpx',
  paddingLeft: '32rpx',
  paddingRight: '32rpx',
})

const tabCounts = computed(() => ({
  in_progress: tasks.value.filter(
    (task) => task.status === 'in_progress' || task.status === 'not_started',
  ).length,
  pending_review: tasks.value.filter(
    (task) => task.status === 'pending_review' || task.pendingReviewCount > 0,
  ).length,
}))

const visibleTasks = computed(() => {
  let list = tasks.value

  switch (activeFilter.value) {
    case 'in_progress':
      list = list.filter((task) => task.status === 'in_progress' || task.status === 'not_started')
      break
    case 'ended':
      list = list.filter((task) => task.status === 'ended')
      break
    case 'pending_review':
      list = list.filter(
        (task) => task.status === 'pending_review' || task.pendingReviewCount > 0,
      )
      break
    default:
      break
  }

  const query = keyword.value.trim().toLowerCase()
  if (!query) {
    return list
  }

  return list.filter((task) => {
    const haystack = [task.title, task.groupName, task.templateName].join(' ').toLowerCase()
    return haystack.includes(query)
  })
})

function syncHeroLayout() {
  if (typeof uni === 'undefined') {
    return
  }

  try {
    const menuButton = uni.getMenuButtonBoundingClientRect()
    heroContentStyle.value = {
      paddingTop: `${menuButton.bottom + 12}px`,
      paddingLeft: '32rpx',
      paddingRight: '32rpx',
    }
  } catch {
    // 非小程序环境保留默认占位
  }
}

function statusLabel(task: TeacherTask) {
  if (task.pendingReviewCount > 0 || task.status === 'pending_review') {
    return '待审核'
  }
  if (task.status === 'ended') {
    return '已结束'
  }
  if (task.status === 'not_started') {
    return '未开始'
  }
  return '进行中'
}

function statusClass(task: TeacherTask) {
  if (task.pendingReviewCount > 0 || task.status === 'pending_review') {
    return 'review'
  }
  if (task.status === 'ended') {
    return 'ended'
  }
  return 'active'
}

function taskIconTone(task: TeacherTask) {
  if (task.taskType === 'location') {
    return 'orange'
  }
  if (task.taskType === 'photo') {
    return 'green'
  }
  if (task.status === 'ended') {
    return 'purple'
  }
  return 'blue'
}

function taskIcon(task: TeacherTask) {
  if (task.taskType === 'location') {
    return '🛏️'
  }
  if (task.taskType === 'photo') {
    return '📝'
  }
  return '📘'
}

function taskTypeLabel(task: TeacherTask) {
  if (task.templateName) {
    return task.templateName
  }
  switch (task.taskType) {
    case 'location':
      return '查寝签到'
    case 'photo':
      return '日报批阅'
    case 'attendance':
      return '课堂签到'
    default:
      return '考勤任务'
  }
}

function formatTaskTime(task: TeacherTask) {
  const start = task.startsAt.match(/(\d{2}:\d{2})/)?.[1] ?? task.startsAt
  const end = task.endsAt.match(/(\d{2}:\d{2})/)?.[1] ?? task.endsAt
  return `${start}-${end}`
}

function completionText(task: TeacherTask) {
  if (task.pendingReviewCount > 0) {
    return `${task.pendingReviewCount} 条待审核`
  }
  return `完成率 ${task.completionRate}%`
}

function loadProfileMeta() {
  const session = readStoredSession()
  if (session?.user.displayName) {
    teacherName.value = session.user.displayName.replace(/^用户/, '') || session.user.displayName
  }
}

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
  uni.navigateTo({ url: `/pages/teacher/task-detail?id=${id}` })
}

function createTask() {
  uni.navigateTo({ url: '/pages/teacher/task-create' })
}

onShow(() => {
  syncHeroLayout()
  loadProfileMeta()
  void loadTasks()
})
</script>

<template>
  <view class="tab-page">
    <scroll-view scroll-y class="tasks-page tab-page__scroll">
      <view class="tasks-page__hero">
        <view class="tasks-page__hero-bg-box" aria-hidden="true">
          <image class="tasks-page__hero-bg" src="/static/teacher-home-hero.png" mode="aspectFill" />
        </view>
        <view class="tasks-page__hero-mask"></view>
        <view class="tasks-page__hero-content" :style="heroContentStyle">
          <text class="tasks-page__title">考勤管理</text>
          <text class="tasks-page__subtitle">高效管理考勤任务，轻松掌握出勤情况</text>
        </view>
      </view>

      <view class="tasks-page__panel">
        <view class="tasks-page__search">
          <text class="tasks-page__search-icon">🔍</text>
          <input
            v-model="keyword"
            class="tasks-page__search-input"
            placeholder="搜索课程/班级/任务名称"
            confirm-type="search"
          />
          <view v-if="keyword" class="tasks-page__search-clear" @click="keyword = ''">×</view>
        </view>

        <scroll-view scroll-x class="tasks-page__filters" :show-scrollbar="false">
          <view class="tasks-page__filters-inner">
            <view
              v-for="tab in filterTabs"
              :key="tab.key"
              class="tasks-page__filter"
              :class="{ 'tasks-page__filter--active': activeFilter === tab.key }"
              @click="activeFilter = tab.key"
            >
              <text>{{ tab.label }}</text>
              <text
                v-if="tab.countKey && tabCounts[tab.countKey] > 0"
                class="tasks-page__filter-badge"
              >
                {{ tabCounts[tab.countKey] }}
              </text>
            </view>
          </view>
        </scroll-view>

        <view class="tasks-page__create" @click="createTask">
          <text class="tasks-page__create-icon">+</text>
          <text>创建任务</text>
        </view>

        <view class="tasks-page__list">
          <view
            v-for="task in visibleTasks"
            :key="task.id"
            class="task-card"
            @click="openTask(task.id)"
          >
            <view class="task-card__head">
              <view class="task-card__icon" :class="`task-card__icon--${taskIconTone(task)}`">
                <text>{{ taskIcon(task) }}</text>
              </view>
              <view class="task-card__main">
                <view class="task-card__title-row">
                  <text class="task-card__title">{{ task.title }}</text>
                  <view class="task-card__status" :class="`task-card__status--${statusClass(task)}`">
                    <text>{{ statusLabel(task) }}</text>
                    <text class="task-card__status-arrow">›</text>
                  </view>
                </view>
                <view class="task-card__tags">
                  <text class="task-card__tag task-card__tag--type">{{ taskTypeLabel(task) }}</text>
                  <text class="task-card__tag">{{ teacherName }}</text>
                </view>
              </view>
            </view>

            <view class="task-card__meta">
              <text class="task-card__meta-line">🕐 {{ formatTaskTime(task) }}</text>
              <text class="task-card__meta-line">👥 {{ task.groupName }}</text>
              <text class="task-card__meta-line">📊 {{ completionText(task) }}</text>
            </view>

            <view class="task-card__progress-row">
              <view class="task-card__progress-track">
                <view
                  class="task-card__progress-bar"
                  :class="`task-card__progress-bar--${taskIconTone(task)}`"
                  :style="{ width: `${Math.min(task.completionRate, 100)}%` }"
                />
              </view>
              <text class="task-card__progress-text">{{ task.completionRate }}%</text>
            </view>
          </view>

          <view v-if="visibleTasks.length === 0" class="tasks-page__empty">
            <text class="tasks-page__empty-title">暂无匹配任务</text>
            <text class="tasks-page__empty-sub">调整筛选条件，或创建一个新的考勤任务</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <TeacherTabBar active="tasks" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.tasks-page {
  min-height: 100%;
  padding-bottom: $tab-bar-safe-bottom;
  background: $page-bg;
  box-sizing: border-box;
}

.tasks-page__hero {
  position: relative;
  height: calc(360rpx + 30px);
  overflow: hidden;
}

.tasks-page__hero-bg-box {
  position: absolute;
  right: 0;
  bottom: 0;
  left: -10%;
  width: 118%;
  height: 200%;
}

.tasks-page__hero-bg {
  width: 100%;
  height: 100%;
}

.tasks-page__hero-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(15, 120, 255, 0.06) 0%,
    rgba(15, 120, 255, 0.28) 100%
  );
}

.tasks-page__hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  color: #fff;
}

.tasks-page__title {
  font-size: 52rpx;
  font-weight: 700;
}

.tasks-page__subtitle {
  font-size: 28rpx;
  opacity: 0.92;
  line-height: 1.5;
}

.tasks-page__panel {
  position: relative;
  z-index: 3;
  margin: -48rpx 24rpx 0;
  padding: 24rpx 20rpx 32rpx;
  border-radius: 28rpx;
  background: $card-bg;
  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.1);
}

.tasks-page__search {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 0 24rpx;
  height: 80rpx;
  border-radius: 999rpx;
  background: #f5f8ff;
  border: 2rpx solid rgba($primary, 0.08);
}

.tasks-page__search-icon {
  flex-shrink: 0;
  font-size: 28rpx;
  opacity: 0.55;
}

.tasks-page__search-input {
  flex: 1;
  min-width: 0;
  height: 80rpx;
  color: $text-primary;
  font-size: 28rpx;
}

.tasks-page__search-clear {
  flex-shrink: 0;
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.08);
  color: $text-secondary;
  font-size: 28rpx;
  line-height: 40rpx;
  text-align: center;
}

.tasks-page__filters {
  width: 100%;
  margin-top: 24rpx;
  white-space: nowrap;
}

.tasks-page__filters-inner {
  display: inline-flex;
  gap: 16rpx;
  padding-right: 8rpx;
}

.tasks-page__filter {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 16rpx 28rpx;
  border-radius: 999rpx;
  background: #f5f8ff;
  color: $text-secondary;
  font-size: 26rpx;
  white-space: nowrap;
}

.tasks-page__filter--active {
  background: $primary;
  color: #fff;
  font-weight: 600;
}

.tasks-page__filter-badge {
  min-width: 32rpx;
  height: 32rpx;
  padding: 0 8rpx;
  border-radius: 999rpx;
  background: $warning;
  color: #fff;
  font-size: 20rpx;
  line-height: 32rpx;
  text-align: center;
}

.tasks-page__filter--active .tasks-page__filter-badge {
  background: rgba(255, 255, 255, 0.92);
  color: $warning;
}

.tasks-page__create {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  margin-top: 24rpx;
  height: 88rpx;
  border-radius: 999rpx;
  background: $primary;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
}

.tasks-page__create-icon {
  font-size: 36rpx;
  line-height: 1;
}

.tasks-page__list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-top: 28rpx;
}

.task-card {
  padding: 24rpx;
  border-radius: 24rpx;
  background: #fff;
  border: 1rpx solid rgba(15, 23, 42, 0.05);
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.04);
}

.task-card__head {
  display: flex;
  gap: 16rpx;
}

.task-card__icon {
  display: flex;
  width: 80rpx;
  height: 80rpx;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 34rpx;
}

.task-card__icon--blue {
  background: rgba($primary, 0.12);
}

.task-card__icon--orange {
  background: rgba($warning, 0.14);
}

.task-card__icon--green {
  background: rgba($success, 0.14);
}

.task-card__icon--purple {
  background: rgba(124, 58, 237, 0.14);
}

.task-card__main {
  flex: 1;
  min-width: 0;
}

.task-card__title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12rpx;
}

.task-card__title {
  flex: 1;
  min-width: 0;
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 700;
  line-height: 1.4;
}

.task-card__status {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  gap: 4rpx;
  font-size: 24rpx;
  font-weight: 600;
}

.task-card__status--active {
  color: $primary;
}

.task-card__status--review {
  color: $warning;
}

.task-card__status--ended {
  color: $text-muted;
}

.task-card__status-arrow {
  font-size: 28rpx;
  line-height: 1;
}

.task-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
  margin-top: 10rpx;
}

.task-card__tag {
  padding: 4rpx 14rpx;
  border-radius: 999rpx;
  background: #f2f4f7;
  color: $text-secondary;
  font-size: 22rpx;
}

.task-card__tag--type {
  background: rgba($primary, 0.1);
  color: $primary;
}

.task-card__meta {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  margin-top: 18rpx;
}

.task-card__meta-line {
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.5;
}

.task-card__progress-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-top: 18rpx;
}

.task-card__progress-track {
  flex: 1;
  height: 12rpx;
  overflow: hidden;
  border-radius: 999rpx;
  background: #eef2f6;
}

.task-card__progress-bar {
  height: 100%;
  border-radius: 999rpx;
}

.task-card__progress-bar--blue {
  background: $primary;
}

.task-card__progress-bar--orange {
  background: $warning;
}

.task-card__progress-bar--green {
  background: $success;
}

.task-card__progress-bar--purple {
  background: #7c3aed;
}

.task-card__progress-text {
  flex-shrink: 0;
  color: $text-secondary;
  font-size: 22rpx;
}

.tasks-page__empty {
  padding: 48rpx 24rpx;
  text-align: center;
}

.tasks-page__empty-title {
  display: block;
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 700;
}

.tasks-page__empty-sub {
  display: block;
  margin-top: 10rpx;
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.5;
}
</style>
