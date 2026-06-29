<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import { useStudentPageHeroLayout } from '@/composables/useStudentPageHeroLayout'
import { logInfo, logError, showError } from '@/services/feedback'
import VectorIcon from '@/components/VectorIcon.vue'
import { UI_ICONS } from '@/constants/ui-icons'
import { getStudentJoinedGroups, type StudentJoinedGroup } from '@/services/student'

const { brandBarStyle, heroContentStyle, backButtonStyle, navRightStyle } = useStudentPageHeroLayout()

const pageSlogan = '查看自己加入的班级列表'

const loading = ref(false)
const groups = ref<StudentJoinedGroup[]>([])
const searchKeyword = ref('')

const groupCountLabel = computed(() => `已加入 ${groups.value.length} 个班级`)

const filteredGroups = computed(() => {
  const keyword = searchKeyword.value.trim()
  if (!keyword) {
    return groups.value
  }
  return groups.value.filter((group) => group.name.includes(keyword))
})

function handleBack() {
  uni.navigateBack({ delta: 1 })
}

function openJoinClass() {
  uni.navigateTo({ url: '/pages/student/join-class' })
}

function openGroupDetail(group: StudentJoinedGroup) {
  const url = `/pages/student/class-detail?id=${group.id}&name=${encodeURIComponent(group.name)}`
  logInfo('[班级详情] 从我的班级进入', { groupId: group.id, groupName: group.name, url })
  uni.navigateTo({
    url,
    fail: (error) => {
      logError('[班级详情] 页面跳转失败', error)
      showError(error, '无法打开班级详情')
    },
  })
}

onShow(async () => {
  loading.value = true
  try {
    groups.value = await getStudentJoinedGroups()
    logInfo('[我的班级] 页面展示数据', {
      count: groups.value.length,
      groups: groups.value.map((group) => ({
        id: group.id,
        name: group.name,
        checkedInCount: group.checkedInCount,
        publishedCount: group.publishedCount,
        teacherName: group.teacherName,
      })),
    })
  } catch (error) {
    groups.value = []
    logError('[我的班级] 班级列表加载失败', error)
    showError(error, '班级列表加载失败')
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <scroll-view scroll-y class="my-classes-page">
    <view class="student-page-header-block">
      <view class="student-page-hero">
        <view class="student-page-hero__visual">
          <view class="student-page-hero__bg-window">
            <image class="student-page-hero__bg" src="/static/home.png" mode="widthFix" />
          </view>
        </view>

        <view class="my-classes-page__nav-bar" :style="brandBarStyle">
          <view
            class="my-classes-page__back"
            :style="backButtonStyle"
            aria-label="返回"
            @click="handleBack"
          ></view>
          <view class="my-classes-page__nav-spacer" :style="navRightStyle"></view>
        </view>

        <view class="student-page-hero__content" :style="heroContentStyle">
          <text class="student-page-hero__title">我的班级</text>
          <text class="student-page-hero__slogan">{{ pageSlogan }}</text>
        </view>
      </view>

      <view class="my-classes-page__panel student-page-overlap-card">
        <view v-if="loading" class="my-classes-page__panel-inner my-classes-page__panel-inner--state">
          <text class="my-classes-page__state-text">加载中...</text>
        </view>

        <view v-else-if="!groups.length" class="my-classes-page__panel-inner my-classes-page__empty-card">
          <text class="my-classes-page__empty-title">暂未加入任何班级</text>
          <text class="my-classes-page__empty-text">向老师索取邀请码，加入班级后即可接收打卡任务</text>
          <button class="my-classes-page__join-btn" @click="openJoinClass">去加入班级</button>
        </view>

        <view v-else class="my-classes-page__panel-inner">
          <view class="my-classes-page__summary">
            <text class="my-classes-page__summary-text">{{ groupCountLabel }}</text>
            <text class="my-classes-page__summary-link" @click="openJoinClass">加入更多班级</text>
          </view>

          <view class="my-classes-page__search">
            <VectorIcon class="my-classes-page__search-icon" :src="UI_ICONS.search" size="32rpx" />
            <input
              v-model="searchKeyword"
              class="my-classes-page__search-input"
              placeholder="搜索班级名称"
              confirm-type="search"
            />
            <view v-if="searchKeyword" class="my-classes-page__search-clear" @click="searchKeyword = ''">×</view>
          </view>
        </view>
      </view>
    </view>

    <view class="student-page-content-sheet my-classes-page__sheet">
      <view v-if="groups.length" class="my-classes-page__list">
        <view v-if="!filteredGroups.length" class="my-classes-page__search-empty">
          <text class="my-classes-page__search-empty-text">未找到匹配的班级</text>
        </view>

        <view
          v-for="group in filteredGroups"
          :key="group.id"
          class="my-classes-page__card"
          @click="openGroupDetail(group)"
        >
          <VectorIcon class="my-classes-page__card-icon" :src="UI_ICONS.classes" size="48rpx" />
          <view class="my-classes-page__card-body">
            <text class="my-classes-page__card-name">{{ group.name }}</text>
            <view class="my-classes-page__card-footer">
              <text class="my-classes-page__card-meta">
                {{ group.teacherName ? `教师：${group.teacherName}` : '教师：--' }}
              </text>
              <text class="my-classes-page__card-record">
                记录 {{ group.checkedInCount ?? 0 }}/{{ group.publishedCount ?? 0 }}
              </text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </scroll-view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.my-classes-page {
  min-height: 100vh;
  background: $page-bg;
}

.my-classes-page__nav-bar {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24rpx 0 32rpx;
  box-sizing: border-box;
}

.my-classes-page__back {
  position: relative;
  flex-shrink: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.28);
  box-shadow: 0 4rpx 16rpx rgba(15, 60, 120, 0.12);

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20rpx;
    height: 20rpx;
    margin-top: -11rpx;
    margin-left: -5rpx;
    border-left: 4rpx solid #fff;
    border-bottom: 4rpx solid #fff;
    transform: rotate(45deg);
  }
}

.my-classes-page__nav-spacer {
  flex-shrink: 0;
}

.my-classes-page__panel {
  padding: 8rpx 24rpx 24rpx;
}

.my-classes-page__panel-inner {
  min-height: 0;
}

.my-classes-page__panel-inner--state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 120rpx;
}

