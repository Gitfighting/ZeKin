<script setup lang="ts">
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { ref } from 'vue'

import { logInfo, showError } from '@/services/feedback'
import { getTaskQrCode, refreshTaskQrCode, type TaskQrCode } from '@/services/teacher'

const taskId = ref(0)
const qr = ref<TaskQrCode | null>(null)
const countdown = ref(0)
const errorMessage = ref('')
let timer: ReturnType<typeof setInterval> | null = null

function clearTimer() {
  if (timer) {
    clearInterval(timer)
    timer = null
  }
}

function startCountdown() {
  clearTimer()
  countdown.value = qr.value?.expireSeconds ?? 0
  timer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0) {
      void refresh()
    }
  }, 1000)
}

async function load() {
  try {
    qr.value = await getTaskQrCode(taskId.value)
    errorMessage.value = ''
    startCountdown()
    logInfo('二维码加载成功', { taskId: taskId.value })
  } catch (error) {
    errorMessage.value = '该任务未启用二维码签到，或获取失败。'
    showError(error, '二维码获取失败')
  }
}

async function refresh() {
  try {
    qr.value = await refreshTaskQrCode(taskId.value)
    errorMessage.value = ''
    startCountdown()
  } catch (error) {
    errorMessage.value = '二维码刷新失败。'
    showError(error, '二维码刷新失败')
  }
}

onLoad((options) => {
  taskId.value = Number(options?.id || 0)
  if (taskId.value > 0) {
    void load()
  } else {
    errorMessage.value = '缺少任务编号'
  }
})

onUnload(() => {
  clearTimer()
})
</script>

<template>
  <view class="qr-page">
    <text class="qr-title">课堂签到二维码</text>
    <text class="qr-subtitle">请学生使用小程序「扫一扫」扫描下方二维码</text>

    <view v-if="qr && qr.qrImage" class="qr-card">
      <image class="qr-image" :src="qr.qrImage" mode="widthFix" />
      <text class="qr-countdown">{{ countdown }} 秒后自动刷新</text>
      <view class="qr-refresh" @click="refresh">手动刷新</view>
    </view>

    <view v-else class="qr-card">
      <text class="qr-error">{{ errorMessage || '二维码加载中...' }}</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.qr-page {
  min-height: 100vh;
  padding: 48rpx 24rpx;
  background: #0b1f3a;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.qr-title {
  font-size: 44rpx;
  font-weight: 700;
  color: #fff;
}

.qr-subtitle {
  margin-top: 16rpx;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.7);
}

.qr-card {
  margin-top: 60rpx;
  padding: 48rpx;
  border-radius: 32rpx;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28rpx;
  width: 70%;
}

.qr-image {
  width: 100%;
}

.qr-countdown {
  font-size: 30rpx;
  color: $text-secondary;
}

.qr-refresh {
  padding: 18rpx 48rpx;
  border-radius: 999rpx;
  background: $primary;
  color: #fff;
  font-size: 28rpx;
  font-weight: 600;
}

.qr-error {
  font-size: 28rpx;
  color: $text-secondary;
  text-align: center;
  line-height: 1.6;
}
</style>
