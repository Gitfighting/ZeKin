<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'

import ThemeDatePicker from '@/components/ThemeDatePicker.vue'
import ThemeTimePicker from '@/components/ThemeTimePicker.vue'
import TeacherLocationPicker from '@/components/TeacherLocationPicker.vue'
import GesturePatternModal from '@/components/GesturePatternModal.vue'
import VectorIcon from '@/components/VectorIcon.vue'
import { useStudentPageHeroLayout } from '@/composables/useStudentPageHeroLayout'
import { getSceneLocationPresets } from '@/constants/location-presets'
import { patternDisplayLabel } from '@/constants/gesture-patterns'
import {
  formatBeijingClockNow,
  formatBeijingDateNow,
  formatBeijingDateTime,
  formatBeijingDateTimeAfterMinutes,
  formatBeijingDateAfterYears,
  formatBeijingDateTimeNow,
  isBeijingDateTimeBeforeNow,
  parseBeijingDateTime,
} from '@/utils/datetime'
import { UI_ICONS } from '@/constants/ui-icons'
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

type SceneType = 'class' | 'dorm' | 'internship' | 'custom'
type WizardStep = 1 | 2 | 3
type ExpandSection = 'scene' | 'time' | 'methods' | 'location' | 'reminder' | null

const groups = ref<TeacherGroup[]>([])
const showGroupPicker = ref(false)
const groupPickerSession = ref(0)
const showGesturePicker = ref(false)
const draftGroupIds = ref<number[]>([])
const groupFilterGrade = ref('')
const groupFilterMajor = ref('')
const groupFilterName = ref('')
const groupCreatedAfter = ref('')
const submitting = ref(false)
const scheduledPublishEnabled = ref(false)
const scheduledPublishAt = ref('')
const currentStep = ref<WizardStep>(1)
const expandedSection = ref<ExpandSection>(null)
const activeScene = ref<SceneType>('class')
const { brandBarStyle, backButtonStyle, navRightStyle, heroContentStyle } = useStudentPageHeroLayout()

const sceneTypes: Array<{ key: SceneType; label: string; iconSrc: string; hint: string }> = [
  { key: 'class', label: '课堂签到', iconSrc: UI_ICONS.class, hint: '教室定点签到' },
  { key: 'dorm', label: '查寝打卡', iconSrc: UI_ICONS.daily, hint: '按学生寝室定位' },
  { key: 'internship', label: '实习打卡', iconSrc: UI_ICONS.internship, hint: '按实习单位定位' },
  { key: 'custom', label: '自定义', iconSrc: UI_ICONS.default, hint: '自行配置各项规则' },
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
    gesture: { presetPattern: '12369' },
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
  if (method === 'location' && !next.includes('location') && expandedSection.value === 'location') {
    expandedSection.value = null
  }
  if (method === 'checkin_code' && next.includes('checkin_code') && !form.methodConfig!.checkin_code!.code) {
    form.methodConfig!.checkin_code!.code = generateCheckinCode(6)
  }
}

function regenerateCheckinCode() {
  form.methodConfig!.checkin_code!.code = generateCheckinCode(6)
}

function isPerStudentScene(scene: SceneType = activeScene.value): boolean {
  return scene === 'dorm' || scene === 'internship'
}

function applySceneDefaults(scene: SceneType) {
  activeScene.value = scene
  if (scene === 'custom') {
    form.templateName = '自定义'
    form.taskType = 'custom'
    return
  }

  form.description = ''
  form.taskType = 'attendance' as TeacherTaskType
  const preset = getSceneLocationPresets(scene)[0]
  if (scene === 'class') {
    form.templateName = '课堂签到'
    form.methods = ['location', 'face']
  } else if (scene === 'dorm') {
    form.templateName = '查寝打卡'
    form.methods = ['location', 'face']
  } else if (scene === 'internship') {
    form.templateName = '实习打卡'
    form.methods = ['location', 'attachment']
    form.methodConfig!.attachment!.label = '今日工作日志'
    if (form.methodConfig?.location) {
      form.methodConfig.location.radius = 500
    }
  }
  if (preset && form.methodConfig?.location) {
    form.methodConfig.location.placeName = preset.placeName
    form.methodConfig.location.radius = preset.radius
    form.methodConfig.location.longitude = 0
    form.methodConfig.location.latitude = 0
  }
}

function isLocationConfigured(): boolean {
  if (!hasMethod('location')) {
    return true
  }
  const location = form.methodConfig?.location
  if (isPerStudentScene()) {
    return (location?.radius ?? 0) > 0
  }
  if (!location?.placeName?.trim()) {
    return false
  }
  return Math.abs(location.latitude ?? 0) > 0.0001 && Math.abs(location.longitude ?? 0) > 0.0001
}

const selectedGroups = computed(() =>
  groups.value.filter((group) => form.groupIds.includes(group.id)),
)

const gradeOptions = computed(() => {
  const values = new Set<string>()
  groups.value.forEach((group) => {
    if (group.grade?.trim()) {
      values.add(group.grade.trim())
    }
  })
  return Array.from(values).sort()
})

const majorOptions = computed(() => {
  const values = new Set<string>()
  groups.value.forEach((group) => {
    if (group.major?.trim()) {
      values.add(group.major.trim())
    }
  })
  return Array.from(values).sort()
})

function matchesGroupFilters(group: TeacherGroup): boolean {
  if (groupFilterGrade.value && (group.grade ?? '') !== groupFilterGrade.value) {
    return false
  }
  if (groupFilterMajor.value && (group.major ?? '') !== groupFilterMajor.value) {
    return false
  }
  const keyword = groupFilterName.value.trim().toLowerCase()
  if (keyword) {
    const nameMatch = group.name.toLowerCase().includes(keyword)
    const majorMatch = (group.major ?? '').toLowerCase().includes(keyword)
    if (!nameMatch && !majorMatch) {
      return false
    }
  }
  if (groupCreatedAfter.value.trim()) {
    const threshold = parseBeijingDateTime(groupCreatedAfter.value)
    const created = parseBeijingDateTime(group.createdAt)
    if (threshold === null || created === null || created <= threshold) {
      return false
    }
  }
  return true
}

const filteredGroups = computed(() => groups.value.filter((group) => matchesGroupFilters(group)))

