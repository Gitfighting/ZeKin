<script setup lang="ts">
const props = defineProps<{
  active: 'home' | 'tasks' | 'groups' | 'profile'
}>()

const items = [
  { key: 'home', label: '首页', badge: 'H', path: '/pages/teacher/home' },
  { key: 'tasks', label: '任务', badge: 'T', path: '/pages/teacher/tasks' },
  { key: 'groups', label: '班级', badge: 'G', path: '/pages/teacher/groups' },
  { key: 'profile', label: '我的', badge: 'M', path: '/pages/teacher/profile' },
] as const

function navigate(path: string, key: typeof props.active) {
  if (key === props.active || typeof uni === 'undefined') {
    return
  }

  uni.reLaunch({ url: path })
}
</script>

<template>
  <view class="teacher-tab-bar">
    <view
      v-for="item in items"
      :key="item.key"
      :class="['tab-item', { active: item.key === active }]"
      @click="navigate(item.path, item.key)"
    >
      <view class="tab-badge">{{ item.badge }}</view>
      <text class="tab-label">{{ item.label }}</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.teacher-tab-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12rpx;
  padding: 18rpx 24rpx calc(18rpx + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.98);
  border-top: 1rpx solid rgba(22, 119, 255, 0.12);
  box-shadow: 0 -10rpx 30rpx rgba(15, 23, 42, 0.06);
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  color: $text-muted;
}

.tab-item.active {
  color: $primary;
}

.tab-badge {
  width: 52rpx;
  height: 52rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef5ff;
  font-size: 22rpx;
  font-weight: 700;
}

.tab-item.active .tab-badge {
  background: linear-gradient(180deg, #1677ff 0%, #4aa7ff 100%);
  color: #fff;
}

.tab-label {
  font-size: 22rpx;
  line-height: 1;
}
</style>
