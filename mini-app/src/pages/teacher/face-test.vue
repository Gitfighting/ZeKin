<script setup lang="ts">
import { onUnmounted, ref } from 'vue'

import VectorIcon from '@/components/VectorIcon.vue'
import { UI_ICONS } from '@/constants/ui-icons'
import { registerFace, verifyFace } from '@/services/face'
import { showError, showSuccess } from '@/services/feedback'

// --- 摄像头相关 ---
const streaming = ref(false)
const videoReady = ref(false)
const cameraContainer = ref<HTMLDivElement | null>(null)
let mediaStream: MediaStream | null = null
let videoEl: HTMLVideoElement | null = null

// --- 照片数据 ---
const currentPhoto = ref('')       // base64
const currentPreview = ref('')     // 预览 URL
const currentInfo = ref('')        // 尺寸信息

// --- 录入状态 ---
const registered = ref(false)
const registering = ref(false)
const registerMessage = ref('')

// --- 验证状态 ---
const verifyPhoto = ref('')
const verifyPreview = ref('')
const verifyInfo = ref('')
const verifying = ref(false)
const verifyResult = ref<{ matched: boolean; similarity?: number; message: string } | null>(null)

// --- 当前步骤 ---
const activeStep = ref<'shoot' | 'register-done' | 'verify'>('shoot')

onUnmounted(() => {
  stopCamera()
})

function stopCamera() {
  if (mediaStream) {
    mediaStream.getTracks().forEach((t) => t.stop())
    mediaStream = null
  }
  if (videoEl && videoEl.parentNode) {
    videoEl.parentNode.removeChild(videoEl)
  }
  streaming.value = false
  videoReady.value = false
  videoEl = null
}

function makeContainerEmpty() {
  const container = cameraContainer.value
  if (container) {
    container.innerHTML = ''
  }
}

async function startCamera() {
  stopCamera()
  makeContainerEmpty()

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    uni.showModal({
      title: '不支持摄像头',
      content: '当前浏览器不支持摄像头访问，请使用最新版 Chrome/Edge 浏览器。',
      showCancel: false,
    })
    return
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
      audio: false,
    })
    mediaStream = stream
    streaming.value = true

    const video = document.createElement('video')
    video.setAttribute('autoplay', '')
    video.setAttribute('playsinline', '')
    video.className = 'camera-video'
    video.srcObject = stream

    video.onloadedmetadata = () => {
      videoReady.value = true
      video.play().catch(() => {})
    }

    videoEl = video
    const container = cameraContainer.value
    if (container) {
      container.appendChild(video)
    }
  } catch (err: any) {
    const msg = err?.message?.includes('Permission')
      ? '摄像头权限被拒绝，请在浏览器设置中允许后刷新页面重试。'
      : '无法访问摄像头：' + (err?.message || '未知错误')
    uni.showModal({ title: '摄像头错误', content: msg, showCancel: false })
  }
}

function captureFrame() {
  if (!videoEl || !videoReady.value) return

  const canvas = document.createElement('canvas')
  canvas.width = videoEl.videoWidth
  canvas.height = videoEl.videoHeight
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  ctx.drawImage(videoEl, 0, 0)

  const base64 = canvas.toDataURL('image/jpeg', 0.85)
  const sizeKB = Math.round(base64.length * 0.75 / 1024)

  setPhoto(base64, `${canvas.width}×${canvas.height} · ${sizeKB}KB`)
  stopCamera()
  showSuccess('拍照成功')
}

function readFileAsBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

async function uploadImage() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return

    stopCamera()
    makeContainerEmpty()

    const base64 = await readFileAsBase64(file)
    const img = new Image()
    img.onload = () => {
      const sizeKB = Math.round(base64.length * 0.75 / 1024)
      setPhoto(base64, `${img.width}×${img.height} · ${sizeKB}KB · ${file.name}`)
      showSuccess('照片已加载')
    }
    img.src = base64
  }
  input.click()
}

function setPhoto(base64: string, info: string) {
  if (activeStep.value === 'verify') {
    verifyPhoto.value = base64
    verifyPreview.value = base64
    verifyInfo.value = info
    verifyResult.value = null
  } else {
    currentPhoto.value = base64
    currentPreview.value = base64
    currentInfo.value = info
  }
}

function clearAll() {
  stopCamera()
  makeContainerEmpty()
  currentPhoto.value = ''
  currentPreview.value = ''
  currentInfo.value = ''
  verifyPhoto.value = ''
  verifyPreview.value = ''
  verifyInfo.value = ''
  registered.value = false
  registerMessage.value = ''
  verifyResult.value = null
  activeStep.value = 'shoot'
}

