<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import TeacherTabBar from '@/components/TeacherTabBar.vue'
import { readStoredSession } from '@/services/auth'
import { logInfo, showError } from '@/services/feedback'
import {
  getTeacherDashboard,
  getTeacherTasks,
  type TeacherDashboard,
  type TeacherTask,
} from '@/services/teacher'

const dailyQuote = '木叶飞舞之处，火亦生生不息。'

const quickEntries = [
  {
    key: 'create',
    label: '发起签到',
    sub: '课堂/活动签到',
    path: '/pages/teacher/task-create',
    tone: 'blue',
    icon: '📅',
  },
  {
    key: 'tasks',
    label: '考勤管理',
    sub: '查看考勤记录',
    path: '/pages/teacher/tasks',
    tone: 'green',
    icon: '📋',
  },
  {
    key: 'groups',
    label: '班级管理',
    sub: '学生与班级',
    path: '/pages/teacher/groups',
    tone: 'orange',
    icon: '👥',
  },
  {
    key: 'review',
    label: '审核管理',
    sub: '缺勤/异常审核',
    path: '/pages/teacher/exceptions',
    tone: 'purple',
    icon: '⚠️',
  },
] as const

const displayName = ref('老师')
const teacherRole = ref('思政教师 / 班主任')
const loading = ref(false)
const dashboard = ref<TeacherDashboard>({
  todayTasks: 0,
  exceptions: 0,
  pendingReviews: 0,
  quickCreateCount: 0,
})
type TodoStatusTone = 'checkin' | 'progress' | 'review' | 'done'
type TodoIconTone = 'blue' | 'green' | 'orange' | 'purple'

interface TodayTodoItem {
  id: number
  title: string
  subtitle: string
  statusLabel: string
  statusTone: TodoStatusTone
  progress: string
  icon: string
  iconTone: TodoIconTone
  task: TeacherTask
}

const todayTasks = ref<TeacherTask[]>([])

const todayTodos = computed<TodayTodoItem[]>(() =>
  todayTasks.value.map((task) => mapTaskToTodoItem(task)),
)

const brandBarStyle = ref<Record<string, string>>({
  top: '48px',
  height: '32px',
})

const heroContentStyle = ref<Record<string, string>>({
  paddingTop: '112rpx',
  paddingLeft: '32rpx',
  paddingRight: '32rpx',
})

function syncHeroLayout() {
  if (typeof uni === 'undefined') {
    return
  }

  try {
    const menuButton = uni.getMenuButtonBoundingClientRect()
    brandBarStyle.value = {
      top: `${menuButton.top}px`,
      height: `${menuButton.height}px`,
    }
    heroContentStyle.value = {
      paddingTop: `${menuButton.bottom + 12}px`,
      paddingLeft: '32rpx',
      paddingRight: '32rpx',
    }
  } catch {
    // 非小程序环境保留默认占位
  }
}

const greetingPrefix = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) {
    return '上午好'
  }
  if (hour < 18) {
    return '下午好'
  }
  return '晚上好'
})

function mapTaskToTodoItem(task: TeacherTask): TodayTodoItem {
  const subtitle = task.groupName || `${task.startsAt} - ${task.endsAt}`
  const iconTone = resolveIconTone(task)
  const statusTone = resolveStatusTone(task)
  return {
    id: task.id,
    title: task.title,
    subtitle,
    statusLabel: resolveStatusLabel(task, statusTone),
    statusTone,
    progress: resolveProgressText(task, statusTone),
    icon: resolveTaskIcon(task, statusTone),
    iconTone,
    task,
  }
}

function resolveStatusTone(task: TeacherTask): TodoStatusTone {
  if (task.pendingReviewCount > 0 || isReviewTask(task)) {
    return 'review'
  }
  if (task.status === 'ended' || task.completionRate >= 100) {
    return 'done'
  }
  if (task.taskType === 'location' || task.templateName?.includes('查寝')) {
    return 'progress'
  }
  return 'checkin'
}

function isReviewTask(task: TeacherTask) {
  return task.taskType === 'photo'
    || task.taskType === 'custom'
    || task.templateName?.includes('日报')
    || task.templateName?.includes('日志')
}

