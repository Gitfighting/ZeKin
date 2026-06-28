<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'

import { useStudentPageHeroLayout } from '@/composables/useStudentPageHeroLayout'
import { openTeacherQuickEntry, TEACHER_QUICK_ENTRIES } from '@/constants/teacher-quick-entries'

withDefaults(
  defineProps<{
    slogan?: string
    title?: string
    showQuickEntries?: boolean
  }>(),
  {
    slogan: '',
    title: '',
    showQuickEntries: false,
  },
)

const { brandBarStyle, heroContentStyle } = useStudentPageHeroLayout()

onShow(() => {
  if (typeof uni !== 'undefined') {
    uni.setNavigationBarTitle({ title: '' })
  }
})
</script>

<template>
  <view
    class="home-page__hero-block"
    :class="{ 'home-page__hero-block--subpage': !showQuickEntries }"
  >
    <view class="home-page__hero">
      <view class="home-page__hero-visual" aria-hidden="true">
        <view class="home-page__hero-bg-window">
          <image class="home-page__hero-bg" src="/static/home.png" mode="widthFix" />
        </view>
      </view>

      <view class="home-page__brand-bar" :style="brandBarStyle">
        <text class="home-page__brand">知勤</text>
      </view>

      <view class="home-page__hero-content" :style="heroContentStyle">
        <text class="home-page__greeting">{{ title }}</text>
        <text v-if="slogan" class="home-page__slogan">{{ slogan }}</text>
      </view>
    </view>

    <view
      v-if="showQuickEntries"
      class="home-page__toolbar-card home-page__panel-card home-page__toolbar home-page__toolbar--four"
    >
      <view
        v-for="entry in TEACHER_QUICK_ENTRIES"
        :key="entry.key"
        class="home-page__tool"
        @click="openTeacherQuickEntry(entry.path)"
      >
        <view class="home-page__tool-icon home-page__tool-icon--image">
          <image class="home-page__tool-icon-img" :src="entry.iconSrc" mode="aspectFit" />
        </view>
        <text class="home-page__tool-label">{{ entry.label }}</text>
        <text class="home-page__tool-sub">{{ entry.sub }}</text>
      </view>
    </view>

    <view class="home-page__content-sheet">
      <view class="home-page__sheet-body">
        <slot />
      </view>
    </view>
  </view>
</template>

<style lang="scss">
@use '@/styles/home-hero.scss';
</style>
