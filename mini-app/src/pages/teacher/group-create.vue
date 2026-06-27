<script setup lang="ts">
import { ref } from 'vue'

import { logInfo, showError, showSuccess } from '@/services/feedback'
import { createTeacherGroup } from '@/services/teacher'

const name = ref('')
const submitting = ref(false)
const createdInviteCode = ref('')

async function submit() {
  const trimmed = name.value.trim()
  if (!trimmed) {
    showError(new Error('请输入班级名称'), '请填写班级名称')
    return
  }

  submitting.value = true
  try {
    const group = await createTeacherGroup(trimmed)
    createdInviteCode.value = group.inviteCode ?? ''
    showSuccess('班级创建成功')
    logInfo('班级创建成功', group)
  } catch (error) {
    showError(error, '创建班级失败')
  } finally {
    submitting.value = false
  }
}

function copyInviteCode() {
  if (!createdInviteCode.value || typeof uni === 'undefined') {
    return
  }

  uni.setClipboardData({
    data: createdInviteCode.value,
    success: () => showSuccess('邀请码已复制'),
  })
}

function openGroupDetail() {
  if (typeof uni === 'undefined') {
    return
  }

  uni.navigateBack()
}
</script>

<template>
  <view class="teacher-page">
    <view class="hero-card">
      <text class="page-title">创建班级</text>
      <text class="page-subtitle">创建后系统将生成 6 位邀请码，学生凭码加入班级。</text>
    </view>

    <view v-if="!createdInviteCode" class="form-card">
      <text class="field-label">班级名称</text>
      <input
        v-model="name"
        class="field-input"
        maxlength="30"
        placeholder="例如：软件工程 2601 班"
        placeholder-class="field-placeholder"
      />
      <button class="primary-btn" :loading="submitting" :disabled="submitting" @click="submit">
        创建并生成邀请码
      </button>
    </view>

    <view v-else class="result-card">
      <text class="result-title">班级已创建</text>
      <text class="result-name">{{ name }}</text>
      <view class="invite-box">
        <text class="invite-label">班级邀请码</text>
        <text class="invite-code">{{ createdInviteCode }}</text>
      </view>
      <text class="result-tip">请把邀请码发给学生，学生在首页「加入班级」中输入即可入班。</text>
      <button class="ghost-btn" @click="copyInviteCode">复制邀请码</button>
      <button class="primary-btn" @click="openGroupDetail">返回班级管理</button>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.teacher-page {
  min-height: 100vh;
  padding: 24rpx;
  background: $page-bg;
}

.hero-card,
.form-card,
.result-card {
  padding: 24rpx;
  border-radius: 22rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.hero-card {
  background: linear-gradient(180deg, #1677ff 0%, #53b1fd 100%);
  color: #fff;
}

.page-title,
.result-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
}

.page-subtitle,
.result-tip {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.6;
  opacity: 0.92;
}

.form-card,
.result-card {
  margin-top: 20rpx;
}

.field-label,
.invite-label {
  display: block;
  font-size: 24rpx;
  color: $text-secondary;
}

.field-input {
  margin-top: 12rpx;
  padding: 22rpx 24rpx;
  border-radius: 16rpx;
  background: #f5f7fb;
  font-size: 28rpx;
  color: $text-primary;
}

.field-placeholder {
  color: #b0b8c4;
}

.primary-btn,
.ghost-btn {
  margin-top: 24rpx;
  border-radius: 999rpx;
  font-size: 28rpx;
}

.primary-btn {
  background: $primary;
  color: #fff;
}

.ghost-btn {
  background: #eef4ff;
  color: $primary;
}

.result-name {
  display: block;
  margin-top: 12rpx;
  font-size: 30rpx;
  font-weight: 600;
  color: $text-primary;
}

.invite-box {
  margin-top: 24rpx;
  padding: 28rpx;
  border-radius: 18rpx;
  background: #f5f8ff;
  text-align: center;
}

.invite-code {
  display: block;
  margin-top: 12rpx;
  font-size: 52rpx;
  font-weight: 700;
  letter-spacing: 8rpx;
  color: $primary;
}

.result-tip {
  color: $text-secondary;
}
</style>
