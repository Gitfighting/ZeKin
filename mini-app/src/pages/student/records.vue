<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import { useStudentPageHeroLayout } from '@/composables/useStudentPageHeroLayout'
import { logInfo, showError } from '@/services/feedback'
import {
  ATTENDANCE_LABELS,
  getStudentRecords,
  type RecordFilterKey,
  type StudentRecord,
} from '@/services/student'

const filters: { key: RecordFilterKey; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'present', label: '签到' },
  { key: 'late', label: '迟到' },
  { key: 'early_leave', label: '早退' },
  { key: 'absent', label: '未签到' },
  { key: 'leave', label: '请假' },
]

const { brandBarStyle, heroContentStyle, backButtonStyle, navRightStyle } = useStudentPageHeroLayout()

const pageSlogan = '按日期查看签到、迟到、早退、未签到与请假情况'

const activeFilter = ref<RecordFilterKey>('all')
const selectedDate = ref('')
const records = ref<StudentRecord[]>([])

const attendanceLabelMap = ATTENDANCE_LABELS

const visibleRecords = computed(() => {
  return records.value.filter((record) => {
    const matchDate = !selectedDate.value || record.occurrenceDate === selectedDate.value
    const matchFilter =
      activeFilter.value === 'all' || record.attendanceStatus === activeFilter.value
    return matchDate && matchFilter
  })
})

function handleBack() {
  uni.navigateBack({ delta: 1 })
}

function onDateChange(event: UniHelper.DatePickerChangeEvent) {
  selectedDate.value = event.detail.value
}

function clearDate() {
  selectedDate.value = ''
}

function openAppeal(record: StudentRecord) {
  uni.navigateTo({
    url: `/pages/student/appeal?recordId=${record.id}`,
  })
}

onShow(async () => {
  try {
    records.value = await getStudentRecords()
    logInfo('学生打卡记录加载成功', { count: records.value.length })
  } catch (error) {
    records.value = []
    showError(error, '打卡记录加载失败')
  }
})
</script>

<template>
  <scroll-view scroll-y class="records-page">
    <view class="student-page-header-block">
      <view class="student-page-hero">
        <view class="student-page-hero__visual">
          <view class="student-page-hero__bg-window">
            <image class="student-page-hero__bg" src="/static/home.png" mode="widthFix" />
          </view>
        </view>

        <view class="records-page__nav-bar" :style="brandBarStyle">
          <view
            class="records-page__back"
            :style="backButtonStyle"
            aria-label="返回"
            @click="handleBack"
          ></view>
          <view class="records-page__nav-spacer" :style="navRightStyle"></view>
        </view>

        <view class="student-page-hero__content" :style="heroContentStyle">
          <text class="student-page-hero__title">打卡记录</text>
          <text class="student-page-hero__slogan">{{ pageSlogan }}</text>
        </view>
      </view>

      <view class="records-page__panel student-page-overlap-card">
        <view class="records-page__date-row">
          <text class="records-page__date-label">日期选择</text>
          <picker mode="date" :value="selectedDate" @change="onDateChange">
            <view class="records-page__date-picker">
              <text>{{ selectedDate || '全部日期' }}</text>
              <text class="records-page__date-arrow">▼</text>
            </view>
          </picker>
          <text v-if="selectedDate" class="records-page__date-clear" @click="clearDate">清除</text>
        </view>

        <view class="records-page__filters">
          <view
            v-for="item in filters"
            :key="item.key"
            class="records-page__filter"
            :class="{ 'records-page__filter--active': activeFilter === item.key }"
            @click="activeFilter = item.key"
          >
            <text>{{ item.label }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="student-page-content-sheet records-page__sheet">
      <view class="records-page__list">
        <view v-for="record in visibleRecords" :key="record.id" class="records-page__card">
          <view class="records-page__header">
            <view class="records-page__title-group">
              <text class="records-page__task-title">{{ record.taskTitle }}</text>
              <text class="records-page__meta">{{ record.occurrenceDate || record.submittedAt }}</text>
            </view>
            <text
              class="records-page__badge"
              :class="`records-page__badge--${record.attendanceStatus}`"
            >
              {{ attendanceLabelMap[record.attendanceStatus] }}
            </text>
          </view>
          <text class="records-page__location">提交时间：{{ record.submittedAt }}</text>
          <text v-if="record.reviewComment" class="records-page__comment">{{ record.reviewComment }}</text>
          <button
            v-if="record.attendanceStatus === 'absent'"
            class="records-page__button"
            type="primary"
            @click="openAppeal(record)"
          >
            发起申诉
          </button>
        </view>
        <view v-if="visibleRecords.length === 0" class="records-page__empty">
          <text>暂无符合条件的打卡记录</text>
        </view>
      </view>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.records-page {
  min-height: 100vh;
  background: $page-bg;
}

.records-page__nav-bar {
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

.records-page__back {
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

.records-page__nav-spacer {
  flex-shrink: 0;
}

.records-page__panel {
  padding: 8rpx 24rpx 24rpx;
}

.records-page__sheet {
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
}

.records-page__date-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.records-page__date-label {
  color: $text-secondary;
  font-size: 26rpx;
}

.records-page__date-picker {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 20rpx;
  border-radius: 999rpx;
  background: #f5f8ff;
  color: $text-primary;
  font-size: 26rpx;
}

.records-page__date-arrow {
  color: $text-secondary;
  font-size: 20rpx;
}

.records-page__date-clear {
  color: $primary;
  font-size: 24rpx;
}

.records-page__filters {
  display: flex;
  gap: 12rpx;
  overflow-x: auto;
}

.records-page__filter {
  flex-shrink: 0;
  min-width: 128rpx;
  height: 68rpx;
  line-height: 68rpx;
  border-radius: 999rpx;
  background: #f5f8ff;
  color: $text-secondary;
  text-align: center;
  font-size: 26rpx;
  font-weight: 600;
}

.records-page__filter--active {
  background: $primary;
  color: #fff;
}

.records-page__list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  padding: 0 24rpx 24rpx;
}

.records-page__card {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.08);
}

.records-page__header {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
}

.records-page__title-group {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 8rpx;
}

.records-page__task-title {
  color: $text-primary;
  font-size: 32rpx;
  font-weight: 700;
}

.records-page__meta,
.records-page__location,
.records-page__comment {
  color: $text-secondary;
  font-size: 26rpx;
  line-height: 1.6;
}

.records-page__badge {
  align-self: flex-start;
  padding: 8rpx 18rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  font-weight: 600;
}

.records-page__badge--present {
  background: rgba($success, 0.12);
  color: $success;
}

.records-page__badge--late {
  background: rgba($warning, 0.14);
  color: $warning;
}

.records-page__badge--early_leave {
  background: rgba(124, 58, 237, 0.12);
  color: #7c3aed;
}

.records-page__badge--absent {
  background: rgba($danger, 0.12);
  color: $danger;
}

.records-page__badge--leave {
  background: rgba($primary, 0.12);
  color: $primary;
}

.records-page__button {
  margin: 0;
  border: none;
  border-radius: 999rpx;
  background: $primary;
  font-size: 26rpx;
  font-weight: 600;
}

.records-page__empty {
  padding: 32rpx;
  border-radius: 24rpx;
  background: $card-bg;
  color: $text-secondary;
  font-size: 26rpx;
  text-align: center;
}
</style>

<style lang="scss">
@use '@/styles/student-page-hero.scss';
</style>
