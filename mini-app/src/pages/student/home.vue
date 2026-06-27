<script setup lang="ts">

import { onShow } from '@dcloudio/uni-app'

import { computed, ref } from 'vue'

import HomeTaskCard from '@/components/HomeTaskCard.vue'
import StudentTabBar from '@/components/StudentTabBar.vue'
import { refreshStudentUnreadMessageCount } from '@/composables/useStudentUnreadMessages'

import { readStoredSession } from '@/services/auth'

import { logInfo, showError } from '@/services/feedback'

import { getStudentProfile, getStudentTasks, type StudentTask } from '@/services/student'



const dailyQuote = '木叶飞舞之处，火亦生生不息'



const quickEntries = [

  {

    key: 'tasks',

    label: '打卡任务',

    sub: '立即完成',

    path: '/pages/student/tasks',

    tone: 'blue',

    icon: '📅',

  },

  {

    key: 'records',

    label: '打卡记录',

    sub: '查看历史',

    path: '/pages/student/records',

    tone: 'green',

    icon: '📋',

  },

  {

    key: 'join',

    label: '加入班群',

    sub: '输入邀请码',

    path: '/pages/student/join-class',

    tone: 'purple',

    icon: '👥',

  },

  {

    key: 'classes',

    label: '我的班级',

    sub: '已加入班级',

    path: '/pages/student/my-classes',

    tone: 'orange',

    icon: '🏫',

  },

] as const

/** 首页「今天的任务」仅展示一条 */
const SHOW_HOME_TODAY_TASKS = true

const displayName = ref('同学')

const todayTasks = ref<StudentTask[]>([])

const loading = ref(false)

const featuredTask = computed(() => {
  const actionable = todayTasks.value.find(
    (task) => task.status === 'in-progress' || task.status === 'pending',
  )
  return actionable ?? todayTasks.value[0] ?? null
})

const brandBarStyle = ref<Record<string, string>>({
  top: '48px',
  height: '32px',
})

const heroContentStyle = ref<Record<string, string>>({
  paddingTop: '112rpx',
  paddingLeft: '32rpx',
  paddingRight: '32rpx',
})

function syncHeroLayout() {
  if (typeof uni === 'undefined') {
    return
  }

  try {
    const menuButton = uni.getMenuButtonBoundingClientRect()
    brandBarStyle.value = {
      top: `${menuButton.top}px`,
      height: `${menuButton.height}px`,
    }
    heroContentStyle.value = {
      paddingTop: `${menuButton.bottom + 12}px`,
      paddingLeft: '32rpx',
      paddingRight: '32rpx',
    }
  } catch {
    // 非小程序环境保留默认占位
  }
}



const greetingPrefix = computed(() => {

  const hour = new Date().getHours()

  if (hour < 12) {

    return '上午好'

  }

  if (hour < 18) {

    return '下午好'

  }

  return '晚上好'

})



function openQuickEntry(path: string) {

  if (path.includes('/pages/student/tasks') || path.includes('/pages/student/home')) {

    uni.switchTab({ url: path })

    return

  }

  uni.navigateTo({ url: path })

}



function openTask(task: StudentTask) {

  uni.navigateTo({

    url: `/pages/student/task-detail?id=${task.id}`,

  })

}



function openAllTasks() {

  uni.switchTab({ url: '/pages/student/tasks' })

}



onShow(async () => {

  syncHeroLayout()

  loading.value = true

  void refreshStudentUnreadMessageCount()

  const session = readStoredSession()

  if (session?.user.displayName) {

    displayName.value = session.user.displayName.replace(/^用户/, '') || session.user.displayName

  }



  try {

    const [tasks, profile] = await Promise.all([

      getStudentTasks(),

      getStudentProfile().catch(() => null),

    ])

    if (profile?.realName) {

      displayName.value = profile.realName

    }

    todayTasks.value = tasks.filter(

      (task) => task.status === 'in-progress' || task.status === 'pending' || task.status === 'normal',

    )

    logInfo('学生首页加载成功', { taskCount: todayTasks.value.length })

  } catch (error) {

    todayTasks.value = []

    showError(error, '首页数据加载失败')

  } finally {

    loading.value = false

  }

})

