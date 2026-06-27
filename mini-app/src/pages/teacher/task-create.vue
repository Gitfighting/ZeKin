<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import { logInfo, showError, showSuccess } from '@/services/feedback'
import {
  createTeacherTask,
  generateCheckinCode,
  getTeacherGroups,
  publishTeacherTask,
  type CheckinMethod,
  type CreateTeacherTaskPayload,
  type ScheduleMode,
  type TeacherGroup,
  type TeacherTaskType,
} from '@/services/teacher'

type SceneType = 'class' | 'dorm' | 'internship'
type WizardStep = 1 | 2 | 3
type ExpandSection = 'title' | 'groups' | 'time' | 'methods' | 'reminder' | null

const groups = ref<TeacherGroup[]>([])
const submitting = ref(false)
const currentStep = ref<WizardStep>(1)
const expandedSection = ref<ExpandSection>(null)
const activeScene = ref<SceneType>('class')

const sceneTypes: Array<{ key: SceneType; label: string; icon: string }> = [
  { key: 'class', label: '课堂签到', icon: '🧑‍🏫' },
  { key: 'dorm', label: '查寝打卡', icon: '🛏️' },
  { key: 'internship', label: '实习打卡', icon: '💼' },
]

const wizardSteps = [
  { step: 1 as WizardStep, label: '任务设置' },
  { step: 2 as WizardStep, label: '规则设置' },
  { step: 3 as WizardStep, label: '确认发布' },
]

const methodOptions: Array<{ label: string; value: CheckinMethod; hint: string }> = [
  { label: '人脸识别', value: 'face', hint: '拍照核验本人' },
  { label: '地理位置', value: 'location', hint: '围栏定位校验' },
  { label: '二维码', value: 'qr_code', hint: '扫码签到防代签' },
  { label: '签到码', value: 'checkin_code', hint: '输入固定签到码' },
  { label: '附件/日志', value: 'attachment', hint: '上传日志或图片' },
  { label: '手势签到', value: 'gesture', hint: '绘制手势图案' },
]

const scheduleModes: Array<{ label: string; value: ScheduleMode }> = [
  { label: '一次任务', value: 'one_time' },
  { label: '定时任务（每日）', value: 'recurring' },
]

const form = reactive<CreateTeacherTaskPayload>({
  title: '',
  description: '',
  groupIds: [],
  taskType: 'attendance',
  templateName: '课堂签到',
  startsAt: '',
  endsAt: '',
  methods: ['location', 'face'],
  scheduleMode: 'one_time',
  methodConfig: {
    face: { tolerance: 0.6 },
    location: { placeName: '教室签到点', longitude: 0, latitude: 0, radius: 300 },
    qr_code: { expireSeconds: 120, refreshIntervalSeconds: 60 },
    checkin_code: { code: '' },
    attachment: { required: true, minTextLength: 10, label: '今日工作日志' },
    gesture: { presetPattern: 'Z' },
  },
  advancedRules: {
    allowLateMinutes: 0,
    needPhoto: false,
    allowAppeal: true,
    autoEnd: true,
  },
})

function hasMethod(method: CheckinMethod): boolean {
  return (form.methods ?? []).includes(method)
}

function toggleMethod(method: CheckinMethod) {
  const current = form.methods ?? []
  const next = current.includes(method)
    ? current.filter((item) => item !== method)
    : [...current, method]
  form.methods = next
  if (method === 'checkin_code' && next.includes('checkin_code') && !form.methodConfig!.checkin_code!.code) {
    form.methodConfig!.checkin_code!.code = generateCheckinCode(6)
  }
}

function regenerateCheckinCode() {
  form.methodConfig!.checkin_code!.code = generateCheckinCode(6)
}

