<script setup lang="ts">
import { computed, reactive, ref } from 'vue'

import { activateStudent, login, type ActivateStudentPayload, type LoginPayload } from '@/services/auth'
import { logInfo, showError, showSuccess } from '@/services/feedback'
import type { UserType } from '@/services/types'

type AuthMode = 'login' | 'register'

const activeMode = ref<AuthMode>('login')
const submitting = ref(false)
const showRegisterPassword = ref(false)
const showRegisterConfirm = ref(false)

const loginForm = reactive<LoginPayload>({
  account: '',
  password: '',
})

const registerForm = reactive<ActivateStudentPayload & { agreed: boolean }>({
  name: '',
  studentNo: '',
  phone: '',
  code: '',
  password: '',
  confirmPassword: '',
  agreed: true,
})

const isLogin = computed(() => activeMode.value === 'login')

function switchMode(mode: AuthMode) {
  activeMode.value = mode
}

function enterHome(userType: UserType) {
  if (userType === 'teacher') {
    uni.reLaunch({
      url: '/pages/teacher/home',
    })
    return
  }

  uni.switchTab({
    url: '/pages/student/home',
  })
}

function validatePhone(phone: string) {
  return /^1\d{10}$/.test(phone)
}

function sendRegisterCode() {
  if (!registerForm.phone) {
    uni.showToast({ title: '请先填写手机号', icon: 'none' })
    return
  }
  if (!validatePhone(registerForm.phone)) {
    uni.showToast({ title: '请输入正确手机号', icon: 'none' })
    return
  }

  showSuccess('验证码已发送')
}

async function handleLogin() {
  if (!loginForm.account || !loginForm.password) {
    uni.showToast({
      title: '请完整填写登录信息',
      icon: 'none',
    })
    return
  }

  submitting.value = true

  try {
    const session = await login(loginForm)
    logInfo('登录成功', {
      account: loginForm.account,
      userType: session.user.userType,
    })
    enterHome(session.user.userType)
  } catch (error) {
    showError(error, '账号或密码错误')
  } finally {
    submitting.value = false
  }
}

