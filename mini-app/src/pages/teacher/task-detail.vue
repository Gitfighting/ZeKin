<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import {
  endTeacherTask,
  getTeacherTaskDetail,
  publishTeacherTask,
  setStudentAttendance,
  type AttendanceStatus,
  type TeacherTaskDetail,
} from '@/services/teacher'
import { logInfo, showError, showSuccess } from '@/services/feedback'

const STATUS_LABELS: Record<string, string> = {
  submitted: '签到',
  present: '签到',
  late: '迟到',
  early_leave: '早退',
  absent: '未签到',
  missing: '未签到',
  approved: '已通过',
  pending_review: '待审核',
  rejected: '已驳回',
  leave: '请假',
}

function statusLabel(status?: string) {
  return STATUS_LABELS[status ?? 'missing'] ?? status ?? '未签到'
}

function statusClass(status?: string) {
  if (status === 'absent' || status === 'missing' || status === 'rejected') return 'status-danger'
  if (status === 'late' || status === 'early_leave') return 'status-warn'
  if (status === 'leave' || status === 'pending_review') return 'status-info'
  return 'status-ok'
}

async function markAttendance(studentId: number, status: AttendanceStatus) {
  if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
    return
  }
  try {
    await setStudentAttendance(detail.value.task.id, studentId, status)
    await loadDetail()
    expandedStudentId.value = null
    showSuccess('已更新考勤')
  } catch (error) {
    showError(error, '更新考勤失败')
  }
}

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

const expandedStudentId = ref<number | null>(null)

function toggleAttendanceEditor(studentId: number) {
  expandedStudentId.value = expandedStudentId.value === studentId ? null : studentId
}

function isAttendanceEditorOpen(studentId: number) {
  return expandedStudentId.value === studentId
}

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

function openQrProjection() {
  if (typeof uni === 'undefined') {
    return
  }

  uni.navigateTo({ url: `/pages/teacher/qr-projection?id=${detail.value.task.id}` })
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
        <view v-if="!detail.task.published" class="secondary-button" @click="publishTask">发布任务</view>
        <view v-if="detail.task.methods?.includes('qr_code')" class="secondary-button" @click="openQrProjection">二维码投屏</view>
        <view class="primary-button" @click="endTask">结束任务</view>
      </view>
      <view v-if="detail.task.checkinCode" class="checkin-code-banner">
        <text class="checkin-code-banner__label">今日签到码</text>
        <text class="checkin-code-banner__value">{{ detail.task.checkinCode }}</text>
        <text class="checkin-code-banner__hint">请口头或投屏公布给学生，学生端不会显示此码</text>
      </view>
    </view>

    <view class="section-card">
      <text class="section-title">学生列表</text>
      <view v-for="student in detail.students" :key="student.id" class="student-card">
        <view class="student-head">
          <view>
            <text class="row-title">{{ student.name }}</text>
            <text class="row-subtitle">{{ student.submittedAt || '未提交' }}</text>
          </view>
          <text class="status-chip" :class="statusClass(student.status)">{{ statusLabel(student.status) }}</text>
        </view>
        <view class="edit-attendance" @click="toggleAttendanceEditor(student.id)">
          <text class="edit-attendance__label">修改签到状态</text>
          <text class="edit-attendance__arrow">{{ isAttendanceEditorOpen(student.id) ? '收起' : '展开' }}</text>
        </view>
        <view v-if="isAttendanceEditorOpen(student.id)" class="attend-row">
          <view class="attend-btn ok" @click="markAttendance(student.id, 'present')">签到</view>
          <view class="attend-btn late" @click="markAttendance(student.id, 'late')">迟到</view>
          <view class="attend-btn early" @click="markAttendance(student.id, 'early_leave')">早退</view>
          <view class="attend-btn info" @click="markAttendance(student.id, 'leave')">请假</view>
          <view class="attend-btn danger" @click="markAttendance(student.id, 'absent')">未签到</view>
        </view>
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

.checkin-code-banner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  margin-top: 20rpx;
  padding: 24rpx;
  border-radius: 18rpx;
  background: linear-gradient(135deg, rgba(22, 119, 255, 0.08), rgba(22, 119, 255, 0.02));
  border: 2rpx dashed rgba(22, 119, 255, 0.25);
}

.checkin-code-banner__label {
  font-size: 24rpx;
  color: $text-secondary;
}

.checkin-code-banner__value {
  font-size: 56rpx;
  font-weight: 800;
  letter-spacing: 12rpx;
  color: $primary;
}

.checkin-code-banner__hint {
  font-size: 20rpx;
  color: $text-secondary;
  text-align: center;
  line-height: 1.5;
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

.student-card {
  padding: 20rpx 0;
  border-bottom: 1rpx solid rgba(102, 112, 133, 0.12);
}

.student-card:last-child {
  border-bottom: 0;
}

.student-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-chip {
  padding: 6rpx 18rpx;
  border-radius: 999rpx;
  font-size: 22rpx;
}

.status-ok {
  background: rgba(22, 163, 74, 0.12);
  color: #16a34a;
}

.status-warn {
  background: rgba(234, 179, 8, 0.16);
  color: #b45309;
}

.status-danger {
  background: rgba(220, 38, 38, 0.12);
  color: #dc2626;
}

.attend-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  margin-top: 16rpx;
}

.attend-btn {
  min-width: calc(33.33% - 8rpx);
  flex: 1;
  padding: 14rpx 0;
  border-radius: 14rpx;
  text-align: center;
  font-size: 22rpx;
  border: 1rpx solid transparent;
}

.attend-btn.ok {
  background: rgba(22, 163, 74, 0.1);
  color: #16a34a;
}

.attend-btn.late,
.attend-btn.early {
  background: rgba(234, 179, 8, 0.12);
  color: #b45309;
}

.attend-btn.info {
  background: rgba(22, 119, 255, 0.1);
  color: #1677ff;
}

.attend-btn.danger {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.status-info {
  background: rgba(22, 119, 255, 0.12);
  color: #1677ff;
}

.edit-attendance {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16rpx;
  padding: 16rpx 20rpx;
  border-radius: 14rpx;
  background: #f5f7fa;
}

.edit-attendance__label {
  font-size: 24rpx;
  color: $text-primary;
}

.edit-attendance__arrow {
  font-size: 22rpx;
  color: $primary;
}
</style>