const groupFilterGradeLabel = computed(() => groupFilterGrade.value || '全部年份')
const groupFilterMajorLabel = computed(() => groupFilterMajor.value || '全部专业')

function openGroupGradePicker() {
  if (typeof uni === 'undefined') {
    return
  }
  const options = [{ key: '', label: '全部年份' }, ...gradeOptions.value.map((grade) => ({
    key: grade,
    label: grade,
  }))]
  uni.showActionSheet({
    itemList: options.map((item) => item.label),
    success: (result) => {
      const picked = options[result.tapIndex]
      if (picked) {
        groupFilterGrade.value = picked.key
      }
    },
  })
}

function openGroupMajorPicker() {
  if (typeof uni === 'undefined') {
    return
  }
  const options = [{ key: '', label: '全部专业' }, ...majorOptions.value.map((major) => ({
    key: major,
    label: major,
  }))]
  uni.showActionSheet({
    itemList: options.map((item) => item.label),
    success: (result) => {
      const picked = options[result.tapIndex]
      if (picked) {
        groupFilterMajor.value = picked.key
      }
    },
  })
}

const groupCreatedAfterSummary = computed(() => {
  if (!groupCreatedAfter.value.trim()) {
    return '不限'
  }
  return formatDisplayTime(groupCreatedAfter.value)
})

const sceneLabel = computed(() =>
  sceneTypes.find((item) => item.key === activeScene.value)?.label ?? '课堂签到',
)

const locationPickerScene = computed(() =>
  activeScene.value === 'custom' ? 'class' : activeScene.value,
)

const durationOptions = [1, 3, 5, 30] as const
const taskDurationMinutes = ref<number>(30)

const groupsSummary = computed(() => {
  if (selectedGroups.value.length === 0) {
    return '请选择班级'
  }
  if (selectedGroups.value.length === 1) {
    return selectedGroups.value[0].name
  }
  return `已选 ${selectedGroups.value.length} 个班级`
})

const draftSelectedCount = computed(() => draftGroupIds.value.length)

const gesturePatternSummary = computed(() =>
  patternDisplayLabel(form.methodConfig?.gesture?.presetPattern),
)

function openGesturePicker() {
  showGesturePicker.value = true
}

const timeSummary = computed(() => {
  if (!form.startsAt) {
    return '选择起始时间与时长'
  }
  return `时长 ${taskDurationMinutes.value} 分钟`
})

const startTimeDisplay = computed(() => formatDisplayTime(form.startsAt) || '请选择')

const endTimeDisplay = computed(() => formatDisplayTime(form.endsAt) || '自动计算')

const todayDate = computed(() => formatBeijingDateNow())
const datePickerStart = computed(() => todayDate.value)
const datePickerEnd = computed(() => formatBeijingDateAfterYears(5))

const startTimePickerStart = computed(() => {
  const date = parseDatePart(form.startsAt) || todayDate.value
  if (date === todayDate.value) {
    return formatBeijingClockNow()
  }
  return '00:00'
})

const scheduledPublishMinTime = computed(() => {
  const publishDate = parseDatePart(scheduledPublishAt.value) || todayDate.value
  if (publishDate === todayDate.value) {
    return formatBeijingClockNow()
  }
  return '00:00'
})

const scheduledPublishMaxTime = computed(() => {
  const publishDate = parseDatePart(scheduledPublishAt.value) || todayDate.value
  const startDate = parseDatePart(form.startsAt)
  if (startDate && publishDate === startDate) {
    return parseTimePart(form.startsAt) || '23:59'
  }
  return '23:59'
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
  return parts.join(' · ')
})

const locationSummary = computed(() => {
  if (!hasMethod('location')) {
    return '设置打卡地点范围'
  }
  const location = form.methodConfig?.location
  const radius = location?.radius ?? 0
  if (activeScene.value === 'dorm') {
    return radius > 0 ? `学生寝室附近 · ${radius} 米` : '设置查寝有效半径'
  }
  if (activeScene.value === 'internship') {
    return radius > 0 ? `学生实习单位附近 · ${radius} 米` : '设置实习打卡有效半径'
  }
  if (activeScene.value === 'custom') {
    if (location?.placeName?.trim()) {
      return `${location.placeName} · ${radius} 米`
    }
    return '设置打卡地点范围'
  }
  if (location?.placeName?.trim()) {
    return `${location.placeName} · ${radius} 米`
  }
  return '设置打卡地点范围'
})

const locationRowDisabled = computed(() => !hasMethod('location'))

const ruleSummary = computed(() => {
  const lines = [
    `任务名称：${form.title || '未填写'}`,
    `任务类型：${sceneLabel.value}`,
  ]
  if (activeScene.value === 'custom' && form.description?.trim()) {
    lines.push(`备注：${form.description.trim()}`)
  }
  lines.push(
    `发布对象：${groupsSummary.value}`,
    `打卡时间：${startTimeDisplay.value} 起 · ${taskDurationMinutes.value} 分钟 · ${endTimeDisplay.value} 止`,
    `打卡方式：${methodsSummary.value}`,
    `提醒规则：${reminderSummary.value}`,
    `任务周期：${scheduleModes.find((item) => item.value === form.scheduleMode)?.label ?? '一次任务'}`,
  )
  if (scheduledPublishEnabled.value) {
    lines.push(`定时发放：${formatDisplayTime(scheduledPublishAt.value) || '未设置'}`)
  } else {
    lines.push('发放方式：立即发布')
  }
  return lines
})

const step1Ready = computed(() => isStep1FieldsFilled() && isTaskTimeValid())

const step2Ready = computed(() => (form.methods ?? []).length > 0 && isLocationConfigured())

const readyToPublish = computed(
  () =>
    step1Ready.value &&
    step2Ready.value &&
    isScheduledPublishValid() &&
    !submitting.value,
)

function isScheduledPublishValid(): boolean {
  if (!scheduledPublishEnabled.value) {
    return true
  }
  const publishMs = parseBeijingDateTime(scheduledPublishAt.value)
  const startMs = parseBeijingDateTime(form.startsAt)
  if (publishMs === null) {
    return false
  }
  if (publishMs <= Date.now()) {
    return false
  }
  if (startMs !== null && publishMs > startMs) {
    return false
  }
  return true
}

