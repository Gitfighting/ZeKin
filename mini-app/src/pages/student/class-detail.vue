<script setup lang="ts">
import { onLoad, onReady, onShow } from '@dcloudio/uni-app'
import { computed, onMounted, ref } from 'vue'

import { useStudentPageHeroLayout } from '@/composables/useStudentPageHeroLayout'
import { logError, logInfo, showError } from '@/services/feedback'
import {
  CLASS_ATTENDANCE_LABELS,
  getStudentGroupAttendance,
  type ClassAttendanceStatus,
  type StudentGroupAttendanceDetail,
  type StudentGroupAttendanceSummary,
  type StudentGroupAttendanceTimelineItem,
  type StudentGroupTaskAttendance,
} from '@/services/student'
import { formatBeijingDate, formatBeijingClock, formatTimelineDateTime } from '@/utils/datetime'

const LOG_PREFIX = '[班级详情]'

const { brandBarStyle, heroContentStyle, backButtonStyle, navRightStyle, syncHeroLayout } =
  useStudentPageHeroLayout()

const pageSlogan = '查看本班级打卡任务与签到统计'

const loading = ref(true)
const loadError = ref('')
const groupId = ref<number>()
const groupName = ref('班级详情')
const detail = ref<StudentGroupAttendanceDetail | null>(null)
const showAttendanceModal = ref(false)
const skipNextShowReload = ref(false)
const scrollHeight = ref(0)

function trace(step: string, payload?: unknown) {
  logInfo(`${LOG_PREFIX} ${step}`, payload)
}

function syncScrollHeight() {
  if (typeof uni === 'undefined') {
    scrollHeight.value = 667
    return
  }
  try {
    const systemInfo = uni.getSystemInfoSync()
    scrollHeight.value = systemInfo.windowHeight ?? 667
    trace('同步滚动区域高度', { scrollHeight: scrollHeight.value })
  } catch (error) {
    scrollHeight.value = 667
    logError(`${LOG_PREFIX} 获取窗口高度失败`, error)
  }
}

function createEmptySummary(): StudentGroupAttendanceSummary {
  return {
    checkedInCount: 0,
    publishedCount: 0,
    presentCount: 0,
    lateCount: 0,
    earlyLeaveCount: 0,
    absentCount: 0,
    leaveCount: 0,
    expiredCount: 0,
    sickLeaveCount: 0,
    personalLeaveCount: 0,
    officialLeaveCount: 0,
  }
}

const displaySummary = computed(() => detail.value?.summary ?? createEmptySummary())
const tasks = computed(() => detail.value?.tasks ?? [])
const timeline = computed(() => detail.value?.timeline ?? [])
const teacherName = computed(() => detail.value?.group.teacherName ?? '')

const attendanceStatGrid = computed(() => {
  const summary = displaySummary.value
  return [
    { key: 'present', label: '出勤', count: summary.presentCount, tone: 'normal' },
    { key: 'expired', label: '已过期', count: summary.expiredCount, tone: 'normal' },
    { key: 'absent', label: '缺勤', count: summary.absentCount, tone: 'danger' },
    { key: 'early_leave', label: '早退', count: summary.earlyLeaveCount, tone: 'normal' },
    { key: 'late', label: '迟到', count: summary.lateCount, tone: 'normal' },
    { key: 'sick', label: '病假', count: summary.sickLeaveCount, tone: 'normal' },
    { key: 'personal', label: '事假', count: summary.personalLeaveCount, tone: 'normal' },
    { key: 'official', label: '公假', count: summary.officialLeaveCount, tone: 'normal' },
  ]
})

const completionRate = computed(() => {
  const total = displaySummary.value.publishedCount
  if (!total) {
    return 0
  }
  return Math.round((displaySummary.value.checkedInCount / total) * 100)
})

const chartSegments = computed(() => {
  const summary = displaySummary.value
  if (!summary.publishedCount) {
    return []
  }
  const items: Array<{ key: ClassAttendanceStatus; count: number; color: string; label: string }> = [
    { key: 'present', count: summary.presentCount, color: '#22c55e', label: CLASS_ATTENDANCE_LABELS.present },
    { key: 'late', count: summary.lateCount, color: '#f59e0b', label: CLASS_ATTENDANCE_LABELS.late },
    {
      key: 'early_leave',
      count: summary.earlyLeaveCount,
      color: '#8b5cf6',
      label: CLASS_ATTENDANCE_LABELS.early_leave,
    },
    { key: 'leave', count: summary.leaveCount, color: '#64748b', label: CLASS_ATTENDANCE_LABELS.leave },
    { key: 'absent', count: summary.absentCount, color: '#ef4444', label: CLASS_ATTENDANCE_LABELS.absent },
  ]
  return items.filter((item) => item.count > 0)
})

