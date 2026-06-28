<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import RuleSummary from '@/components/RuleSummary.vue'
import StatusTag from '@/components/StatusTag.vue'
import { logInfo, showError } from '@/services/feedback'
import { getStudentTaskDetail, type StudentTask } from '@/services/student'

const task = ref<StudentTask | null>(null)
const checkinDone = ref(false)

const navBarStyle = ref<Record<string, string>>({
  height: '88px',
})
const navRowStyle = ref<Record<string, string>>({
  top: '48px',
  height: '32px',
})
const backButtonStyle = ref<Record<string, string>>({
  width: '32px',
  height: '32px',
})
const navRightStyle = ref<Record<string, string>>({
  width: '96px',
  height: '32px',
})

function syncNavLayout() {
  if (typeof uni === 'undefined') {
    return
  }

  try {
    const menuButton = uni.getMenuButtonBoundingClientRect()
    const systemInfo = uni.getSystemInfoSync()
    const gapBelow = 10

    navBarStyle.value = {
      height: `${menuButton.bottom + gapBelow}px`,
    }
    navRowStyle.value = {
      top: `${menuButton.top}px`,
      height: `${menuButton.height}px`,
    }
    backButtonStyle.value = {
      width: `${menuButton.height}px`,
      height: `${menuButton.height}px`,
    }
    navRightStyle.value = {
      width: `${(systemInfo.windowWidth ?? 375) - menuButton.left}px`,
      height: `${menuButton.height}px`,
    }
  } catch {
    // 非小程序环境保留默认占位
  }
}

const hasException = computed(() => task.value?.status === 'exception')
const isCompleted = computed(
  () => checkinDone.value || task.value?.status === 'normal' || task.value?.status === 'ended',
)
const primaryLabel = computed(() => {
  if (hasException.value) {
    return '去申诉'
  }
  if (isCompleted.value) {
    return '打卡完成'
  }
  return '签到'
})

function previousPageRoute(): string {
  if (typeof getCurrentPages !== 'function') {
    return ''
  }
  const pages = getCurrentPages()
  return pages.length > 1 ? pages[pages.length - 2]?.route ?? '' : ''
}

function handleBack() {
  const previousRoute = previousPageRoute()
  if (previousRoute && !previousRoute.includes('pages/auth/login')) {
    uni.navigateBack({ delta: 1 })
    return
  }

  uni.switchTab({ url: '/pages/student/tasks' })
}

async function loadTask(id?: string) {
  try {
    if (!id) {
      task.value = null
      uni.showToast({ title: '缺少任务编号', icon: 'none' })
      return
    }
    task.value = await getStudentTaskDetail(id)
    logInfo('学生任务详情加载成功', { taskId: id })
  } catch (error) {
    task.value = null
    showError(error, '任务详情加载失败')
  }
}

function handlePrimaryAction() {
  if (!task.value) {
    uni.showToast({ title: '任务尚未加载', icon: 'none' })
    return
  }

  if (isCompleted.value) {
    uni.navigateBack({ delta: 1 })
    return
  }

  if (hasException.value) {
    uni.navigateTo({
      url: '/pages/student/appeal?recordId=record-3',
    })
    return
  }

  uni.navigateTo({
    url: `/pages/student/checkin-submit?id=${task.value.id}`,
  })
}

onLoad((options) => {
  syncNavLayout()
  checkinDone.value = options?.done === '1'
  void loadTask(options?.id)
})
</script>

