<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import RuleSummary from '@/components/RuleSummary.vue'
import StatusTag from '@/components/StatusTag.vue'
import { demoStudentTasks, getStudentTaskDetail, type StudentTask } from '@/services/student'

const task = ref<StudentTask>(demoStudentTasks[0])

const hasException = computed(() => task.value.status === 'exception')

async function loadTask(id?: string) {
  const fallbackTask = demoStudentTasks.find((item) => item.id === id) ?? demoStudentTasks[0]

  try {
    if (!id) {
      task.value = fallbackTask
      return
    }
    task.value = await getStudentTaskDetail(id)
  } catch {
    task.value = fallbackTask
  }
}

function handlePrimaryAction() {
  if (hasException.value) {
    uni.navigateTo({
      url: '/pages/student/appeal?recordId=record-3',
    })
    return
  }

  uni.navigateTo({
    url: `/pages/student/checkin-submit?id=${task.value.id}`,
  })
}

onLoad((options) => {
  void loadTask(options?.id)
})
</script>

<template>
  <scroll-view scroll-y class="detail-page">
    <view class="detail-page__card">
      <view class="detail-page__header">
        <view class="detail-page__title-group">
          <text class="detail-page__type">{{ task.type }}</text>
          <text class="detail-page__title">{{ task.title }}</text>
          <text class="detail-page__desc">{{ task.description }}</text>
        </view>
        <StatusTag :status="task.status" />
      </view>
    </view>

    <RuleSummary
      :time-window="task.timeWindow"
      :location-name="task.locationName"
      :location-hint="task.locationHint"
      :requirements="task.requirements"
    />

    <view class="detail-page__card">
      <text class="detail-page__section-title">时间与地点</text>
      <view class="detail-page__row">
        <text class="detail-page__label">打卡窗口</text>
        <text class="detail-page__value">{{ task.timeWindow }}</text>
      </view>
      <view class="detail-page__row">
        <text class="detail-page__label">签到地点</text>
        <text class="detail-page__value">{{ task.locationName }}</text>
      </view>
      <view class="detail-page__row">
        <text class="detail-page__label">提交要求</text>
        <text class="detail-page__value">{{ task.requirements.join('、') }}</text>
      </view>
    </view>

    <view class="detail-page__card">
      <text class="detail-page__section-title">状态说明</text>
      <text class="detail-page__status-text">
        {{
          hasException
            ? '本任务存在异常记录，请补充申诉材料后等待辅导员复核。'
            : '请在规定时间内完成定位与信息填写，提交后结果会同步到记录与消息页。'
        }}
      </text>
    </view>

    <view class="detail-page__footer">
      <button class="detail-page__button" type="primary" @click="handlePrimaryAction">
        {{ hasException ? '去申诉' : task.actionText }}
      </button>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.detail-page {
  min-height: 100vh;
  padding: 24rpx;
  background: $page-bg;
}

.detail-page__card {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 24rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.08);
}

.detail-page__header,
.detail-page__row {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
}

.detail-page__title-group {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 12rpx;
}

.detail-page__type {
  color: $primary;
  font-size: 24rpx;
  font-weight: 600;
}

.detail-page__title {
  color: $text-primary;
  font-size: 36rpx;
  font-weight: 700;
}

.detail-page__desc,
.detail-page__status-text,
.detail-page__value {
  color: $text-primary;
  font-size: 28rpx;
  line-height: 1.6;
}

.detail-page__section-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.detail-page__label {
  width: 140rpx;
  flex-shrink: 0;
  color: $text-secondary;
  font-size: 26rpx;
}

.detail-page__footer {
  padding-bottom: 24rpx;
}

.detail-page__button {
  border: none;
  border-radius: 999rpx;
  background: $primary;
  font-size: 30rpx;
  font-weight: 600;
}
</style>
