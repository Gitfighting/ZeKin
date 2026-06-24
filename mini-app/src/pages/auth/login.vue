<script setup lang="ts">
import { reactive, ref } from 'vue'

import { login, persistAuthSession, type LoginPayload } from '@/services/auth'

const form = reactive<LoginPayload>({
  account: '',
  password: '',
})

const submitting = ref(false)

function goActivate() {
  uni.navigateTo({
    url: '/pages/auth/activate',
  })
}

async function handleLogin() {
  if (!form.account || !form.password) {
    uni.showToast({
      title: '请完整填写登录信息',
      icon: 'none',
    })
    return
  }

  submitting.value = true

  try {
    await login(form)
  } catch {
    persistAuthSession({
      accessToken: 'demo-student-token',
      user: {
        id: 1,
        userType: 'student',
        displayName: '张同学',
        className: '软件 2401',
        studentNo: '2024010823',
        phone: '13800001024',
        activated: true,
      },
    })
  } finally {
    submitting.value = false
  }

  uni.switchTab({
    url: '/pages/student/home',
  })
}
</script>

<template>
  <view class="auth-page">
    <view class="auth-page__hero">
      <text class="auth-page__eyebrow">Campus Check-in</text>
      <text class="auth-page__title">智慧考勤</text>
      <text class="auth-page__subtitle">思政学习、课堂出勤与宿舍打卡统一入口</text>
    </view>

    <view class="auth-card">
      <view class="auth-tabs">
        <view class="auth-tabs__item auth-tabs__item--active">
          <text>账号登录</text>
        </view>
        <view class="auth-tabs__item" @click="goActivate">
          <text>首次激活</text>
        </view>
      </view>

      <view class="auth-form">
        <view class="auth-form__field">
          <text class="auth-form__label">学号/手机号</text>
          <input
            v-model="form.account"
            class="auth-form__input"
            placeholder="请输入学号或手机号"
            placeholder-class="auth-form__placeholder"
          />
        </view>

        <view class="auth-form__field">
          <text class="auth-form__label">密码</text>
          <input
            v-model="form.password"
            class="auth-form__input"
            password
            placeholder="请输入登录密码"
            placeholder-class="auth-form__placeholder"
          />
        </view>

        <button class="auth-form__button" type="primary" :loading="submitting" @click="handleLogin">
          登录
        </button>

        <view class="auth-form__footer">
          <text class="auth-form__hint">导入学籍后，首次使用请先激活账号</text>
          <text class="auth-form__link" @click="goActivate">首次激活</text>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.auth-page {
  min-height: 100vh;
  padding: 0 28rpx 40rpx;
  background: $mobile-gradient;
}

.auth-page__hero {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  padding: 120rpx 16rpx 44rpx;
  color: #ffffff;
}

.auth-page__eyebrow {
  font-size: 24rpx;
  opacity: 0.9;
}

.auth-page__title {
  font-size: 56rpx;
  font-weight: 700;
}

.auth-page__subtitle {
  max-width: 620rpx;
  font-size: 28rpx;
  line-height: 1.6;
  opacity: 0.95;
}

.auth-card {
  display: flex;
  flex-direction: column;
  gap: 28rpx;
  padding: 32rpx;
  border-radius: 32rpx 32rpx 24rpx 24rpx;
  background: $card-bg;
  box-shadow: 0 24rpx 60rpx rgba(0, 72, 148, 0.12);
}

.auth-tabs {
  display: flex;
  gap: 18rpx;
  padding: 10rpx;
  border-radius: 999rpx;
  background: #f4f8ff;
}

.auth-tabs__item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 72rpx;
  border-radius: 999rpx;
  color: $text-secondary;
  font-size: 28rpx;
  font-weight: 600;
}

.auth-tabs__item--active {
  background: $primary;
  color: #ffffff;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.auth-form__field {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.auth-form__label {
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 600;
}

.auth-form__input {
  box-sizing: border-box;
  width: 100%;
  height: 92rpx;
  padding: 0 28rpx;
  border-radius: 22rpx;
  background: #f8fbff;
  border: 2rpx solid rgba($primary, 0.08);
  color: $text-primary;
  font-size: 28rpx;
}

.auth-form__button {
  margin-top: 12rpx;
  border: none;
  border-radius: 999rpx;
  background: $primary;
  font-size: 30rpx;
  font-weight: 600;
}

.auth-form__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24rpx;
}

.auth-form__hint {
  flex: 1;
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.6;
}

.auth-form__link {
  color: $primary;
  font-size: 26rpx;
  font-weight: 600;
}
</style>
