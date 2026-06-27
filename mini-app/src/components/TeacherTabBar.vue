<script setup lang="ts">
const props = defineProps<{
  active: 'home' | 'tasks' | 'groups' | 'profile'
}>()

const items = [
  {
    key: 'home' as const,
    label: '首页',
    path: '/pages/teacher/home',
    icon: '/static/tabbar/home.png',
    activeIcon: '/static/tabbar/home-active.png',
  },
  {
    key: 'tasks' as const,
    label: '考勤',
    path: '/pages/teacher/tasks',
    icon: '/static/tabbar/tasks.png',
    activeIcon: '/static/tabbar/tasks-active.png',
  },
  {
    key: 'groups' as const,
    label: '班级',
    path: '/pages/teacher/groups',
    icon: '/static/tabbar/messages.png',
    activeIcon: '/static/tabbar/messages-active.png',
  },
  {
    key: 'profile' as const,
    label: '我的',
    path: '/pages/teacher/profile',
    icon: '/static/tabbar/profile.png',
    activeIcon: '/static/tabbar/profile-active.png',
  },
]

function navigate(path: string, key: typeof props.active) {
  if (key === props.active || typeof uni === 'undefined') {
    return
  }
  uni.reLaunch({ url: path })
}
</script>

<template>
  <view class="teacher-tab-bar">
    <view class="teacher-tab-bar__halo" aria-hidden="true"></view>
    <view class="teacher-tab-bar__inner">
      <view
        v-for="item in items"
        :key="item.key"
        class="teacher-tab-bar__item"
        @tap="navigate(item.path, item.key)"
      >
        <image
          class="teacher-tab-bar__icon"
          :src="active === item.key ? item.activeIcon : item.icon"
          mode="aspectFit"
        />
        <text class="teacher-tab-bar__label" :class="{ 'teacher-tab-bar__label--active': active === item.key }">
          {{ item.label }}
        </text>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.teacher-tab-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 1000;
  padding-bottom: env(safe-area-inset-bottom);
  background: #fdfdfd;
  border-top: 1rpx solid rgba(15, 23, 42, 0.03);
  box-shadow:
    0 -28rpx 56rpx rgba(22, 119, 255, 0.1),
    0 -14rpx 32rpx rgba(22, 119, 255, 0.07),
    0 -6rpx 18rpx rgba(15, 23, 42, 0.04);
}

.teacher-tab-bar__halo {
  position: absolute;
  top: -48rpx;
  right: 0;
  left: 0;
  height: 48rpx;
  background: linear-gradient(
    180deg,
    rgba(243, 248, 255, 0) 0%,
    rgba(22, 119, 255, 0.05) 45%,
    rgba(255, 255, 255, 0.92) 100%
  );
  pointer-events: none;
}

.teacher-tab-bar__inner {
  position: relative;
  z-index: 1;
  display: flex;
  height: $tab-bar-height;
  align-items: stretch;
}

.teacher-tab-bar__item {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
}

.teacher-tab-bar__icon {
  width: 48rpx;
  height: 48rpx;
}

.teacher-tab-bar__label {
  color: $text-secondary;
  font-size: 26rpx;
  line-height: 1.2;
  letter-spacing: 1px;
}

.teacher-tab-bar__label--active {
  color: $primary;
  font-weight: 600;
}
</style>