function attendanceLabel(status: ClassAttendanceStatus): string {
  return CLASS_ATTENDANCE_LABELS[status] ?? CLASS_ATTENDANCE_LABELS.absent
}

function openAttendanceModal() {
  trace('打开签到记录弹窗')
  showAttendanceModal.value = true
}

function closeAttendanceModal() {
  showAttendanceModal.value = false
}

function timelineTimeLabel(item: StudentGroupAttendanceTimelineItem): string {
  return formatTimelineDateTime(item.occurredAt)
}

function timelineStatusTone(item: StudentGroupAttendanceTimelineItem): string {
  if (item.isExpired) return 'expired'
  if (item.statusLabel === '出勤') return 'present'
  if (item.statusLabel === '缺勤') return 'absent'
  if (item.statusLabel === '迟到' || item.statusLabel === '早退') return 'warning'
  return 'muted'
}

function handleBack() {
  trace('点击返回')
  uni.navigateBack({ delta: 1 })
}

function formatTaskWindow(task: StudentGroupTaskAttendance): string {
  const startDate = formatBeijingDate(task.startsAt)
  const endDate = formatBeijingDate(task.endsAt)
  const startClock = formatBeijingClock(task.startsAt)
  const endClock = formatBeijingClock(task.endsAt)
  if (startDate && endDate && startDate === endDate) {
    return `${startDate} ${startClock}-${endClock}`
  }
  if (startDate && endDate) {
    return `${startDate} ${startClock} ~ ${endDate} ${endClock}`
  }
  return startDate || endDate || '—'
}

function taskOccurrenceLabel(task: StudentGroupTaskAttendance): string {
  if (!task.isRecurring || task.occurrenceCount <= 1) {
    return ''
  }
  return `已签 ${task.checkedInCount}/${task.occurrenceCount} 次`
}

function statusTone(status: ClassAttendanceStatus): string {
  if (status === 'present') return 'done'
  if (status === 'late' || status === 'early_leave' || status === 'partial') return 'warning'
  if (status === 'leave') return 'muted'
  return 'missed'
}

function openTaskDetail(task: StudentGroupTaskAttendance) {
  trace('打开任务详情', { taskId: task.id, title: task.title })
  uni.navigateTo({ url: `/pages/student/task-detail?id=${task.id}` })
}

async function loadDetail(id: number, reason: string) {
  trace('开始加载考勤详情', { groupId: id, reason })
  loading.value = true
  loadError.value = ''
  try {
    detail.value = await getStudentGroupAttendance(id)
    groupName.value = detail.value.group.name || groupName.value
    trace('考勤详情加载成功', {
      groupId: id,
      groupName: groupName.value,
      summary: detail.value.summary,
      taskCount: detail.value.tasks.length,
    })
  } catch (error) {
    detail.value = null
    loadError.value = '班级考勤加载失败，请稍后重试'
    logError(`${LOG_PREFIX} 考勤详情加载失败`, error)
    showError(error, '班级考勤加载失败')
  } finally {
    loading.value = false
    trace('加载流程结束', {
      groupId: id,
      loading: loading.value,
      hasDetail: Boolean(detail.value),
      loadError: loadError.value,
    })
  }
}

function bootstrap(options?: Record<string, string | undefined>, reason = 'onLoad') {
  trace(`进入页面：${reason}`, options)
  syncHeroLayout()
  syncScrollHeight()

  const rawId = options?.id ?? options?.groupId
  const rawName = options?.name
  if (rawName) {
    groupName.value = decodeURIComponent(String(rawName))
    trace('解析班级名称', { groupName: groupName.value })
  }

  const id = Number(rawId)
  if (!rawId || Number.isNaN(id)) {
    loading.value = false
    loadError.value = '缺少班级编号，无法加载详情'
    trace('缺少班级编号', { rawId })
    uni.showToast({ title: '缺少班级编号', icon: 'none' })
    return
  }

  groupId.value = id
  loadDetail(id, reason)
}

onMounted(() => {
  trace('页面组件已挂载')
  syncHeroLayout()
  syncScrollHeight()
})

onReady(() => {
  trace('页面初次渲染完成', {
    groupId: groupId.value,
    groupName: groupName.value,
    scrollHeight: scrollHeight.value,
    loading: loading.value,
  })
  syncScrollHeight()
})

onLoad((options) => {
  skipNextShowReload.value = true
  bootstrap(options as Record<string, string | undefined>, 'onLoad')
})

