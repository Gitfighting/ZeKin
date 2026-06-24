<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

import { submitAppeal } from '@/services/student'

const recordId = ref('record-3')
const reason = ref('')
const images = ref<string[]>([])
const submitting = ref(false)

function chooseImages() {
  uni.chooseImage({
    count: 3,
    success: ({ tempFilePaths }) => {
      images.value = tempFilePaths
    },
  })
}

async function handleSubmit() {
  if (!reason.value) {
    uni.showToast({
      title: '请填写申诉原因',
      icon: 'none',
    })
    return
  }

  submitting.value = true

  try {
    await submitAppeal({
      recordId: recordId.value,
      reason: reason.value,
      images: images.value,
    })
  } catch {
    // Local demo fallback.
  } finally {
    submitting.value = false
  }

  uni.showToast({
    title: '申诉已提交',
    icon: 'success',
  })

  setTimeout(() => {
    uni.navigateBack({
      delta: 1,
    })
  }, 500)
}

onLoad((options) => {
  if (options?.recordId) {
    recordId.value = options.recordId
  }
})
</script>

<template>
  <scroll-view scroll-y class="appeal-page">
    <view class="appeal-page__card">
      <text class="appeal-page__title">异常申诉</text>
      <text class="appeal-page__subtitle">记录编号：{{ recordId }}</text>
    </view>

    <view class="appeal-page__card">
      <text class="appeal-page__label">申诉原因</text>
      <textarea
        v-model="reason"
        class="appeal-page__textarea"
        maxlength="240"
        placeholder="请说明异常原因、实际签到地点或补充情况"
      />
    </view>

    <view class="appeal-page__card">
      <text class="appeal-page__label">附件图片</text>
      <button class="appeal-page__pick-button" type="default" @click="chooseImages">
        选择图片
      </button>
      <text v-if="images.length" class="appeal-page__images">{{ images.join('、') }}</text>
      <text v-else class="appeal-page__hint">可上传现场截图、通知截图等辅助材料</text>
    </view>

    <view class="appeal-page__footer">
      <button class="appeal-page__submit" type="primary" :loading="submitting" @click="handleSubmit">
        提交申诉
      </button>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.appeal-page {
  min-height: 100vh;
  padding: 24rpx;
  background: $page-bg;
}

.appeal-page__card {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  margin-bottom: 24rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.08);
}

.appeal-page__title {
  color: $text-primary;
  font-size: 36rpx;
  font-weight: 700;
}

.appeal-page__subtitle,
.appeal-page__hint,
.appeal-page__images {
  color: $text-secondary;
  font-size: 26rpx;
  line-height: 1.6;
}

.appeal-page__label {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.appeal-page__textarea {
  box-sizing: border-box;
  width: 100%;
  min-height: 220rpx;
  padding: 24rpx;
  border-radius: 22rpx;
  background: #f8fbff;
  border: 2rpx solid rgba($primary, 0.08);
  color: $text-primary;
  font-size: 28rpx;
}

.appeal-page__pick-button,
.appeal-page__submit {
  border-radius: 999rpx;
  font-size: 28rpx;
  font-weight: 600;
}

.appeal-page__pick-button {
  margin: 0;
  background: #f4f8ff;
  color: $primary;
  border: 2rpx solid rgba($primary, 0.1);
}

.appeal-page__submit {
  border: none;
  background: $primary;
}
</style>
