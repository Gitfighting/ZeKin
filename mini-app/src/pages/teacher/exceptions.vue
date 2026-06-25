<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import {
  getTeacherExceptions,
  reviewTeacherException,
  type TeacherException,
  type TeacherExceptionStatus,
} from '@/services/teacher'
import { logInfo, showError, showSuccess } from '@/services/feedback'

const activeTab = ref<'pending' | 'reviewed'>('pending')
const exceptions = ref<TeacherException[]>([])

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
    logInfo('教师异常列表加载成功', { count: exceptions.value.length })
  } catch (error) {
    exceptions.value = []
    showError(error, '异常列表加载失败')
  }
}

async function review(id: number, action: 'approve' | 'reject' | 'need_more') {
  const comment = commentDrafts[id]?.trim() ?? ''
  const nextStatus: Record<typeof action, TeacherExceptionStatus> = {
    approve: 'approved',
    reject: 'rejected',
    need_more: 'need_more',
  }

  try {
    if (typeof uni !== 'undefined' && typeof uni.request === 'function') {
      await reviewTeacherException(id, { decision: action, comment })
    }

    exceptions.value = exceptions.value.map((item) =>
      item.id === id ? { ...item, status: nextStatus[action], comment } : item,
    )

    if (typeof uni !== 'undefined') {
      logInfo('教师异常审核成功', { id, action })
      showSuccess('已处理')
    }
  } catch (error) {
    showError(error, '提交失败')
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
      <view v-if="visibleExceptions.length === 0" class="empty-card">
        <text>暂无异常记录</text>
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

.empty-card {
  padding: 28rpx;
  border-radius: 20rpx;
  background: $card-bg;
  color: $text-secondary;
  font-size: 26rpx;
  text-align: center;
}
</style>
