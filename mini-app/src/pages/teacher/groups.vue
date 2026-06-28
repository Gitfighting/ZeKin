<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { computed, ref } from 'vue'

import TeacherHeroShell from '@/components/TeacherHeroShell.vue'
import TeacherTabBar from '@/components/TeacherTabBar.vue'
import VectorIcon from '@/components/VectorIcon.vue'
import { UI_ICONS } from '@/constants/ui-icons'
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
  iconSrc: string
  iconTone: 'blue' | 'purple' | 'cyan' | 'green'
}

const GROUP_ICONS: Array<{ iconSrc: string; tone: GroupCardItem['iconTone'] }> = [
  { iconSrc: UI_ICONS.class, tone: 'blue' },
  { iconSrc: UI_ICONS.activity, tone: 'purple' },
  { iconSrc: UI_ICONS.internship, tone: 'cyan' },
  { iconSrc: UI_ICONS.daily, tone: 'green' },
]

const loading = ref(false)
const groups = ref<GroupCardItem[]>([])
const riskStudents = ref<TeacherRiskStudent[]>([])
const todayTasks = ref(0)
const exceptionCount = ref(0)

const topRiskStudent = computed(() => riskStudents.value[0] ?? null)

const stats = computed(() => [
  { key: 'groups', label: '管理班级', value: String(groups.value.length), tone: 'blue', iconSrc: UI_ICONS.classes },
  { key: 'tasks', label: '今日任务', value: String(todayTasks.value), tone: 'green', iconSrc: UI_ICONS.records },
  { key: 'rate', label: '出勤率', value: `${overallAttendance.value}%`, tone: 'orange', iconSrc: UI_ICONS.chart },
  { key: 'risk', label: '异常人数', value: String(exceptionCount.value), tone: 'red', iconSrc: UI_ICONS.bell },
])

const overallAttendance = computed(() => {
  if (!groups.value.length) {
    return 0
  }
  const total = groups.value.reduce((sum, group) => sum + group.attendanceRate, 0)
  return Math.round((total / groups.value.length) * 10) / 10
})

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
            iconSrc: iconCfg.iconSrc,
            iconTone: iconCfg.tone,
          }
        } catch {
          return {
            ...group,
            attendanceRate: 0,
            checkedCount: 0,
            iconSrc: iconCfg.iconSrc,
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
  void loadGroups()
})
</script>

<template>
  <view class="tab-page">
    <scroll-view scroll-y class="home-page tab-page__scroll">
      <TeacherHeroShell title="班级管理" slogan="用心管理，助力每一位学生成长">
        <view class="groups-page__stats-card home-page__panel-card">
          <view v-for="item in stats" :key="item.key" class="groups-page__stat">
            <view class="groups-page__stat-icon" :class="`groups-page__stat-icon--${item.tone}`">
              <VectorIcon :src="item.iconSrc" size="36rpx" />
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
              <VectorIcon :src="group.iconSrc" size="40rpx" />
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
            <VectorIcon class="groups-page__risk-icon" :src="UI_ICONS.warning" size="34rpx" />
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
      </TeacherHeroShell>

      <view class="home-page__bottom-spacer" aria-hidden="true"></view>
    </scroll-view>

    <TeacherTabBar active="groups" />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.groups-page__stats-card {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12rpx;
  margin-bottom: 28rpx;
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
  margin: 8rpx 0 20rpx;
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
  padding: 0 0 24rpx;
}

.groups-page__risk-card {
  margin: 28rpx 0 0;
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
  flex-shrink: 0;
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

<style lang="scss">
@use '@/styles/home-hero.scss';
</style>