onShow(() => {
  trace('页面显示', { groupId: groupId.value, skipNextShowReload: skipNextShowReload.value })
  syncHeroLayout()
  syncScrollHeight()
  if (skipNextShowReload.value) {
    skipNextShowReload.value = false
    return
  }
  if (groupId.value) {
    loadDetail(groupId.value, 'onShow')
  }
})
</script>

<template>
  <view class="class-detail-page">
    <scroll-view
      scroll-y
      class="class-detail-page__scroll"
      :style="scrollHeight ? { height: `${scrollHeight}px` } : undefined"
      :enable-back-to-top="true"
    >
    <view class="student-page-header-block">
      <view class="student-page-hero">
        <view class="student-page-hero__visual">
          <view class="student-page-hero__bg-window">
            <image class="student-page-hero__bg" src="/static/home.png" mode="widthFix" />
          </view>
        </view>

        <view class="class-detail-page__nav-bar" :style="brandBarStyle">
          <view
            class="class-detail-page__back"
            :style="backButtonStyle"
            aria-label="返回"
            @click="handleBack"
          ></view>
          <view class="class-detail-page__nav-spacer" :style="navRightStyle"></view>
        </view>

        <view class="student-page-hero__content" :style="heroContentStyle">
          <text class="student-page-hero__title">{{ groupName }}</text>
          <text class="student-page-hero__slogan">{{ pageSlogan }}</text>
        </view>
      </view>

      <view class="class-detail-page__panel student-page-overlap-card">
        <view v-if="loading" class="class-detail-page__panel-inner class-detail-page__panel-inner--state">
          <text class="class-detail-page__state-text">加载中...</text>
        </view>

        <view v-else-if="loadError" class="class-detail-page__panel-inner class-detail-page__panel-inner--state">
          <text class="class-detail-page__error-text">{{ loadError }}</text>
          <button
            v-if="groupId"
            class="class-detail-page__retry-btn"
            @click="loadDetail(groupId!, 'retry')"
          >
            重新加载
          </button>
        </view>

        <view v-else class="class-detail-page__panel-inner">
          <view class="class-detail-page__summary-head" @click="openAttendanceModal">
            <view>
              <text class="class-detail-page__summary-label">签到记录</text>
              <text class="class-detail-page__summary-value">
                {{ displaySummary.checkedInCount }}/{{ displaySummary.publishedCount }}
              </text>
            </view>
            <text class="class-detail-page__summary-rate">完成率 {{ completionRate }}%</text>
          </view>

          <view v-if="teacherName" class="class-detail-page__teacher">
            教师：{{ teacherName }}
          </view>

          <view v-if="chartSegments.length" class="class-detail-page__chart">
            <view class="class-detail-page__chart-bar">
              <view
                v-for="segment in chartSegments"
                :key="segment.key"
                class="class-detail-page__chart-segment"
                :style="{
                  flex: segment.count,
                  background: segment.color,
                }"
              ></view>
            </view>
            <view class="class-detail-page__chart-legend">
              <view
                v-for="segment in chartSegments"
                :key="segment.key"
                class="class-detail-page__legend-item"
              >
                <view
                  class="class-detail-page__legend-dot"
                  :style="{ background: segment.color }"
                ></view>
                <text class="class-detail-page__legend-text">
                  {{ segment.label }} {{ segment.count }}
                </text>
              </view>
            </view>
          </view>

          <view v-else class="class-detail-page__chart-empty">
            <text class="class-detail-page__chart-empty-text">暂无签到统计数据</text>
          </view>
        </view>
      </view>
    </view>

    <view class="student-page-content-sheet class-detail-page__sheet">
      <view v-if="!loading && !loadError" class="class-detail-page__list-wrap">
        <text class="class-detail-page__section-title">打卡任务记录</text>

        <view v-if="!tasks.length" class="class-detail-page__empty">
          <text class="class-detail-page__empty-text">该班级暂无已发布的打卡任务</text>
        </view>

        <view v-else class="class-detail-page__list">
          <view
            v-for="task in tasks"
            :key="task.id"
            class="class-detail-page__card"
            @click="openTaskDetail(task)"
          >
            <view class="class-detail-page__card-main">
              <text class="class-detail-page__card-title">{{ task.title }}</text>
              <text class="class-detail-page__card-time">{{ formatTaskWindow(task) }}</text>
              <text v-if="taskOccurrenceLabel(task)" class="class-detail-page__card-sub">
                {{ taskOccurrenceLabel(task) }}
              </text>
            </view>
            <text
              class="class-detail-page__card-status"
              :class="`class-detail-page__card-status--${statusTone(task.attendanceStatus)}`"
            >
              {{ attendanceLabel(task.attendanceStatus) }}
            </text>
          </view>
        </view>
      </view>
    </view>
    </scroll-view>

    <view
      v-if="showAttendanceModal"
      class="class-detail-page__modal-mask"
      @click="closeAttendanceModal"
    >
      <view class="class-detail-page__modal" @click.stop>
        <view class="class-detail-page__modal-stats">
          <view
            v-for="stat in attendanceStatGrid"
            :key="stat.key"
            class="class-detail-page__stat-cell"
          >
            <text
              class="class-detail-page__stat-value"
              :class="{
                'class-detail-page__stat-value--danger': stat.tone === 'danger',
              }"
            >
              {{ stat.count }}
            </text>
            <text class="class-detail-page__stat-label">{{ stat.label }}</text>
          </view>
        </view>

        <scroll-view scroll-y class="class-detail-page__modal-timeline">
          <view v-if="!timeline.length" class="class-detail-page__timeline-empty">
            <text class="class-detail-page__timeline-empty-text">暂无签到记录</text>
          </view>
          <view v-else class="class-detail-page__timeline">
            <view
              v-for="(item, index) in timeline"
              :key="`${item.taskId}-${item.occurrenceDate}-${index}`"
              class="class-detail-page__timeline-item"
            >
              <view class="class-detail-page__timeline-rail">
                <view class="class-detail-page__timeline-dot"></view>
                <view
                  v-if="index < timeline.length - 1"
                  class="class-detail-page__timeline-line"
                ></view>
              </view>
              <view class="class-detail-page__timeline-body">
                <text class="class-detail-page__timeline-time">{{ timelineTimeLabel(item) }}</text>
                <text v-if="item.initiatorName" class="class-detail-page__timeline-initiator">
                  发起人:{{ item.initiatorName }}
                </text>
                <text
                  class="class-detail-page__timeline-status"
                  :class="`class-detail-page__timeline-status--${timelineStatusTone(item)}`"
                >
                  {{ item.statusLabel }}
                </text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.class-detail-page {
  min-height: 100vh;
  background: $page-bg;
}

