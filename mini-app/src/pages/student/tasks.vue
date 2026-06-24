<script setup lang="ts">
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import TaskCard from '@/components/TaskCard.vue'
import { demoStudentTasks, getStudentTasks, type StudentTask } from '@/services/student'

type FilterKey = 'all' | 'in-progress' | 'pending' | 'exception'

const filters: { key: FilterKey; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'in-progress', label: '进行中' },
  { key: 'pending', label: '待处理' },
  { key: 'exception', label: '异常' },
]

const activeFilter = ref<FilterKey>('all')
const tasks = ref<StudentTask[]>(demoStudentTasks)

const visibleTasks = computed(() => {
  if (activeFilter.value === 'all') {
    return tasks.value
  }
  return tasks.value.filter((task) => task.status === activeFilter.value)
})

function openTask(task: StudentTask) {
  uni.navigateTo({
    url: `/pages/student/task-detail?id=${task.id}`,
  })
}

onShow(async () => {
  try {
    tasks.value = await getStudentTasks()
  } catch {
    tasks.value = demoStudentTasks
  }
})
</script>

<template>
  <scroll-view scroll-y class="tasks-page">
    <view class="tasks-page__hero">
      <text class="tasks-page__title">打卡任务</text>
      <text class="tasks-page__subtitle">按时完成课堂、宿舍和实践签到</text>
    </view>

    <view class="tasks-page__filters">
      <view
        v-for="item in filters"
        :key="item.key"
        class="tasks-page__filter"
        :class="{ 'tasks-page__filter--active': activeFilter === item.key }"
        @click="activeFilter = item.key"
      >
        <text>{{ item.label }}</text>
      </view>
    </view>

    <view class="tasks-page__list">
      <TaskCard v-for="task in visibleTasks" :key="task.id" :task="task" @action="openTask" @click="openTask" />
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.tasks-page {
  min-height: 100vh;
  background: $page-bg;
}

.tasks-page__hero {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding: 112rpx 28rpx 34rpx;
  background: $mobile-gradient;
}

.tasks-page__title,
.tasks-page__subtitle {
  color: #ffffff;
}

.tasks-page__title {
  font-size: 48rpx;
  font-weight: 700;
}

.tasks-page__subtitle {
  font-size: 28rpx;
  opacity: 0.95;
}

.tasks-page__filters {
  display: flex;
  gap: 16rpx;
  padding: 0 24rpx;
  margin-top: -34rpx;
  overflow-x: auto;
}

.tasks-page__filter {
  flex-shrink: 0;
  min-width: 132rpx;
  height: 72rpx;
  line-height: 72rpx;
  border-radius: 999rpx;
  background: rgba(#ffffff, 0.82);
  color: $text-secondary;
  text-align: center;
  font-size: 26rpx;
  font-weight: 600;
  box-shadow: 0 18rpx 36rpx rgba(15, 107, 214, 0.08);
}

.tasks-page__filter--active {
  background: $primary;
  color: #ffffff;
}

.tasks-page__list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  padding: 24rpx;
}
</style>