function applySceneDefaults(scene: SceneType) {
  activeScene.value = scene
  form.taskType = 'attendance' as TeacherTaskType
  if (scene === 'class') {
    form.templateName = '课堂签到'
    form.methods = ['location', 'face']
    form.methodConfig!.location!.placeName = '教室签到点'
  } else if (scene === 'dorm') {
    form.templateName = '查寝打卡'
    form.methods = ['location', 'face']
    form.methodConfig!.location!.placeName = '宿舍签到点'
  } else {
    form.templateName = '实习打卡'
    form.methods = ['location', 'attachment']
    form.methodConfig!.attachment!.label = '今日工作日志'
  }
}

const selectedGroups = computed(() =>
  groups.value.filter((group) => form.groupIds.includes(group.id)),
)

const sceneLabel = computed(
  () => sceneTypes.find((item) => item.key === activeScene.value)?.label ?? '课堂签到',
)

const groupsSummary = computed(() => {
  if (selectedGroups.value.length === 0) {
    return '选择班级/学生'
  }
  return selectedGroups.value.map((group) => group.name).join('、')
})

const timeSummary = computed(() => {
  if (!form.startsAt && !form.endsAt) {
    return '选择开始与结束时间'
  }
  const start = formatDisplayTime(form.startsAt)
  const end = formatDisplayTime(form.endsAt)
  if (start && end) {
    return `${start} - ${end}`
  }
  return start || end || '选择开始与结束时间'
})

const methodsSummary = computed(() => {
  const labels = methodOptions
    .filter((item) => hasMethod(item.value))
    .map((item) => item.label)
  return labels.length ? labels.join('、') : '选择打卡方式'
})

const reminderSummary = computed(() => {
  const minutes = form.advancedRules?.allowLateMinutes ?? 0
  const parts = [`迟到宽限 ${minutes} 分钟`]
  if (form.advancedRules?.autoEnd) {
    parts.push('到点自动结束')
  }
  if (form.advancedRules?.allowAppeal) {
    parts.push('允许申诉')
  }
  return parts.join(' · ')
})

const ruleSummary = computed(() => [
  `任务名称：${form.title || '未填写'}`,
  `任务类型：${sceneLabel.value}`,
  `发布对象：${groupsSummary.value}`,
  `打卡时间：${timeSummary.value}`,
  `打卡方式：${methodsSummary.value}`,
  `提醒规则：${reminderSummary.value}`,
  `任务周期：${scheduleModes.find((item) => item.value === form.scheduleMode)?.label ?? '一次任务'}`,
])

const step1Ready = computed(
  () =>
    form.title.trim().length > 0 &&
    form.groupIds.length > 0 &&
    form.startsAt.trim().length > 0 &&
    form.endsAt.trim().length > 0,
)

const step2Ready = computed(() => (form.methods ?? []).length > 0)

const readyToPublish = computed(
  () => step1Ready.value && step2Ready.value && !submitting.value,
)

function toggleExpand(section: ExpandSection) {
  expandedSection.value = expandedSection.value === section ? null : section
}

function goToStep(step: WizardStep) {
  if (step === 2 && !step1Ready.value) {
    showError('请先完成任务设置')
    return
  }
  if (step === 3 && !readyToPublish.value) {
    showError('请先完成规则设置')
    return
  }
  currentStep.value = step
  expandedSection.value = null
}

function nextStep() {
  if (currentStep.value === 1) {
    goToStep(2)
    return
  }
  if (currentStep.value === 2) {
    goToStep(3)
  }
}

async function loadGroups() {
  if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
    groups.value = []
    return
  }

  try {
    groups.value = await getTeacherGroups()
    if (!groups.value.some((group) => form.groupIds.includes(group.id))) {
      form.groupIds = groups.value[0] ? [groups.value[0].id] : []
    }
    logInfo('创建任务分组加载成功', { count: groups.value.length })
  } catch (error) {
    groups.value = []
    form.groupIds = []
    showError(error, '分组加载失败')
  }
}

function parseDatePart(value: string): string {
  const match = value.match(/^(\d{4}-\d{2}-\d{2})/)
  return match ? match[1] : ''
}

function parseTimePart(value: string): string {
  const match = value.match(/(\d{2}:\d{2})/)
  return match ? match[1] : ''
}

