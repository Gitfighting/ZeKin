<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { buildCaptchaDisplay, createCaptchaCode, type CaptchaCharView } from '@/utils/captcha'

const props = withDefaults(
  defineProps<{
    width?: string
    height?: string
  }>(),
  {
    width: '200rpx',
    height: '52rpx',
  },
)

const emit = defineEmits<{
  change: [code: string]
}>()

const displayChars = ref<CaptchaCharView[]>([])
const refreshKey = ref(0)

function refresh() {
  const code = createCaptchaCode(4)
  displayChars.value = buildCaptchaDisplay(code)
  refreshKey.value += 1
  emit('change', code)
}

defineExpose({ refresh })

onMounted(refresh)
</script>

<template>
  <view
    class="captcha-wrap"
    :style="{ width: props.width, height: props.height }"
    @click="refresh"
  >
    <view class="captcha-noise" aria-hidden="true">
      <view class="noise-line noise-line-a"></view>
      <view class="noise-line noise-line-b"></view>
      <view class="noise-dot noise-dot-a"></view>
      <view class="noise-dot noise-dot-b"></view>
    </view>
    <view :key="refreshKey" class="captcha-chars">
      <text
        v-for="(item, index) in displayChars"
        :key="`${refreshKey}-${index}`"
        class="captcha-char"
        :style="{
          color: item.color,
          fontSize: `${item.fontSize}rpx`,
          transform: `rotate(${item.rotate}deg) translateY(${item.offsetY}rpx)`,
        }"
      >{{ item.char }}</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.captcha-wrap {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: none;
  flex-shrink: 0;
  box-sizing: border-box;
  margin-left: -5px;
  border-radius: 12rpx;
  border: 2rpx solid #dcecff;
  background: #eef6ff;
}

.captcha-noise {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.noise-line {
  position: absolute;
  height: 2rpx;
  border-radius: 999rpx;
  background: rgba(8, 119, 242, 0.22);
}

.noise-line-a {
  top: 18rpx;
  left: 8rpx;
  right: 12rpx;
  transform: rotate(-8deg);
}

.noise-line-b {
  bottom: 14rpx;
  left: 12rpx;
  right: 8rpx;
  transform: rotate(10deg);
}

.noise-dot {
  position: absolute;
  width: 4rpx;
  height: 4rpx;
  border-radius: 50%;
  background: rgba(100, 116, 139, 0.35);
}

.noise-dot-a {
  top: 10rpx;
  right: 18rpx;
}

.noise-dot-b {
  bottom: 8rpx;
  left: 20rpx;
}

.captcha-chars {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 100%;
  padding: 0 6rpx;
  box-sizing: border-box;
}

.captcha-char {
  flex: 1;
  text-align: center;
  font-weight: 800;
  line-height: 1;
}
</style>
