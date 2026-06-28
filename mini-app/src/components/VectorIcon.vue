<script setup lang="ts">
withDefaults(
  defineProps<{
    src: string
    size?: string
  }>(),
  {
    size: '32rpx',
  },
)
</script>

<template>
  <image
    class="vector-icon"
    :src="src"
    mode="aspectFit"
    :style="{ width: size, height: size }"
  />
</template>

<style scoped lang="scss">
.vector-icon {
  display: block;
  flex-shrink: 0;
}
</style>
