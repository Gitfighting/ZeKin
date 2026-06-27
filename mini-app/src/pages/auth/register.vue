<script setup lang="ts">
import { onLoad } from '@dcloudio/uni-app'

/** 兼容旧链接：注册与登录为同一页，仅切换中间表单 */
onLoad(() => {
  uni.redirectTo({ url: '/pages/auth/login?tab=register' })
})
</script>

<template>
  <view></view>
</template>
