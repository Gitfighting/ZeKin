<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

import { showError } from '@/services/feedback'
import { submitDailyReport } from '@/services/student'

const today = (() => {
  const d = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
})()

const taskId = ref<number | null>(null)
const reportDate = ref(today)
const content = ref('')
const workHours = ref<string>('')
const mood = ref<'good' | 'normal' | 'bad'>('normal')
const submitting = ref(false)
const submitted = ref(false)

const moodOptions: { label: string; value: 'good' | 'normal' | 'bad' }[] = [
  { label: '良好', value: 'good' },
  { label: '一般', value: 'normal' },
  { label: '较差', value: 'bad' },
]

onLoad((options) => {
  if (options?.task_id) {
    taskId.value = Number(options.task_id)
  }
  if (options?.date) {
    reportDate.value = options.date as string
  }
})

async function handleSubmit() {
  if (!content.value || content.value.trim().length < 10) {
    uni.showToast({ title: '日报内容不能少于10个字', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    await submitDailyReport({
      task_id: taskId.value ?? undefined,
      report_date: reportDate.value,
      content: content.value.trim(),
      work_hours: workHours.value ? Number(workHours.value) : undefined,
      mood: mood.value,
      photo_urls: [],
    })
    submitted.value = true
    uni.showToast({ title: '日报提交成功', icon: 'success' })
    setTimeout(() => {
      uni.navigateBack()
    }, 1500)
  } catch (error) {
    showError(error, '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <scroll-view scroll-y class="report-page">
    <view class="report-page__header">
      <text class="report-page__title">每日日报</text>
      <text class="report-page__date">{{ reportDate }}</text>
    </view>

    <view class="report-page__card">
      <text class="report-page__section-title">今日状态</text>
      <view class="report-page__mood-row">
        <view
          v-for="opt in moodOptions"
          :key="opt.value"
          class="report-page__mood-btn"
          :class="{ 'report-page__mood-btn--active': mood === opt.value }"
          @click="mood = opt.value"
        >
          <text class="report-page__mood-text">{{ opt.label }}</text>
        </view>
      </view>
    </view>

    <view class="report-page__card">
      <text class="report-page__section-title">今日工作内容 <text class="report-page__required">*</text></text>
      <textarea
        v-model="content"
        class="report-page__textarea"
        placeholder="请详细描述今日工作/学习内容，不少于10个字"
        :maxlength="2000"
        auto-height
      />
      <text class="report-page__char-count">{{ content.length }} / 2000</text>
    </view>

    <view class="report-page__card">
      <text class="report-page__section-title">工作时长（小时）</text>
      <input
        v-model="workHours"
        class="report-page__input"
        type="digit"
        placeholder="例如：8"
      />
    </view>

    <view class="report-page__footer">
      <button
        class="report-page__btn"
        :loading="submitting"
        :disabled="submitted"
        @click="handleSubmit"
      >
        {{ submitted ? '已提交' : '提交日报' }}
      </button>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.report-page {
  min-height: 100vh;
  padding: 24rpx;
  background: $page-bg;
}

.report-page__header {
  padding: 16rpx 0 24rpx;
  text-align: center;
}

.report-page__title {
  display: block;
  color: $text-primary;
  font-size: 40rpx;
  font-weight: 700;
}

.report-page__date {
  display: block;
  margin-top: 8rpx;
  color: $text-secondary;
  font-size: 26rpx;
}

.report-page__card {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 24rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.08);
}

.report-page__section-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.report-page__required {
  color: #f53f3f;
  margin-left: 4rpx;
}

.report-page__mood-row {
  display: flex;
  gap: 16rpx;
}

.report-page__mood-btn {
  flex: 1;
  padding: 20rpx 8rpx;
  border-radius: 18rpx;
  background: #f5f7fa;
  text-align: center;
  transition: background 0.2s;
}

.report-page__mood-btn--active {
  background: rgba($primary, 0.12);
  border: 2rpx solid $primary;
}

.report-page__mood-text {
  font-size: 26rpx;
}

.report-page__textarea {
  box-sizing: border-box;
  width: 100%;
  min-height: 200rpx;
  padding: 20rpx;
  border-radius: 18rpx;
  background: #f8fbff;
  border: 2rpx solid rgba($primary, 0.08);
  color: $text-primary;
  font-size: 28rpx;
  line-height: 1.6;
}

.report-page__char-count {
  align-self: flex-end;
  color: $text-secondary;
  font-size: 22rpx;
}

.report-page__input {
  box-sizing: border-box;
  width: 100%;
  height: 92rpx;
  padding: 0 24rpx;
  border-radius: 22rpx;
  background: #f8fbff;
  border: 2rpx solid rgba($primary, 0.08);
  color: $text-primary;
  font-size: 28rpx;
}

.report-page__footer {
  padding-bottom: 40rpx;
}

.report-page__btn {
  border: none;
  border-radius: 999rpx;
  background: $primary;
  font-size: 30rpx;
  font-weight: 600;
  color: #fff;
}
</style>