.class-detail-page__scroll {
  width: 100%;
  min-height: 100vh;
  box-sizing: border-box;
  background: $page-bg;
}

.class-detail-page__nav-bar {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24rpx 0 32rpx;
  box-sizing: border-box;
}

.class-detail-page__back {
  position: relative;
  flex-shrink: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.28);
  box-shadow: 0 4rpx 16rpx rgba(15, 60, 120, 0.12);

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20rpx;
    height: 20rpx;
    margin-top: -11rpx;
    margin-left: -5rpx;
    border-left: 4rpx solid #fff;
    border-bottom: 4rpx solid #fff;
    transform: rotate(45deg);
  }
}

.class-detail-page__nav-spacer {
  flex-shrink: 0;
}

.class-detail-page__panel {
  padding: 8rpx 24rpx 24rpx;
}

.class-detail-page__panel-inner {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.class-detail-page__panel-inner--state {
  align-items: center;
  justify-content: center;
  min-height: 120rpx;
}

.class-detail-page__state-text,
.class-detail-page__error-text {
  color: $text-secondary;
  font-size: 26rpx;
  text-align: center;
}

.class-detail-page__error-text {
  color: $danger;
}

.class-detail-page__retry-btn {
  margin-top: 16rpx;
  border-radius: 999rpx;
  background: $primary;
  color: #fff;
  font-size: 26rpx;
}

.class-detail-page__sheet {
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
}

.class-detail-page__summary-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16rpx;
  padding: 4rpx 0;
}

.class-detail-page__summary-head:active {
  opacity: 0.88;
}

.class-detail-page__summary-label {
  display: block;
  color: $text-secondary;
  font-size: 24rpx;
}

.class-detail-page__summary-value {
  display: block;
  margin-top: 8rpx;
  color: $text-primary;
  font-size: 44rpx;
  font-weight: 700;
  line-height: 1.2;
}

.class-detail-page__summary-rate {
  color: $primary;
  font-size: 26rpx;
  font-weight: 600;
}

.class-detail-page__teacher {
  color: $text-secondary;
  font-size: 24rpx;
}

.class-detail-page__chart {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.class-detail-page__chart-bar {
  display: flex;
  overflow: hidden;
  height: 20rpx;
  border-radius: 999rpx;
  background: #e5e7eb;
}

.class-detail-page__chart-segment {
  min-width: 4rpx;
}

.class-detail-page__chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx 20rpx;
}

.class-detail-page__legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.class-detail-page__legend-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
}