function resolveStatusLabel(task: TeacherTask, tone: TodoStatusTone) {
  switch (tone) {
    case 'review':
      return '待批阅'
    case 'done':
      return '已完成'
    case 'progress':
      return '待完成'
    default:
      return '待签到'
  }
}

function resolveProgressText(task: TeacherTask, tone: TodoStatusTone) {
  if (tone === 'review') {
    const pending = task.pendingReviewCount
    if (pending > 0) {
      return `${pending} 条待批阅`
    }
    return `${task.exceptionCount} 条异常`
  }
  if (tone === 'progress') {
    return `完成率 ${task.completionRate}%`
  }
  if (task.groupName.includes('、') || task.groupName.includes('/')) {
    return `完成率 ${task.completionRate}%`
  }
  return `完成率 ${task.completionRate}%`
}

function resolveTaskIcon(task: TeacherTask, tone: TodoStatusTone) {
  if (tone === 'review') {
    return '📝'
  }
  if (task.taskType === 'location' || tone === 'progress') {
    return '🛏️'
  }
  return '📘'
}

function resolveIconTone(task: TeacherTask): TodoIconTone {
  if (task.pendingReviewCount > 0 || isReviewTask(task)) {
    return 'purple'
  }
  if (task.taskType === 'location') {
    return 'green'
  }
  if (task.taskType === 'photo') {
    return 'purple'
  }
  return 'blue'
}

function openQuickEntry(path: string) {
  uni.navigateTo({ url: path })
}

function openTask(task: TeacherTask) {
  uni.navigateTo({ url: `/pages/teacher/task-detail?id=${task.id}` })
}

function openAllTasks() {
  uni.navigateTo({ url: '/pages/teacher/tasks' })
}

function loadProfileMeta() {
  const session = readStoredSession()
  if (session?.user.displayName) {
    displayName.value = session.user.displayName.replace(/^用户/, '') || session.user.displayName
  }

  if (typeof uni !== 'undefined') {
    const cachedUser = uni.getStorageSync('user_profile') as
      | { display_name?: string; title?: string }
      | undefined
    if (cachedUser?.display_name) {
      displayName.value = cachedUser.display_name
    }
    if (cachedUser?.title) {
      teacherRole.value = cachedUser.title
    }
  }
}