function formatDisplayTime(value: string): string {
  const date = parseDatePart(value)
  const time = parseTimePart(value)
  if (date && time) {
    return `${date} ${time}`
  }
  return date || time
}

function onDateChange(field: 'startsAt' | 'endsAt', e: { detail: { value: string } }) {
  const date = e.detail.value
  const time = parseTimePart(form[field]) || '00:00'
  form[field] = `${date} ${time}`
}

function onTimeChange(field: 'startsAt' | 'endsAt', e: { detail: { value: string } }) {
  const time = e.detail.value
  const date = parseDatePart(form[field]) || formatDate(new Date())
  form[field] = `${date} ${time}`
}

function formatDate(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function toggleGroup(id: number) {
  const nextGroups = form.groupIds.includes(id)
    ? form.groupIds.filter((groupId) => groupId !== id)
    : [...form.groupIds, id]
  form.groupIds = nextGroups
}

async function submitTask() {
  if (!readyToPublish.value) {
    return
  }

  submitting.value = true

  try {
    if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
      return
    }

    const createdTask = await createTeacherTask(form)
    await publishTeacherTask(createdTask.id)
    logInfo('教师任务创建成功', { taskId: createdTask.id })
    showSuccess('已发布')
    uni.redirectTo({ url: `/pages/teacher/task-detail?id=${createdTask.id}` })
  } catch (error) {
    showError(error, '发布失败')
  } finally {
    submitting.value = false
  }
}

function goBack() {
  if (currentStep.value > 1) {
    currentStep.value = (currentStep.value - 1) as WizardStep
    expandedSection.value = null
    return
  }
  if (typeof uni === 'undefined') {
    return
  }
  uni.navigateBack({ delta: 1 })
}

onMounted(loadGroups)
</script>