.class-detail-page__legend-text {
  color: $text-secondary;
  font-size: 22rpx;
}

.class-detail-page__chart-empty {
  padding: 8rpx 0;
}

.class-detail-page__chart-empty-text {
  color: $text-secondary;
  font-size: 24rpx;
}

.class-detail-page__list-wrap {
  padding: 0 24rpx 24rpx;
}

.class-detail-page__section-title {
  display: block;
  margin-bottom: 16rpx;
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.class-detail-page__empty {
  padding: 48rpx 0;
  text-align: center;
}

.class-detail-page__empty-text {
  color: $text-secondary;
  font-size: 26rpx;
}

.class-detail-page__list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.class-detail-page__card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16rpx;
  padding: 24rpx;
  border-radius: 22rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.class-detail-page__card:active {
  opacity: 0.92;
}

.class-detail-page__card-main {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 8rpx;
}

.class-detail-page__card-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.4;
}

.class-detail-page__card-time {
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.5;
}

.class-detail-page__card-sub {
  color: $primary;
  font-size: 22rpx;
}

.class-detail-page__card-status {
  flex-shrink: 0;
  padding: 6rpx 16rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
  font-weight: 600;
  white-space: nowrap;
}

.class-detail-page__card-status--done {
  background: rgba($success, 0.14);
  color: $success;
}

.class-detail-page__card-status--warning {
  background: rgba($warning, 0.14);
  color: $warning;
}

.class-detail-page__card-status--missed {
  background: rgba($danger, 0.12);
  color: $danger;
}

.class-detail-page__card-status--muted {
  background: rgba($text-muted, 0.12);
  color: $text-muted;
}

.class-detail-page__modal-mask {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48rpx 40rpx;
  box-sizing: border-box;
  background: rgba(15, 23, 42, 0.45);
}

.class-detail-page__modal {
  display: flex;
  width: 100%;
  max-height: 78vh;
  flex-direction: column;
  border-radius: 28rpx;
  background: #fff;
  box-shadow: 0 24rpx 48rpx rgba(15, 23, 42, 0.18);
  overflow: hidden;
}

.class-detail-page__modal-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20rpx 8rpx;
  padding: 36rpx 28rpx 28rpx;
  border-bottom: 1rpx solid #f1f5f9;
}

.class-detail-page__stat-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.class-detail-page__stat-value {
  color: $text-primary;
  font-size: 36rpx;
  font-weight: 700;
  line-height: 1.2;
}

.class-detail-page__stat-value--danger {
  color: $danger;
}

.class-detail-page__stat-label {
  color: $text-secondary;
  font-size: 22rpx;
}

.class-detail-page__modal-timeline {
  max-height: 52vh;
  padding: 24rpx 28rpx 32rpx;
  box-sizing: border-box;
}

.class-detail-page__timeline-empty {
  padding: 48rpx 0;
  text-align: center;
}

.class-detail-page__timeline-empty-text {
  color: $text-secondary;
  font-size: 26rpx;
}

.class-detail-page__timeline {
  display: flex;
  flex-direction: column;
}

.class-detail-page__timeline-item {
  display: flex;
  gap: 20rpx;
  min-height: 120rpx;
}

.class-detail-page__timeline-rail {
  position: relative;
  display: flex;
  width: 24rpx;
  flex-shrink: 0;
  flex-direction: column;
  align-items: center;
}

.class-detail-page__timeline-dot {
  width: 16rpx;
  height: 16rpx;
  margin-top: 8rpx;
  border-radius: 50%;
  background: #fbbf24;
  flex-shrink: 0;
}

.class-detail-page__timeline-line {
  width: 2rpx;
  flex: 1;
  min-height: 80rpx;
  margin-top: 8rpx;
  background: #fde68a;
}

.class-detail-page__timeline-body {
  display: flex;
  min-width: 0;
  flex: 1;
  flex-direction: column;
  gap: 8rpx;
  padding-bottom: 28rpx;
}

.class-detail-page__timeline-time {
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 600;
  line-height: 1.4;
}

.class-detail-page__timeline-initiator {
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.5;
}

.class-detail-page__timeline-status {
  font-size: 26rpx;
  font-weight: 600;
  line-height: 1.4;
}

.class-detail-page__timeline-status--present {
  color: $success;
}

.class-detail-page__timeline-status--absent,
.class-detail-page__timeline-status--expired {
  color: $danger;
}

.class-detail-page__timeline-status--warning {
  color: $warning;
}

.class-detail-page__timeline-status--muted {
  color: $text-muted;
}
</style>

<style lang="scss">
@use '@/styles/student-page-hero.scss';
</style>