.my-classes-page__state-text {
  color: $text-secondary;
  font-size: 26rpx;
}

.my-classes-page__sheet {
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
}

.my-classes-page__summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
  min-height: 72rpx;
}

.my-classes-page__search {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-top: 8rpx;
  height: 80rpx;
  padding: 0 24rpx;
  border: 2rpx solid rgba($primary, 0.08);
  border-radius: 999rpx;
  background: #f5f8ff;
}

.my-classes-page__search-icon {
  flex-shrink: 0;
  opacity: 0.55;
}

.my-classes-page__search-input {
  flex: 1;
  min-width: 0;
  height: 80rpx;
  color: $text-primary;
  font-size: 28rpx;
}

.my-classes-page__search-clear {
  flex-shrink: 0;
  width: 40rpx;
  height: 40rpx;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.08);
  color: $text-secondary;
  font-size: 28rpx;
  line-height: 40rpx;
  text-align: center;
}

.my-classes-page__search-empty {
  padding: 48rpx 0;
  text-align: center;
}

.my-classes-page__search-empty-text {
  color: $text-secondary;
  font-size: 26rpx;
}

.my-classes-page__summary-text {
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 600;
}

.my-classes-page__summary-link {
  color: $primary;
  font-size: 24rpx;
}

.my-classes-page__empty-card {
  text-align: center;
  padding: 16rpx 8rpx 8rpx;
}

.my-classes-page__empty-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $text-primary;
}

.my-classes-page__empty-text {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  line-height: 1.6;
  color: $text-secondary;
}

.my-classes-page__join-btn {
  margin-top: 28rpx;
  border-radius: 999rpx;
  background: $primary;
  color: #fff;
  font-size: 28rpx;
}

.my-classes-page__list {
  display: flex;
  flex-direction: column;
  gap: 18rpx;
  padding: 0 24rpx 24rpx;
}

.my-classes-page__card {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx;
  border-radius: 22rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.my-classes-page__card:active {
  opacity: 0.92;
}

.my-classes-page__card-icon {
  display: flex;
  width: 88rpx;
  height: 88rpx;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 24rpx;
  background: linear-gradient(180deg, #ffb347 0%, #ff9f1a 100%);
}

.my-classes-page__card-body {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  min-width: 0;
}

.my-classes-page__card-name {
  font-size: 30rpx;
  font-weight: 700;
  color: $text-primary;
}

.my-classes-page__card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.my-classes-page__card-meta {
  min-width: 0;
  flex: 1;
  font-size: 24rpx;
  color: $text-secondary;
}

.my-classes-page__card-record {
  flex-shrink: 0;
  font-size: 24rpx;
  color: $primary;
  font-weight: 600;
}
</style>

<style lang="scss">
@use '@/styles/student-page-hero.scss';
</style>
