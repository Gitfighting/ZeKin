<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import { logInfo, showError, showSuccess } from '@/services/feedback'
import {
  createTeacherTask,
  getTeacherGroups,
  type CreateTeacherTaskPayload,
  type TeacherGroup,
  type TeacherTaskTemplate,
  type TeacherTaskType,
} from '@/services/teacher'

const groups = ref<TeacherGroup[]>([])
const showAdvanced = ref(false)
const submitting = ref(false)

const taskTypes: Array<{ label: string; value: TeacherTaskType }> = [
  { label: '考勤', value: 'attendance' },
  { label: '照片', value: 'photo' },
  { label: '位置', value: 'location' },
  { label: '自定义', value: 'custom' },
]

const templates = ref<TeacherTaskTemplate[]>([])

const form = reactive<CreateTeacherTaskPayload>({
  title: '',
  description: '',
  groupIds: [],
  taskType: 'attendance',
  templateName: '',
  startsAt: '',
  endsAt: '',
  advancedRules: {
    allowLateMinutes: 0,
    needPhoto: false,
    allowAppeal: true,
    autoEnd: true,
  },
})

const selectedGroups = computed(() =>
  groups.value.filter((group) => form.groupIds.includes(group.id)),
)

const ruleSummary = computed(() => {
  const rules = form.advancedRules ?? {}

  return [
    `${selectedGroups.value.length} 个分组`,
    form.templateName ? `模板 ${form.templateName}` : '未选择模板',
    `迟到宽限 ${rules.allowLateMinutes ?? 0} 分钟`,
    rules.needPhoto ? '需照片佐证' : '无需照片',
    rules.allowAppeal ? '允许申诉' : '不允许申诉',
    rules.autoEnd ? '到点自动结束' : '手动结束',
  ]
})

const readyToPublish = computed(
  () =>
    form.title.trim().length > 0 &&
    form.startsAt.trim().length > 0 &&
    form.endsAt.trim().length > 0 &&
    form.groupIds.length > 0 &&
    !submitting.value,
)

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
  if (typeof uni === 'undefined') {
    return
  }

  uni.navigateBack({ delta: 1 })
}

onMounted(loadGroups)
</script>

<template>
  <view class="teacher-page">
    <view class="top-bar">
      <text class="top-back" @click="goBack">< 返回</text>
      <text class="top-title">创建任务</text>
      <text class="top-action">{{ form.templateName || '自定义' }}</text>
    </view>

    <view class="hero-card">
      <text class="hero-title">填写任务信息后发布。</text>
      <text class="hero-subtitle">选择真实分组并填写时间，接口失败时不会使用本地样例代替。</text>
    </view>

    <view class="section-card">
      <text class="section-title">基础信息</text>
      <view class="field-block">
        <text class="field-label">任务标题</text>
        <input v-model="form.title" class="field-input" placeholder="请输入任务标题" />
      </view>
      <view class="field-block">
        <text class="field-label">任务说明</text>
        <textarea v-model="form.description" class="field-textarea" maxlength="120" />
      </view>
      <view class="field-grid">
        <view class="field-block">
          <text class="field-label">开始时间</text>
          <input v-model="form.startsAt" class="field-input" />
        </view>
        <view class="field-block">
          <text class="field-label">结束时间</text>
          <input v-model="form.endsAt" class="field-input" />
        </view>
      </view>
    </view>

    <view class="section-card">
      <text class="section-title">选择分组</text>
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

    <view class="section-card">
      <text class="section-title">选择模板</text>
      <view class="compact-selector">
        <view
          v-for="type in taskTypes"
          :key="type.value"
          :class="['compact-option', { active: form.taskType === type.value }]"
          @click="form.taskType = type.value"
        >
          {{ type.label }}
        </view>
      </view>
      <view class="template-list">
        <view
          v-for="template in templates"
          :key="template"
          :class="['template-card', { active: form.templateName === template }]"
          @click="form.templateName = template"
        >
          <text class="template-title">{{ template }}</text>
          <text class="template-subtitle">来自后端规则模板。</text>
        </view>
        <text v-if="templates.length === 0" class="empty-line">暂无可用模板，可直接使用自定义规则发布。</text>
      </view>
    </view>

    <view class="section-card">
      <view class="fold-header" @click="showAdvanced = !showAdvanced">
        <text class="section-title">高级规则</text>
        <text class="fold-text">{{ showAdvanced ? '收起' : '展开' }}</text>
      </view>
      <view v-if="showAdvanced" class="advanced-grid">
        <view class="field-block">
          <text class="field-label">迟到宽限分钟</text>
          <input
            :value="String(form.advancedRules?.allowLateMinutes ?? 0)"
            class="field-input"
            type="number"
            @input="form.advancedRules!.allowLateMinutes = Number($event.detail.value || 0)"
          />
        </view>
        <view class="toggle-row">
          <text class="field-label">需要照片佐证</text>
          <switch
            :checked="Boolean(form.advancedRules?.needPhoto)"
            color="#1677ff"
            @change="form.advancedRules!.needPhoto = $event.detail.value"
          />
        </view>
        <view class="toggle-row">
          <text class="field-label">允许申诉</text>
          <switch
            :checked="Boolean(form.advancedRules?.allowAppeal)"
            color="#1677ff"
            @change="form.advancedRules!.allowAppeal = $event.detail.value"
          />
        </view>
        <view class="toggle-row">
          <text class="field-label">到点自动结束</text>
          <switch
            :checked="Boolean(form.advancedRules?.autoEnd)"
            color="#1677ff"
            @change="form.advancedRules!.autoEnd = $event.detail.value"
          />
        </view>
      </view>
    </view>

    <view class="section-card">
      <text class="section-title">确认发布</text>
      <view class="summary-box">
        <text v-for="item in ruleSummary" :key="item" class="summary-line">{{ item }}</text>
      </view>
      <view :class="['publish-button', { disabled: !readyToPublish }]" @click="submitTask">
        {{ submitting ? '发布中...' : '确认发布' }}
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
@use '@/styles/tokens.scss' as *;