</script>



<template>

  <view class="student-tab-page">

  <scroll-view scroll-y class="home-page student-tab-page__scroll">

    <view class="home-page__hero">

      <view class="home-page__hero-bg-box" aria-hidden="true">
        <image class="home-page__hero-bg" src="/static/student-home-hero.png" mode="aspectFill" />
      </view>

      <view class="home-page__hero-mask"></view>

      <view class="home-page__brand-bar" :style="brandBarStyle">
        <text class="home-page__brand">知勤</text>
      </view>

      <view class="home-page__hero-content" :style="heroContentStyle">

        <text class="home-page__greeting">{{ greetingPrefix }}，{{ displayName }} 👋</text>

        <text class="home-page__slogan">诚信打卡，安全成长</text>

      </view>

    </view>



    <view class="home-page__toolbar home-page__toolbar--four">

      <view

        v-for="entry in quickEntries"

        :key="entry.key"

        class="home-page__tool"

        @click="openQuickEntry(entry.path)"

      >

        <view class="home-page__tool-icon" :class="`home-page__tool-icon--${entry.tone}`">

          <text>{{ entry.icon }}</text>

        </view>

        <text class="home-page__tool-label">{{ entry.label }}</text>

        <text class="home-page__tool-sub">{{ entry.sub }}</text>

      </view>

    </view>



    <view v-if="SHOW_HOME_TODAY_TASKS" class="home-page__section">

      <view class="home-page__tasks-card">

        <view class="home-page__section-head">

          <view class="home-page__section-title-wrap">

            <text class="home-page__section-icon">📅</text>

            <text class="home-page__section-title">今天的任务</text>

          </view>

          <text class="home-page__section-link" @click.stop="openAllTasks">全部任务 ›</text>

        </view>



        <view v-if="loading" class="home-page__tasks-empty">加载中...</view>

        <view v-else-if="!featuredTask" class="home-page__tasks-empty">今日暂无打卡任务</view>

        <HomeTaskCard v-else embedded :task="featuredTask" @click="openTask" />

      </view>

    </view>



    <view class="home-page__quote-spacer" aria-hidden="true"></view>

  </scroll-view>

  <view class="home-page__quote home-page__quote--pinned">
    <image
      class="home-page__quote-bg"
      src="/static/man-blue-daily.png"
      mode="aspectFill"
      aria-hidden="true"
    />
    <view class="home-page__quote-copy">
      <text class="home-page__quote-title">每日一言</text>
      <text class="home-page__quote-text">{{ dailyQuote }}</text>
    </view>
  </view>

  <StudentTabBar active="home" />

  </view>

</template>



<style scoped lang="scss">

@use '@/styles/tokens.scss' as *;



.home-page {
  background: $page-bg;
}



.home-page__hero {

  position: relative;

  height: calc(420rpx + 30px);

  overflow: hidden;

}



.home-page__hero-bg-box {

  position: absolute;

  right: 0;

  bottom: 0;

  left: 0;

  height: 175%;

}



.home-page__hero-bg {

  width: 100%;

  height: 100%;

}



.home-page__hero-mask {

  position: absolute;

  inset: 0;

  background: linear-gradient(180deg, rgba(15, 120, 255, 0.1) 0%, rgba(15, 120, 255, 0.38) 100%);

}



.home-page__hero-content {

  position: relative;

  z-index: 2;

  display: flex;

  flex-direction: column;

  gap: 12rpx;

  color: #fff;

}



.home-page__brand-bar {

  position: absolute;

  left: 0;

  right: 0;

  z-index: 3;

  display: flex;

  align-items: center;

  padding-left: 32rpx;

  box-sizing: border-box;

}



.home-page__brand {

  font-size: 42rpx;

  font-weight: 700;

  color: #fff;

  line-height: 1;

}



.home-page__greeting {

  margin-top: 8rpx;

  font-size: 52rpx;

  font-weight: 700;

}



