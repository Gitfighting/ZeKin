<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import TaskCard from '@/components/TaskCard.vue'
import StudentTabBar from '@/components/StudentTabBar.vue'
import { refreshStudentUnreadMessageCount } from '@/composables/useStudentUnreadMessages'
import { logInfo, showError } from '@/services/feedback'
import { getStudentTasks, type StudentTask } from '@/services/student'

type StatusFilter = 'all' | 'todo' | 'done' | 'exception'
type TypeFilter = 'all' | 'daily' | 'class' | 'internship' | 'activity'
type TimeFilter = 'all' | '7d' | '30d'

const statusTabs: { key: StatusFilter; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'todo', label: '待完成' },
  { key: 'done', label: '已完成' },
  { key: 'exception', label: '异常' },
]

const typeOptions: { key: TypeFilter; label: string }[] = [
  { key: 'all', label: '全部类型' },
  { key: 'daily', label: '日常任务' },
  { key: 'class', label: '课堂类' },
  { key: 'internship', label: '实习类' },
  { key: 'activity', label: '活动类' },
]

const timeOptions: { key: TimeFilter; label: string }[] = [
  { key: '7d', label: '最近7天' },
  { key: '30d', label: '最近30天' },
  { key: 'all', label: '全部时间' },
]

const activeStatus = ref<StatusFilter>('all')
const activeType = ref<TypeFilter>('all')
const activeTime = ref<TimeFilter>('7d')
const tasks = ref<StudentTask[]>([])

function inferTypeKey(task: StudentTask): TypeFilter {
  const haystack = `${task.title}${task.type}${task.description}`
  if (/宿舍|查寝|晚间/.test(haystack)) return 'daily'
  if (/课堂|课程|上课/.test(haystack)) return 'class'
  if (/实习|实践|校外/.test(haystack)) return 'internship'
  if (/活动|班团|会议/.test(haystack)) return 'activity'
  return 'daily'
}

function parseTaskDate(task: StudentTask): Date | null {
  const match = task.deadline.match(/(\d{4})-(\d{2})-(\d{2})/)
  if (!match) return null
  return new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]))
}

function matchStatusFilter(task: StudentTask, filter: StatusFilter) {
  if (filter === 'all') return true
  if (filter === 'todo') return task.status === 'in-progress' || task.status === 'pending'
  if (filter === 'done') return task.status === 'normal' || task.status === 'ended'
  if (filter === 'exception') return task.status === 'exception'
  return true
}

function matchTimeFilter(task: StudentTask, filter: TimeFilter) {
  if (filter === 'all') return true
  const taskDate = parseTaskDate(task)
  if (!taskDate) return true
  const days = filter === '7d' ? 7 : 30
  const cutoff = new Date()
  cutoff.setHours(0, 0, 0, 0)
  cutoff.setDate(cutoff.getDate() - days)
  return taskDate >= cutoff
}

const activeTypeLabel = computed(
  () => typeOptions.find((item) => item.key === activeType.value)?.label ?? '全部类型',
)
const activeTimeLabel = computed(
  () => timeOptions.find((item) => item.key === activeTime.value)?.label ?? '最近7天',
)

const visibleTasks = computed(() =>
  tasks.value.filter(
    (task) =>
      matchStatusFilter(task, activeStatus.value) &&
      (activeType.value === 'all' || inferTypeKey(task) === activeType.value) &&
      matchTimeFilter(task, activeTime.value),
  ),
)

function openTask(task: StudentTask) {
  uni.navigateTo({
    url: `/pages/student/task-detail?id=${task.id}`,
  })
}

function openTypePicker() {
  uni.showActionSheet({
    itemList: typeOptions.map((item) => item.label),
    success: (result) => {
      const picked = typeOptions[result.tapIndex]
      if (picked) {
        activeType.value = picked.key
      }
    },
  })
}

function openTimePicker() {
  uni.showActionSheet({
    itemList: timeOptions.map((item) => item.label),
    success: (result) => {
      const picked = timeOptions[result.tapIndex]
      if (picked) {
        activeTime.value = picked.key
      }
    },
  })
}

onShow(async () => {
  void refreshStudentUnreadMessageCount()
  try {
    tasks.value = await getStudentTasks()
    logInfo('学生任务列表加载成功', { count: tasks.value.length })
  } catch (error) {
    tasks.value = []
    showError(error, '任务列表加载失败')
  }
})
</script>

