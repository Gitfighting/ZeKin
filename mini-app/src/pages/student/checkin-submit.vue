<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import LocationPicker from '@/components/LocationPicker.vue'
import GestureGridPicker from '@/components/GestureGridPicker.vue'
import { patternDisplayLabel, patternIdToSequence } from '@/constants/gesture-patterns'
import { formatBeijingDateTimeNow } from '@/utils/datetime'
import VectorIcon from '@/components/VectorIcon.vue'
import { UI_ICONS } from '@/constants/ui-icons'
import { logInfo, parseCheckinFailure, showCheckinErrorModal, showCheckinFailureActionModal, showError } from '@/services/feedback'
import { calcDistance } from '@/services/location'
import {
  getStudentTaskDetail,
  submitCheckin,
  type CheckinMethod,
  type StudentTask,
} from '@/services/student'
import type { LocationResult } from '@/services/location'

const task = ref<StudentTask | null>(null)
const submitting = ref(false)
const stepIndex = ref(0)

// 各签到方式收集的数据
const location = ref<LocationResult | null>(null)
const faceImage = ref('')
const facePreview = ref('')
const qrPayload = ref('')
const checkinCode = ref('')
const attachmentText = ref('')
const attachmentFiles = ref<string[]>([])
const gesturePattern = ref('')

const methods = computed<CheckinMethod[]>(() => task.value?.methods ?? [])
const totalSteps = computed(() => methods.value.length)
const currentMethod = computed<CheckinMethod | null>(() => methods.value[stepIndex.value] ?? null)
const isLastStep = computed(() => stepIndex.value >= totalSteps.value - 1)

const METHOD_TITLES: Record<CheckinMethod, string> = {
  face: '人脸核验',
  location: '位置校验',
  qr_code: '扫码签到',
  checkin_code: '签到码',
  attachment: '日志/附件',
  gesture: '手势签到',
}

function locationErrorMessage(fallback: string): string {
  const hint = task.value?.locationHint?.trim()
  if (hint) {
    return `${hint}。位置不符时可重新定位签到，或提交异常申诉。`
  }
  return fallback
}

