<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

import DynamicForm from '@/components/DynamicForm.vue'
import LocationPicker from '@/components/LocationPicker.vue'
import { demoStudentTasks, demoCheckinResults, submitCheckin, type StudentTask } from '@/services/student'
import type { LocationResult } from '@/services/location'

const task = ref<StudentTask>(demoStudentTasks[0])
const location = ref<LocationResult | null>(null)
const verificationCode = ref('')
const dynamicForm = ref<Record<string, string>>({})
const submitting = ref(false)

function applyTask(nextTask: StudentTask) {
  task.value = nextTask
  dynamicForm.value = {}
}

async function loadTask(id?: string) {
  const matched = demoStudentTasks.find((item) => item.id === id) ?? demoStudentTasks[0]
  applyTask(matched)
}

async function handleSubmit() {
  if (!location.value) {
    uni.showToast({
      title: '请先获取当前位置',
      icon: 'none',
    })
    return
  }

  if (!verificationCode.value) {
    uni.showToast({
      title: '请输入动态签到码',
      icon: 'none',
    })
    return
  }

  submitting.value = true

  try {
    await submitCheckin({
      taskId: task.value.id,
      longitude: location.value.longitude,
      latitude: location.value.latitude,
      verificationCode: verificationCode.value,
      formData: { ...dynamicForm.value },
    })
  } catch {
    // Demo fallback keeps the closed loop usable when backend contracts are absent.
  } finally {
    submitting.value = false
  }

  const state = task.value.status === 'exception' ? 'exception' : 'pending_review'
  const demoResult = demoCheckinResults[state]
  uni.navigateTo({
    url: `/pages/student/result?state=${demoResult.state}`,
  })
}

onLoad((options) => {
  void loadTask(options?.id)
})
</script>

<template>
  <scroll-view scroll-y class="submit-page">
    <view class="submit-page__card">
      <text class="submit-page__title">{{ task.title }}</text>
      <text class="submit-page__subtitle">{{ task.timeWindow }} · {{ task.locationName }}</text>
    </view>

    <view class="submit-page__card">
      <text class="submit-page__section-title">位置校验</text>
      <LocationPicker v-model="location" />
    </view>

    <view class="submit-page__card">
      <text class="submit-page__section-title">动态签到码</text>
      <input
        v-model="verificationCode"
        class="submit-page__input"
        placeholder="请输入老师发布的动态签到码"
      />
    </view>

    <view class="submit-page__card">
      <text class="submit-page__section-title">补充信息</text>
      <DynamicForm v-model="dynamicForm" :fields="task.dynamicFields" />
    </view>

    <view v-if="task.faceRule.enabled" class="submit-page__card">
      <text class="submit-page__section-title">人脸核验</text>
      <text class="submit-page__note">{{ task.faceRule.tip }}</text>
    </view>

    <view class="submit-page__footer">
      <button class="submit-page__button" type="primary" :loading="submitting" @click="handleSubmit">
        提交打卡
      </button>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.submit-page {
  min-height: 100vh;
  padding: 24rpx;
  background: $page-bg;
}

.submit-page__card {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 24rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.08);
}

.submit-page__title {
  color: $text-primary;
  font-size: 36rpx;
  font-weight: 700;
}

.submit-page__subtitle,
.submit-page__note {
  color: $text-secondary;
  font-size: 26rpx;
  line-height: 1.6;
}

.submit-page__section-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.submit-page__input {
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

.submit-page__footer {
  padding-bottom: 24rpx;
}

.submit-page__button {
  border: none;
  border-radius: 999rpx;
  background: $primary;
  font-size: 30rpx;
  font-weight: 600;
}
</style>
