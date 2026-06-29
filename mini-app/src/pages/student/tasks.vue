<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import TaskCard from '@/components/TaskCard.vue'
import VectorIcon from '@/components/VectorIcon.vue'
import { UI_ICONS } from '@/constants/ui-icons'
import StudentTabBar from '@/components/StudentTabBar.vue'
import { useStudentPageHeroLayout } from '@/composables/useStudentPageHeroLayout'
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
const { brandBarStyle, heroContentStyle } = useStudentPageHeroLayout()

const pageSlogan = '知以明志，勤以立身'

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
  if (filter === 'done') return task.status === 'normal'
  if (filter === 'todo') {
    return task.status !== 'normal' && task.status !== 'exception' && task.status !== 'pending'
  }
  if (filter === 'exception') return task.status === 'exception' || task.status === 'pending'
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
    logInfo('学生任务列表加载成功', {
      count: tasks.value.length,
      todo: tasks.value.filter(
        (t) => t.status !== 'normal' && t.status !== 'exception' && t.status !== 'pending',
      ).length,
      done: tasks.value.filter((t) => t.status === 'normal').length,
      statuses: tasks.value.map((t) => ({ id: t.id, status: t.status })),
    })
  } catch (error) {
    tasks.value = []
    showError(error, '任务列表加载失败')
  }
})
</script>

<template>
  <view class="student-tab-page">
    <scroll-view scroll-y class="tasks-page student-tab-page__scroll">
      <view class="student-page-header-block">
        <view class="student-page-hero">
          <view class="student-page-hero__visual">
            <view class="student-page-hero__bg-window">
              <image class="student-page-hero__bg" src="/static/home.png" mode="widthFix" />
            </view>
          </view>
          <view class="student-page-hero__brand-bar" :style="brandBarStyle">
            <text class="student-page-hero__brand">知勤</text>
          </view>
          <view class="student-page-hero__content" :style="heroContentStyle">
            <text class="student-page-hero__title">打卡任务</text>
            <text class="student-page-hero__slogan">{{ pageSlogan }}</text>
          </view>
        </view>

        <view class="tasks-page__panel student-page-overlap-card">
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
      </view>

      <view class="student-page-content-sheet">
        <view class="tasks-page__list">
          <TaskCard
            v-for="task in visibleTasks"
            :key="task.id"
            :task="task"
            @action="openTask"
            @click="openTask"
          />
          <view v-if="visibleTasks.length === 0" class="tasks-page__empty">
            <VectorIcon class="tasks-page__empty-icon" :src="UI_ICONS.empty" size="64rpx" />
            <text class="tasks-page__empty-text">暂无符合条件的任务</text>
          </view>
        </view>

        <view class="tasks-page__tip">
          <VectorIcon class="tasks-page__tip-icon" :src="UI_ICONS.info" size="28rpx" />
          <text class="tasks-page__tip-text">任务时间以实际发起为准，请及时完成打卡</text>
        </view>
      </view>

      <view class="tab-page__safe-bottom"></view>
    </scroll-view>
    <StudentTabBar active="tasks" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.tasks-page {
  background: $page-bg;
}

.tasks-page__panel {
  padding: 8rpx 24rpx 24rpx;
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
  padding: 0 24rpx 24rpx;
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

<style lang="scss">
@use '@/styles/student-page-hero.scss';
</style>
