<script setup lang="ts">
import { onMounted, ref } from 'vue'

import TeacherTabBar from './components/TeacherTabBar.vue'
import { getTeacherGroups, type TeacherGroup } from '@/services/teacher'

const groups = ref<TeacherGroup[]>([
  { id: 1, name: '思政一班', studentCount: 42, recentTaskCount: 8, courseName: '马克思主义原理' },
  { id: 2, name: '思政二班', studentCount: 39, recentTaskCount: 7, courseName: '思想道德与法治' },
  { id: 3, name: '思政三班', studentCount: 45, recentTaskCount: 6, courseName: '中国近现代史纲要' },
])

async function loadGroups() {
  if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
    return
  }

  try {
    groups.value = await getTeacherGroups()
  } catch {
    // Keep fallback data visible.
  }
}

function openGroup(id: number) {
  if (typeof uni === 'undefined') {
    return
  }

  uni.navigateTo({ url: `/pages/teacher/group-detail?id=${id}` })
}

onMounted(loadGroups)
</script>

<template>
  <view class="teacher-page">
    <view class="page-head">
      <text class="page-title">班级管理</text>
      <text class="page-subtitle">按班级看学生规模、最近任务和待处理压力。</text>
    </view>

    <view class="group-list">
      <view v-for="group in groups" :key="group.id" class="group-card" @click="openGroup(group.id)">
        <view class="group-header">
          <text class="group-title">{{ group.name }}</text>
          <text class="group-link">查看 ></text>
        </view>
        <text class="group-course">{{ group.courseName }}</text>
        <view class="group-stats">
          <text>{{ group.studentCount }} 名学生</text>
          <text>近 7 日 {{ group.recentTaskCount }} 个任务</text>
        </view>
      </view>
    </view>

    <TeacherTabBar active="groups" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.teacher-page {
  min-height: 100vh;
  padding: 24rpx 24rpx 180rpx;
  background: $page-bg;
}

.page-title,
.group-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: $text-primary;
}

.page-subtitle,
.group-course,
.group-stats {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.5;
  color: $text-secondary;
}

.group-list {
  display: grid;
  gap: 16rpx;
  margin-top: 20rpx;
}

.group-card {
  padding: 24rpx;
  border-radius: 20rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.group-header,
.group-stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.group-link {
  font-size: 22rpx;
  color: $primary;
}
</style>
