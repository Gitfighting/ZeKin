<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import TeacherTabBar from '@/components/TeacherTabBar.vue'
import { readStoredSession } from '@/services/auth'
import { logInfo, showError } from '@/services/feedback'
import {
  getTeacherDashboard,
  getTeacherGroupDetail,
  getTeacherGroups,
  getTeacherRiskStudents,
  type TeacherGroup,
  type TeacherRiskStudent,
} from '@/services/teacher'

interface GroupCardItem extends TeacherGroup {
  attendanceRate: number
  checkedCount: number
  icon: string
  iconTone: 'blue' | 'purple' | 'cyan' | 'green'
}

const GROUP_ICONS: Array<{ icon: string; tone: GroupCardItem['iconTone'] }> = [
  { icon: '💻', tone: 'blue' },
  { icon: '🤖', tone: 'purple' },
  { icon: '💼', tone: 'cyan' },
  { icon: '📚', tone: 'green' },
]

const displayName = ref('老师')
const loading = ref(false)
const groups = ref<GroupCardItem[]>([])
const riskStudents = ref<TeacherRiskStudent[]>([])
const todayTasks = ref(0)
const exceptionCount = ref(0)

const topRiskStudent = computed(() => riskStudents.value[0] ?? null)

const heroContentStyle = ref<Record<string, string>>({
  paddingTop: '112rpx',
  paddingLeft: '32rpx',
  paddingRight: '32rpx',
})

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

const overallAttendance = computed(() => {
  if (!groups.value.length) {
    return 0
  }
  const total = groups.value.reduce((sum, group) => sum + group.attendanceRate, 0)
  return Math.round((total / groups.value.length) * 10) / 10
})

const stats = computed(() => [
  { key: 'groups', label: '管理班级', value: String(groups.value.length), tone: 'blue', icon: '👥' },
  { key: 'tasks', label: '今日任务', value: String(todayTasks.value), tone: 'green', icon: '📋' },
  { key: 'rate', label: '出勤率', value: `${overallAttendance.value}%`, tone: 'orange', icon: '📊' },
  { key: 'risk', label: '异常人数', value: String(exceptionCount.value), tone: 'red', icon: '🔔' },
])

function syncHeroLayout() {
  if (typeof uni === 'undefined') {
    return
  }

  try {
    const menuButton = uni.getMenuButtonBoundingClientRect()
    heroContentStyle.value = {
      paddingTop: `${menuButton.bottom + 12}px`,
      paddingLeft: '32rpx',
      paddingRight: '32rpx',
    }
  } catch {
    // 非小程序环境保留默认占位
  }
}

function loadProfileMeta() {
  const session = readStoredSession()
  if (session?.user.displayName) {
    displayName.value = session.user.displayName.replace(/^用户/, '') || session.user.displayName
  }
}

async function loadGroups() {
  if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
    groups.value = []
    return
  }

  loading.value = true
  try {
    const [dashboard, groupList] = await Promise.all([
      getTeacherDashboard(),
      getTeacherGroups(),
    ])
    todayTasks.value = dashboard.todayTasks
    exceptionCount.value = dashboard.exceptions

    const cards = await Promise.all(
      groupList.map(async (group, index) => {
        const iconCfg = GROUP_ICONS[index % GROUP_ICONS.length]
        try {
          const detail = await getTeacherGroupDetail(group.id)
          const rate = detail.stats.attendanceRate ?? 0
          const checkedCount = Math.min(
            group.studentCount,
            Math.round(group.studentCount * rate / 100),
          )
          return {
            ...group,
            attendanceRate: rate,
            checkedCount,
            icon: iconCfg.icon,
            iconTone: iconCfg.tone,
          }
        } catch {
          return {
            ...group,
            attendanceRate: 0,
            checkedCount: 0,
            icon: iconCfg.icon,
            iconTone: iconCfg.tone,
          }
        }
      }),
    )

    groups.value = cards
    riskStudents.value = await getTeacherRiskStudents()
    exceptionCount.value = riskStudents.value.length || dashboard.exceptions
    logInfo('教师班级列表加载成功', { count: cards.length, riskCount: riskStudents.value.length })
  } catch (error) {
    groups.value = []
    riskStudents.value = []
    showError(error, '班级列表加载失败')
  } finally {
    loading.value = false
  }
}

function openGroup(id: number) {
  uni.navigateTo({ url: `/pages/teacher/group-detail?id=${id}` })
}

function openCreate() {
  uni.navigateTo({ url: '/pages/teacher/group-create' })
}

function openAllRiskStudents() {
  uni.navigateTo({ url: '/pages/teacher/risk-students' })
}

function riskReason(student: TeacherRiskStudent) {
  return `连续 ${student.missCount} 次未签到`
}

function avatarText(name: string) {
  return name.trim().slice(-2) || '学'
}

onShow(() => {
  syncHeroLayout()
  loadProfileMeta()
  void loadGroups()
})
</script>