function initScheduledPublishTime() {
  scheduledPublishAt.value = form.startsAt.trim() || formatBeijingDateTimeNow()
}

function onScheduledPublishToggle(event: { detail: { value: boolean } }) {
  scheduledPublishEnabled.value = Boolean(event.detail.value)
  if (scheduledPublishEnabled.value && !scheduledPublishAt.value.trim()) {
    initScheduledPublishTime()
  }
}

function applyScheduledPublishDateChange(date: string) {
  const time =
    parseTimePart(scheduledPublishAt.value) ||
    parseTimePart(form.startsAt) ||
    formatBeijingClockNow()
  scheduledPublishAt.value = `${date} ${time}`
}

function applyScheduledPublishTimeChange(time: string) {
  const date =
    parseDatePart(scheduledPublishAt.value) ||
    parseDatePart(form.startsAt) ||
    todayDate.value
  scheduledPublishAt.value = `${date} ${time}`
}

function isStep1FieldsFilled(): boolean {
  return (
    form.title.trim().length > 0 &&
    form.groupIds.length > 0 &&
    form.startsAt.trim().length > 0 &&
    form.endsAt.trim().length > 0
  )
}

function isTaskTimeValid(): boolean {
  const startMs = parseBeijingDateTime(form.startsAt)
  const endMs = parseBeijingDateTime(form.endsAt)
  return startMs !== null && endMs !== null && endMs > startMs
}

function normalizeTaskTimes() {
  if (!form.startsAt.trim()) {
    form.startsAt = clampStartDateTime(formatBeijingDateTimeNow())
  } else {
    form.startsAt = clampStartDateTime(form.startsAt)
  }
  syncEndFromStartAndDuration()
}

function toggleExpand(section: ExpandSection) {
  if (section === 'location' && locationRowDisabled.value) {
    showError('请先在打卡方式中选择「地理位置」')
    return
  }
  if (section === 'time' && expandedSection.value !== 'time') {
    initDefaultTaskTimes()
  }
  expandedSection.value = expandedSection.value === section ? null : section
}

function selectScene(scene: SceneType) {
  applySceneDefaults(scene)
}

function goToConfirm() {
  normalizeTaskTimes()

  if (!readyToPublish.value) {
    if (!form.title.trim()) {
      showError('请填写任务名称')
      return
    }
    if (!form.groupIds.length) {
      showError('请选择发布对象')
      return
    }
    if (!form.startsAt.trim()) {
      showError('请设置打卡起始时间')
      return
    }
    if (!isTaskTimeValid()) {
      showError('请重新选择打卡起始时间与时长')
      return
    }
    if (!(form.methods ?? []).length) {
      showError('请选择打卡方式')
      return
    }
    if (!isLocationConfigured()) {
      showError(
        hasMethod('location')
          ? (isPerStudentScene()
            ? (activeScene.value === 'internship'
              ? '请设置实习打卡定位半径'
              : '请设置查寝定位半径')
            : '请在地图上确认签到位置')
          : '请完成规则配置',
      )
      return
    }
    if (scheduledPublishEnabled.value && !isScheduledPublishValid()) {
      showError('请设置有效的定时发放时间（须晚于当前且不晚于打卡开始）')
      return
    }
    return
  }
  expandedSection.value = null
  currentStep.value = 3
}

function goToStep(step: WizardStep) {
  if (step === 3) {
    goToConfirm()
    return
  }
  currentStep.value = step
  expandedSection.value = null
}