onShow(async () => {
  syncHeroLayout()
  loadProfileMeta()
  loading.value = true

  try {
    const [stats, tasks] = await Promise.all([
      getTeacherDashboard(),
      getTeacherTasks(),
    ])
    dashboard.value = stats
    todayTasks.value = tasks
      .filter((task) => task.status === 'in_progress' || task.status === 'not_started' || task.status === 'pending_review')
      .sort((a, b) => {
        const reviewDiff = b.pendingReviewCount - a.pendingReviewCount
        if (reviewDiff !== 0) {
          return reviewDiff
        }
        return b.completionRate - a.completionRate
      })
      .slice(0, 3)
    logInfo('教师首页加载成功', { taskCount: todayTasks.value.length })
  } catch (error) {
    todayTasks.value = []
    showError(error, '教师首页加载失败')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <view class="tab-page">
    <scroll-view scroll-y class="home-page tab-page__scroll">
      <view class="home-page__hero">
        <view class="home-page__hero-bg-box home-page__hero-bg-box--teacher" aria-hidden="true">
          <image class="home-page__hero-bg" src="/static/teacher-home-hero.png" mode="aspectFill" />
        </view>
        <view class="home-page__hero-mask"></view>

        <view class="home-page__brand-bar" :style="brandBarStyle">
          <text class="home-page__brand">知勤</text>
        </view>

        <view class="home-page__hero-content" :style="heroContentStyle">
          <text class="home-page__greeting">{{ greetingPrefix }}，{{ displayName }} 👋</text>
          <text class="home-page__slogan">{{ teacherRole }}</text>
        </view>
      </view>

      <view class="home-page__toolbar home-page__toolbar--four">
        <view
          v-for="entry in quickEntries"
          :key="entry.key"
          class="home-page__tool"
          @click="openQuickEntry(entry.path)"
        >
          <view class="home-page__tool-icon" :class="`home-page__tool-icon--${entry.tone}`">
            <text>{{ entry.icon }}</text>
          </view>
          <text class="home-page__tool-label">{{ entry.label }}</text>
          <text class="home-page__tool-sub">{{ entry.sub }}</text>
        </view>
      </view>

      <view class="home-page__quote-spacer" aria-hidden="true"></view>
    </scroll-view>

    <view class="home-page__pinned-stack">
      <view class="home-page__tasks-card home-page__tasks-card--pinned">
        <view class="home-page__section-head">
          <view class="home-page__section-title-wrap">
            <text class="home-page__section-icon">✅</text>
            <text class="home-page__section-title">今日待办</text>
          </view>
          <text class="home-page__section-link" @click.stop="openAllTasks">全部任务 ›</text>
        </view>

        <view v-if="loading" class="home-page__tasks-empty">加载中...</view>
        <view v-else-if="todayTodos.length === 0" class="home-page__tasks-empty">今日暂无待办任务</view>
        <view v-else class="home-page__todo-list">
          <view
            v-for="item in todayTodos"
            :key="item.id"
            class="home-page__todo-item"
            @click="openTask(item.task)"
          >
            <view class="home-page__todo-icon" :class="`home-page__todo-icon--${item.iconTone}`">
              <text>{{ item.icon }}</text>
            </view>
            <view class="home-page__todo-main">
              <text class="home-page__todo-title">{{ item.title }}</text>
              <text class="home-page__todo-subtitle">{{ item.subtitle }}</text>
            </view>
            <view class="home-page__todo-side">
              <text class="home-page__todo-status" :class="`home-page__todo-status--${item.statusTone}`">
                {{ item.statusLabel }}
              </text>
              <text class="home-page__todo-progress">{{ item.progress }}</text>
            </view>
            <text class="home-page__todo-arrow">›</text>
          </view>
        </view>
      </view>

      <view class="home-page__quote home-page__quote--stacked">
        <view class="home-page__quote-bg-box" aria-hidden="true">
          <image
            class="home-page__quote-bg"
            src="/static/man-blue-write.png"
            mode="aspectFill"
          />
        </view>
        <view class="home-page__quote-copy">
          <text class="home-page__quote-title">每日一言</text>
          <text class="home-page__quote-text">{{ dailyQuote }}</text>
        </view>
      </view>
    </view>

    <TeacherTabBar active="home" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.home-page {
  background: $page-bg;
}

.home-page__hero {
  position: relative;
  height: calc(420rpx + 30px);
  overflow: hidden;
}

.home-page__hero-bg-box {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 175%;
}

.home-page__hero-bg-box--teacher {
  left: -10%;
  width: 118%;
  height: 200%;
}

.home-page__hero-bg {
  width: 100%;
  height: 100%;
}

.home-page__hero-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(15, 120, 255, 0.06) 0%,
    rgba(15, 120, 255, 0.22) 55%,
    rgba(15, 120, 255, 0.42) 100%
  );
}

.home-page__hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  color: #fff;
}

.home-page__brand-bar {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 3;
  display: flex;
  align-items: center;
  padding-left: 32rpx;
  box-sizing: border-box;
}

.home-page__brand {
  font-size: 42rpx;
  font-weight: 700;
  color: #fff;
  line-height: 1;
}

.home-page__greeting {
  margin-top: 8rpx;
  font-size: 52rpx;
  font-weight: 700;
}

.home-page__slogan {
  font-size: 30rpx;
  opacity: 0.92;
}

.home-page__toolbar {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16rpx;
  margin: -56rpx 24rpx 0;
  padding: 28rpx 20rpx;
  border-radius: 28rpx;
  background: $card-bg;
  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.1);
  position: relative;
  z-index: 3;
}

.home-page__toolbar--four {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12rpx;
  padding: 28rpx 16rpx;
}