// ========== 录入人脸 ==========
async function doRegister() {
  if (!currentPhoto.value) return
  registering.value = true
  registerMessage.value = ''

  try {
    const result = await registerFace({ faceImage: currentPhoto.value })
    registered.value = result.registered
    registerMessage.value = result.message
    if (result.registered) {
      showSuccess('人脸录入成功')
      activeStep.value = 'register-done'
    } else {
      showError(result.message, '录入失败')
    }
  } catch (error) {
    showError(error, '人脸录入失败')
  } finally {
    registering.value = false
  }
}

// ========== 验证人脸 ==========
function goToVerify() {
  activeStep.value = 'verify'
}

function goBackToShoot() {
  activeStep.value = 'shoot'
  currentPhoto.value = ''
  currentPreview.value = ''
  currentInfo.value = ''
}

async function doVerify() {
  if (!verifyPhoto.value) return
  verifying.value = true
  verifyResult.value = null

  try {
    const result = await verifyFace({ faceImage: verifyPhoto.value })
    verifyResult.value = result
    if (result.matched) {
      showSuccess('验证通过')
    } else {
      uni.showToast({ title: '验证不匹配', icon: 'none' })
    }
  } catch (error) {
    showError(error, '验证失败')
  } finally {
    verifying.value = false
  }
}
</script>

<template>
  <view class="face-page">
    <view class="hero-card">
      <text class="hero-title">人脸识别测试</text>
      <text class="hero-subtitle">完整流程：录入人脸 → 验证比对。支持拍照和上传照片两种方式。</text>
    </view>

    <!-- ====== 第一步：录入人脸 ====== -->
    <view v-if="activeStep === 'shoot'" class="section-card">
      <text class="section-title step-label">第一步：录入人脸</text>
      <text class="field-label">拍摄或上传一张正面照片，提交到后端提取人脸特征并存储。</text>

      <view v-if="streaming && !currentPhoto" ref="cameraContainer" class="camera-wrapper" />
      <image v-if="currentPreview" class="face-preview" :src="currentPreview" mode="aspectFill" />
      <text v-if="currentInfo" class="face-info">{{ currentInfo }}</text>

      <view class="button-row">
        <template v-if="!streaming && !currentPhoto">
          <button class="btn-primary" @click="startCamera">拍照录入</button>
          <button class="btn-secondary" @click="uploadImage">上传照片</button>
        </template>
        <template v-if="streaming && !currentPhoto">
          <button class="btn-primary" :disabled="!videoReady" @click="captureFrame">
            {{ videoReady ? '拍照' : '等待摄像头...' }}
          </button>
          <button class="btn-secondary" @click="stopCamera">取消</button>
        </template>
        <template v-if="currentPhoto">
          <button class="btn-primary" :loading="registering" @click="doRegister">
            {{ registering ? '录入中...' : '提交录入' }}
          </button>
          <button class="btn-secondary" @click="clearAll">重新拍摄</button>
        </template>
      </view>

      <text v-if="registerMessage" :class="['result-hint', registered ? 'hint-ok' : 'hint-fail']">
        {{ registerMessage }}
      </text>
    </view>

    <!-- ====== 录入成功，下一步 ====== -->
    <view v-if="activeStep === 'register-done'" class="section-card">
      <view class="success-header">
        <VectorIcon class="success-icon" :src="UI_ICONS.check" size="48rpx" />
        <text class="success-title">人脸录入成功</text>
      </view>
      <text class="field-label" style="text-align: center;">特征已提取并存储，可以进行验证测试了。</text>
      <button class="btn-primary btn-full" @click="goToVerify">下一步：验证人脸</button>
      <button class="btn-secondary btn-full" @click="clearAll">重新录入</button>
    </view>

    <!-- ====== 第二步：验证人脸 ====== -->
    <view v-if="activeStep === 'verify'" class="section-card">
      <text class="section-title step-label">第二步：验证人脸</text>
      <text class="field-label">重新拍照或上传一张照片，后端会与已录入的人脸特征进行比对。</text>

      <view v-if="streaming && !verifyPhoto" ref="cameraContainer" class="camera-wrapper" />
      <image v-if="verifyPreview" class="face-preview" :src="verifyPreview" mode="aspectFill" />
      <text v-if="verifyInfo" class="face-info">{{ verifyInfo }}</text>

      <view class="button-row">
        <template v-if="!streaming && !verifyPhoto">
          <button class="btn-primary" @click="startCamera">拍照验证</button>
          <button class="btn-secondary" @click="uploadImage">上传照片</button>
        </template>
        <template v-if="streaming && !verifyPhoto">
          <button class="btn-primary" :disabled="!videoReady" @click="captureFrame">
            {{ videoReady ? '拍照' : '等待摄像头...' }}
          </button>
          <button class="btn-secondary" @click="stopCamera">取消</button>
        </template>
        <template v-if="verifyPhoto">
          <button class="btn-primary" :loading="verifying" @click="doVerify">
            {{ verifying ? '验证中...' : '开始验证' }}
          </button>
          <button class="btn-secondary" @click="clearAll">重新开始</button>
        </template>
      </view>

      <!-- 验证结果 -->
      <view v-if="verifyResult" :class="['verify-result', verifyResult.matched ? 'result-pass' : 'result-fail']">
        <VectorIcon
          class="verify-icon"
          :src="verifyResult.matched ? UI_ICONS.check : UI_ICONS.close"
          size="48rpx"
        />
        <text class="verify-title">{{ verifyResult.matched ? '验证通过' : '验证不通过' }}</text>
        <text class="verify-msg">{{ verifyResult.message }}</text>
        <text v-if="verifyResult.similarity !== undefined" class="verify-score">
          相似度：{{ (verifyResult.similarity * 100).toFixed(1) }}%
        </text>
      </view>
    </view>

    <!-- 说明 -->
    <view class="section-card">
      <text class="section-title">流程说明</text>
      <text class="tip-text">
        1. 人脸录入 → 拍照/上传 → 后端检测人脸 → 提取 128 维特征向量 → 存入数据库{'\n'}
        2. 人脸验证 → 重新拍照/上传 → 后端提取特征 → 与已录入特征比对 → 返回相似度{'\n'}
        3. 相似度 &gt; 60%（阈值 0.6）认为匹配，&lt; 60% 认为不匹配{'\n'}
        4. 如果不匹配可以调整光线、角度后重试，也可以换一张不同的照片验证
      </text>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.face-page {
  min-height: 100vh;
  padding: 24rpx;
  background: $page-bg;
}