function goBackToForm() {
  currentStep.value = 1
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

function initDefaultTaskTimes() {
  const now = formatBeijingDateTimeNow()
  form.startsAt = clampStartDateTime(form.startsAt.trim() || now)
  if (form.endsAt.trim()) {
    taskDurationMinutes.value = inferDurationMinutes(form.startsAt, form.endsAt)
  }
  syncEndFromStartAndDuration()
}

function inferDurationMinutes(start: string, end: string): number {
  const startMs = parseBeijingDateTime(start)
  const endMs = parseBeijingDateTime(end)
  if (!startMs || !endMs || endMs <= startMs) {
    return 30
  }
  const diff = Math.round((endMs - startMs) / 60000)
  const matched = durationOptions.find((item) => item === diff)
  if (matched) {
    return matched
  }
  return durationOptions.find((item) => item >= diff) ?? 30
}

function syncEndFromStartAndDuration() {
  const startMs = parseBeijingDateTime(form.startsAt)
  if (!startMs) {
    return
  }
  form.endsAt = formatBeijingDateTimeAfterMinutes(taskDurationMinutes.value, startMs)
}

function resolveStartFallbackTime(date: string): string {
  if (date === todayDate.value) {
    return formatBeijingClockNow()
  }
  return '00:00'
}

function clampStartDateTime(value: string): string {
  const normalized = formatBeijingDateTime(value)
  if (isBeijingDateTimeBeforeNow(normalized)) {
    return formatBeijingDateTimeNow()
  }
  return normalized
}

function applyStartDateChange(date: string) {
  const nextDate = date < datePickerStart.value ? datePickerStart.value : date
  const time = parseTimePart(form.startsAt) || resolveStartFallbackTime(nextDate)
  form.startsAt = clampStartDateTime(`${nextDate} ${time}`)
  syncEndFromStartAndDuration()
}

function applyStartTimeChange(time: string) {
  const date = parseDatePart(form.startsAt) || formatBeijingDateNow()
  form.startsAt = clampStartDateTime(`${date} ${time}`)
  syncEndFromStartAndDuration()
}

function selectDuration(minutes: number) {
  taskDurationMinutes.value = minutes
  syncEndFromStartAndDuration()
}

function toggleDraftGroup(id: number) {
  const current = draftGroupIds.value
  draftGroupIds.value = current.includes(id)
    ? current.filter((groupId) => groupId !== id)
    : [...current, id]
}

function openGroupPicker() {
  draftGroupIds.value = [...form.groupIds]
  groupPickerSession.value += 1
  showGroupPicker.value = true
}

function closeGroupPicker() {
  showGroupPicker.value = false
}

function confirmGroupPicker() {
  if (draftGroupIds.value.length === 0) {
    showError('请至少选择一个班级')
    return
  }
  form.groupIds = [...draftGroupIds.value]
  closeGroupPicker()
}

function formatGroupCreatedAt(value?: string): string {
  if (!value?.trim()) {
    return '创建时间未知'
  }
  return formatDisplayTime(formatBeijingDateTime(value))
}

function groupMetaSubtitle(group: TeacherGroup): string {
  const parts: string[] = []
  if (group.grade) {
    parts.push(group.grade)
  }
  if (group.major) {
    parts.push(group.major)
  }
  parts.push(`${group.studentCount} 人`)
  parts.push(`创建于 ${formatGroupCreatedAt(group.createdAt)}`)
  return parts.join(' · ')
}

function applyGroupCreatedDate(date: string) {
  const time = parseTimePart(groupCreatedAfter.value) || '00:00'
  groupCreatedAfter.value = `${date} ${time}`
}

function applyGroupCreatedTime(time: string) {
  const date = parseDatePart(groupCreatedAfter.value) || todayDate.value
  groupCreatedAfter.value = `${date} ${time}`
}

function clearGroupCreatedAfter() {
  groupCreatedAfter.value = ''
}

function resetGroupFilters() {
  groupFilterGrade.value = ''
  groupFilterMajor.value = ''
  groupFilterName.value = ''
  groupCreatedAfter.value = ''
}

async function submitTask() {
  if (!readyToPublish.value) {
    return
  }

  initDefaultTaskTimes()
  normalizeTaskTimes()

  submitting.value = true

  try {
    if (typeof uni === 'undefined' || typeof uni.request !== 'function') {
      return
    }

    const createdTask = await createTeacherTask({
      ...form,
      checkinScene: activeScene.value,
      scheduledPublishAt: scheduledPublishEnabled.value ? scheduledPublishAt.value : undefined,
    })
    if (scheduledPublishEnabled.value) {
      logInfo('教师任务定时发放已设置', {
        taskId: createdTask.id,
        scheduledPublishAt: scheduledPublishAt.value,
      })
      showSuccess('已设置定时发放')
    } else {
      await publishTeacherTask(createdTask.id)
      logInfo('教师任务创建成功', { taskId: createdTask.id })
      showSuccess('已发布')
    }
    uni.redirectTo({ url: `/pages/teacher/task-detail?id=${createdTask.id}` })
  } catch (error) {
    showError(error, '发布失败')
  } finally {
    submitting.value = false
  }
}

function saveDraft() {
  if (typeof uni === 'undefined') {
    return
  }
  uni.showToast({ title: '草稿已保存', icon: 'success' })
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

onMounted(async () => {
  initDefaultTaskTimes()
  await loadGroups()
})

onShow(() => {
  if (typeof uni === 'undefined') {
    return
  }
  uni.setNavigationBarTitle({ title: '' })
  if (form.startsAt.trim()) {
    normalizeTaskTimes()
  }
})
</script>

<route lang="json">
{
  "style": {
    "navigationStyle": "custom",
    "navigationBarTitleText": "",
    "backgroundColor": "#F5F8FC"
  }
}
</route>

<template>
  <view class="create-page">
    <scroll-view scroll-y class="create-page__scroll home-page">
      <view class="home-page__hero-block">
        <view class="home-page__hero">
          <view class="home-page__hero-visual" aria-hidden="true">
            <view class="home-page__hero-bg-window">
              <image class="home-page__hero-bg" src="/static/home.png" mode="widthFix" />
            </view>
          </view>

          <view class="create-page__nav-bar" :style="brandBarStyle">
            <view
              class="create-page__back"
              :style="backButtonStyle"
              aria-label="返回"
              @click="goBack"
            ></view>
            <view class="create-page__nav-spacer" :style="navRightStyle"></view>
          </view>

          <view class="home-page__hero-content" :style="heroContentStyle">
            <text class="home-page__greeting">创建考勤任务</text>
            <text class="home-page__slogan">灵活设置，高效管理考勤</text>
          </view>
        </view>

        <view class="create-page__sheet">
          <view class="home-page__panel-card create-page__panel">
        <view class="create-page__steps">
          <view
            v-for="(item, index) in wizardSteps"
            :key="item.step"
            class="create-page__step-wrap"
            @click="goToStep(item.step)"
          >
            <view class="create-page__step-item">
              <view
                class="create-page__step-dot"
                :class="{
                  'create-page__step-dot--active': currentStep === item.step || (currentStep < 3 && item.step === 1),
                  'create-page__step-dot--done': currentStep > item.step,
                }"
              >
                <text>{{ item.step }}</text>
              </view>
              <text
                class="create-page__step-label"
                :class="{
                  'create-page__step-label--active': currentStep === item.step || (currentStep < 3 && item.step === 1),
                }"
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

        <view v-if="currentStep < 3" class="create-page__form">
          <view class="form-row form-row--input">
            <view class="form-row__icon"><VectorIcon :src="UI_ICONS.document" size="32rpx" /></view>
            <text class="form-row__label">任务名称</text>
            <input
              v-model="form.title"
              class="form-row__input"
              maxlength="40"
              placeholder="请输入任务名称"
              placeholder-class="form-row__placeholder"
            />
          </view>

          <view class="form-row form-row--select" @click="toggleExpand('scene')">
            <view class="form-row__icon"><VectorIcon :src="UI_ICONS.grid" size="32rpx" /></view>
            <text class="form-row__label">任务类型</text>
            <text class="form-row__value">{{ sceneLabel }}</text>
            <text
              class="form-row__chevron"
              :class="{ 'form-row__chevron--open': expandedSection === 'scene' }"
            >›</text>
          </view>
          <view v-if="expandedSection === 'scene'" class="form-expand">
            <text class="scene-section__hint">常用场景自动填充规则；选「自定义」后请自行设置打卡方式、地点等</text>
            <view class="type-chips">
              <view
                v-for="scene in sceneTypes"
                :key="scene.key"
                class="type-chip"
                :class="{ 'type-chip--active': activeScene === scene.key }"
                @click="selectScene(scene.key)"
              >
                <VectorIcon class="type-chip__icon" :src="scene.iconSrc" size="36rpx" />
                <text class="type-chip__label">{{ scene.label }}</text>
                <text class="type-chip__hint">{{ scene.hint }}</text>
              </view>
            </view>
          </view>

          <view v-if="activeScene === 'custom'" class="form-row form-row--input">
            <view class="form-row__icon"><VectorIcon :src="UI_ICONS.info" size="32rpx" /></view>
            <text class="form-row__label">备注</text>
            <input
              v-model="form.description"
              class="form-row__input"
              maxlength="100"
              placeholder="选填，说明本次考勤用途"
              placeholder-class="form-row__placeholder"
            />
          </view>

          <view class="form-row form-row--select" @click="openGroupPicker">
            <view class="form-row__icon"><VectorIcon :src="UI_ICONS.classes" size="32rpx" /></view>
            <text class="form-row__label">发布对象</text>
            <text
              class="form-row__value"
              :class="{ 'form-row__value--placeholder': selectedGroups.length === 0 }"
            >
              {{ groupsSummary }}
            </text>
            <text class="form-row__chevron">›</text>
          </view>

          <view
            class="form-row form-row--select form-row--time"
            :class="{ 'form-row--stack': expandedSection !== 'time' && form.startsAt }"
            @click="toggleExpand('time')"
          >
            <view class="form-row__head">
              <view class="form-row__icon"><VectorIcon :src="UI_ICONS.clock" size="32rpx" /></view>
              <text class="form-row__label">打卡时间</text>
              <text
                v-if="!form.startsAt || expandedSection === 'time'"
                class="form-row__value"
                :class="{ 'form-row__value--placeholder': !form.startsAt }"
              >
                {{ timeSummary }}
              </text>
              <text
                class="form-row__chevron"
                :class="{ 'form-row__chevron--open': expandedSection === 'time' }"
              >›</text>
            </view>
            <view v-if="expandedSection !== 'time' && form.startsAt" class="time-preview">
              <view class="time-preview__field">
                <text class="time-preview__label">起始时间</text>
                <text class="time-preview__value">{{ startTimeDisplay }}</text>
              </view>
              <view class="time-preview__field">
                <text class="time-preview__label">结束时间</text>
                <text class="time-preview__value">{{ endTimeDisplay }}</text>
              </view>
            </view>
          </view>
          <view v-if="expandedSection === 'time'" class="form-expand">
            <view class="time-block">
              <text class="time-block__label">起始时间</text>
              <view class="datetime-row">
                <ThemeDatePicker
                  class="picker-box-wrap"
                  :model-value="parseDatePart(form.startsAt) || todayDate"
                  :min-date="datePickerStart"
                  :max-date="datePickerEnd"
                  @change="applyStartDateChange"
                />
                <ThemeTimePicker
                  :model-value="parseTimePart(form.startsAt) || startTimePickerStart"
                  :min-time="startTimePickerStart"
                  @change="applyStartTimeChange"
                />
              </view>
            </view>
            <view class="time-block">
              <text class="time-block__label">打卡时长</text>
              <view class="duration-row">
                <view
                  v-for="minutes in durationOptions"
                  :key="minutes"
                  class="duration-chip"
                  :class="{ 'duration-chip--active': taskDurationMinutes === minutes }"
                  @click="selectDuration(minutes)"
                >
                  {{ minutes }} 分钟
                </view>
              </view>
            </view>
            <view class="time-block">
              <text class="time-block__label">结束时间</text>
              <view class="time-readonly">
                <text>{{ endTimeDisplay }}</text>
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

          <view class="form-row form-row--select" @click="toggleExpand('methods')">
            <view class="form-row__icon"><VectorIcon :src="UI_ICONS.location" size="32rpx" /></view>
            <text class="form-row__label">打卡方式</text>
            <text
              class="form-row__value"
              :class="{ 'form-row__value--placeholder': !(form.methods ?? []).length }"
            >
              {{ methodsSummary }}
            </text>
            <text
              class="form-row__chevron"
              :class="{ 'form-row__chevron--open': expandedSection === 'methods' }"
            >›</text>
          </view>
          <view v-if="expandedSection === 'methods'" class="form-expand">
            <view class="chip-grid">
              <view
                v-for="method in methodOptions"
                :key="method.value"
                :class="['choice-chip', { active: hasMethod(method.value) }]"
                @click="toggleMethod(method.value)"
              >
                <view class="chip-title-row">
                  <VectorIcon v-if="hasMethod(method.value)" :src="UI_ICONS.check" size="24rpx" />
                  <text class="chip-title">{{ method.label }}</text>
                </view>
                <text class="chip-subtitle">{{ method.hint }}</text>
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
                  <view class="toggle-row__switch">
                    <switch
                      :checked="Boolean(form.methodConfig!.attachment!.required)"
                      color="#1677ff"
                      @change="form.methodConfig!.attachment!.required = ($event as any).detail.value"
                    />
                  </view>
                </view>
              </view>
            </view>

            <view v-if="hasMethod('gesture')" class="config-block config-block--plain">
              <text class="config-title">手势配置</text>
              <view class="gesture-config-row" @click="openGesturePicker">
                <text class="gesture-config-row__label">预设图案</text>
                <text class="gesture-config-row__value">{{ gesturePatternSummary }}</text>
                <text class="gesture-config-row__chevron">›</text>
              </view>
            </view>
          </view>

          <view
            class="form-row form-row--select"
            :class="{ 'form-row--disabled': locationRowDisabled }"
            @click="toggleExpand('location')"
          >
            <view class="form-row__icon"><VectorIcon :src="UI_ICONS.search" size="32rpx" /></view>
            <text class="form-row__label">地点规则</text>
            <text
              class="form-row__value"
              :class="{ 'form-row__value--placeholder': locationRowDisabled || !isLocationConfigured() }"
            >
              {{ locationSummary }}
            </text>
            <text
              class="form-row__chevron"
              :class="{ 'form-row__chevron--open': expandedSection === 'location' }"
            >›</text>
          </view>
          <view v-if="expandedSection === 'location'" class="form-expand">
            <view class="config-block config-block--plain">
              <view v-if="isPerStudentScene()" class="dorm-location-hint">
                <text class="dorm-location-hint__title">
                  {{ activeScene === 'internship' ? '按学生实习单位位置校验' : '按学生寝室位置校验' }}
                </text>
                <text class="dorm-location-hint__desc">
                  {{
                    activeScene === 'internship'
                      ? '系统将读取每位学生档案中的实习单位坐标，学生需在本人实习地附近打卡，无需教师统一选点。'
                      : '系统将读取每位学生档案中的寝室坐标，学生需在本人寝室附近打卡，无需教师统一选点。'
                  }}
                </text>
                <view class="field-block">
                  <text class="field-label">有效半径（米）</text>
                  <input
                    :value="String(form.methodConfig!.location!.radius ?? (activeScene === 'internship' ? 500 : 200))"
                    class="field-input"
                    type="number"
                    @input="form.methodConfig!.location!.radius = Number(($event as any).detail.value || (activeScene === 'internship' ? 500 : 200))"
                  />
                </view>
              </view>
              <TeacherLocationPicker
                v-else
                v-model="form.methodConfig!.location!"
                :scene="locationPickerScene"
              />
            </view>
          </view>

          <view class="form-row form-row--select" @click="toggleExpand('reminder')">
            <view class="form-row__icon"><VectorIcon :src="UI_ICONS.bell" size="32rpx" /></view>
            <text class="form-row__label">提醒规则</text>
            <text class="form-row__value">{{ reminderSummary }}</text>
            <text
              class="form-row__chevron"
              :class="{ 'form-row__chevron--open': expandedSection === 'reminder' }"
            >›</text>
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
              <text class="field-label">到点自动结束</text>
              <view class="toggle-row__switch">
                <switch
                  :checked="Boolean(form.advancedRules?.autoEnd)"
                  color="#1677ff"
                  @change="form.advancedRules!.autoEnd = ($event as any).detail.value"
                />
              </view>
            </view>
          </view>

          <view class="toggle-row toggle-row--standalone">
            <text class="field-label">定时发放</text>
            <view class="toggle-row__switch">
              <switch
                :checked="scheduledPublishEnabled"
                color="#1677ff"
                @change="onScheduledPublishToggle"
              />
            </view>
          </view>
          <view v-if="scheduledPublishEnabled" class="form-expand form-expand--scheduled">
            <view class="time-block">
              <text class="time-block__label">发放时间</text>
              <view class="datetime-row">
                <ThemeDatePicker
                  class="picker-box-wrap"
                  :model-value="parseDatePart(scheduledPublishAt) || todayDate"
                  :min-date="datePickerStart"
                  :max-date="parseDatePart(form.startsAt) || datePickerEnd"
                  @change="applyScheduledPublishDateChange"
                />
                <ThemeTimePicker
                  :model-value="parseTimePart(scheduledPublishAt) || scheduledPublishMinTime"
                  :min-time="scheduledPublishMinTime"
                  :max-time="scheduledPublishMaxTime"
                  @change="applyScheduledPublishTimeChange"
                />
              </view>
              <text class="scheduled-hint">发放时间须晚于当前，且不晚于打卡开始时间</text>
            </view>
          </view>
        </view>

        <view v-else class="create-page__form">
          <view class="confirm-card">
            <text class="confirm-card__title">发布前确认</text>
            <text v-for="(item, index) in ruleSummary" :key="`rule-${index}`" class="confirm-card__line">{{ item }}</text>
          </view>
        </view>

        <view class="create-page__footer">
          <view class="create-page__tip">
            <VectorIcon class="create-page__tip-icon-img" :src="UI_ICONS.check" size="28rpx" />
            <text class="create-page__tip-text">
              {{
                scheduledPublishEnabled
                  ? '任务将在设定时间自动发放，学生届时收到通知'
                  : '发布后，学生将收到任务通知并按规则进行打卡'
              }}
            </text>
          </view>

          <template v-if="currentStep < 3">
            <view
              class="create-page__btn"
              :class="{ 'create-page__btn--disabled': !readyToPublish }"
              @click="goToConfirm"
            >
              立即发布
            </view>
            <view class="create-page__btn create-page__btn--ghost" @click="saveDraft">
              保存草稿
            </view>
          </template>
          <template v-else>
            <view
              class="create-page__btn"
              :class="{ 'create-page__btn--disabled': !readyToPublish }"
              @click="submitTask"
            >
              {{
                submitting
                  ? scheduledPublishEnabled
                    ? '提交中...'
                    : '发布中...'
                  : scheduledPublishEnabled
                    ? '确认定时发放'
                    : '确认发布'
              }}
            </view>
            <view class="create-page__btn create-page__btn--ghost" @click="goBackToForm">
              返回修改
            </view>
          </template>
        </view>
          </view>
        </view>

      <view class="create-page__safe-bottom"></view>
      </view>
    </scroll-view>

    <view v-if="showGroupPicker" class="group-picker-mask" @click="closeGroupPicker">
      <view class="group-picker-sheet" :key="groupPickerSession" @click.stop>
        <view class="group-picker-header">
          <text class="group-picker-title">选择发布对象</text>
          <view class="group-picker-close" @click="closeGroupPicker">
            <VectorIcon :src="UI_ICONS.close" size="32rpx" />
          </view>
        </view>

        <view class="group-picker-toolbar">
          <view class="group-picker-search">
            <VectorIcon class="group-picker-search__icon" :src="UI_ICONS.search" size="32rpx" />
            <input
              v-model="groupFilterName"
              class="group-picker-search__input"
              maxlength="40"
              placeholder="搜索班级名称、专业"
              confirm-type="search"
            />
            <view
              v-if="groupFilterName"
              class="group-picker-search__clear"
              @click="groupFilterName = ''"
            >
              ×
            </view>
          </view>
          <view class="group-picker-dropdowns">
            <view class="group-picker-dropdown" @click="openGroupMajorPicker">
              <text class="group-picker-dropdown__text">{{ groupFilterMajorLabel }}</text>
              <text class="group-picker-dropdown__arrow">▾</text>
            </view>
            <view class="group-picker-dropdown" @click="openGroupGradePicker">
              <text class="group-picker-dropdown__text">{{ groupFilterGradeLabel }}</text>
              <text class="group-picker-dropdown__arrow">▾</text>
            </view>
          </view>
        </view>

        <scroll-view scroll-y class="group-picker-body">
          <view class="group-filter-block">
            <text class="field-label">创建时间</text>
            <text class="group-filter-hint">仅显示该时间之后创建的班级（便于找到新建班级）</text>
            <view class="datetime-row">
              <ThemeDatePicker
                class="picker-box-wrap"
                :model-value="parseDatePart(groupCreatedAfter) || todayDate"
                :min-date="formatBeijingDateAfterYears(-10)"
                :max-date="datePickerEnd"
                @change="applyGroupCreatedDate"
              />
              <ThemeTimePicker
                :model-value="parseTimePart(groupCreatedAfter) || '00:00'"
                @change="applyGroupCreatedTime"
              />
            </view>
            <view class="group-filter-actions">
              <text class="group-filter-summary">当前：{{ groupCreatedAfterSummary }}</text>
              <text
                v-if="groupCreatedAfter"
                class="group-filter-clear"
                @click="clearGroupCreatedAfter"
              >
                清除
              </text>
              <text
                v-if="groupFilterGrade || groupFilterMajor || groupFilterName || groupCreatedAfter"
                class="group-filter-clear"
                @click="resetGroupFilters"
              >
                重置筛选
              </text>
            </view>
          </view>

          <view class="chip-grid group-picker-list">
            <view
              v-for="group in filteredGroups"
              :key="group.id"
              :class="['choice-chip', { active: draftGroupIds.includes(group.id) }]"
              @click="toggleDraftGroup(group.id)"
            >
              <text class="chip-title">{{ group.name }}</text>
              <text class="chip-subtitle">{{ groupMetaSubtitle(group) }}</text>
            </view>
            <text v-if="groups.length === 0" class="empty-line">暂无可选班级，请先在班级管理中创建。</text>
            <text v-else-if="filteredGroups.length === 0" class="empty-line">没有符合条件的班级，请调整筛选条件。</text>
          </view>
        </scroll-view>

        <view class="group-picker-footer">
          <text class="group-picker-footer__hint">已选 {{ draftSelectedCount }} 个班级</text>
          <view class="group-picker-footer__actions">
            <view class="group-picker-btn group-picker-btn--ghost" @click="closeGroupPicker">取消</view>
            <view class="group-picker-btn" @click="confirmGroupPicker">确定</view>
          </view>
        </view>
      </view>
    </view>

    <GesturePatternModal
      v-model:visible="showGesturePicker"
      v-model="form.methodConfig!.gesture!.presetPattern"
    />
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;
@use '@/styles/student-page-hero.scss' as hero;

