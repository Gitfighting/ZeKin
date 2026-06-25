<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import type { CheckinResult, ResultState } from '@/services/student'

const state = ref<ResultState>('pending_review')
const result = ref<CheckinResult>({
  id: '',
  taskId: '',
  state: 'pending_review',
  title: '提交完成',
  subtitle: '结果已提交，请返回记录页查看最新状态。',
  tips: ['如果页面未显示最新结果，请刷新打卡记录。'],
  submittedAt: '',
  locationLabel: '',
})

const toneClass = computed(() => `result-page__status--${result.value.state}`)

onLoad((options) => {
  const nextState = options?.state as ResultState | undefined
  if (nextState && ['normal', 'exception', 'pending_review'].includes(nextState)) {
    state.value = nextState
  }

  const storedResult = typeof uni !== 'undefined'
    ? (uni.getStorageSync('latest_checkin_result') as CheckinResult | undefined)
    : undefined

  if (storedResult?.state === state.value) {
    result.value = storedResult
    return
  }

  result.value = {
    id: '',
    taskId: '',
    state: state.value,
    title: state.value === 'normal' ? '打卡成功' : state.value === 'exception' ? '已记录为异常' : '提交完成，等待复核',
    subtitle: '请以打卡记录页和教师审核结果为准。',
    tips: ['打卡记录页会同步展示后续审核状态。'],
    submittedAt: '',
    locationLabel: '',
  }
})
</script>

<template>
  <scroll-view scroll-y class="result-page">
    <view class="result-page__hero" :class="toneClass">
      <text class="result-page__title">{{ result.title }}</text>
      <text class="result-page__subtitle">{{ result.subtitle }}</text>
    </view>

    <view class="result-page__card">
      <view class="result-page__row">
        <text class="result-page__label">提交时间</text>
        <text class="result-page__value">{{ result.submittedAt }}</text>
      </view>
      <view class="result-page__row">
        <text class="result-page__label">定位结果</text>
        <text class="result-page__value">{{ result.locationLabel }}</text>
      </view>
    </view>

    <view class="result-page__card">
      <text class="result-page__section-title">后续提示</text>
      <text v-for="item in result.tips" :key="item" class="result-page__tip">{{ item }}</text>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.result-page {
  min-height: 100vh;
  padding: 24rpx;
  background: $page-bg;
}

.result-page__hero {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  padding: 40rpx 32rpx;
  border-radius: 28rpx;
  margin-bottom: 24rpx;
  color: #ffffff;
}

.result-page__status--normal {
  background: linear-gradient(180deg, #20c55a 0%, #49d17d 100%);
}

.result-page__status--exception {
  background: linear-gradient(180deg, #f04438 0%, #ff746b 100%);
}

.result-page__status--pending_review {
  background: linear-gradient(180deg, #1677ff 0%, #4ca3ff 100%);
}

.result-page__title {
  font-size: 44rpx;
  font-weight: 700;
}

.result-page__subtitle {
  font-size: 28rpx;
  line-height: 1.6;
}

.result-page__card {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 24rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.08);
}

.result-page__row {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
}

.result-page__label {
  color: $text-secondary;
  font-size: 26rpx;
}

.result-page__value,
.result-page__tip {
  color: $text-primary;
  font-size: 28rpx;
  line-height: 1.6;
}

.result-page__section-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}
</style>