.hero-card {
  padding: 24rpx;
  border-radius: 22rpx;
  background: linear-gradient(180deg, #1677ff 0%, #53b1fd 100%);
  color: #fff;
}

.hero-title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
}

.hero-subtitle {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.5;
}

.section-card {
  margin-top: 20rpx;
  padding: 24rpx;
  border-radius: 22rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.section-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $text-primary;
}

.step-label {
  color: $primary;
}

.field-label {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  color: $text-secondary;
  line-height: 1.6;
}

.camera-wrapper {
  margin-top: 16rpx;
  border-radius: 18rpx;
  overflow: hidden;
  background: #000;
  min-height: 340rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.camera-video {
  display: block;
  width: 100%;
  height: 340rpx;
  object-fit: cover;
  background: #000;
}

.face-preview {
  display: block;
  width: 100%;
  height: 340rpx;
  border-radius: 18rpx;
  background: #eef5ff;
  margin-top: 16rpx;
  object-fit: cover;
}

.face-info {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  color: $primary;
  text-align: center;
}

.button-row {
  display: flex;
  gap: 16rpx;
  margin-top: 16rpx;
}

.btn-full {
  width: 100%;
  margin-top: 12rpx;
}

.btn-primary,
.btn-secondary {
  flex: 1;
  margin: 0;
  height: 80rpx;
  line-height: 80rpx;
  border: none;
  border-radius: 18rpx;
  font-size: 26rpx;
  font-weight: 600;
}

.btn-primary {
  background: $primary;
  color: #fff;
}

.btn-primary:disabled {
  opacity: 0.5;
}

.btn-secondary {
  background: #eef5ff;
  color: $primary;
}

.result-hint {
  display: block;
  margin-top: 12rpx;
  text-align: center;
  font-size: 26rpx;
  font-weight: 600;
}

.hint-ok { color: #16a34a; }
.hint-fail { color: #dc2626; }

// 录入成功
.success-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.success-icon {
  width: 80rpx;
  height: 80rpx;
  line-height: 80rpx;
  border-radius: 50%;
  background: #dcfce7;
  color: #16a34a;
  font-size: 40rpx;
  font-weight: 700;
  text-align: center;
}

.success-title {
  font-size: 32rpx;
  font-weight: 700;
  color: $text-primary;
}

// 验证结果
.verify-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  margin-top: 16rpx;
  padding: 24rpx;
  border-radius: 18rpx;
}

.result-pass {
  background: #dcfce7;
}

.result-fail {
  background: #fef2f2;
}

.verify-icon {
  font-size: 48rpx;
  font-weight: 700;
}

.result-pass .verify-icon { color: #16a34a; }
.result-fail .verify-icon { color: #dc2626; }

.verify-title {
  font-size: 30rpx;
  font-weight: 700;
  color: $text-primary;
}

.verify-msg {
  font-size: 24rpx;
  color: $text-secondary;
  text-align: center;
}

.verify-score {
  font-size: 28rpx;
  font-weight: 600;
  color: $primary;
}

.tip-text {
  display: block;
  margin-top: 12rpx;
  font-size: 22rpx;
  line-height: 1.8;
  color: $text-secondary;
  white-space: pre-wrap;
}
</style>
