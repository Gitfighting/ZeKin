<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import {
  getTeacherExceptions,
  reviewTeacherException,
  type TeacherException,
  type TeacherExceptionStatus,
} from '@/services/teacher'

const activeTab = ref<'pending' | 'reviewed'>('pending')
const exceptions = ref<TeacherException[]>([
  {
    id: 1,
    studentName: '张悦',
    taskTitle: '思政一班晨检',
    groupName: '思政一班',
    submittedAt: '08:09',
    reason: '定位偏移，申请人工确认',
    status: 'pending',
  },
  {
    id: 2,
    studentName: '陈雪',
    taskTitle: '课堂签到',
    groupName: '思政二班',
    submittedAt: '09:58',
    reason: '图片模糊，需要补充',
    status: 'need_more',
    comment: '请重新上传清晰照片',
  },
  {
    id: 3,
    studentName: '何源',
    taskTitle: '晚点名',
    groupName: '思政三班',
    submittedAt: '21:14',
    reason: '已线下请假',
    status: 'approved',
    comment: '辅导员确认通过',
  },
])

const commentDrafts = reactive<Record<number, string>>({})

const visibleExceptions = computed(() =>
  exceptions.value.filter((item) =>
    activeTab.value === 'pending' ? item.status === 'pending' : item.status !== 'pending',
  ),
)

async function loadExceptions() {
  if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
    return
  }

  try {
    exceptions.value = await getTeacherExceptions()
  } catch {
    // Keep fallback data.
  }
}

async function review(id: number, action: 'approve' | 'reject' | 'need_more') {
  const comment = commentDrafts[id]?.trim()
  const nextStatus: Record<typeof action, TeacherExceptionStatus> = {
    approve: 'approved',
    reject: 'rejected',
    need_more: 'need_more',
  }

  try {
    if (typeof uni !== 'undefined' && typeof uni.request === 'function') {
      await reviewTeacherException(id, { action, comment })
    }

    exceptions.value = exceptions.value.map((item) =>
      item.id === id ? { ...item, status: nextStatus[action], comment } : item,
    )

    if (typeof uni !== 'undefined') {
      uni.showToast({ title: '已处理', icon: 'success' })
    }
  } catch {
    if (typeof uni !== 'undefined') {
      uni.showToast({ title: '提交失败', icon: 'none' })
    }
  }
}

onMounted(loadExceptions)
</script>

<template>
  <view class="teacher-page">
    <view class="page-head">
      <text class="page-title">异常审核</text>
      <text class="page-subtitle">先处理待审，再回看已结论记录。</text>
    </view>

    <view class="tab-row">
      <view :class="['tab-item', { active: activeTab === 'pending' }]" @click="activeTab = 'pending'">待审核</view>
      <view :class="['tab-item', { active: activeTab === 'reviewed' }]" @click="activeTab = 'reviewed'">已处理</view>
    </view>

    <view class="list-card">
      <view v-for="item in visibleExceptions" :key="item.id" class="exception-card">
        <text class="card-title">{{ item.studentName }} · {{ item.groupName }}</text>
        <text class="card-subtitle">{{ item.taskTitle }} · {{ item.submittedAt }}</text>
        <text class="reason-line">{{ item.reason }}</text>
        <textarea
          v-model="commentDrafts[item.id]"
          class="comment-box"
          placeholder="填写审核备注"
          maxlength="60"
        />
        <view class="action-row">
          <view class="ghost-button" @click="review(item.id, 'need_more')">补充材料</view>
          <view class="ghost-button danger" @click="review(item.id, 'reject')">驳回</view>
          <view class="solid-button" @click="review(item.id, 'approve')">通过</view>
        </view>
        <text v-if="item.comment" class="comment-line">当前意见：{{ item.comment }}</text>
      </view>
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

.page-title,
.card-title {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: $text-primary;
}

.page-subtitle,
.card-subtitle,
.reason-line,
.comment-line {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.5;
  color: $text-secondary;
}

.tab-row,
.action-row {
  display: flex;
  gap: 12rpx;
}

.tab-row {
  margin-top: 20rpx;
}

.tab-item {
  flex: 1;
  padding: 18rpx 0;
  border-radius: 16rpx;
  background: rgba(22, 119, 255, 0.08);
  color: $text-secondary;
  text-align: center;
  font-size: 24rpx;
}

.tab-item.active {
  background: $primary;
  color: #fff;
}

.list-card {
  margin-top: 20rpx;
  display: grid;
  gap: 16rpx;
}

.exception-card {
  padding: 24rpx;
  border-radius: 20rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.comment-box {
  width: 100%;
  min-height: 120rpx;
  margin-top: 14rpx;
  padding: 18rpx;
  border-radius: 16rpx;
  background: #f7faff;
  box-sizing: border-box;
}

.action-row {
  margin-top: 16rpx;
}

.ghost-button,
.solid-button {
  flex: 1;
  padding: 18rpx 0;
  border-radius: 16rpx;
  text-align: center;
  font-size: 22rpx;
}

.ghost-button {
  background: #eef5ff;
  color: $primary;
}

.ghost-button.danger {
  color: $danger;
}

.solid-button {
  background: $primary;
  color: #fff;
}
</style>