.create-page {
  min-height: 100vh;
  background: $page-bg;
}

.create-page__scroll {
  height: 100vh;
}

.create-page__scroll.home-page {
  background: $page-bg;
}

.create-page__nav-bar {
  position: absolute;
  left: 0;
  right: 0;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24rpx 0 32rpx;
  box-sizing: border-box;
}

.create-page__back {
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

.create-page__nav-spacer {
  flex-shrink: 0;
}

.create-page__sheet {
  position: relative;
  z-index: 4;
  margin-top: calc(-1 * #{hero.$student-hero-overlap-card-height} * 0.25 - 5px);
  padding: 0 24rpx;
  box-sizing: border-box;
}

.create-page__panel {
  padding: 28rpx 24rpx 32rpx;
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

.form-row--input {
  cursor: default;
}

.form-row--select {
  transition: background 0.2s ease;
}

.form-row--select:active {
  background: rgba($primary, 0.04);
}

.form-row--disabled {
  opacity: 0.72;
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

.form-row--time.form-row--stack .form-row__head {
  width: 100%;
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
  font-weight: 400;
}

.form-row__input {
  flex: 1;
  min-width: 0;
  height: 48rpx;
  color: $text-primary;
  font-size: 26rpx;
  text-align: right;
}

.form-row__placeholder {
  color: $text-muted;
  font-weight: 400;
}

.form-row__chevron {
  flex-shrink: 0;
  color: $text-muted;
  font-size: 32rpx;
  line-height: 1;
  transition: transform 0.2s ease;
}

.form-row__chevron--open {
  transform: rotate(90deg);
  color: $primary;
}

.scene-section__hint {
  display: block;
  margin-bottom: 12rpx;
  color: $text-secondary;
  font-size: 22rpx;
  line-height: 1.5;
}

.type-chips {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12rpx;
  padding-top: 4rpx;
}

.type-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
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

.type-chip__hint {
  color: rgba(15, 23, 42, 0.45);
  font-size: 18rpx;
  line-height: 1.3;
  text-align: center;
}

.type-chip--active .type-chip__hint {
  color: rgba($primary, 0.72);
}

.form-expand {
  padding: 0 0 20rpx 64rpx;
  animation: form-expand-in 0.2s ease;
}

@keyframes form-expand-in {
  from {
    opacity: 0;
    transform: translateY(-8rpx);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
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

.form-expand--groups {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.group-picker-mask {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  background: rgba(15, 23, 42, 0.45);
}

.group-picker-sheet {
  display: flex;
  width: 100%;
  max-height: 86vh;
  flex-direction: column;
  border-radius: 28rpx 28rpx 0 0;
  background: #fff;
  box-shadow: 0 -12rpx 40rpx rgba(15, 23, 42, 0.12);
}

.group-picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 28rpx 32rpx 16rpx;
  border-bottom: 1rpx solid rgba(15, 23, 42, 0.06);
}

.group-picker-title {
  color: $text-primary;
  font-size: 34rpx;
  font-weight: 700;
}

.group-picker-close {
  display: flex;
  width: 56rpx;
  height: 56rpx;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #f5f8ff;
}

.group-picker-toolbar {
  flex-shrink: 0;
  padding: 16rpx 32rpx 20rpx;
  border-bottom: 1rpx solid rgba(15, 23, 42, 0.06);
  background: #fff;
}

.group-picker-search {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 0 20rpx;
  height: 72rpx;
  border-radius: 999rpx;
  background: #f3f6fb;
}

.group-picker-search__icon {
  flex-shrink: 0;
  opacity: 0.55;
}

.group-picker-search__input {
  flex: 1;
  min-width: 0;
  height: 72rpx;
  color: $text-primary;
  font-size: 28rpx;
}

.group-picker-search__clear {
  flex-shrink: 0;
  width: 40rpx;
  height: 40rpx;
  color: $text-muted;
  font-size: 32rpx;
  line-height: 40rpx;
  text-align: center;
}

.group-picker-dropdowns {
  display: flex;
  gap: 16rpx;
  margin-top: 16rpx;
}

.group-picker-dropdown {
  display: flex;
  flex: 1;
  min-width: 0;
  height: 72rpx;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 0 20rpx;
  border-radius: 16rpx;
  background: #f3f6fb;
}

.group-picker-dropdown:active {
  opacity: 0.88;
}

.group-picker-dropdown__text {
  overflow: hidden;
  color: $text-primary;
  font-size: 26rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.group-picker-dropdown__arrow {
  flex-shrink: 0;
  color: $text-secondary;
  font-size: 22rpx;
}

.group-picker-body {
  flex: 1;
  min-height: 0;
  max-height: calc(86vh - 320rpx);
  padding: 24rpx 32rpx;
  box-sizing: border-box;
}

.group-picker-list {
  margin-top: 8rpx;
}

.group-picker-footer {
  padding: 16rpx 32rpx calc(16rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid rgba(15, 23, 42, 0.06);
  background: #fff;
}

.group-picker-footer__hint {
  display: block;
  margin-bottom: 16rpx;
  color: $text-secondary;
  font-size: 24rpx;
  text-align: center;
}

.group-picker-footer__actions {
  display: flex;
  gap: 16rpx;
}

.group-picker-btn {
  display: flex;
  flex: 1;
  height: 88rpx;
  align-items: center;
  justify-content: center;
  border-radius: 999rpx;
  background: $primary;
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
}

.group-picker-btn--ghost {
  background: #fff;
  border: 2rpx solid rgba($primary, 0.25);
  color: $primary;
}

.gesture-config-row {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 22rpx 24rpx;
  border-radius: 16rpx;
  background: #f7faff;
}

.gesture-config-row__label {
  color: $text-secondary;
  font-size: 26rpx;
}

.gesture-config-row__value {
  flex: 1;
  min-width: 0;
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 600;
  text-align: right;
}

.gesture-config-row__chevron {
  color: $text-muted;
  font-size: 34rpx;
  line-height: 1;
}

.group-filter-block {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.group-filter-hint {
  color: $text-secondary;
  font-size: 22rpx;
  line-height: 1.5;
}

.group-filter-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 16rpx;
  margin-top: 8rpx;
}

.group-filter-summary {
  color: $text-secondary;
  font-size: 22rpx;
}

.group-filter-clear {
  color: $primary;
  font-size: 22rpx;
}

.filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 10rpx;
}

.filter-chip {
  padding: 10rpx 18rpx;
  border: 1rpx solid rgba(15, 23, 42, 0.08);
  border-radius: 999rpx;
  background: #f7faff;
  color: $text-secondary;
  font-size: 22rpx;
}

.filter-chip--active {
  border-color: rgba($primary, 0.35);
  background: rgba($primary, 0.1);
  color: $primary;
  font-weight: 600;
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

.chip-title-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
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

.time-preview {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  padding: 4rpx 0 8rpx 64rpx;
}

.time-preview__field {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.time-preview__label {
  flex-shrink: 0;
  color: $text-secondary;
  font-size: 24rpx;
}

.time-preview__value {
  flex: 1;
  min-width: 0;
  color: $text-primary;
  font-size: 26rpx;
  font-weight: 600;
  text-align: right;
}

.duration-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.duration-chip {
  flex: 1;
  min-width: calc(50% - 6rpx);
  padding: 18rpx 0;
  border: 1rpx solid rgba(15, 23, 42, 0.08);
  border-radius: 14rpx;
  background: #f7faff;
  color: $text-secondary;
  font-size: 26rpx;
  text-align: center;
}

.duration-chip--active {
  border-color: rgba($primary, 0.35);
  background: $primary-light;
  color: $primary;
  font-weight: 700;
}

.time-readonly {
  display: flex;
  align-items: center;
  min-height: 80rpx;
  padding: 22rpx 24rpx;
  border-radius: 16rpx;
  background: #f0f4fa;
  color: $text-primary;
  font-size: 28rpx;
  font-weight: 600;
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
  margin-top: 16rpx;
}

.form-expand > .field-block:first-child {
  margin-top: 0;
}

.picker-box-wrap {
  flex: 1;
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

.config-block--plain {
  margin-top: 0;
  padding: 0;
  border: none;
  background: transparent;
}

.config-title {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: $primary;
}

.dorm-location-hint {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-top: 12rpx;
}

.dorm-location-hint__title {
  font-size: 28rpx;
  font-weight: 700;
  color: $text-primary;
}

.dorm-location-hint__desc {
  font-size: 24rpx;
  line-height: 1.6;
  color: $text-secondary;
}

.toggle-row {
  justify-content: space-between;
  align-items: center;
  min-height: 72rpx;
  margin-top: 20rpx;
  padding: 4rpx 0;
}

.toggle-row .field-label {
  margin-bottom: 0;
  flex: 1;
}

.toggle-row__switch {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  width: 84rpx;
  height: 48rpx;
  overflow: hidden;
}

.toggle-row__switch switch {
  transform: scale(0.68);
  transform-origin: center center;
}

.toggle-row--standalone {
  margin: 8rpx 0 0;
  padding: 20rpx 24rpx;
  border-radius: 20rpx;
  background: #fff;
}

.form-expand--scheduled {
  margin-top: 0;
  padding-top: 0;
}

.scheduled-hint {
  display: block;
  margin-top: 12rpx;
  color: $text-secondary;
  font-size: 22rpx;
  line-height: 1.5;
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
  margin-top: 24rpx;
  padding-top: 8rpx;
}

.create-page__tip {
  display: flex;
  align-items: flex-start;
  gap: 10rpx;
  margin-bottom: 24rpx;
}

.create-page__tip-icon-img {
  flex-shrink: 0;
  margin-top: 2rpx;
  color: $primary;
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
  background: linear-gradient(135deg, $primary 0%, $sky-blue 100%);
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

.create-page__btn--ghost {
  margin-top: 20rpx;
  background: #fff;
  color: $primary;
  border: 2rpx solid rgba($primary, 0.35);
  box-shadow: none;
}

.create-page__safe-bottom {
  height: calc(env(safe-area-inset-bottom) + 24rpx);
}
</style>

<style lang="scss">
@use '@/styles/home-hero.scss';
</style>