<template>
  <scroll-view scroll-y class="detail-page">
    <view class="detail-page__nav" :style="navBarStyle">
      <view class="detail-page__nav-row" :style="navRowStyle">
        <button class="detail-page__back" :style="backButtonStyle" aria-label="返回" @click="handleBack"></button>
        <text class="detail-page__nav-title">打卡详情</text>
        <view class="detail-page__nav-right" :style="navRightStyle"></view>
      </view>
    </view>

    <view class="detail-page__body">
    <view v-if="!task" class="detail-page__card">
      <text class="detail-page__section-title">暂无任务详情</text>
      <text class="detail-page__status-text">请返回任务列表重新进入，或检查后端服务是否正常。</text>
    </view>

    <template v-else>
    <view class="detail-page__card">
      <view class="detail-page__header">
        <view class="detail-page__title-group">
          <text class="detail-page__type">{{ task.type }}</text>
          <text class="detail-page__title">{{ task.title }}</text>
          <text class="detail-page__desc">{{ task.description }}</text>
        </view>
        <StatusTag :status="task.status" />
      </view>
    </view>

    <RuleSummary
      :time-window="task.timeWindow"
      :location-name="task.locationName"
      :location-hint="task.locationHint"
      :requirements="task.requirements"
    />

    <view class="detail-page__card">
      <text class="detail-page__section-title">时间与地点</text>
      <view class="detail-page__row">
        <text class="detail-page__label">打卡窗口</text>
        <text class="detail-page__value">{{ task.timeWindow }}</text>
      </view>
      <view class="detail-page__row">
        <text class="detail-page__label">签到地点</text>
        <text class="detail-page__value">{{ task.locationName }}</text>
      </view>
      <view class="detail-page__row">
        <text class="detail-page__label">提交要求</text>
        <text class="detail-page__value">{{ task.requirements.join('、') }}</text>
      </view>
    </view>

    <view class="detail-page__card">
      <text class="detail-page__section-title">状态说明</text>
      <text class="detail-page__status-text">
        {{
          hasException
            ? '本任务存在异常记录，请补充申诉材料后等待辅导员复核。'
            : '请在规定时间内完成定位与信息填写，提交后结果会同步到记录与消息页。'
        }}
      </text>
    </view>

    <view class="detail-page__footer">
      <button
        class="detail-page__button"
        :class="{ 'detail-page__button--done': isCompleted }"
        type="primary"
        @click="handlePrimaryAction"
      >
        {{ primaryLabel }}
      </button>
      <button
        v-if="task.type === '实习打卡'"
        class="detail-page__button detail-page__button--secondary"
        @click="uni.navigateTo({ url: `/pages/student/daily-report?task_id=${task.id}` })"
      >
        提交日报
      </button>
    </view>
    </template>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.detail-page {
  height: 100vh;
  box-sizing: border-box;
  background: $page-bg;
}

.detail-page__body {
  box-sizing: border-box;
  width: 100%;
  padding: 24rpx 24rpx calc(24rpx + env(safe-area-inset-bottom));
}

.detail-page__nav {
  position: relative;
  flex-shrink: 0;
  box-sizing: border-box;
  background: $page-bg;
}

.detail-page__nav-row {
  position: absolute;
  right: 0;
  left: 24rpx;
  display: flex;
  align-items: center;
  box-sizing: border-box;
}

.detail-page__back {
  position: relative;
  flex-shrink: 0;
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20rpx;
    height: 20rpx;
    margin-top: -11rpx;
    margin-left: -7rpx;
    border-left: 4rpx solid $text-primary;
    border-bottom: 4rpx solid $text-primary;
    transform: rotate(45deg);
  }
}

.detail-page__nav-title {
  flex: 1;
  min-width: 0;
  color: $text-primary;
  font-size: 34rpx;
  font-weight: 700;
  text-align: center;
}

.detail-page__nav-right {
  flex-shrink: 0;
}

.detail-page__card {
  display: flex;
  box-sizing: border-box;
  width: 100%;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 24rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 18rpx 40rpx rgba(15, 107, 214, 0.08);
}

:deep(.rule-card) {
  box-sizing: border-box;
  width: 100%;
  margin-bottom: 24rpx;
}

.detail-page__header,
.detail-page__row {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
}

.detail-page__title-group {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 12rpx;
}

.detail-page__type {
  color: $primary;
  font-size: 24rpx;
  font-weight: 600;
}

.detail-page__title {
  color: $text-primary;
  font-size: 36rpx;
  font-weight: 700;
}

.detail-page__desc,
.detail-page__status-text,
.detail-page__value {
  color: $text-primary;
  font-size: 28rpx;
  line-height: 1.6;
}

.detail-page__section-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.detail-page__label {
  width: 140rpx;
  flex-shrink: 0;
  color: $text-secondary;
  font-size: 26rpx;
}

.detail-page__footer {
  position: sticky;
  bottom: 0;
  box-sizing: border-box;
  width: 100%;
  padding: 24rpx 0 0;
  background: linear-gradient(180deg, rgba($page-bg, 0) 0%, $page-bg 28%);
}

.detail-page__button {
  box-sizing: border-box;
  width: 100%;
  border: none;
  border-radius: 999rpx;
  background: $primary;
  font-size: 30rpx;
  font-weight: 600;

  & + & {
    margin-top: 16rpx;
  }
}

.detail-page__button--done {
  background: $success;
}

.detail-page__button--secondary {
  background: #fff;
  border: 2rpx solid $primary;
  color: $primary;
}
</style>