.teacher-page {
  min-height: 100vh;
  padding: 24rpx;
  background: $page-bg;
}

.top-bar,
.fold-header,
.toggle-row,
.field-grid,
.compact-selector {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.top-bar {
  margin-bottom: 20rpx;
}

.top-back,
.top-action,
.fold-text {
  font-size: 24rpx;
  color: $primary;
}

.top-title {
  font-size: 32rpx;
  font-weight: 700;
  color: $text-primary;
}

.hero-card,
.section-card {
  padding: 24rpx;
  border-radius: 22rpx;
  background: $card-bg;
  box-shadow: 0 10rpx 24rpx rgba(15, 23, 42, 0.05);
}

.hero-card {
  background: linear-gradient(180deg, #1677ff 0%, #53b1fd 100%);
  color: #fff;
}

.hero-title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
}

.hero-subtitle {
  display: block;
  margin-top: 10rpx;
  font-size: 24rpx;
  line-height: 1.5;
}

.section-card {
  margin-top: 20rpx;
}

.section-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: $text-primary;
}

.field-block {
  margin-top: 18rpx;
}

.field-grid {
  align-items: stretch;
}

.field-grid > .field-block {
  flex: 1;
}

.field-label {
  display: block;
  margin-bottom: 10rpx;
  font-size: 24rpx;
  color: $text-secondary;
}

.field-input,
.field-textarea {
  width: 100%;
  padding: 18rpx 20rpx;
  border-radius: 16rpx;
  background: #f7faff;
  font-size: 24rpx;
  color: $text-primary;
  box-sizing: border-box;
}

.field-textarea {
  min-height: 150rpx;
}

.chip-grid,
.template-list,
.advanced-grid {
  display: grid;
  gap: 14rpx;
  margin-top: 18rpx;
}

.choice-chip,
.template-card {
  padding: 20rpx;
  border-radius: 18rpx;
  background: #f7faff;
  border: 1rpx solid transparent;
}

.choice-chip.active,
.template-card.active,
.compact-option.active {
  border-color: rgba(22, 119, 255, 0.3);
  background: $primary-light;
}

.chip-title,
.template-title {
  display: block;
  font-size: 26rpx;
  font-weight: 700;
  color: $text-primary;
}

.chip-subtitle,
.template-subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  line-height: 1.4;
  color: $text-secondary;
}

.compact-selector {
  margin-top: 18rpx;
}

.compact-option {
  flex: 1;
  padding: 18rpx 0;
  border-radius: 16rpx;
  background: #f7faff;
  text-align: center;
  font-size: 24rpx;
  color: $text-secondary;
}

.summary-box {
  margin-top: 18rpx;
  padding: 20rpx;
  border-radius: 18rpx;
  background: #f7faff;
}

.summary-line {
  display: block;
  font-size: 22rpx;
  line-height: 1.6;
  color: $text-secondary;
}

.publish-button {
  margin-top: 18rpx;
  padding: 24rpx 0;
  border-radius: 18rpx;
  background: $primary;
  color: #fff;
  font-size: 28rpx;
  font-weight: 700;
  text-align: center;
}

.publish-button.disabled {
  opacity: 0.45;
}

.empty-line {
  color: $text-secondary;
  font-size: 24rpx;
  line-height: 1.6;
}
</style>