.home-page__tool {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.home-page__tool-icon {
  display: flex;
  width: 88rpx;
  height: 88rpx;
  align-items: center;
  justify-content: center;
  border-radius: 24rpx;
  font-size: 36rpx;
}

.home-page__tool-icon--blue {
  background: linear-gradient(180deg, #4ca3ff 0%, #1677ff 100%);
}

.home-page__tool-icon--green {
  background: linear-gradient(180deg, #5fe08d 0%, #20c55a 100%);
}

.home-page__tool-icon--orange {
  background: linear-gradient(180deg, #ffb347 0%, #ff9f1a 100%);
}

.home-page__tool-icon--purple {
  background: linear-gradient(180deg, #b794ff 0%, #7c3aed 100%);
}

.home-page__tool-label {
  color: $text-primary;
  font-size: 24rpx;
  font-weight: 700;
  text-align: center;
}

.home-page__tool-sub {
  color: $text-secondary;
  font-size: 20rpx;
  text-align: center;
}

.home-page__section {
  margin: 28rpx 24rpx 0;
}

.home-page__tasks-card {
  padding: 28rpx 20rpx;
  border-radius: 28rpx;
  background: $card-bg;
  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.1);
}

.home-page__section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid rgba(15, 23, 42, 0.06);
}

.home-page__section-title-wrap {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.home-page__section-icon {
  font-size: 34rpx;
}

.home-page__section-title {
  color: $text-primary;
  font-size: 34rpx;
  font-weight: 700;
}

.home-page__section-link {
  color: $text-secondary;
  font-size: 26rpx;
}

.home-page__todo-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.home-page__todo-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.home-page__todo-icon {
  display: flex;
  width: 80rpx;
  height: 80rpx;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 22rpx;
  font-size: 34rpx;
}

.home-page__todo-icon--blue {
  background: rgba($primary, 0.12);
}

.home-page__todo-icon--green {
  background: rgba($success, 0.14);
}

.home-page__todo-icon--orange {
  background: rgba($warning, 0.14);
}

.home-page__todo-icon--purple {
  background: rgba(124, 58, 237, 0.14);
}

.home-page__todo-main {
  flex: 1;
  min-width: 0;
}

.home-page__todo-title {
  display: block;
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 700;
  line-height: 1.4;
}

.home-page__todo-subtitle {
  display: block;
  margin-top: 6rpx;
  color: $text-secondary;
  font-size: 22rpx;
  line-height: 1.4;
}

.home-page__todo-side {
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  align-items: flex-end;
  gap: 6rpx;
}

.home-page__todo-status {
  font-size: 24rpx;
  font-weight: 600;
}

.home-page__todo-status--checkin {
  color: $primary;
}

.home-page__todo-status--progress {
  color: $warning;
}

.home-page__todo-status--review {
  color: #7c3aed;
}

.home-page__todo-status--done {
  color: $success;
}

.home-page__todo-progress {
  color: $text-muted;
  font-size: 22rpx;
}

.home-page__todo-arrow {
  flex-shrink: 0;
  color: $text-muted;
  font-size: 36rpx;
  font-weight: 600;
  line-height: 1;
}

.home-page__tasks-empty {
  padding: 8rpx 0;
  color: $text-secondary;
  font-size: 26rpx;
  text-align: center;
}

.home-page__summary-line {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid rgba(15, 23, 42, 0.06);
  color: $text-secondary;
  font-size: 24rpx;
  text-align: center;
}

.home-page__pinned-stack {
  position: fixed;
  right: 24rpx;
  left: 24rpx;
  bottom: calc(#{$tab-bar-height} + env(safe-area-inset-bottom) + 24rpx);
  z-index: 900;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.home-page__tasks-card--pinned {
  margin: 0;
  max-height: 360rpx;
  overflow: hidden;
}

.home-page__quote {
  position: relative;
  overflow: hidden;
  min-height: 200rpx;
  margin: 28rpx 24rpx 0;
  padding: 28rpx 20rpx;
  border-radius: 28rpx;
  background: linear-gradient(90deg, #eef6ff 0%, #f7fbff 48%, #fdfdfd 100%);
  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.1);
}

.home-page__quote--stacked {
  margin: 0;
}

.home-page__quote-spacer {
  height: calc(200rpx + 16rpx + 360rpx + 56rpx + 24rpx);
}

.home-page__quote-bg-box {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 58%;
}

.home-page__quote-bg {
  width: 100%;
  height: 100%;
}

.home-page__quote-copy {
  position: relative;
  z-index: 1;
  display: flex;
  max-width: 58%;
  flex-direction: column;
  gap: calc(10rpx + 2px);
}

.home-page__quote-title {
  color: $primary;
  font-size: 30rpx;
  font-weight: 700;
}

.home-page__quote-text {
  color: $text-primary;
  font-size: 26rpx;
  line-height: calc(1.7em + 2px);
}
</style>
