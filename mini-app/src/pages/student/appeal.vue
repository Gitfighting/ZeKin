<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import { logInfo, showError, showSuccess } from '@/services/feedback'
import { getStudentProfile, submitAppeal } from '@/services/student'

const recordId = ref('')
const taskTitle = ref('打卡任务')
const exceptionReason = ref('定位不在打卡范围内')
const exceptionTime = ref('')
const reason = ref('')
const images = ref<string[]>([])
const contactPhone = ref('')
const submitting = ref(false)

const reasonCount = computed(() => reason.value.length)

function maskPhone(phone: string): string {
  if (phone.length < 7) {
    return phone
  }
  return `${phone.slice(0, 3)}****${phone.slice(-4)}`
}

function handleBack() {
  uni.navigateBack({ delta: 1 })
}

function chooseImages() {
  const remain = Math.max(0, 3 - images.value.length)
  if (remain === 0) {
    uni.showToast({ title: '最多上传 3 张图片', icon: 'none' })
    return
  }
  uni.chooseImage({
    count: remain,
    success: ({ tempFilePaths }) => {
      images.value = [...images.value, ...tempFilePaths].slice(0, 3)
    },
  })
}

function removeImage(index: number) {
  images.value = images.value.filter((_, itemIndex) => itemIndex !== index)
}

async function loadProfile() {
  try {
    const profile = await getStudentProfile()
    contactPhone.value = maskPhone(profile.phone)
  } catch {
    contactPhone.value = ''
  }
}

