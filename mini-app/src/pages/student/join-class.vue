<script setup lang="ts">
import { ref } from 'vue'

import { useStudentPageHeroLayout } from '@/composables/useStudentPageHeroLayout'
import { logInfo, showError, showSuccess } from '@/services/feedback'
import { joinClassByInviteCode, type StudentJoinedGroup } from '@/services/student'

const { brandBarStyle, heroContentStyle, backButtonStyle, navRightStyle } = useStudentPageHeroLayout()

const pageSlogan = '输入邀请码即可加入班群，签到方式由教师统一设置'

const inviteCode = ref('')
const submitting = ref(false)
const joinedGroup = ref<StudentJoinedGroup | null>(null)

function handleBack() {
  uni.navigateBack({ delta: 1 })
}

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
  <scroll-view scroll-y class="join-class-page">
    <view class="student-page-header-block">
      <view class="student-page-hero">
        <view class="student-page-hero__visual">
          <view class="student-page-hero__bg-window">
            <image class="student-page-hero__bg" src="/static/home.png" mode="widthFix" />
          </view>
        </view>

        <view class="join-class-page__nav-bar" :style="brandBarStyle">
          <view
            class="join-class-page__back"
            :style="backButtonStyle"
            aria-label="返回"
            @click="handleBack"
          ></view>
          <view class="join-class-page__nav-spacer" :style="navRightStyle"></view>
        </view>

        <view class="student-page-hero__content" :style="heroContentStyle">
          <text class="student-page-hero__title">加入班群</text>
          <text class="student-page-hero__slogan">{{ pageSlogan }}</text>
        </view>
      </view>

      <view class="join-class-page__panel student-page-overlap-card">
        <view v-if="!joinedGroup" class="join-class-page__form">
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

        <view v-else class="join-class-page__result">
          <text class="result-title">{{ joinedGroup.alreadyMember ? '已在班级中' : '加入成功' }}</text>
          <text class="result-name">{{ joinedGroup.name }}</text>
          <text class="result-meta">当前班级共 {{ joinedGroup.studentCount }} 名学生</text>
          <button class="ghost-btn" @click="resetForm">继续加入其他班级</button>
          <button class="ghost-btn" @click="goMyClasses">查看我的班级</button>
          <button class="primary-btn" @click="goHome">返回首页</button>
        </view>
      </view>
    </view>

    <view class="student-page-content-sheet join-class-page__sheet"></view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.join-class-page {
  min-height: 100vh;
  background: $page-bg;
}

.join-class-page__nav-bar {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24rpx 0 32rpx;
  box-sizing: border-box;
}

.join-class-page__back {
  position: relative;
  flex-shrink: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.28);
  box-shadow: 0 4rpx 16rpx rgba(15, 60, 120, 0.12);

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20rpx;
    height: 20rpx;
    margin-top: -11rpx;
    margin-left: -5rpx;
    border-left: 4rpx solid #fff;
    border-bottom: 4rpx solid #fff;
    transform: rotate(45deg);
  }
}

.join-class-page__nav-spacer {
  flex-shrink: 0;
}

.join-class-page__panel {
  padding: 8rpx 24rpx 24rpx;
}

.join-class-page__sheet {
  min-height: 120rpx;
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
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

.result-title {
  display: block;
  font-size: 34rpx;
  font-weight: 700;
  color: $text-primary;
}

.result-name {
  display: block;
  margin-top: 12rpx;
  font-size: 32rpx;
  font-weight: 600;
  color: $text-primary;
}

.result-meta {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: $text-secondary;
}
</style>

<style lang="scss">
@use '@/styles/student-page-hero.scss';
</style>
