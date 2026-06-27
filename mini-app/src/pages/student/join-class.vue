<script setup lang="ts">
import { ref } from 'vue'

import { logInfo, showError, showSuccess } from '@/services/feedback'
import { joinClassByInviteCode, type StudentJoinedGroup } from '@/services/student'

const inviteCode = ref('')
const submitting = ref(false)
const joinedGroup = ref<StudentJoinedGroup | null>(null)

async function submit() {
  const code = inviteCode.value.trim()
  if (!code) {
    showError(new Error('请输入邀请码'), '请填写班级邀请码')
    return
  }

  submitting.value = true
  try {
    const result = await joinClassByInviteCode(code)
    joinedGroup.value = result
    showSuccess(result.alreadyMember ? '你已在该班级中' : '加入班级成功')
    logInfo('加入班级成功', result)
  } catch (error) {
    joinedGroup.value = null
    showError(error, '加入班级失败')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  joinedGroup.value = null
  inviteCode.value = ''
}

function goMyClasses() {
  if (typeof uni === 'undefined') {
    return
  }

  uni.navigateTo({ url: '/pages/student/my-classes' })
}

function goHome() {
  if (typeof uni === 'undefined') {
    return
  }

  uni.switchTab({ url: '/pages/student/home' })
}
</script>

<template>
  <view class="student-page">
    <view class="hero-card">
      <text class="page-title">加入班级</text>
      <text class="page-subtitle">向老师索取班级邀请码，输入后即可加入对应班群。签到方式由教师统一设置。</text>
    </view>

    <view v-if="!joinedGroup" class="form-card">
      <text class="field-label">班级邀请码（6 位数字/字母）</text>
      <input
        v-model="inviteCode"
        class="field-input"
        type="text"
        inputmode="text"
        maxlength="8"
        placeholder="请输入邀请码"
        placeholder-class="field-placeholder"
      />
      <button class="primary-btn" :loading="submitting" :disabled="submitting" @click="submit">
        确认加入
      </button>
    </view>

    <view v-else class="result-card">
      <text class="result-title">{{ joinedGroup.alreadyMember ? '已在班级中' : '加入成功' }}</text>
      <text class="result-name">{{ joinedGroup.name }}</text>
      <text class="result-meta">当前班级共 {{ joinedGroup.studentCount }} 名学生</text>
      <button class="ghost-btn" @click="resetForm">继续加入其他班级</button>
      <button class="ghost-btn" @click="goMyClasses">查看我的班级</button>
      <button class="primary-btn" @click="goHome">返回首页</button>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.student-page {
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
.result-meta {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.6;
}

.form-card,
.result-card {
  margin-top: 20rpx;
}

.field-label {
  display: block;
  font-size: 24rpx;
  color: $text-secondary;
}

.field-input {
  margin-top: 12rpx;
  padding: 22rpx 24rpx;
  border-radius: 16rpx;
  background: #f5f7fb;
  font-size: 32rpx;
  letter-spacing: 4rpx;
  text-transform: uppercase;
  color: $text-primary;
}

.field-placeholder {
  color: #b0b8c4;
  text-transform: none;
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
  font-size: 32rpx;
  font-weight: 600;
  color: $text-primary;
}

.result-meta {
  color: $text-secondary;
}
</style>
