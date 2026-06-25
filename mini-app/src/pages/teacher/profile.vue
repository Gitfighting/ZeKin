<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import TeacherTabBar from './components/TeacherTabBar.vue'
import { clearLoginState } from '@/services/auth'
import { logInfo, showError } from '@/services/feedback'
import { getTeacherGroups, type TeacherGroup } from '@/services/teacher'

const teacherName = ref('教师')
const teacherRole = ref('思政教师 / 班主任')
const groups = ref<TeacherGroup[]>([])
const messageSettings = reactive({
  exceptionAlert: true,
  dailyDigest: true,
})

async function loadProfile() {
  if (typeof uni !== 'undefined') {
    const cachedUser = uni.getStorageSync('user_profile') as
      | { display_name?: string; title?: string }
      | undefined

    if (cachedUser?.display_name) {
      teacherName.value = cachedUser.display_name
    }

    if (cachedUser?.title) {
      teacherRole.value = cachedUser.title
    }
  }

  if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
    groups.value = []
    return
  }

  try {
    groups.value = await getTeacherGroups()
    logInfo('教师个人页班级加载成功', { count: groups.value.length })
  } catch (error) {
    groups.value = []
    showError(error, '教师班级信息加载失败')
  }
}

function finishLogout() {
  clearLoginState()
  logInfo('教师退出登录成功')
  uni.reLaunch({ url: '/pages/auth/login' })
}

function handleLogout() {
  uni.showModal({
    title: '退出登录',
    content: '确认退出当前账号？',
    confirmText: '退出',
    success: (result: { confirm?: boolean }) => {
      if (result.confirm) {
        finishLogout()
      }
    },
  })
}

onMounted(loadProfile)
</script>

<template>
  <view class="teacher-page">
    <view class="profile-card">
      <text class="profile-name">{{ teacherName }}</text>
      <text class="profile-role">{{ teacherRole }}</text>
      <text class="profile-note">优先处理待审核异常，保持班级任务节奏稳定。</text>
    </view>

    <view class="section-card">
      <text class="section-title">管理班级</text>
      <view v-for="group in groups" :key="group.id" class="row-card">
        <view>
          <text class="row-title">{{ group.name }}</text>
          <text class="row-subtitle">{{ group.studentCount }} 人 · 近 7 日 {{ group.recentTaskCount }} 个任务</text>
        </view>
      </view>
      <text v-if="groups.length === 0" class="empty-line">暂无管理班级</text>
    </view>

    <view class="section-card">
      <text class="section-title">消息设置</text>
      <view class="setting-row">
        <text class="row-title">异常审核提醒</text>
        <switch
          :checked="messageSettings.exceptionAlert"
          color="#1677ff"
          @change="messageSettings.exceptionAlert = $event.detail.value"
        />
      </view>
      <view class="setting-row">
        <text class="row-title">每日日报入口</text>
        <switch
          :checked="messageSettings.dailyDigest"
          color="#1677ff"
          @change="messageSettings.dailyDigest = $event.detail.value"
        />
      </view>
    </view>

    <view class="section-card">
      <view class="logout-button" @click="handleLogout">退出登录</view>
    </view>

    <TeacherTabBar active="profile" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.teacher-page {
  min-height: 100vh;
  padding: 24rpx 24rpx 180rpx;
  background: $page-bg;
}

.profile-card,
.section-card {
  padding: 24rpx;
  border-radius: 22rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.profile-card {
  background: linear-gradient(180deg, #1677ff 0%, #53b1fd 100%);
  color: #fff;
}

.profile-name,
.section-title,
.row-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: $text-primary;
}

.profile-name {
  color: #fff;
}

.profile-role,
.profile-note,
.row-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.5;
  color: $text-secondary;
}

.profile-role,
.profile-note {
  color: rgba(255, 255, 255, 0.92);
}

.section-card {
  margin-top: 20rpx;
}

.row-card,
.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  padding: 20rpx 0;
  border-bottom: 1rpx solid rgba(102, 112, 133, 0.12);
}

.row-card:last-child,
.setting-row:last-child {
  border-bottom: 0;
}

.row-subtitle {
  color: $text-secondary;
}

.empty-line {
  display: block;
  padding: 20rpx 0 0;
  color: $text-secondary;
  font-size: 24rpx;
}

.logout-button {
  padding: 20rpx 0;
  border-radius: 18rpx;
  background: #fff1f0;
  color: #d92d20;
  font-size: 28rpx;
  font-weight: 700;
  text-align: center;
}
</style>