async function handleSubmit() {
  if (!recordId.value) {
    uni.showToast({ title: '缺少申诉记录', icon: 'none' })
    return
  }
  if (!reason.value.trim()) {
    uni.showToast({ title: '请填写申诉说明', icon: 'none' })
    return
  }

  submitting.value = true
  try {
    await submitAppeal({
      recordId: recordId.value,
      reason: reason.value.trim(),
      images: images.value,
    })
    logInfo('学生申诉提交成功', { recordId: recordId.value })
    showSuccess('申诉已提交')
    setTimeout(() => {
      uni.navigateBack({ delta: 1 })
    }, 600)
  } catch (error) {
    showError(error, '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

onLoad((options) => {
  recordId.value = options?.recordId ? String(options.recordId) : ''
  taskTitle.value = options?.taskTitle ? decodeURIComponent(String(options.taskTitle)) : '打卡任务'
  exceptionReason.value = options?.reason ? decodeURIComponent(String(options.reason)) : '定位不在打卡范围内'
  exceptionTime.value = options?.time ? decodeURIComponent(String(options.time)) : ''
  void loadProfile()
})
</script>

<template>
  <view class="appeal-page">
    <view class="appeal-page__nav">
      <view class="appeal-page__back" @click="handleBack">
        <text>‹</text>
      </view>
      <text class="appeal-page__nav-title">异常申诉</text>
      <view class="appeal-page__nav-spacer"></view>
    </view>

    <scroll-view scroll-y class="appeal-page__scroll">
      <view class="appeal-page__alert">
        <view class="appeal-page__alert-main">
          <text class="appeal-page__alert-icon">⚠️</text>
          <view class="appeal-page__alert-copy">
            <text class="appeal-page__alert-title">{{ taskTitle }}异常</text>
            <text class="appeal-page__alert-line">异常原因：{{ exceptionReason }}</text>
            <text v-if="exceptionTime" class="appeal-page__alert-line">异常时间：{{ exceptionTime }}</text>
          </view>
        </view>
      </view>

      <view class="appeal-page__section">
        <view class="appeal-page__section-head">
          <view class="appeal-page__section-bar"></view>
          <text class="appeal-page__section-title">申诉说明</text>
        </view>
        <view class="appeal-page__textarea-wrap">
          <textarea
            v-model="reason"
            class="appeal-page__textarea"
            maxlength="200"
            placeholder="请说明异常原因，如系统识别人脸失败、定位偏差但人已在现场等"
          />
          <text class="appeal-page__counter">{{ reasonCount }}/200</text>
        </view>
      </view>

      <view class="appeal-page__section">
        <view class="appeal-page__section-head">
          <view class="appeal-page__section-bar"></view>
          <text class="appeal-page__section-title">上传证明（选填）</text>
        </view>
        <view class="appeal-page__upload-grid">
          <view v-for="(image, index) in images" :key="image" class="appeal-page__upload-item appeal-page__upload-item--filled">
            <image class="appeal-page__upload-preview" :src="image" mode="aspectFill" />
            <view class="appeal-page__upload-remove" @click="removeImage(index)">×</view>
          </view>
          <view
            v-if="images.length < 3"
            class="appeal-page__upload-item"
            @click="chooseImages"
          >
            <text class="appeal-page__upload-plus">+</text>
            <text class="appeal-page__upload-label">上传图片</text>
          </view>
        </view>
      </view>

      <view class="appeal-page__section">
        <view class="appeal-page__section-head">
          <view class="appeal-page__section-bar"></view>
          <text class="appeal-page__section-title">联系方式</text>
        </view>
        <view class="appeal-page__contact">
          <text>{{ contactPhone || '未绑定手机号' }}</text>
        </view>
      </view>

      <view class="appeal-page__footer">
        <button class="appeal-page__submit" type="primary" :loading="submitting" @click="handleSubmit">
          提交申诉
        </button>
      </view>
    </scroll-view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.appeal-page {
  min-height: 100vh;
  background: #f5f8fc;
}

.appeal-page__nav {
  display: grid;
  grid-template-columns: 72rpx 1fr 72rpx;
  align-items: center;
  height: 112rpx;
  padding: 0 24rpx;
  padding-top: env(safe-area-inset-top);
  background: #fff;
}

.appeal-page__back {
  display: flex;
  width: 64rpx;
  height: 64rpx;
  align-items: center;
  justify-content: center;
  color: $text-primary;
  font-size: 48rpx;
  line-height: 1;
}

.appeal-page__nav-title {
  color: $text-primary;
  font-size: 34rpx;
  font-weight: 700;
  text-align: center;
}

.appeal-page__nav-spacer {
  width: 64rpx;
}

.appeal-page__scroll {
  height: calc(100vh - 112rpx - env(safe-area-inset-top));
  padding: 24rpx;
  box-sizing: border-box;
}

.appeal-page__alert {
  margin-bottom: 24rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border: 1rpx solid rgba(255, 159, 26, 0.18);
}

.appeal-page__alert-main {
  display: flex;
  gap: 16rpx;
}

.appeal-page__alert-icon {
  font-size: 40rpx;
  line-height: 1.2;
}

.appeal-page__alert-copy {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 10rpx;
}

.appeal-page__alert-title {
  color: #ea580c;
  font-size: 32rpx;
  font-weight: 700;
}

.appeal-page__alert-line {
  color: #9a3412;
  font-size: 26rpx;
  line-height: 1.5;
}

.appeal-page__section {
  margin-bottom: 24rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: #fff;
  box-shadow: 0 12rpx 32rpx rgba(15, 107, 214, 0.06);
}

.appeal-page__section-head {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.appeal-page__section-bar {
  width: 8rpx;
  height: 28rpx;
  border-radius: 999rpx;
  background: $primary;
}

.appeal-page__section-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.appeal-page__textarea-wrap {
  position: relative;
}

.appeal-page__textarea {
  box-sizing: border-box;
  width: 100%;
  min-height: 220rpx;
  padding: 24rpx;
  padding-bottom: 56rpx;
  border: 1rpx solid rgba(15, 23, 42, 0.08);
  border-radius: 20rpx;
  background: #fafbfd;
  color: $text-primary;
  font-size: 28rpx;
  line-height: 1.6;
}

.appeal-page__counter {
  position: absolute;
  right: 20rpx;
  bottom: 16rpx;
  color: $text-muted;
  font-size: 22rpx;
}

.appeal-page__upload-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.appeal-page__upload-item {
  position: relative;
  display: flex;
  width: 180rpx;
  height: 180rpx;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  border: 2rpx dashed rgba(15, 23, 42, 0.12);
  border-radius: 18rpx;
  background: #fafbfd;
}

.appeal-page__upload-item--filled {
  border-style: solid;
  padding: 0;
  overflow: hidden;
}

.appeal-page__upload-preview {
  width: 100%;
  height: 100%;
}

.appeal-page__upload-remove {
  position: absolute;
  top: 8rpx;
  right: 8rpx;
  display: flex;
  width: 36rpx;
  height: 36rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  font-size: 24rpx;
}

.appeal-page__upload-plus {
  color: $text-muted;
  font-size: 48rpx;
  line-height: 1;
}

.appeal-page__upload-label {
  color: $text-secondary;
  font-size: 22rpx;
}

.appeal-page__contact {
  padding: 24rpx;
  border-radius: 18rpx;
  background: #fafbfd;
  color: $text-primary;
  font-size: 28rpx;
}

.appeal-page__footer {
  padding: 8rpx 0 32rpx;
}

.appeal-page__submit {
  border: none;
  border-radius: 999rpx;
  background: $primary;
  font-size: 30rpx;
  font-weight: 700;
}
</style>
