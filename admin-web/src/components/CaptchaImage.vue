<script setup lang="ts">
defineOptions({ name: 'CaptchaImage' })

import { onMounted, ref } from 'vue'

import { buildCaptchaDisplay, createCaptchaCode, type CaptchaCharView } from '../utils/captcha'

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
  <button type="button" class="captcha-image" aria-label="点击刷新验证码" @click="refresh">
    <span class="captcha-image__noise" aria-hidden="true">
      <span class="captcha-image__line captcha-image__line--a"></span>
      <span class="captcha-image__line captcha-image__line--b"></span>
    </span>
    <span :key="refreshKey" class="captcha-image__chars">
      <span
        v-for="(item, index) in displayChars"
        :key="`${refreshKey}-${index}`"
        class="captcha-image__char"
        :style="{
          color: item.color,
          fontSize: `${item.fontSize}px`,
          transform: `rotate(${item.rotate}deg) translateY(${item.offsetY}px)`,
        }"
      >{{ item.char }}</span>
    </span>
  </button>
</template>

<style scoped lang="scss">
.captcha-image {
  flex: none;
  width: 112px;
  height: 44px;
  padding: 0;
  border: 1px solid #dcecff;
  border-radius: 10px;
  background: linear-gradient(180deg, #f3f8ff 0%, #e8f2ff 100%);
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.captcha-image__noise {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.captcha-image__line {
  position: absolute;
  height: 1px;
  border-radius: 999px;
  background: rgba(8, 119, 242, 0.22);
}

.captcha-image__line--a {
  top: 14px;
  left: 8px;
  right: 10px;
  transform: rotate(-8deg);
}

.captcha-image__line--b {
  bottom: 12px;
  left: 10px;
  right: 8px;
  transform: rotate(10deg);
}

.captcha-image__chars {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 100%;
  padding: 0 8px;
  box-sizing: border-box;
}

.captcha-image__char {
  flex: 1;
  text-align: center;
  font-weight: 800;
  line-height: 1;
  user-select: none;
}
</style>
