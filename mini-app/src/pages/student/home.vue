<script setup lang="ts">

import { onShow } from '@dcloudio/uni-app'

import { computed, ref } from 'vue'

import HomeTaskCard from '@/components/HomeTaskCard.vue'
import StudentTabBar from '@/components/StudentTabBar.vue'
import { refreshStudentUnreadMessageCount } from '@/composables/useStudentUnreadMessages'

import { readStoredSession } from '@/services/auth'

import { logInfo, showError } from '@/services/feedback'

import { getStudentProfile, getStudentTasks, type StudentTask } from '@/services/student'



const dailyQuoteLine1 = '吾日三省吾身'
const dailyQuoteLine2 = '「省」「悟」'



interface HomeQuickEntry {
  key: 'tasks' | 'records' | 'join' | 'classes'
  label: string
  sub: string
  path: string
  iconSrc: string
}

const quickEntries: HomeQuickEntry[] = [
  {
    key: 'tasks',
    label: '打卡任务',
    sub: '立即完成',
    path: '/pages/student/tasks',
    iconSrc: '/static/home-icons/task-calendar.svg',
  },
  {
    key: 'records',
    label: '打卡记录',
    sub: '查看历史',
    path: '/pages/student/records',
    iconSrc: '/static/home-icons/task-records.svg',
  },
  {
    key: 'join',
    label: '加入班群',
    sub: '输入邀请码',
    path: '/pages/student/join-class',
    iconSrc: '/static/home-icons/join-class.svg',
  },
  {
    key: 'classes',
    label: '我的班级',
    sub: '已加入班级',
    path: '/pages/student/my-classes',
    iconSrc: '/static/home-icons/my-classes.svg',
  },
]

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
  logInfo('打开任务详情', { taskId: task.id, title: task.title })
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

    logInfo('学生首页加载成功', {
      taskCount: todayTasks.value.length,
      featuredTaskId: featuredTask.value?.id,
      featuredStatus: featuredTask.value?.status,
      tasks: todayTasks.value.map((task) => ({
        id: task.id,
        title: task.title,
        status: task.status,
      })),
    })

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

    <view class="home-page__hero-block">
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
          <text class="home-page__greeting">{{ greetingPrefix }}，{{ displayName }}</text>
          <text class="home-page__slogan">知以明志，勤以立身</text>
        </view>
      </view>

      <view class="home-page__toolbar-card home-page__panel-card home-page__toolbar home-page__toolbar--four">
        <view
          v-for="entry in quickEntries"
          :key="entry.key"
          class="home-page__tool"
          @click="openQuickEntry(entry.path)"
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
          <view v-if="SHOW_HOME_TODAY_TASKS" class="home-page__section home-page__section--in-sheet">
            <view class="home-page__panel-card">
              <view class="home-page__section-head">
                <view class="home-page__section-title-wrap">
                  <image
                    class="home-page__section-icon-img"
                    src="/static/home-icons/task-calendar.svg"
                    mode="aspectFit"
                  />
                  <text class="home-page__section-title">今天的任务</text>
                </view>
                <text class="home-page__section-link" @click.stop="openAllTasks">全部任务 ›</text>
              </view>

              <view v-if="loading" class="home-page__tasks-empty">加载中...</view>
              <view v-else-if="!featuredTask" class="home-page__tasks-empty">今日暂无打卡任务</view>
              <view
                v-else
                class="home-page__task-entry"
                hover-class="home-page__task-entry--active"
                @tap="openTask(featuredTask)"
              >
                <HomeTaskCard embedded :task="featuredTask" />
              </view>
            </view>
          </view>

          <view class="home-page__section home-page__section--in-sheet">
            <view class="home-page__panel-card home-page__quote-card">
              <image
                class="home-page__quote-bg"
                src="/static/man-blue-daily.png"
                mode="aspectFill"
              />
              <view class="home-page__quote-content">
                <text class="home-page__quote-title">每日一言</text>
                <text class="home-page__quote-text">{{ dailyQuoteLine1 }}</text>
                <text class="home-page__quote-text">{{ dailyQuoteLine2 }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="home-page__bottom-spacer" aria-hidden="true"></view>

  </scroll-view>

  <StudentTabBar active="home" />

  </view>

</template>



<style scoped lang="scss">
.home-page__task-entry {
  display: block;
}

.home-page__task-entry--active {
  opacity: 0.92;
}
</style>

<style lang="scss">
@use '@/styles/home-hero.scss';
</style>


