<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { ref } from 'vue'

import DynamicForm from '@/components/DynamicForm.vue'
import LocationPicker from '@/components/LocationPicker.vue'
import { logInfo, showError } from '@/services/feedback'
import { getStudentTaskDetail, submitCheckin, type StudentTask } from '@/services/student'
import type { LocationResult } from '@/services/location'

const task = ref<StudentTask | null>(null)
const location = ref<LocationResult | null>(null)
const verificationCode = ref('')
const dynamicForm = ref<Record<string, string>>({})
const faceImage = ref('')
const facePreview = ref('')
const submitting = ref(false)

function applyTask(nextTask: StudentTask | null) {
  task.value = nextTask
  dynamicForm.value = {}
  faceImage.value = ''
  facePreview.value = ''
}

async function loadTask(id?: string) {
  if (!id || typeof uni === 'undefined' || typeof uni.request !== 'function') {
    applyTask(null)
    uni.showToast({ title: '缺少任务编号', icon: 'none' })
    return
  }

  try {
    applyTask(await getStudentTaskDetail(id))
    logInfo('学生打卡任务加载成功', { taskId: id })
  } catch (error) {
    applyTask(null)
    showError(error, '任务加载失败')
  }
}

async function handleSubmit() {
  if (!task.value) {
    uni.showToast({
      title: '任务尚未加载',
      icon: 'none',
    })
    return
  }

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

  if (task.value.faceRule.enabled && !faceImage.value) {
    uni.showToast({
      title: '请先完成人脸核验',
      icon: 'none',
    })
    return
  }

  submitting.value = true

  try {
    const result = await submitCheckin({
      taskId: task.value.id,
      longitude: location.value.longitude,
      latitude: location.value.latitude,
      verificationCode: verificationCode.value,
      formData: { ...dynamicForm.value },
      faceImage: faceImage.value,
    })
    logInfo('学生打卡提交成功', {
      taskId: task.value.id,
      state: result.state,
    })
    uni.setStorageSync('latest_checkin_result', result)
    uni.navigateTo({
      url: `/pages/student/result?state=${result.state}`,
    })
  } catch (error) {
    showError(error, '提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

function pathToBase64(path: string): Promise<string> {
  return new Promise((resolve, reject) => {
    uni.getFileSystemManager().readFile({
      filePath: path,
      encoding: 'base64',
      success: (result) => {
        resolve(`data:image/jpeg;base64,${result.data}`)
      },
      fail: reject,
    })
  })
}

async function captureFace() {
  try {
    const result = await uni.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['camera'],
    })
    const path = result.tempFilePaths[0]
    if (!path) {
      return
    }
    facePreview.value = path
    faceImage.value = await pathToBase64(path)
    uni.showToast({
      title: '人脸照片已采集',
      icon: 'success',
    })
  } catch (error) {
    showError(error, '人脸采集失败')
  }
}

onLoad((options) => {
  void loadTask(options?.id)
})
</script>

<template>
  <scroll-view scroll-y class="submit-page">
    <view v-if="!task" class="submit-page__card">
      <text class="submit-page__title">暂无任务数据</text>
      <text class="submit-page__subtitle">请从任务列表重新进入，或检查网络和后端服务。</text>
    </view>

    <template v-else>
    <view class="submit-page__card">
      <text class="submit-page__title">{{ task.title }}</text>
      <text class="submit-page__subtitle">{{ task.timeWindow }} · {{ task.locationName }}</text>
    </view>

    <view class="submit-page__card">
      <text class="submit-page__section-title">位置校验</text>
      <LocationPicker
        v-model="location"
        :target="task && task.targetLat && task.targetLng ? { latitude: task.targetLat, longitude: task.targetLng, radius: task.targetRadius ?? 100 } : null"
      />
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
      <image v-if="facePreview" class="submit-page__face-preview" :src="facePreview" mode="aspectFill" />
      <button class="submit-page__face-button" @click="captureFace">
        {{ faceImage ? '重新拍摄' : '拍摄人脸' }}
      </button>
    </view>

    <view class="submit-page__footer">
      <button class="submit-page__button" :loading="submitting" @click="handleSubmit">
        提交打卡
      </button>
    </view>
    </template>
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

.submit-page__face-preview {
  width: 100%;
  height: 360rpx;
  border-radius: 18rpx;
  background: #eef5ff;
}

.submit-page__face-button {
  border-radius: 999rpx;
  color: $primary;
  font-size: 28rpx;
}
</style>
