<script setup lang="ts">
import { computed, onMounted } from 'vue'

import { buildAuthIconSrc, type AuthIconName } from '@/utils/auth-icons'

export type IconFontName = AuthIconName

const props = withDefaults(
  defineProps<{
    name: IconFontName
    size?: string
    color?: string
  }>(),
  {
    size: '32rpx',
    color: '#1788ff',
  },
)

const iconSrc = computed(() => buildAuthIconSrc(props.name, props.color))

onMounted(() => {
  console.info('[auth-icon]', 'L1 组件挂载', { name: props.name, mode: 'svg-image' })
  console.info('[auth-icon]', 'L2 图标地址已生成', {
    name: props.name,
    color: props.color,
    srcPrefix: iconSrc.value.slice(0, 48),
  })
  console.info('[auth-icon]', 'L3 就绪', { name: props.name, ok: true })
})
</script>

<template>
  <image
    class="auth-icon"
    :src="iconSrc"
    :style="{ width: size, height: size }"
    mode="aspectFit"
    aria-hidden="true"
  />
</template>

<style scoped lang="scss">
.auth-icon {
  display: inline-block;
  flex-shrink: 0;
  vertical-align: middle;
}
</style>