function todayDate(): string {
  const now = new Date()
  const pad = (value: number) => String(value).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`
}

async function loadTask(id?: string) {
  if (!id) {
    task.value = null
    uni.showToast({ title: '缺少任务编号', icon: 'none' })
    return
  }
  try {
    task.value = await getStudentTaskDetail(id)
    stepIndex.value = 0
    logInfo('学生打卡任务加载成功', { taskId: id, methods: task.value.methods })
  } catch (error) {
    task.value = null
    showError(error, '任务加载失败')
  }
}

function hasLocationTarget(): boolean {
  const current = task.value
  if (!current) {
    return false
  }
  return Math.abs(current.targetLat ?? 0) > 0.0001 && Math.abs(current.targetLng ?? 0) > 0.0001
}

function isLocationValid(): boolean {
  if (!location.value) {
    return false
  }
  if (!hasLocationTarget() || !task.value) {
    return true
  }
  const distance = calcDistance(
    location.value.latitude,
    location.value.longitude,
    task.value.targetLat ?? 0,
    task.value.targetLng ?? 0,
  )
  return distance <= (task.value.targetRadius ?? 100)
}

function stepCompleted(method: CheckinMethod | null): boolean {
  switch (method) {
    case 'location':
      return isLocationValid()
    case 'face':
      return Boolean(faceImage.value)
    case 'qr_code':
      return Boolean(qrPayload.value)
    case 'checkin_code':
      return checkinCode.value.trim().length >= 4
    case 'attachment':
      return attachmentText.value.length >= (task.value?.attachmentRule.minTextLength ?? 0)
        && (!task.value?.attachmentRule.required || attachmentText.value.length > 0 || attachmentFiles.value.length > 0)
    case 'gesture':
      return gesturePattern.value.length >= 3
    default:
      return false
  }
}

function goNext() {
  if (currentMethod.value === 'location') {
    if (!location.value) {
      showCheckinErrorModal('请先获取当前位置后再继续')
      return
    }
    if (!isLocationValid()) {
      showCheckinErrorModal(locationErrorMessage('当前位置不在签到范围内，请到指定地点附近后重新定位'))
      return
    }
  }

  if (!stepCompleted(currentMethod.value)) {
    uni.showToast({ title: '请先完成当前步骤', icon: 'none' })
    return
  }
  if (!isLastStep.value) {
    stepIndex.value += 1
  }
}

function goPrev() {
  if (stepIndex.value > 0) {
    stepIndex.value -= 1
  }
}

function pathToBase64(path: string): Promise<string> {
  return new Promise((resolve, reject) => {
    uni.getFileSystemManager().readFile({
      filePath: path,
      encoding: 'base64',
      success: (result) => resolve(`data:image/jpeg;base64,${result.data}`),
      fail: reject,
    })
  })
}

async function captureFace() {
  try {
    logInfo('开始采集人脸照片')
    const result = await uni.chooseImage({ count: 1, sizeType: ['compressed'], sourceType: ['camera'] })
    const path = result.tempFilePaths[0]
    if (!path) {
      return
    }
    facePreview.value = path
    faceImage.value = await pathToBase64(path)
    logInfo('人脸照片采集成功', {
      path,
      base64Length: faceImage.value.length,
    })
    uni.showToast({ title: '人脸照片已采集', icon: 'success' })
  } catch (error) {
    showError(error, '人脸采集失败')
  }
}

async function scanQrCode() {
  try {
    const result = await uni.scanCode({ scanType: ['qrCode'] })
    qrPayload.value = result.result
    uni.showToast({ title: '扫码成功', icon: 'success' })
  } catch (error) {
    showError(error, '扫码失败，请重试')
  }
}

async function pickAttachment() {
  try {
    const result = await uni.chooseImage({ count: task.value?.attachmentRule.maxFileCount ?? 3 })
    attachmentFiles.value = result.tempFilePaths
    uni.showToast({ title: `已选择 ${result.tempFilePaths.length} 个附件`, icon: 'none' })
  } catch (error) {
    showError(error, '附件选择失败')
  }
}

function gesturePointsFromPattern(pattern: string): number[][] {
  return patternIdToSequence(pattern).map((index) => {
    const cell = index - 1
    const col = cell % 3
    const row = Math.floor(cell / 3)
    return [Number((col / 2).toFixed(2)), Number((row / 2).toFixed(2))]
  })
}

function formatNow(): string {
  return formatBeijingDateTimeNow()
}

function buildAppealUrl(recordId: string, taskTitle: string, reason: string) {
  const query = [
    `recordId=${encodeURIComponent(recordId)}`,
    `taskTitle=${encodeURIComponent(taskTitle)}`,
    `reason=${encodeURIComponent(reason)}`,
    `time=${encodeURIComponent(formatNow())}`,
  ].join('&')
  return `/pages/student/appeal?${query}`
}

async function handleCheckinFailure(error: unknown) {
  const failure = parseCheckinFailure(error, '签到失败，请稍后重试')
  const action = await showCheckinFailureActionModal(failure.message)
  if (action !== 'appeal') {
    return
  }
  if (!failure.recordId) {
    uni.showToast({ title: '请先提交签到后再申诉', icon: 'none' })
    return
  }
  if (!task.value) {
    return
  }
  uni.navigateTo({
    url: buildAppealUrl(failure.recordId, task.value.title, failure.message),
  })
}

async function handleSubmit() {
  if (!task.value) {
    return
  }

  if (methods.value.includes('location') && !isLocationValid()) {
    showCheckinErrorModal(locationErrorMessage('当前位置不在签到范围内，请到指定地点附近后重新定位'))
    return
  }

  // 校验所有步骤完成
  for (const method of methods.value) {
    if (!stepCompleted(method)) {
      if (method === 'location') {
        showCheckinErrorModal(locationErrorMessage('当前位置不在签到范围内，请到指定地点附近后重新定位'))
      } else if (method === 'checkin_code') {
        showCheckinErrorModal('请输入正确的签到码')
      } else if (method === 'face') {
        showCheckinErrorModal('请先完成人脸拍摄')
      } else {
        uni.showToast({ title: `请完成「${METHOD_TITLES[method]}」`, icon: 'none' })
      }
      return
    }
  }

  submitting.value = true
  try {
    logInfo('开始提交打卡', {
      taskId: task.value.id,
      methods: methods.value,
      hasFaceImage: Boolean(faceImage.value),
      faceImageLength: faceImage.value.length,
    })
    const result = await submitCheckin({
      taskId: task.value.id,
      ...(location.value
        ? { longitude: location.value.longitude, latitude: location.value.latitude }
        : {}),
      formData: {},
      ...(faceImage.value ? { faceImage: faceImage.value } : {}),
      ...(qrPayload.value ? { qrPayload: qrPayload.value } : {}),
      ...(checkinCode.value.trim() ? { checkinCode: checkinCode.value.trim() } : {}),
      ...(methods.value.includes('attachment')
        ? { attachment: { text: attachmentText.value, files: attachmentFiles.value } }
        : {}),
      ...(methods.value.includes('gesture')
        ? {
            gesture: {
              pattern_id: gesturePattern.value,
              points: gesturePointsFromPattern(gesturePattern.value),
            },
          }
        : {}),
      occurrenceDate: todayDate(),
    })
    logInfo('学生打卡提交成功', {
      taskId: task.value.id,
      state: result.state,
      faceVerified: Boolean(faceImage.value),
    })
    uni.setStorageSync('latest_checkin_result', result)
    uni.showToast({ title: '打卡完成', icon: 'success', duration: 1800 })
    setTimeout(() => {
      uni.navigateBack({ delta: 2 })
    }, 1600)
  } catch (error) {
    await handleCheckinFailure(error)
  } finally {
    submitting.value = false
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
        <text class="submit-page__subtitle">
          {{ task.timeWindow }} · {{ task.scheduleMode === 'recurring' ? '每日打卡' : '一次打卡' }}
        </text>
        <view class="submit-page__steps">
          <view
            v-for="(method, index) in methods"
            :key="method"
            class="submit-page__chip"
            :class="{
              'submit-page__chip--active': index === stepIndex,
              'submit-page__chip--done': stepCompleted(method) && index !== stepIndex,
            }"
          >
            {{ index + 1 }}. {{ METHOD_TITLES[method] }}
          </view>
        </view>
      </view>

      <view v-if="totalSteps === 0" class="submit-page__card">
        <text class="submit-page__note">该任务未配置签到方式，请联系老师。</text>
      </view>

      <view v-else class="submit-page__card">
        <text class="submit-page__section-title">
          Step {{ stepIndex + 1 }}/{{ totalSteps }} · {{ currentMethod ? METHOD_TITLES[currentMethod] : '' }}
        </text>

        <!-- 位置 -->
        <view v-if="currentMethod === 'location'">
          <LocationPicker
            v-model="location"
            :place-name="task.locationName"
            :target="
              Math.abs(task.targetLat) > 0.0001 && Math.abs(task.targetLng) > 0.0001
                ? { latitude: task.targetLat, longitude: task.targetLng, radius: task.targetRadius ?? 100 }
                : null
            "
          />
          <text class="submit-page__note">{{ task.locationHint || `请在${task.locationName}附近完成定位` }}</text>
        </view>

        <!-- 人脸 -->
        <view v-else-if="currentMethod === 'face'">
          <text class="submit-page__note">{{ task.faceRule.tip }}</text>
          <image v-if="facePreview" class="submit-page__face-preview" :src="facePreview" mode="aspectFill" />
          <button class="submit-page__face-button" @click="captureFace">
            {{ faceImage ? '重新拍摄' : '拍摄人脸' }}
          </button>
        </view>

        <!-- 二维码 -->
        <view v-else-if="currentMethod === 'qr_code'">
          <text class="submit-page__note">请扫描老师展示的签到二维码。</text>
          <view v-if="qrPayload" class="submit-page__note submit-page__note--ok">
            <VectorIcon :src="UI_ICONS.check" size="24rpx" />
            <text>二维码已扫描</text>
          </view>
          <button class="submit-page__face-button" @click="scanQrCode">
            {{ qrPayload ? '重新扫码' : '扫一扫' }}
          </button>
        </view>

        <!-- 签到码 -->
        <view v-else-if="currentMethod === 'checkin_code'">
          <text class="submit-page__note">请输入老师在课堂或群聊中公布的签到码。</text>
          <input
            v-model="checkinCode"
            class="submit-page__code-input"
            maxlength="12"
            placeholder="请输入签到码"
          />
        </view>

        <!-- 附件/日志 -->
        <view v-else-if="currentMethod === 'attachment'">
          <text class="submit-page__note">
            {{ task.attachmentRule.label }}{{ task.attachmentRule.required ? '（必填）' : '（选填）' }}
            <text v-if="task.attachmentRule.minTextLength">，至少 {{ task.attachmentRule.minTextLength }} 字</text>
          </text>
          <textarea
            v-model="attachmentText"
            class="submit-page__textarea"
            placeholder="请输入今日工作/情况说明"
          />
          <button class="submit-page__face-button" @click="pickAttachment">
            选择图片附件（{{ attachmentFiles.length }}）
          </button>
        </view>

        <!-- 手势 -->
        <view v-else-if="currentMethod === 'gesture'">
          <text class="submit-page__note">
            请按顺序在九宫格上一笔绘制手势
            <text v-if="task.gestureRule.presetPattern">
              （参考：{{ patternDisplayLabel(task.gestureRule.presetPattern) }}）
            </text>
          </text>
          <GestureGridPicker v-model="gesturePattern" canvas-id="studentGestureCanvas" />
        </view>
      </view>

      <view v-if="totalSteps > 0" class="submit-page__footer">
        <button v-if="stepIndex > 0" class="submit-page__button submit-page__button--ghost" @click="goPrev">
          上一步
        </button>
        <button v-if="!isLastStep" class="submit-page__button" @click="goNext">
          下一步
        </button>
        <button v-else class="submit-page__button" :loading="submitting" @click="handleSubmit">
          {{ submitting ? '签到中...' : '签到' }}
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

.submit-page__note--ok {
  display: flex;
  align-items: center;
  gap: 8rpx;
  color: $primary;
  font-weight: 600;
}

.submit-page__steps {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.submit-page__chip {
  padding: 8rpx 20rpx;
  border-radius: 999rpx;
  background: #f0f5ff;
  color: $text-secondary;
  font-size: 24rpx;
}

.submit-page__chip--active {
  background: $primary;
  color: #fff;
}

.submit-page__chip--done {
  background: rgba($primary, 0.12);
  color: $primary;
}

.submit-page__section-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.submit-page__textarea {
  box-sizing: border-box;
  width: 100%;
  height: 200rpx;
  padding: 20rpx 24rpx;
  border-radius: 22rpx;
  background: #f8fbff;
  border: 2rpx solid rgba($primary, 0.08);
  color: $text-primary;
  font-size: 28rpx;
}

.submit-page__code-input {
  box-sizing: border-box;
  width: 100%;
  height: 96rpx;
  padding: 0 28rpx;
  border-radius: 22rpx;
  background: #f8fbff;
  border: 2rpx solid rgba($primary, 0.08);
  color: $text-primary;
  font-size: 36rpx;
  font-weight: 700;
  letter-spacing: 6rpx;
  text-align: center;
}

.submit-page__grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
  margin: 16rpx 0;
}

.submit-page__grid-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 140rpx;
  border-radius: 18rpx;
  background: #f0f5ff;
  color: $text-secondary;
  font-size: 32rpx;
}

.submit-page__footer {
  display: flex;
  gap: 16rpx;
  padding-bottom: 24rpx;
}

.submit-page__button {
  flex: 1;
  border: none;
  border-radius: 999rpx;
  background: $primary;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
}

.submit-page__button--ghost {
  background: #fff;
  color: $primary;
  border: 2rpx solid rgba($primary, 0.3);
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
