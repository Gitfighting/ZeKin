<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import StatusTag from '@/components/StatusTag.vue'
import { demoStudentRecords, getStudentRecords, type ResultState, type StudentRecord } from '@/services/student'

type FilterKey = 'all' | ResultState

const filters: { key: FilterKey; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'normal', label: '正常' },
  { key: 'pending_review', label: '待复核' },
  { key: 'exception', label: '异常' },
]

const activeFilter = ref<FilterKey>('all')
const records = ref<StudentRecord[]>(demoStudentRecords)

const statusToneMap: Record<ResultState, 'normal' | 'pending' | 'exception'> = {
  normal: 'normal',
  pending_review: 'pending',
  exception: 'exception',
}

const visibleRecords = computed(() => {
  if (activeFilter.value === 'all') {
    return records.value
  }
  return records.value.filter((record) => record.status === activeFilter.value)
})

function openAppeal(record: StudentRecord) {
  uni.navigateTo({
    url: `/pages/student/appeal?recordId=${record.id}`,
  })
}

onShow(async () => {
  try {
    records.value = await getStudentRecords(activeFilter.value)
  } catch {
    records.value = demoStudentRecords
  }
})
</script>

<template>
  <scroll-view scroll-y class="records-page">
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

    <view class="records-page__list">
      <view v-for="record in visibleRecords" :key="record.id" class="records-page__card">
        <view class="records-page__header">
          <view class="records-page__title-group">
            <text class="records-page__title">{{ record.taskTitle }}</text>
            <text class="records-page__meta">{{ record.type }} · {{ record.submittedAt }}</text>
          </view>
          <StatusTag :status="statusToneMap[record.status]" />
        </view>
        <text class="records-page__location">定位：{{ record.locationLabel }}</text>
        <text v-if="record.reviewComment" class="records-page__comment">{{ record.reviewComment }}</text>
        <button
          v-if="record.status === 'exception'"
          class="records-page__button"
          type="primary"
          @click="openAppeal(record)"
        >
          发起申诉
        </button>
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

.records-page__filters {
  display: flex;
  gap: 16rpx;
  padding: 24rpx;
  overflow-x: auto;
}

.records-page__filter {
  flex-shrink: 0;
  min-width: 132rpx;
  height: 72rpx;
  line-height: 72rpx;
  border-radius: 999rpx;
  background: #ffffff;
  color: $text-secondary;
  text-align: center;
  font-size: 26rpx;
  font-weight: 600;
}

.records-page__filter--active {
  background: $primary;
  color: #ffffff;
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
  gap: 16rpx;
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
  gap: 10rpx;
}

.records-page__title {
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

.records-page__button {
  margin: 0;
  border: none;
  border-radius: 999rpx;
  background: $primary;
  font-size: 26rpx;
  font-weight: 600;
}
</style>