<template>
  <view class="student-tab-page">
    <scroll-view scroll-y class="tasks-page student-tab-page__scroll">
      <view class="tasks-page__hero">
        <view class="tasks-page__hero-bg-box" aria-hidden="true">
          <image class="tasks-page__hero-bg" src="/static/student-home-hero.png" mode="aspectFill" />
        </view>
        <view class="tasks-page__hero-mask" aria-hidden="true"></view>
        <view class="tasks-page__hero-content">
          <text class="tasks-page__title">打卡任务</text>
          <text class="tasks-page__subtitle">按时完成打卡任务，养成自律习惯，记录成长每一步</text>
        </view>
      </view>

      <view class="tasks-page__panel">
        <view class="tasks-page__tabs">
          <view
            v-for="item in statusTabs"
            :key="item.key"
            class="tasks-page__tab"
            :class="{ 'tasks-page__tab--active': activeStatus === item.key }"
            @click="activeStatus = item.key"
          >
            <text>{{ item.label }}</text>
          </view>
        </view>

        <view class="tasks-page__dropdowns">
          <view class="tasks-page__dropdown" @click="openTypePicker">
            <text>{{ activeTypeLabel }}</text>
            <text class="tasks-page__dropdown-arrow">▾</text>
          </view>
          <view class="tasks-page__dropdown tasks-page__dropdown--static">
            <text>全部班级</text>
            <text class="tasks-page__dropdown-arrow">▾</text>
          </view>
          <view class="tasks-page__dropdown" @click="openTimePicker">
            <text>{{ activeTimeLabel }}</text>
            <text class="tasks-page__dropdown-arrow">▾</text>
          </view>
        </view>
      </view>

      <view class="tasks-page__list">
        <TaskCard
          v-for="task in visibleTasks"
          :key="task.id"
          :task="task"
          @action="openTask"
          @click="openTask"
        />
        <view v-if="visibleTasks.length === 0" class="tasks-page__empty">
          <text class="tasks-page__empty-icon">📭</text>
          <text class="tasks-page__empty-text">暂无符合条件的任务</text>
        </view>
      </view>

      <view class="tasks-page__tip">
        <text class="tasks-page__tip-icon">ⓘ</text>
        <text class="tasks-page__tip-text">任务时间以实际发起为准，请及时完成打卡</text>
      </view>

      <view class="tab-page__safe-bottom"></view>
    </scroll-view>
    <StudentTabBar active="tasks" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.tasks-page {
  background: #f5f8fc;
}

.tasks-page__hero {
  position: relative;
  height: 360rpx;
  overflow: hidden;
}

.tasks-page__hero-bg-box {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 175%;
}

.tasks-page__hero-bg {
  width: 100%;
  height: 100%;
}

.tasks-page__hero-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(15, 120, 255, 0.08) 0%, rgba(15, 120, 255, 0.42) 100%);
}

.tasks-page__hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding: 112rpx 32rpx 48rpx;
}

.tasks-page__title,
.tasks-page__subtitle {
  color: #ffffff;
}

.tasks-page__title {
  font-size: 48rpx;
  font-weight: 700;
}

.tasks-page__subtitle {
  max-width: 620rpx;
  font-size: 26rpx;
  line-height: 1.55;
  opacity: 0.96;
}

.tasks-page__panel {
  position: relative;
  z-index: 3;
  margin: -36rpx 24rpx 0;
  padding: 8rpx 24rpx 24rpx;
  border-radius: 28rpx 28rpx 24rpx 24rpx;
  background: #fff;
  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.08);
}

.tasks-page__tabs {
  display: flex;
  border-bottom: 1rpx solid rgba(15, 23, 42, 0.06);
}

.tasks-page__tab {
  position: relative;
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  height: 88rpx;
  color: $text-secondary;
  font-size: 28rpx;
  font-weight: 500;
}

.tasks-page__tab--active {
  color: $primary;
  font-weight: 700;
}

.tasks-page__tab--active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 48rpx;
  height: 6rpx;
  border-radius: 999rpx;
  background: $primary;
  transform: translateX(-50%);
}

.tasks-page__dropdowns {
  display: flex;
  gap: 12rpx;
  margin-top: 20rpx;
}

.tasks-page__dropdown {
  display: flex;
  min-width: 0;
  flex: 1;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
  height: 64rpx;
  padding: 0 12rpx;
  border: 1rpx solid rgba(15, 23, 42, 0.08);
  border-radius: 16rpx;
  background: #fafbfd;
  color: $text-primary;
  font-size: 24rpx;
}

.tasks-page__dropdown--static {
  color: $text-secondary;
}

.tasks-page__dropdown-arrow {
  color: $text-muted;
  font-size: 20rpx;
}

.tasks-page__list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding: 24rpx;
}

.tasks-page__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  padding: 64rpx 32rpx;
  border-radius: 24rpx;
  background: #fff;
}

.tasks-page__empty-icon {
  font-size: 56rpx;
}

.tasks-page__empty-text {
  color: $text-secondary;
  font-size: 26rpx;
}

.tasks-page__tip {
  display: flex;
  align-items: flex-start;
  gap: 10rpx;
  padding: 0 32rpx 16rpx;
}

.tasks-page__tip-icon {
  flex-shrink: 0;
  color: $text-muted;
  font-size: 24rpx;
  line-height: 1.5;
}

.tasks-page__tip-text {
  color: $text-muted;
  font-size: 24rpx;
  line-height: 1.5;
}

.tab-page__safe-bottom {
  height: $tab-bar-safe-bottom;
}
</style>