<template>
  <view class="create-page">
    <scroll-view scroll-y class="create-page__scroll">
      <view class="create-page__hero">
        <view class="create-page__hero-bg-box" aria-hidden="true">
          <image class="create-page__hero-bg" src="/static/teacher-home-hero.png" mode="aspectFill" />
        </view>
        <view class="create-page__hero-mask" aria-hidden="true"></view>
        <view class="create-page__nav" @click="goBack">
          <text class="create-page__nav-back">‹</text>
        </view>
        <view class="create-page__hero-content">
          <text class="create-page__title">创建考勤任务</text>
          <text class="create-page__subtitle">灵活设置，高效管理考勤</text>
        </view>
      </view>

      <view class="create-page__panel">
        <view class="create-page__steps">
          <view
            v-for="(item, index) in wizardSteps"
            :key="item.step"
            class="create-page__step-wrap"
          >
            <view class="create-page__step-item">
              <view
                class="create-page__step-dot"
                :class="{
                  'create-page__step-dot--active': currentStep === item.step,
                  'create-page__step-dot--done': currentStep > item.step,
                }"
              >
                <text>{{ item.step }}</text>
              </view>
              <text
                class="create-page__step-label"
                :class="{ 'create-page__step-label--active': currentStep === item.step }"
              >
                {{ item.label }}
              </text>
            </view>
            <view
              v-if="index < wizardSteps.length - 1"
              class="create-page__step-line"
              :class="{ 'create-page__step-line--active': currentStep > item.step }"
            ></view>
          </view>
        </view>

        <view v-if="currentStep === 1" class="create-page__form">
          <view class="form-row" @click="toggleExpand('title')">
            <view class="form-row__icon">📄</view>
            <text class="form-row__label">任务名称</text>
            <text class="form-row__value" :class="{ 'form-row__value--placeholder': !form.title }">
              {{ form.title || '请输入任务名称' }}
            </text>
            <text class="form-row__chevron">›</text>
          </view>
          <view v-if="expandedSection === 'title'" class="form-expand">
            <input v-model="form.title" class="form-expand__input" placeholder="请输入任务名称" />
            <textarea
              v-model="form.description"
              class="form-expand__textarea"
              maxlength="120"
              placeholder="任务说明（可选）"
            />
          </view>

          <view class="form-row form-row--stack">
            <view class="form-row__head" @click.stop>
              <view class="form-row__icon">▦</view>
              <text class="form-row__label">任务类型</text>
              <text class="form-row__value">{{ sceneLabel }}</text>
              <text class="form-row__chevron">›</text>
            </view>
            <view class="type-chips">
              <view
                v-for="scene in sceneTypes"
                :key="scene.key"
                class="type-chip"
                :class="{ 'type-chip--active': activeScene === scene.key }"
                @click="applySceneDefaults(scene.key)"
              >
                <text class="type-chip__icon">{{ scene.icon }}</text>
                <text class="type-chip__label">{{ scene.label }}</text>
              </view>
            </view>
          </view>

          <view class="form-row" @click="toggleExpand('groups')">
            <view class="form-row__icon">👥</view>
            <text class="form-row__label">发布对象</text>
            <text
              class="form-row__value"
              :class="{ 'form-row__value--placeholder': selectedGroups.length === 0 }"
            >
              {{ groupsSummary }}
            </text>
            <text class="form-row__chevron">›</text>
          </view>
          <view v-if="expandedSection === 'groups'" class="form-expand">
            <view class="chip-grid">
              <view
                v-for="group in groups"
                :key="group.id"
                :class="['choice-chip', { active: form.groupIds.includes(group.id) }]"
                @click="toggleGroup(group.id)"
              >
                <text class="chip-title">{{ group.name }}</text>
                <text class="chip-subtitle">{{ group.studentCount }} 人 · 最近 {{ group.recentTaskCount }} 次</text>
              </view>
              <text v-if="groups.length === 0" class="empty-line">暂无可选分组，请先确认教师已绑定班级。</text>
            </view>
          </view>

          <view class="form-row" @click="toggleExpand('time')">
            <view class="form-row__icon">🕐</view>
            <text class="form-row__label">打卡时间</text>
            <text
              class="form-row__value"
              :class="{ 'form-row__value--placeholder': !form.startsAt && !form.endsAt }"
            >
              {{ timeSummary }}
            </text>
            <text class="form-row__chevron">›</text>
          </view>
          <view v-if="expandedSection === 'time'" class="form-expand">
            <view class="time-block">
              <text class="time-block__label">开始时间</text>
              <view class="datetime-row">
                <picker mode="date" :value="parseDatePart(form.startsAt)" @change="onDateChange('startsAt', $event)">
                  <view class="picker-box">
                    <text>{{ parseDatePart(form.startsAt) || '选择日期' }}</text>
                  </view>
                </picker>
                <picker mode="time" :value="parseTimePart(form.startsAt)" @change="onTimeChange('startsAt', $event)">
                  <view class="picker-box picker-box--time">
                    <text>{{ parseTimePart(form.startsAt) || '--:--' }}</text>
                  </view>
                </picker>
              </view>
            </view>
            <view class="time-block">
              <text class="time-block__label">结束时间</text>
              <view class="datetime-row">
                <picker mode="date" :value="parseDatePart(form.endsAt)" @change="onDateChange('endsAt', $event)">
                  <view class="picker-box">
                    <text>{{ parseDatePart(form.endsAt) || '选择日期' }}</text>
                  </view>
                </picker>
                <picker mode="time" :value="parseTimePart(form.endsAt)" @change="onTimeChange('endsAt', $event)">
                  <view class="picker-box picker-box--time">
                    <text>{{ parseTimePart(form.endsAt) || '--:--' }}</text>
                  </view>
                </picker>
              </view>
            </view>
            <view class="schedule-row">
              <text class="schedule-row__label">任务周期</text>
              <view class="schedule-row__options">
                <view
                  v-for="mode in scheduleModes"
                  :key="mode.value"
                  class="schedule-chip"
                  :class="{ 'schedule-chip--active': form.scheduleMode === mode.value }"
                  @click="form.scheduleMode = mode.value"
                >
                  {{ mode.label }}
                </view>
              </view>
            </view>
          </view>
        </view>

        <view v-else-if="currentStep === 2" class="create-page__form">
          <view class="form-row" @click="toggleExpand('methods')">
            <view class="form-row__icon">📍</view>
            <text class="form-row__label">打卡方式</text>
            <text
              class="form-row__value"
              :class="{ 'form-row__value--placeholder': !(form.methods ?? []).length }"
            >
              {{ methodsSummary }}
            </text>
            <text class="form-row__chevron">›</text>
          </view>
          <view v-if="expandedSection === 'methods' || currentStep === 2" class="form-expand">
            <view class="chip-grid">
              <view
                v-for="method in methodOptions"
                :key="method.value"
                :class="['choice-chip', { active: hasMethod(method.value) }]"
                @click="toggleMethod(method.value)"
              >
                <text class="chip-title">{{ hasMethod(method.value) ? '✓ ' : '' }}{{ method.label }}</text>
                <text class="chip-subtitle">{{ method.hint }}</text>
              </view>
            </view>

            <view v-if="hasMethod('location')" class="config-block">
              <text class="config-title">地理位置配置</text>
              <view class="field-block">
                <text class="field-label">地点名称</text>
                <input v-model="form.methodConfig!.location!.placeName" class="field-input" placeholder="如：3号宿舍楼" />
              </view>
              <view class="field-grid">
                <view class="field-block">
                  <text class="field-label">经度</text>
                  <input
                    :value="String(form.methodConfig!.location!.longitude ?? 0)"
                    class="field-input"
                    type="digit"
                    @input="form.methodConfig!.location!.longitude = Number(($event as any).detail.value || 0)"
                  />
                </view>
                <view class="field-block">
                  <text class="field-label">纬度</text>
                  <input
                    :value="String(form.methodConfig!.location!.latitude ?? 0)"
                    class="field-input"
                    type="digit"
                    @input="form.methodConfig!.location!.latitude = Number(($event as any).detail.value || 0)"
                  />
                </view>
              </view>
              <view class="field-block">
                <text class="field-label">围栏半径（米）</text>
                <input
                  :value="String(form.methodConfig!.location!.radius ?? 300)"
                  class="field-input"
                  type="number"
                  @input="form.methodConfig!.location!.radius = Number(($event as any).detail.value || 0)"
                />
              </view>
            </view>

            <view v-if="hasMethod('face')" class="config-block">
              <text class="config-title">人脸识别配置</text>
              <view class="field-block">
                <text class="field-label">相似度阈值（0-1）</text>
                <input
                  :value="String(form.methodConfig!.face!.tolerance ?? 0.6)"
                  class="field-input"
                  type="digit"
                  @input="form.methodConfig!.face!.tolerance = Number(($event as any).detail.value || 0.6)"
                />
              </view>
            </view>

            <view v-if="hasMethod('qr_code')" class="config-block">
              <text class="config-title">二维码配置</text>
              <view class="field-grid">
                <view class="field-block">
                  <text class="field-label">单码有效期（秒）</text>
                  <input
                    :value="String(form.methodConfig!.qr_code!.expireSeconds ?? 120)"
                    class="field-input"
                    type="number"
                    @input="form.methodConfig!.qr_code!.expireSeconds = Number(($event as any).detail.value || 120)"
                  />
                </view>
                <view class="field-block">
                  <text class="field-label">刷新间隔（秒）</text>
                  <input
                    :value="String(form.methodConfig!.qr_code!.refreshIntervalSeconds ?? 60)"
                    class="field-input"
                    type="number"
                    @input="
                      form.methodConfig!.qr_code!.refreshIntervalSeconds = Number(($event as any).detail.value || 60)
                    "
                  />
                </view>
              </view>
            </view>

            <view v-if="hasMethod('checkin_code')" class="config-block">
              <text class="config-title">签到码配置</text>
              <view class="field-block">
                <text class="field-label">签到码（留空自动生成）</text>
                <view class="code-row">
                  <input
                    v-model="form.methodConfig!.checkin_code!.code"
                    class="field-input field-input--code"
                    maxlength="12"
                    placeholder="如：A3K9P2"
                  />
                  <view class="code-action" @click="regenerateCheckinCode">重新生成</view>
                </view>
              </view>
            </view>

            <view v-if="hasMethod('attachment')" class="config-block">
              <text class="config-title">附件/日志配置</text>
              <view class="field-block">
                <text class="field-label">提示文案</text>
                <input v-model="form.methodConfig!.attachment!.label" class="field-input" placeholder="如：今日工作日志" />
              </view>
              <view class="field-grid">
                <view class="field-block">
                  <text class="field-label">最少字数</text>
                  <input
                    :value="String(form.methodConfig!.attachment!.minTextLength ?? 10)"
                    class="field-input"
                    type="number"
                    @input="form.methodConfig!.attachment!.minTextLength = Number(($event as any).detail.value || 0)"
                  />
                </view>
                <view class="toggle-row">
                  <text class="field-label">必填</text>
                  <switch
                    :checked="Boolean(form.methodConfig!.attachment!.required)"
                    color="#1677ff"
                    @change="form.methodConfig!.attachment!.required = ($event as any).detail.value"
                  />
                </view>
              </view>
            </view>

            <view v-if="hasMethod('gesture')" class="config-block">
              <text class="config-title">手势配置</text>
              <view class="field-block">
                <text class="field-label">预设图案（如 Z / N / L）</text>
                <input v-model="form.methodConfig!.gesture!.presetPattern" class="field-input" placeholder="Z" />
              </view>
            </view>
          </view>

          <view class="form-row" @click="toggleExpand('reminder')">
            <view class="form-row__icon">🔔</view>
            <text class="form-row__label">提醒规则</text>
            <text class="form-row__value">{{ reminderSummary }}</text>
            <text class="form-row__chevron">›</text>
          </view>
          <view v-if="expandedSection === 'reminder'" class="form-expand">
            <view class="field-block">
              <text class="field-label">迟到宽限（分钟）</text>
              <input
                :value="String(form.advancedRules?.allowLateMinutes ?? 0)"
                class="field-input"
                type="number"
                @input="form.advancedRules!.allowLateMinutes = Number(($event as any).detail.value || 0)"
              />
            </view>
            <view class="toggle-row">
              <text class="field-label">允许申诉</text>
              <switch
                :checked="Boolean(form.advancedRules?.allowAppeal)"
                color="#1677ff"
                @change="form.advancedRules!.allowAppeal = ($event as any).detail.value"
              />
            </view>
            <view class="toggle-row">
              <text class="field-label">到点自动结束</text>
              <switch
                :checked="Boolean(form.advancedRules?.autoEnd)"
                color="#1677ff"
                @change="form.advancedRules!.autoEnd = ($event as any).detail.value"
              />
            </view>
          </view>
        </view>

        <view v-else class="create-page__form">
          <view class="confirm-card">
            <text class="confirm-card__title">发布前确认</text>
            <text v-for="item in ruleSummary" :key="item" class="confirm-card__line">{{ item }}</text>
          </view>
        </view>
      </view>

      <view class="create-page__footer">
        <view class="create-page__tip">
          <text class="create-page__tip-icon">ⓘ</text>
          <text class="create-page__tip-text">发布后，学生将收到任务通知并按规则进行打卡</text>
        </view>

        <view
          v-if="currentStep < 3"
          class="create-page__btn"
          :class="{ 'create-page__btn--disabled': currentStep === 1 ? !step1Ready : !step2Ready }"
          @click="nextStep"
        >
          下一步
        </view>
        <view
          v-else
          class="create-page__btn"
          :class="{ 'create-page__btn--disabled': !readyToPublish }"
          @click="submitTask"
        >
          {{ submitting ? '发布中...' : '立即发布' }}
        </view>
      </view>

      <view class="create-page__safe-bottom"></view>
    </scroll-view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.create-page {
  min-height: 100vh;
  background: #f5f8fc;
}

