<script setup lang="ts">
import { onMounted } from 'vue'

import {
  formatUnreadBadge,
  refreshStudentUnreadMessageCount,
  studentUnreadMessageCount,
} from '@/composables/useStudentUnreadMessages'

const props = defineProps<{
  active: 'home' | 'tasks' | 'messages' | 'profile'
}>()

const items = [
  {
    key: 'home' as const,
    label: '首页',
    path: '/pages/student/home',
    icon: '/static/tabbar/home.png',
    activeIcon: '/static/tabbar/home-active.png',
  },
  {
    key: 'tasks' as const,
    label: '打卡任务',
    path: '/pages/student/tasks',
    icon: '/static/tabbar/tasks.png',
    activeIcon: '/static/tabbar/tasks-active.png',
  },
  {
    key: 'messages' as const,
    label: '消息',
    path: '/pages/student/messages',
    icon: '/static/tabbar/messages.png',
    activeIcon: '/static/tabbar/messages-active.png',
  },
  {
    key: 'profile' as const,
    label: '我的',
    path: '/pages/student/profile',
    icon: '/static/tabbar/profile.png',
    activeIcon: '/static/tabbar/profile-active.png',
  },
]

function switchTab(path: string, key: typeof props.active) {
  if (key === props.active) {
    return
  }
  uni.switchTab({ url: path })
}

onMounted(() => {
  void refreshStudentUnreadMessageCount()
})
</script>

<template>
  <view class="student-tab-bar">
    <view class="student-tab-bar__inner">
      <view
        v-for="item in items"
        :key="item.key"
        class="student-tab-bar__item"
        @tap="switchTab(item.path, item.key)"
      >
        <view class="student-tab-bar__icon-wrap">
          <image
            class="student-tab-bar__icon"
            :src="active === item.key ? item.activeIcon : item.icon"
            mode="aspectFit"
          />
          <view
            v-if="item.key === 'messages' && studentUnreadMessageCount > 0"
            class="student-tab-bar__badge"
          >
            <text class="student-tab-bar__badge-text">{{ formatUnreadBadge(studentUnreadMessageCount) }}</text>
          </view>
        </view>
        <text class="student-tab-bar__label" :class="{ 'student-tab-bar__label--active': active === item.key }">
          {{ item.label }}
        </text>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.student-tab-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 1000;
  padding-bottom: env(safe-area-inset-bottom);
  background: #ffffff;
  border-top: 1rpx solid rgba(15, 23, 42, 0.06);
  box-shadow: 0 -4rpx 16rpx rgba(15, 23, 42, 0.04);
}

.student-tab-bar__inner {
  display: flex;
  height: $tab-bar-height;
  align-items: stretch;
}

.student-tab-bar__item {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4rpx;
}

.student-tab-bar__icon-wrap {
  position: relative;
  width: 54rpx;
  height: 54rpx;
}

.student-tab-bar__icon {
  display: block;
  width: 54rpx;
  height: 54rpx;
}

.student-tab-bar__badge {
  position: absolute;
  top: -6rpx;
  right: -14rpx;
  min-width: 30rpx;
  height: 30rpx;
  padding: 0 8rpx;
  border: 2rpx solid #ffffff;
  border-radius: 999rpx;
  background: #ff4d4f;
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.student-tab-bar__badge-text {
  color: #fff;
  font-size: 18rpx;
  font-weight: 700;
  line-height: 1;
}

.student-tab-bar__label {
  color: #667085;
  font-size: 22rpx;
  font-weight: 500;
  line-height: 1.2;
}

.student-tab-bar__label--active {
  color: #1677ff;
  font-weight: 600;
}
</style>