async function handleRegister() {
  if (
    !registerForm.name ||
    !registerForm.studentNo ||
    !registerForm.phone ||
    !registerForm.code ||
    !registerForm.password ||
    !registerForm.confirmPassword
  ) {
    uni.showToast({ title: '请完整填写注册信息', icon: 'none' })
    return
  }

  if (!validatePhone(registerForm.phone)) {
    uni.showToast({ title: '请输入正确手机号', icon: 'none' })
    return
  }

  if (registerForm.password !== registerForm.confirmPassword) {
    uni.showToast({ title: '两次密码输入不一致', icon: 'none' })
    return
  }

  if (!registerForm.agreed) {
    uni.showToast({ title: '请先同意协议', icon: 'none' })
    return
  }

  submitting.value = true

  try {
    const session = await activateStudent({
      name: registerForm.name,
      studentNo: registerForm.studentNo,
      phone: registerForm.phone,
      code: registerForm.code,
      password: registerForm.password,
      confirmPassword: registerForm.confirmPassword,
    })
    logInfo('学生注册成功', {
      studentNo: registerForm.studentNo,
      userId: session.user.id,
    })
    uni.switchTab({
      url: '/pages/student/home',
    })
  } catch (error) {
    showError(error, '注册失败，请核对姓名、学号和手机号')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <view class="auth-page">
    <view class="hero">
      <text class="app-title">考勤助手</text>
      <text class="app-subtitle">智慧考勤，轻松校园生活</text>
      <view class="cloud cloud-a"></view>
      <view class="cloud cloud-b"></view>
      <view class="campus-scene" aria-hidden="true">
        <view class="building building-left"></view>
        <view class="tower"><view class="clock"></view></view>
        <view class="building building-right"></view>
        <view class="tree tree-one"></view>
        <view class="tree tree-two"></view>
      </view>
    </view>

    <view class="auth-card" :class="{ 'auth-card--register': !isLogin }">
      <view class="tabs">
        <view class="tab-btn" :class="{ active: isLogin }" @click="switchMode('login')">登录</view>
        <view class="tab-btn" :class="{ active: !isLogin }" @click="switchMode('register')">注册</view>
      </view>

      <view v-if="isLogin" class="auth-panel">
        <view class="field">
          <view class="field-icon field-icon--user" aria-hidden="true"></view>
          <input
            v-model="loginForm.account"
            placeholder="学号/手机号"
            placeholder-class="field-placeholder"
          />
        </view>

        <view class="field">
          <view class="field-icon field-icon--lock" aria-hidden="true"></view>
          <input
            v-model="loginForm.password"
            password
            placeholder="密码"
            placeholder-class="field-placeholder"
          />
        </view>

        <button class="primary-btn" type="primary" :loading="submitting" @click="handleLogin">
          {{ submitting ? '登录中...' : '立即登录' }}
        </button>
      </view>

      <view v-else class="auth-panel">
        <view class="field">
          <view class="field-icon field-icon--user" aria-hidden="true"></view>
          <input v-model="registerForm.name" placeholder="姓名" placeholder-class="field-placeholder" />
        </view>

        <view class="field">
          <view class="field-icon field-icon--graduate" aria-hidden="true"></view>
          <input
            v-model="registerForm.studentNo"
            placeholder="学号"
            placeholder-class="field-placeholder"
          />
        </view>

        <view class="field">
          <view class="field-icon field-icon--phone" aria-hidden="true"></view>
          <input
            v-model="registerForm.phone"
            type="text"
            maxlength="11"
            placeholder="手机号"
            placeholder-class="field-placeholder"
          />
        </view>

        <view class="field field--code">
          <view class="field-icon field-icon--shield" aria-hidden="true"></view>
          <input
            v-model="registerForm.code"
            type="text"
            maxlength="6"
            placeholder="验证码"
            placeholder-class="field-placeholder"
          />
          <button class="code-btn" @click="sendRegisterCode">获取验证码</button>
        </view>

        <view class="field field--password">
          <view class="field-icon field-icon--lock" aria-hidden="true"></view>
          <input
            v-model="registerForm.password"
            :password="!showRegisterPassword"
            placeholder="密码"
            placeholder-class="field-placeholder"
          />
          <button class="eye-btn" @click="showRegisterPassword = !showRegisterPassword">
            {{ showRegisterPassword ? '隐藏' : '显示' }}
          </button>
        </view>

        <view class="field field--password">
          <view class="field-icon field-icon--lock" aria-hidden="true"></view>
          <input
            v-model="registerForm.confirmPassword"
            :password="!showRegisterConfirm"
            placeholder="确认密码"
            placeholder-class="field-placeholder"
          />
          <button class="eye-btn" @click="showRegisterConfirm = !showRegisterConfirm">
            {{ showRegisterConfirm ? '隐藏' : '显示' }}
          </button>
        </view>

        <view class="agreement">
          <view
            class="checkbox"
            :class="{ 'checkbox--checked': registerForm.agreed }"
            @click="registerForm.agreed = !registerForm.agreed"
          >
            <text v-if="registerForm.agreed">✓</text>
          </view>
          <text>我已阅读并同意</text>
          <text class="agreement-link">《用户协议》</text>
          <text class="agreement-link">《隐私政策》</text>
        </view>

        <button class="primary-btn" type="primary" :loading="submitting" @click="handleRegister">
          {{ submitting ? '注册中...' : '立即注册' }}
        </button>
      </view>
    </view>

    <view class="policy">
      <text>{{ isLogin ? '登录' : '注册' }}即表示同意《用户协议》《隐私政策》</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.auth-page {
  min-height: 100vh;
  overflow: hidden;
  background: linear-gradient(180deg, #2597ff 0%, #8ad2ff 28%, #f4f9ff 64%, #f3f8ff 100%);
  color: $text-primary;
}

.hero {
  position: relative;
  height: 384rpx;
  padding: 78rpx 44rpx 0;
  color: #ffffff;
}

.app-title {
  position: relative;
  z-index: 2;
  display: block;
  font-size: 80rpx;
  line-height: 1;
  font-weight: 900;
  text-shadow: 0 12rpx 36rpx rgba(0, 73, 162, 0.15);
}

.app-subtitle {
  position: relative;
  z-index: 2;
  display: block;
  margin-top: 32rpx;
  color: rgba(255, 255, 255, 0.9);
  font-size: 38rpx;
  font-weight: 600;
}

.cloud {
  position: absolute;
  z-index: 1;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.82);
  filter: drop-shadow(0 12rpx 20rpx rgba(46, 111, 178, 0.14));

  &::before,
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    border-radius: 50%;
    background: inherit;
  }

  &::before {
    left: 24rpx;
    width: 48rpx;
    height: 48rpx;
  }

  &::after {
    left: 68rpx;
    width: 36rpx;
    height: 36rpx;
  }
}

.cloud-a {
  top: 188rpx;
  right: 312rpx;
  width: 116rpx;
  height: 26rpx;
}

.cloud-b {
  top: 226rpx;
  right: 8rpx;
  width: 104rpx;
  height: 24rpx;
  opacity: 0.84;
}

.campus-scene {
  position: absolute;
  right: -40rpx;
  bottom: -18rpx;
  z-index: 1;
  width: 516rpx;
  height: 256rpx;
}

.building {
  position: absolute;
  bottom: 24rpx;
  border-radius: 16rpx 16rpx 8rpx 8rpx;
  background: linear-gradient(180deg, #cae7ff 0%, #9fcaff 32%, #6da9f3 100%);
  box-shadow: inset 0 8rpx 0 rgba(255, 255, 255, 0.62);

  &::after {
    content: '';
    position: absolute;
    inset: 36rpx 18rpx 24rpx;
    opacity: 0.76;
    background:
      linear-gradient(#ffffff 0 0) 0 0 / 16rpx 26rpx,
      linear-gradient(#ffffff 0 0) 44rpx 0 / 16rpx 26rpx,
      linear-gradient(#ffffff 0 0) 88rpx 0 / 16rpx 26rpx,
      linear-gradient(#ffffff 0 0) 0 48rpx / 16rpx 26rpx,
      linear-gradient(#ffffff 0 0) 44rpx 48rpx / 16rpx 26rpx,
      linear-gradient(#ffffff 0 0) 88rpx 48rpx / 16rpx 26rpx;
    background-repeat: no-repeat;
  }
}

.building-left {
  left: 8rpx;
  width: 152rpx;
  height: 112rpx;
}

.building-right {
  right: 8rpx;
  width: 164rpx;
  height: 132rpx;
  background: linear-gradient(180deg, #b6dcff 0%, #7fb5f6 100%);
}

.tower {
  position: absolute;
  left: 188rpx;
  bottom: 24rpx;
  width: 116rpx;
  height: 192rpx;
  border-radius: 16rpx 16rpx 10rpx 10rpx;
  background: linear-gradient(180deg, #ffe7bd 0%, #ffc781 100%);
  box-shadow: inset 0 8rpx 0 rgba(255, 255, 255, 0.7), 0 20rpx 36rpx rgba(31, 102, 169, 0.18);

  &::before {
    content: '';
    position: absolute;
    top: -64rpx;
    left: 16rpx;
    right: 16rpx;
    height: 68rpx;
    clip-path: polygon(50% 0, 100% 100%, 0 100%);
    background: linear-gradient(180deg, #c8f1ff 0%, #65b8ff 100%);
  }
}

.clock {
  position: absolute;
  top: 30rpx;
  left: 36rpx;
  width: 44rpx;
  height: 44rpx;
  border: 6rpx solid #4aa5ff;
  border-radius: 50%;
  background: #ffffff;

  &::before {
    content: '';
    position: absolute;
    left: 18rpx;
    top: 8rpx;
    width: 4rpx;
    height: 14rpx;
    background: #4aa5ff;
  }

  &::after {
    content: '';
    position: absolute;
    left: 18rpx;
    top: 18rpx;
    width: 14rpx;
    height: 4rpx;
    background: #4aa5ff;
    transform: rotate(30deg);
    transform-origin: left;
  }
}

.tree {
  position: absolute;
  bottom: 0;
  width: 96rpx;
  height: 96rpx;
  border-radius: 45% 55% 50% 45%;
  background: linear-gradient(135deg, #67d87d, #20a95f);
  box-shadow: inset -20rpx -16rpx 0 rgba(0, 107, 72, 0.08);

  &::after {
    content: '';
    position: absolute;
    left: 44rpx;
    bottom: -24rpx;
    width: 10rpx;
    height: 52rpx;
    border-radius: 8rpx;
    background: #9d6841;
  }
}

.tree-one {
  left: 84rpx;
}

.tree-two {
  right: 68rpx;
  bottom: 4rpx;
  transform: scale(1.08);
}

.auth-card {
  position: relative;
  z-index: 5;
  display: flex;
  flex-direction: column;
  margin: -18rpx 36rpx 0;
  padding: 0 42rpx 42rpx;
  border-radius: 44rpx;
  background: rgba(255, 255, 255, 0.97);
  box-shadow: 0 28rpx 72rpx rgba(40, 111, 196, 0.14);
  overflow: hidden;
}

.auth-card--register {
  margin-top: -48rpx;
  padding-bottom: 32rpx;
}

.tabs {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  height: 132rpx;
  margin: 0 -42rpx 36rpx;
  border-bottom: 2rpx solid #eef3fb;
}

.tab-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8e97a7;
  font-size: 40rpx;
  font-weight: 900;
}

.tab-btn.active {
  color: #0877f2;

  &::after {
    content: '';
    position: absolute;
    left: 50%;
    bottom: 20rpx;
    width: 56rpx;
    height: 6rpx;
    border-radius: 999rpx;
    background: #0877f2;
    transform: translateX(-50%);
  }
}

.auth-panel {
  display: flex;
  flex-direction: column;
}

.field {
  height: 84rpx;
  margin-bottom: 24rpx;
  display: grid;
  grid-template-columns: 68rpx 1fr;
  align-items: center;
  border: 2rpx solid #dcecff;
  border-radius: 28rpx;
  background: #ffffff;
  box-shadow: inset 0 2rpx 0 rgba(232, 242, 255, 0.75);

  input {
    width: 100%;
    min-width: 0;
    color: #182233;
    font-size: 30rpx;
    font-weight: 600;
  }
}

.field--code,
.field--password {
  grid-template-columns: 68rpx 1fr auto;
}

.field-icon {
  position: relative;
  display: block;
  width: 32rpx;
  height: 32rpx;
  margin-left: 22rpx;
  color: #1788ff;
}

.field-icon::before,
.field-icon::after {
  content: '';
  position: absolute;
  box-sizing: border-box;
}

.field-icon--user::before {
  top: 1rpx;
  left: 9rpx;
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: currentColor;
}

.field-icon--user::after {
  left: 3rpx;
  bottom: 2rpx;
  width: 26rpx;
  height: 14rpx;
  border-radius: 18rpx 18rpx 8rpx 8rpx;
  background: currentColor;
}

.field-icon--graduate::before {
  top: 4rpx;
  left: 1rpx;
  width: 30rpx;
  height: 18rpx;
  background: currentColor;
  clip-path: polygon(50% 0, 100% 36%, 50% 72%, 0 36%);
}

.field-icon--graduate::after {
  left: 9rpx;
  bottom: 4rpx;
  width: 14rpx;
  height: 7rpx;
  border-radius: 3rpx;
  background: currentColor;
}

.field-icon--phone::before {
  top: 1rpx;
  left: 8rpx;
  width: 17rpx;
  height: 30rpx;
  border: 4rpx solid currentColor;
  border-radius: 6rpx;
}

.field-icon--phone::after {
  left: 14rpx;
  bottom: 4rpx;
  width: 6rpx;
  height: 3rpx;
  border-radius: 999rpx;
  background: currentColor;
}

.field-icon--shield::before {
  top: 0;
  left: 2rpx;
  width: 28rpx;
  height: 32rpx;
  background: currentColor;
  clip-path: polygon(50% 0, 90% 14%, 84% 58%, 50% 100%, 16% 58%, 10% 14%);
}

.field-icon--lock::before {
  top: 0;
  left: 7rpx;
  width: 18rpx;
  height: 15rpx;
  border: 4rpx solid currentColor;
  border-bottom: 0;
  border-radius: 14rpx 14rpx 0 0;
}

.field-icon--lock::after {
  left: 4rpx;
  bottom: 0;
  width: 24rpx;
  height: 21rpx;
  border-radius: 6rpx;
  background: currentColor;
}

.field-placeholder {
  color: #9ca5b5;
  font-weight: 500;
}

.code-btn,
.eye-btn {
  height: 64rpx;
  margin-right: 16rpx;
  padding: 0 18rpx;
  border: 0;
  border-left: 2rpx solid #e5eef9;
  border-radius: 0;
  color: #0877f2;
  background: transparent;
  font-size: 26rpx;
  font-weight: 800;
  line-height: 64rpx;
  white-space: nowrap;
}

.eye-btn {
  color: #9ca5b5;
}

.agreement {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6rpx;
  margin: -4rpx 0 22rpx;
  color: #8c96a7;
  font-size: 24rpx;
  line-height: 1.6;
}

.agreement-link {
  color: #0877f2;
  font-weight: 700;
}

.checkbox {
  flex: none;
  display: grid;
  place-items: center;
  width: 28rpx;
  height: 28rpx;
  border: 2rpx solid #d3dbe8;
  border-radius: 8rpx;
  color: #ffffff;
  background: #ffffff;
  font-size: 20rpx;
  font-weight: 900;
}

.checkbox--checked {
  border-color: #0877f2;
  background: #0877f2;
}

.primary-btn {
  width: 100%;
  height: 92rpx;
  margin-top: 4rpx;
  border: none;
  border-radius: 32rpx;
  color: #ffffff;
  background: linear-gradient(90deg, #278dff 0%, #0568f1 100%);
  box-shadow: 0 18rpx 36rpx rgba(8, 119, 242, 0.25);
  font-size: 36rpx;
  font-weight: 900;
}

.policy {
  margin: 32rpx 36rpx 0;
  text-align: center;
  color: #8c96a7;
  font-size: 24rpx;
  line-height: 1.7;
}
</style>