.create-page__scroll {
  height: 100vh;
}

.create-page__hero {
  position: relative;
  height: 360rpx;
  overflow: hidden;
}

.create-page__hero-bg-box {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 175%;
}

.create-page__hero-bg {
  width: 100%;
  height: 100%;
}

.create-page__hero-mask {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(15, 120, 255, 0.08) 0%, rgba(15, 120, 255, 0.42) 100%);
}

.create-page__nav {
  position: absolute;
  top: 88rpx;
  left: 24rpx;
  z-index: 3;
  display: flex;
  width: 64rpx;
  height: 64rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.22);
}

.create-page__nav-back {
  color: #fff;
  font-size: 48rpx;
  font-weight: 300;
  line-height: 1;
}

.create-page__hero-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding: 140rpx 32rpx 48rpx;
}

.create-page__title,
.create-page__subtitle {
  color: #fff;
}

.create-page__title {
  font-size: 48rpx;
  font-weight: 700;
}

.create-page__subtitle {
  font-size: 26rpx;
  line-height: 1.55;
  opacity: 0.96;
}

.create-page__panel {
  position: relative;
  z-index: 3;
  margin: -36rpx 24rpx 0;
  padding: 28rpx 24rpx 8rpx;
  border-radius: 28rpx 28rpx 24rpx 24rpx;
  background: #fff;
  box-shadow: 0 16rpx 40rpx rgba(15, 107, 214, 0.08);
}

