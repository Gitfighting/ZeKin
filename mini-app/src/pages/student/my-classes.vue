<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { ref } from 'vue'

import { logInfo, showError } from '@/services/feedback'
import { getStudentJoinedGroups, type StudentJoinedGroup } from '@/services/student'

const loading = ref(false)
const groups = ref<StudentJoinedGroup[]>([])

function openJoinClass() {
  uni.navigateTo({ url: '/pages/student/join-class' })
}

onShow(async () => {
  loading.value = true
  try {
    groups.value = await getStudentJoinedGroups()
    logInfo('我的班级加载成功', { count: groups.value.length })
  } catch (error) {
    groups.value = []
    showError(error, '班级列表加载失败')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <scroll-view scroll-y class="my-classes-page">
    <view class="my-classes-page__hero">
      <text class="my-classes-page__title">我的班级</text>
      <text class="my-classes-page__subtitle">查看自己进入的班级列表</text>
    </view>

    <view v-if="loading" class="my-classes-page__empty">加载中...</view>

    <view v-else-if="!groups.length" class="my-classes-page__empty-card">
      <text class="my-classes-page__empty-title">暂未加入任何班级</text>
      <text class="my-classes-page__empty-text">向老师索取邀请码，加入班级后即可接收打卡任务</text>
      <button class="my-classes-page__join-btn" @click="openJoinClass">去加入班级</button>
    </view>

    <view v-else class="my-classes-page__list">
      <view v-for="group in groups" :key="group.id" class="my-classes-page__card">
        <view class="my-classes-page__card-icon">🏫</view>
        <view class="my-classes-page__card-body">
          <text class="my-classes-page__card-name">{{ group.name }}</text>
          <text class="my-classes-page__card-meta">
            {{ group.teacherName ? `任课教师：${group.teacherName} · ` : '' }}{{ group.studentCount }} 名同学 · {{ group.recentTaskCount ?? 0 }} 个考勤任务
          </text>
        </view>
      </view>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.my-classes-page {
  min-height: 100vh;
  padding: 24rpx;
  background: $page-bg;
  box-sizing: border-box;
}

.my-classes-page__hero {
  padding: 28rpx 24rpx;
  border-radius: 22rpx;
  background: linear-gradient(180deg, #1677ff 0%, #53b1fd 100%);
  color: #fff;
}

.my-classes-page__title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
}

.my-classes-page__subtitle {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.6;
  opacity: 0.92;
}

.my-classes-page__empty {
  margin-top: 24rpx;
  padding: 40rpx 0;
  color: $text-secondary;
  font-size: 26rpx;
  text-align: center;
}

.my-classes-page__empty-card {
  margin-top: 24rpx;
  padding: 40rpx 28rpx;
  border-radius: 22rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
  text-align: center;
}

.my-classes-page__empty-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $text-primary;
}

.my-classes-page__empty-text {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: $text-secondary;
}

.my-classes-page__join-btn {
  margin-top: 28rpx;
  border-radius: 999rpx;
  background: $primary;
  color: #fff;
  font-size: 28rpx;
}

.my-classes-page__list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  margin-top: 24rpx;
}

.my-classes-page__card {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx;
  border-radius: 22rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.my-classes-page__card-icon {
  display: flex;
  width: 88rpx;
  height: 88rpx;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 24rpx;
  background: linear-gradient(180deg, #ffb347 0%, #ff9f1a 100%);
  font-size: 40rpx;
}

.my-classes-page__card-body {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  min-width: 0;
}

.my-classes-page__card-name {
  font-size: 30rpx;
  font-weight: 700;
  color: $text-primary;
}

.my-classes-page__card-meta {
  font-size: 24rpx;
  color: $text-secondary;
}
</style>