.home-page__slogan {

  font-size: 30rpx;

  opacity: 0.92;

}



.home-page__toolbar {

  display: grid;

  grid-template-columns: repeat(3, minmax(0, 1fr));

  gap: 16rpx;

  margin: -56rpx 24rpx 0;

  padding: 28rpx 20rpx;

  border-radius: 28rpx;

  background: $card-bg;

  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.1);

  position: relative;

  z-index: 3;

}

.home-page__toolbar--four {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12rpx;
  padding: 28rpx 16rpx;
}



.home-page__tool {

  display: flex;

  flex-direction: column;

  align-items: center;

  gap: 10rpx;

}



.home-page__tool-icon {

  display: flex;

  width: 96rpx;

  height: 96rpx;

  align-items: center;

  justify-content: center;

  border-radius: 28rpx;

  font-size: 40rpx;

}



.home-page__tool-icon--blue {

  background: linear-gradient(180deg, #4ca3ff 0%, #1677ff 100%);

}



.home-page__tool-icon--green {

  background: linear-gradient(180deg, #5fe08d 0%, #20c55a 100%);

}



.home-page__tool-icon--purple {

  background: linear-gradient(180deg, #b794ff 0%, #7c3aed 100%);

}

.home-page__tool-icon--orange {
  background: linear-gradient(180deg, #ffb347 0%, #ff9f1a 100%);
}

.home-page__tool-label {

  color: $text-primary;

  font-size: 24rpx;

  font-weight: 700;

  text-align: center;

}



.home-page__tool-sub {

  color: $text-secondary;

  font-size: 20rpx;

  text-align: center;

}



.home-page__section {

  margin: 28rpx 24rpx 0;

}



.home-page__tasks-card {

  padding: 28rpx 20rpx;

  border-radius: 28rpx;

  background: $card-bg;

  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.1);

}



.home-page__section-head {

  display: flex;

  align-items: center;

  justify-content: space-between;

  margin-bottom: 20rpx;

  padding-bottom: 20rpx;

  border-bottom: 1rpx solid rgba(15, 23, 42, 0.06);

}



.home-page__section-title-wrap {

  display: flex;

  align-items: center;

  gap: 10rpx;

}



.home-page__section-icon {

  font-size: 34rpx;

}



.home-page__section-title {

  color: $text-primary;

  font-size: 34rpx;

  font-weight: 700;

}



.home-page__section-link {

  color: $text-secondary;

  font-size: 26rpx;

}



.home-page__tasks-empty {

  padding: 8rpx 0;

  color: $text-secondary;

  font-size: 26rpx;

  text-align: center;

}



.home-page__task-list {

  display: flex;

  flex-direction: column;

  gap: 18rpx;

}



.home-page__empty {

  padding: 40rpx 24rpx;

  border-radius: 24rpx;

  background: $card-bg;

  color: $text-secondary;

  font-size: 26rpx;

  text-align: center;

}



.home-page__quote {
  position: relative;
  overflow: hidden;
  min-height: 200rpx;
  margin: 28rpx 24rpx 0;
  padding: 28rpx 20rpx;
  border-radius: 28rpx;
  background: $card-bg;
  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.1);
}

.home-page__quote--pinned {
  position: fixed;
  right: 24rpx;
  left: 24rpx;
  bottom: calc(#{$tab-bar-height} + env(safe-area-inset-bottom) + 24rpx);
  z-index: 900;
  margin: 0;
}

.home-page__quote-spacer {
  height: calc(200rpx + 56rpx + 24rpx + 320rpx);
}

.home-page__quote-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
}

.home-page__quote-copy {
  position: relative;
  z-index: 1;
  display: flex;
  max-width: 58%;
  flex-direction: column;
  gap: calc(10rpx + 2px);
}



.home-page__quote-title {

  color: $primary;

  font-size: 30rpx;

  font-weight: 700;

}



.home-page__quote-text {

  color: $text-primary;

  font-size: 26rpx;

  line-height: calc(1.7em + 2px);

}

</style>


