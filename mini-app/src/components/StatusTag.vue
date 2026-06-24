<script setup lang="ts">
import { computed } from 'vue'

import type { StatusTone } from '@/services/student'

const props = defineProps<{
  status: StatusTone
}>()

const labelMap: Record<StatusTone, string> = {
  normal: '正常',
  'in-progress': '进行中',
  pending: '待处理',
  exception: '异常',
  ended: '已结束',
}

const className = computed(() => `tag--${props.status}`)
const label = computed(() => labelMap[props.status])
</script>

<template>
  <text class="tag" :class="className">
    {{ label }}
  </text>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 116rpx;
  padding: 10rpx 20rpx;
  border-radius: 999rpx;
  font-size: 24rpx;
  font-weight: 600;
}

.tag--normal {
  background: rgba($success, 0.12);
  color: $success;
}

.tag--in-progress {
  background: rgba($primary, 0.12);
  color: $primary;
}

.tag--pending {
  background: rgba($warning, 0.12);
  color: $warning;
}

.tag--exception {
  background: rgba($danger, 0.12);
  color: $danger;
}

.tag--ended {
  background: rgba(#667085, 0.12);
  color: #667085;
}
</style>