<template>
  <view class="tab-page">
    <scroll-view scroll-y class="groups-page tab-page__scroll">
      <view class="groups-page__hero">
        <view class="groups-page__hero-bg-box" aria-hidden="true">
          <image class="groups-page__hero-bg" src="/static/teacher-home-hero.png" mode="aspectFill" />
        </view>
        <view class="groups-page__hero-mask"></view>
        <view class="groups-page__hero-content" :style="heroContentStyle">
          <text class="groups-page__title">班级管理</text>
          <text class="groups-page__greeting">{{ greetingPrefix }}，{{ displayName }} 👋</text>
          <text class="groups-page__subtitle">用心管理，助力每一位学生成长</text>
        </view>
      </view>

      <view class="groups-page__stats-card">
        <view v-for="item in stats" :key="item.key" class="groups-page__stat">
          <view class="groups-page__stat-icon" :class="`groups-page__stat-icon--${item.tone}`">
            <text>{{ item.icon }}</text>
          </view>
          <text class="groups-page__stat-value">{{ item.value }}</text>
          <text class="groups-page__stat-label">{{ item.label }}</text>
        </view>
      </view>

      <view class="groups-page__section-head">
        <text class="groups-page__section-title">我的班级</text>
        <view class="groups-page__create-link" @click="openCreate">
          <text class="groups-page__create-icon">+</text>
          <text>创建班级</text>
        </view>
      </view>

      <view class="groups-page__list">
        <view v-if="loading" class="groups-page__empty">加载中...</view>
        <view
          v-for="group in groups"
          :key="group.id"
          class="group-card"
          @click="openGroup(group.id)"
        >
          <view class="group-card__head">
            <view class="group-card__icon" :class="`group-card__icon--${group.iconTone}`">
              <text>{{ group.icon }}</text>
            </view>
            <view class="group-card__info">
              <view class="group-card__title-row">
                <text class="group-card__title">{{ group.name }}</text>
                <text class="group-card__arrow">›</text>
              </view>
              <text class="group-card__meta">
                学生 {{ group.studentCount }} 人
                <text v-if="group.courseName"> · {{ group.courseName }}</text>
              </text>
            </view>
          </view>

          <view class="group-card__progress-block">
            <view class="group-card__progress-head">
              <text class="group-card__progress-label">今日出勤进度</text>
              <text class="group-card__progress-count">
                {{ group.checkedCount }}/{{ group.studentCount }}
              </text>
            </view>
            <view class="group-card__progress-track">
              <view
                class="group-card__progress-bar"
                :style="{ width: `${Math.min(group.attendanceRate, 100)}%` }"
              />
            </view>
          </view>
        </view>

        <view v-if="!loading && groups.length === 0" class="groups-page__empty">
          <text class="groups-page__empty-title">暂无班级</text>
          <text class="groups-page__empty-sub">点击右上角创建班级，开始管理学生考勤</text>
        </view>
      </view>

      <view v-if="topRiskStudent" class="groups-page__risk-card">
        <view class="groups-page__risk-head">
          <view class="groups-page__risk-title-wrap">
            <text class="groups-page__risk-icon">⚠️</text>
            <text class="groups-page__risk-title">风险提醒</text>
          </view>
          <text class="groups-page__risk-link" @click.stop="openAllRiskStudents">
            查看全部 ({{ riskStudents.length }}) ›
          </text>
        </view>

        <view class="groups-page__risk-item">
          <view class="groups-page__risk-avatar">
            <text>{{ avatarText(topRiskStudent.name) }}</text>
          </view>
          <view class="groups-page__risk-body">
            <text class="groups-page__risk-name">{{ topRiskStudent.name }}</text>
            <text class="groups-page__risk-group">{{ topRiskStudent.groupName }}</text>
            <text class="groups-page__risk-reason">{{ riskReason(topRiskStudent) }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <TeacherTabBar active="groups" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.groups-page {
  min-height: 100%;
  padding-bottom: $tab-bar-safe-bottom;
  background: $page-bg;
  box-sizing: border-box;
}

.groups-page__hero {
  position: relative;
  height: calc(380rpx + 30px);
  overflow: hidden;
}

.groups-page__hero-bg-box {
  position: absolute;
  right: 0;
  bottom: 0;
  left: -10%;
  width: 118%;
  height: 200%;
}

.groups-page__hero-bg {
  width: 100%;
  height: 100%;
}

.groups-page__hero-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    rgba(15, 120, 255, 0.06) 0%,
    rgba(15, 120, 255, 0.28) 100%
  );
}

.groups-page__hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  color: #fff;
}

.groups-page__title {
  font-size: 52rpx;
  font-weight: 700;
}

.groups-page__greeting {
  margin-top: 4rpx;
  font-size: 34rpx;
  font-weight: 600;
}

