<script setup lang="ts">
import { reactive, ref } from 'vue'

import { activateStudent, type ActivateStudentPayload } from '@/services/auth'
import { logInfo, showError } from '@/services/feedback'

const form = reactive<ActivateStudentPayload>({
  name: '',
  studentNo: '',
  phone: '',
  code: '',
  password: '',
  confirmPassword: '',
})

const submitting = ref(false)

function goLogin() {
  uni.navigateBack({
    delta: 1,
  })
}

async function handleActivate() {
  if (!form.name || !form.studentNo || !form.phone || !form.code || !form.password || !form.confirmPassword) {
    uni.showToast({
      title: '请完整填写激活信息',
      icon: 'none',
    })
    return
  }

  if (form.password !== form.confirmPassword) {
    uni.showToast({
      title: '两次密码输入不一致',
      icon: 'none',
    })
    return
  }

  submitting.value = true

  try {
    const session = await activateStudent(form)
    logInfo('学生账号激活成功', {
      studentNo: form.studentNo,
      userId: session.user.id,
    })
    uni.switchTab({
      url: '/pages/student/home',
    })
  } catch (error) {
    showError(error, '激活失败，请核对学号和手机号')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <view class="auth-page">
    <view class="auth-page__hero">
      <text class="auth-page__eyebrow">Student Activation</text>
      <text class="auth-page__title">首次激活</text>
      <text class="auth-page__subtitle">导入学籍后，使用学号与手机号激活学生账号</text>
    </view>

    <view class="auth-card">
      <view class="auth-tabs">
        <view class="auth-tabs__item" @click="goLogin">
          <text>账号登录</text>
        </view>
        <view class="auth-tabs__item auth-tabs__item--active">
          <text>首次激活</text>
        </view>
      </view>

      <view class="auth-form">
        <view class="auth-form__field">
          <text class="auth-form__label">姓名</text>
          <input v-model="form.name" class="auth-form__input" placeholder="请输入姓名" />
        </view>
        <view class="auth-form__field">
          <text class="auth-form__label">学号</text>
          <input v-model="form.studentNo" class="auth-form__input" placeholder="请输入学号" />
        </view>
        <view class="auth-form__field">
          <text class="auth-form__label">手机号</text>
          <input v-model="form.phone" class="auth-form__input" type="number" placeholder="请输入预留手机号" />
        </view>
        <view class="auth-form__field">
          <text class="auth-form__label">验证码</text>
          <input v-model="form.code" class="auth-form__input" type="number" placeholder="测试验证码 000000" />
        </view>
        <view class="auth-form__field">
          <text class="auth-form__label">设置密码</text>
          <input v-model="form.password" class="auth-form__input" password placeholder="不少于 6 位" />
        </view>
        <view class="auth-form__field">
          <text class="auth-form__label">确认密码</text>
          <input
            v-model="form.confirmPassword"
            class="auth-form__input"
            password
            placeholder="再次输入登录密码"
          />
        </view>

        <button class="auth-form__button" type="primary" :loading="submitting" @click="handleActivate">
          激活并进入
        </button>
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
</style>