.create-page__steps {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.create-page__step-wrap {
  display: flex;
  flex: 1;
  align-items: flex-start;
}

.create-page__step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  width: 120rpx;
}

.create-page__step-dot {
  display: flex;
  width: 44rpx;
  height: 44rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #eef2f6;
  color: $text-muted;
  font-size: 24rpx;
  font-weight: 700;
}

.create-page__step-dot--active,
.create-page__step-dot--done {
  background: $primary;
  color: #fff;
}

.create-page__step-label {
  color: $text-muted;
  font-size: 22rpx;
  text-align: center;
  white-space: nowrap;
}

.create-page__step-label--active {
  color: $primary;
  font-weight: 600;
}

.create-page__step-line {
  flex: 1;
  height: 0;
  margin-top: 22rpx;
  border-top: 2rpx dashed #dbe3ee;
}

.create-page__step-line--active {
  border-top-color: rgba($primary, 0.45);
}

.create-page__form {
  display: flex;
  flex-direction: column;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  min-height: 96rpx;
  padding: 20rpx 0;
  border-bottom: 1rpx solid rgba(15, 23, 42, 0.06);
}

.form-row--stack {
  flex-direction: column;
  align-items: stretch;
  gap: 0;
}

.form-row__head {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.form-row__icon {
  display: flex;
  width: 48rpx;
  height: 48rpx;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 14rpx;
  background: rgba($primary, 0.1);
  color: $primary;
  font-size: 24rpx;
}

.form-row__label {
  flex-shrink: 0;
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 600;
}

.form-row__value {
  flex: 1;
  min-width: 0;
  color: $text-primary;
  font-size: 26rpx;
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.form-row__value--placeholder {
  color: $text-muted;
}

.form-row__chevron {
  flex-shrink: 0;
  color: $text-muted;
  font-size: 32rpx;
  line-height: 1;
}

.type-chips {
  display: flex;
  gap: 12rpx;
  padding: 16rpx 0 8rpx 64rpx;
}

.type-chip {
  display: flex;
  flex: 1;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 18rpx 8rpx;
  border: 2rpx solid rgba(15, 23, 42, 0.08);
  border-radius: 18rpx;
  background: #fafbfd;
}

.type-chip--active {
  border-color: rgba($primary, 0.35);
  background: rgba($primary, 0.08);
}

.type-chip__icon {
  font-size: 32rpx;
}

.type-chip__label {
  color: $text-secondary;
  font-size: 22rpx;
  font-weight: 600;
  text-align: center;
}

.type-chip--active .type-chip__label {
  color: $primary;
}

.form-expand {
  padding: 0 0 20rpx 64rpx;
}

.form-expand__input,
.form-expand__textarea,
.field-input {
  width: 100%;
  padding: 22rpx 24rpx;
  border-radius: 16rpx;
  background: #f7faff;
  font-size: 28rpx;
  color: $text-primary;
  box-sizing: border-box;
}

.form-expand__input {
  min-height: 80rpx;
}

.form-expand__textarea {
  min-height: 140rpx;
  margin-top: 12rpx;
}

.chip-grid {
  display: grid;
  gap: 14rpx;
}

.choice-chip {
  padding: 20rpx;
  border-radius: 18rpx;
  background: #f7faff;
  border: 1rpx solid transparent;
}

.choice-chip.active {
  border-color: rgba($primary, 0.3);
  background: $primary-light;
}

.chip-title {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: $text-primary;
}

.chip-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.4;
  color: $text-secondary;
}

.time-block {
  margin-bottom: 16rpx;
}

.time-block__label,
.field-label,
.schedule-row__label {
  display: block;
  margin-bottom: 10rpx;
  color: $text-secondary;
  font-size: 24rpx;
}

.datetime-row,
.field-grid,
.toggle-row,
.code-row,
.schedule-row__options {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.field-grid {
  align-items: stretch;
}

.field-grid > .field-block,
.field-block {
  flex: 1;
  margin-top: 12rpx;
}

.picker-box {
  flex: 1;
  padding: 22rpx 24rpx;
  border-radius: 16rpx;
  background: #f7faff;
  text-align: center;
  min-height: 80rpx;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  color: $text-primary;
}

.picker-box--time {
  flex: 0 0 auto;
  width: 160rpx;
}

.schedule-row {
  margin-top: 8rpx;
}

.schedule-chip {
  flex: 1;
  padding: 16rpx 0;
  border-radius: 14rpx;
  background: #f7faff;
  color: $text-secondary;
  font-size: 22rpx;
  text-align: center;
}

.schedule-chip--active {
  background: $primary-light;
  color: $primary;
  font-weight: 600;
}

.config-block {
  margin-top: 16rpx;
  padding: 20rpx;
  border-radius: 18rpx;
  background: #f7faff;
  border: 1rpx solid rgba($primary, 0.12);
}

.config-title {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: $primary;
}

.toggle-row {
  justify-content: space-between;
  margin-top: 12rpx;
}

.field-input--code {
  flex: 1;
  letter-spacing: 4rpx;
  font-weight: 700;
}

.code-action {
  flex-shrink: 0;
  padding: 16rpx 24rpx;
  border-radius: 14rpx;
  background: rgba($primary, 0.1);
  color: $primary;
  font-size: 24rpx;
  font-weight: 600;
}

.confirm-card {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding: 8rpx 0 16rpx;
}

.confirm-card__title {
  color: $text-primary;
  font-size: 30rpx;
  font-weight: 700;
}

.confirm-card__line {
  color: $text-secondary;
  font-size: 26rpx;
  line-height: 1.6;
}

.empty-line {
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.6;
}

.create-page__footer {
  padding: 24rpx;
}

.create-page__tip {
  display: flex;
  align-items: flex-start;
  gap: 10rpx;
  margin-bottom: 20rpx;
}

.create-page__tip-icon {
  flex-shrink: 0;
  color: $primary;
  font-size: 24rpx;
  line-height: 1.5;
}

.create-page__tip-text {
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.5;
}

.create-page__btn {
  height: 96rpx;
  line-height: 96rpx;
  border-radius: 999rpx;
  background: $primary;
  color: #fff;
  font-size: 32rpx;
  font-weight: 700;
  text-align: center;
  box-shadow: 0 16rpx 32rpx rgba($primary, 0.28);
}

.create-page__btn--disabled {
  opacity: 0.45;
  box-shadow: none;
}

.create-page__safe-bottom {
  height: calc(env(safe-area-inset-bottom) + 24rpx);
}
</style>