.groups-page__subtitle {
  font-size: 26rpx;
  opacity: 0.92;
  line-height: 1.5;
}

.groups-page__stats-card {
  position: relative;
  z-index: 3;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12rpx;
  margin: -56rpx 24rpx 0;
  padding: 28rpx 16rpx;
  border-radius: 28rpx;
  background: $card-bg;
  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.1);
}

.groups-page__stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}

.groups-page__stat-icon {
  display: flex;
  width: 72rpx;
  height: 72rpx;
  align-items: center;
  justify-content: center;
  border-radius: 22rpx;
  font-size: 32rpx;
}

.groups-page__stat-icon--blue {
  background: rgba($primary, 0.12);
}

.groups-page__stat-icon--green {
  background: rgba($success, 0.14);
}

.groups-page__stat-icon--orange {
  background: rgba($warning, 0.14);
}

.groups-page__stat-icon--red {
  background: rgba($danger, 0.12);
}

.groups-page__stat-value {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.2;
}

.groups-page__stat-label {
  color: $text-secondary;
  font-size: 22rpx;
  text-align: center;
}

.groups-page__section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 32rpx 24rpx 20rpx;
}

.groups-page__section-title {
  color: $text-primary;
  font-size: 34rpx;
  font-weight: 700;
}

.groups-page__create-link {
  display: flex;
  align-items: center;
  gap: 8rpx;
  color: $primary;
  font-size: 28rpx;
  font-weight: 600;
}

.groups-page__create-icon {
  display: flex;
  width: 36rpx;
  height: 36rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba($primary, 0.12);
  font-size: 28rpx;
  line-height: 1;
}

.groups-page__list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  padding: 0 24rpx 24rpx;
}

.groups-page__risk-card {
  margin: 0 24rpx 32rpx;
  padding: 24rpx 20rpx;
  border-radius: 24rpx;
  background: #fffaf3;
  border: 1rpx solid rgba($warning, 0.18);
  box-shadow: 0 10rpx 24rpx rgba(255, 159, 26, 0.08);
}

.groups-page__risk-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.groups-page__risk-title-wrap {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.groups-page__risk-icon {
  font-size: 30rpx;
}

.groups-page__risk-title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.groups-page__risk-link {
  color: $text-secondary;
  font-size: 24rpx;
}

.groups-page__risk-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.groups-page__risk-avatar {
  display: flex;
  width: 80rpx;
  height: 80rpx;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba($warning, 0.16);
  color: $warning;
  font-size: 26rpx;
  font-weight: 700;
}

.groups-page__risk-body {
  flex: 1;
  min-width: 0;
}

.groups-page__risk-name {
  display: block;
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 700;
}

.groups-page__risk-group {
  display: block;
  margin-top: 6rpx;
  color: $text-secondary;
  font-size: 24rpx;
}

.groups-page__risk-reason {
  display: block;
  margin-top: 6rpx;
  color: $warning;
  font-size: 24rpx;
}

.group-card {
  padding: 24rpx;
  border-radius: 24rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.group-card__head {
  display: flex;
  gap: 18rpx;
}

.group-card__icon {
  display: flex;
  width: 88rpx;
  height: 88rpx;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 22rpx;
  font-size: 40rpx;
}

.group-card__icon--blue {
  background: rgba($primary, 0.12);
}

.group-card__icon--purple {
  background: rgba(124, 58, 237, 0.14);
}

.group-card__icon--cyan {
  background: rgba(14, 165, 233, 0.14);
}

.group-card__icon--green {
  background: rgba($success, 0.14);
}

.group-card__info {
  flex: 1;
  min-width: 0;
}

.group-card__title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
}

.group-card__title {
  flex: 1;
  min-width: 0;
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
  line-height: 1.4;
}

.group-card__arrow {
  flex-shrink: 0;
  color: $text-muted;
  font-size: 36rpx;
  font-weight: 600;
  line-height: 1;
}

.group-card__meta {
  display: block;
  margin-top: 8rpx;
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.5;
}

.group-card__progress-block {
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid rgba(15, 23, 42, 0.06);
}

.group-card__progress-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.group-card__progress-label {
  color: $text-secondary;
  font-size: 24rpx;
}

.group-card__progress-count {
  color: $text-primary;
  font-size: 24rpx;
  font-weight: 600;
}

.group-card__progress-track {
  height: 12rpx;
  overflow: hidden;
  border-radius: 999rpx;
  background: #eef2f6;
}

.group-card__progress-bar {
  height: 100%;
  border-radius: 999rpx;
  background: linear-gradient(90deg, #4ca3ff 0%, $primary 100%);
}

.groups-page__empty {
  padding: 48rpx 24rpx;
  color: $text-secondary;
  font-size: 26rpx;
  text-align: center;
}

.groups-page__empty-title {
  display: block;
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 700;
}

.groups-page__empty-sub {
  display: block;
  margin-top: 10rpx;
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.5;
}
</style>
