import { request } from './request'
import type { ApiResponse, TaskStatus } from './types'

export type TeacherTaskStatus = TaskStatus | 'pending_review'
export type TeacherExceptionStatus = 'pending' | 'approved' | 'rejected' | 'need_more'
export type TeacherTaskTemplate = string
export type TeacherTaskType = 'attendance' | 'photo' | 'location' | 'custom'

export interface TeacherDashboard {
  todayTasks: number
  exceptions: number
  pendingReviews: number
  quickCreateCount: number
}

export interface TeacherGroup {
  id: number
  name: string
  studentCount: number
  recentTaskCount: number
  courseName?: string
}

export interface TeacherTask {
  id: number
  title: string
  status: TeacherTaskStatus
  groupName: string
  templateName: TeacherTaskTemplate
  taskType: TeacherTaskType
  startsAt: string
  endsAt: string
  completionRate: number
  pendingReviewCount: number
  exceptionCount: number
}

export interface TeacherTaskStudent {
  id: number
  name: string
  status: 'submitted' | 'missing' | 'pending_review' | 'approved' | 'rejected'
  submittedAt?: string
}

export interface TeacherException {
  id: number
  studentName: string
  taskTitle: string
  groupName: string
  submittedAt: string
  reason: string
  status: TeacherExceptionStatus
  comment?: string
}

export interface TeacherTaskDetail {
  task: TeacherTask & {
    description?: string
    published: boolean
  }
  students: TeacherTaskStudent[]
  exceptions: TeacherException[]
}

export interface CreateTeacherTaskPayload {
  title: string
  description?: string
  groupIds: number[]
  taskType: TeacherTaskType
  templateName: TeacherTaskTemplate
  startsAt: string
  endsAt: string
  advancedRules?: {
    allowLateMinutes?: number
    needPhoto?: boolean
    allowAppeal?: boolean
    autoEnd?: boolean
  }
}

export interface ReviewTeacherExceptionPayload {
  action?: 'approve' | 'reject' | 'need_more'
  decision?: 'approve' | 'reject' | 'need_more'
  comment?: string
}

export interface TeacherGroupDetail {
  group: TeacherGroup
  stats: {
    attendanceRate: number
    exceptionRate: number
    pendingReviewCount: number
  }
  students: TeacherTaskStudent[]
  tasks: TeacherTask[]
}

interface BackendList<T> {
  items: T[]
  total?: number
}

interface BackendTeacherGroup {
  id: number
  name?: string
  group_type?: string
  student_count?: number
  studentCount?: number
  recent_task_count?: number
  recentTaskCount?: number
  course_name?: string
  courseName?: string
}

interface BackendTeacherTask {
  id: number
  title?: string
  type_id?: number
  taskType?: string
  templateName?: string
  description?: string
  status?: string
  starts_at?: string
  startsAt?: string
  ends_at?: string
  endsAt?: string
  group_ids?: number[]
  groupName?: string
  group_name?: string
  group_names?: string[]
  completion_rate?: number
  completionRate?: number
  pending_review_count?: number
  pendingReviewCount?: number
  exception_count?: number
  exceptionCount?: number
  rules_snapshot?: Record<string, unknown>
  published?: boolean
}

interface BackendTeacherException {
  id: number
  record_id?: number
  task_id?: number
  status?: string
  exception_types?: string[]
  messages?: string[]
  student_name?: string
  studentName?: string
  task_title?: string
  taskTitle?: string
  group_name?: string
  groupName?: string
  submitted_at?: string
  submittedAt?: string
  reason?: string
  comment?: string
}

interface BackendTeacherTaskStudent {
  id: number
  name?: string
  status?: string
  submitted_at?: string | null
  submittedAt?: string | null
}

interface BackendTeacherTaskDetail extends BackendTeacherTask {
  task?: BackendTeacherTask
  students?: BackendTeacherTaskStudent[]
  exceptions?: BackendTeacherException[]
}

interface BackendTeacherDashboard {
  task_count?: number
  exception_count?: number
  pending_review_count?: number
  quick_create_count?: number
}

interface BackendReviewResult {
  reviewed?: boolean
  record_status?: string
}

function unwrapData<T>(response: ApiResponse<T> | T): T {
  if (typeof response === 'object' && response !== null && 'data' in response) {
    return (response as ApiResponse<T>).data
  }
  return response as T
}

async function requestData<T>(options: UniApp.RequestOptions): Promise<T> {
  return unwrapData(await request<ApiResponse<T> | T>(options))
}

async function requestItems<T>(options: UniApp.RequestOptions): Promise<T[]> {
  const data = await requestData<BackendList<T> | T[]>(options)
  if (Array.isArray(data)) {
    return data
  }
  return Array.isArray(data.items) ? data.items : []
}

function readObject(value: unknown): Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {}
}

function readArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : []
}

function readString(value: unknown, fallback = ''): string {
  return typeof value === 'string' && value.length > 0 ? value : fallback
}

function readNumber(value: unknown, fallback = 0): number {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}

function formatDateTime(value?: string | null): string {
  if (!value) {
    return ''
  }

  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/)
  if (match) {
    return `${match[1]}-${match[2]}-${match[3]} ${match[4]}:${match[5]}`
  }

  return value
}

function formatTime(value?: string | null): string {
  if (!value) {
    return ''
  }

  const match = value.match(/[T ](\d{2}):(\d{2})/)
  if (match) {
    return `${match[1]}:${match[2]}`
  }

  return value
}

function normalizeTaskStatus(status?: string): TeacherTaskStatus {
  switch (status) {
    case 'draft':
    case 'not_started':
    case 'in_progress':
    case 'ended':
    case 'pending_review':
      return status
    default:
      return 'not_started'
  }
}

function normalizeExceptionStatus(status?: string): TeacherExceptionStatus {
  switch (status) {
    case 'approved':
    case 'rejected':
    case 'need_more':
      return status
    case 'pending':
    case 'pending_review':
    case 'exception':
    default:
      return 'pending'
  }
}

function templateFromRules(rules: Record<string, unknown>): TeacherTaskTemplate {
  const templateName = readString(rules.templateName)
  return templateName
}

function taskTypeFromBackend(raw: BackendTeacherTask, rules: Record<string, unknown>): TeacherTaskType {
  if (['attendance', 'photo', 'location', 'custom'].includes(readString(raw.taskType))) {
    return raw.taskType as TeacherTaskType
  }

  const taskType = readString(rules.taskType)
  if (['attendance', 'photo', 'location', 'custom'].includes(taskType)) {
    return taskType as TeacherTaskType
  }
  return raw.type_id === 1 ? 'attendance' : 'custom'
}

function taskTypeId(_taskType: TeacherTaskType): number {
  return 1
}

function timePart(value: string): string {
  const match = value.match(/[T ](\d{2}:\d{2})/)
  return match?.[1] ?? value
}

function mapTeacherGroup(raw: BackendTeacherGroup): TeacherGroup {
  return {
    id: raw.id,
    name: readString(raw.name, `分组 ${raw.id}`),
    studentCount: raw.studentCount ?? raw.student_count ?? 0,
    recentTaskCount: raw.recentTaskCount ?? raw.recent_task_count ?? 0,
    courseName: raw.courseName ?? raw.course_name ?? raw.group_type,
  }
}

function mapTeacherTask(raw: BackendTeacherTask): TeacherTask {
  const rules = readObject(raw.rules_snapshot)
  const groupIds = raw.group_ids ?? []
  const groupName = raw.groupName ?? raw.group_name ?? raw.group_names?.join(' / ')

  return {
    id: raw.id,
    title: readString(raw.title, '打卡任务'),
    status: normalizeTaskStatus(raw.status),
    groupName: groupName ?? (groupIds.length ? `分组 ${groupIds.join('、')}` : '未指定分组'),
    templateName: readString(raw.templateName) ? (raw.templateName as TeacherTaskTemplate) : templateFromRules(rules),
    taskType: taskTypeFromBackend(raw, rules),
    startsAt: formatDateTime(raw.startsAt ?? raw.starts_at),
    endsAt: formatDateTime(raw.endsAt ?? raw.ends_at),
    completionRate: raw.completionRate ?? raw.completion_rate ?? 0,
    pendingReviewCount: raw.pendingReviewCount ?? raw.pending_review_count ?? 0,
    exceptionCount: raw.exceptionCount ?? raw.exception_count ?? 0,
  }
}

function mapTeacherException(raw: BackendTeacherException): TeacherException {
  const messages = raw.messages ?? []
  const exceptionTypes = raw.exception_types ?? []
  const reason = readString(raw.reason, [...messages, ...exceptionTypes].join('；') || '异常待审核')

  return {
    id: raw.id,
    studentName: readString(raw.studentName ?? raw.student_name, raw.record_id ? `记录 #${raw.record_id}` : '学生'),
    taskTitle: readString(raw.taskTitle ?? raw.task_title, raw.task_id ? `任务 #${raw.task_id}` : '打卡任务'),
    groupName: readString(raw.groupName ?? raw.group_name, '相关分组'),
    submittedAt: formatDateTime(raw.submittedAt ?? raw.submitted_at),
    reason,
    status: normalizeExceptionStatus(raw.status),
    comment: raw.comment,
  }
}

function normalizeStudentStatus(status?: string): TeacherTaskStudent['status'] {
  switch (status) {
    case 'submitted':
    case 'missing':
    case 'pending_review':
    case 'approved':
    case 'rejected':
      return status
    default:
      return 'missing'
  }
}

function mapTeacherTaskStudent(raw: BackendTeacherTaskStudent): TeacherTaskStudent {
  return {
    id: raw.id,
    name: readString(raw.name, `学生 ${raw.id}`),
    status: normalizeStudentStatus(raw.status),
    submittedAt: formatDateTime(raw.submittedAt ?? raw.submitted_at),
  }
}

function mapTaskDetail(raw: BackendTeacherTaskDetail): TeacherTaskDetail {
  const rawTask = raw.task ?? raw
  const task = mapTeacherTask(rawTask)
  return {
    task: {
      ...task,
      description: readString(rawTask.description, readString(readObject(rawTask.rules_snapshot).description)),
      published: Boolean(rawTask.published ?? rawTask.status !== 'draft'),
    },
    students: (raw.students ?? []).map(mapTeacherTaskStudent),
    exceptions: (raw.exceptions ?? []).map(mapTeacherException),
  }
}

function buildRulesSnapshot(payload: CreateTeacherTaskPayload) {
  const rules = payload.advancedRules ?? {}
  const needsPhoto = Boolean(rules.needPhoto)

  return {
    templateName: payload.templateName,
    taskType: payload.taskType,
    description: payload.description ?? '',
    timeRule: {
      mode: 'single',
      startTime: timePart(payload.startsAt),
      endTime: timePart(payload.endsAt),
      allowLate: (rules.allowLateMinutes ?? 0) > 0,
      allowLateMinutes: rules.allowLateMinutes ?? 0,
      allowMakeup: true,
      makeupNeedReview: true,
    },
    locationRule: {
      mode: 'fixed_area',
      placeName: '指定签到地点',
      longitude: 0,
      latitude: 0,
      radius: 300,
      allowExceptionSubmit: true,
    },
    verificationRule: {
      methods: needsPhoto ? ['location', 'photo'] : ['location'],
    },
    submitRule: {
      fields: [
        {
          key: 'remark',
          label: '情况说明',
          type: 'textarea',
          required: false,
        },
      ],
    },
    reviewRule: {
      mode: rules.allowAppeal === false ? 'manual' : 'exception_only',
      allowAppeal: rules.allowAppeal ?? true,
      autoEnd: rules.autoEnd ?? true,
    },
    reminderRule: {
      beforeStartMinutes: 10,
      beforeEndMinutes: 5,
      notifyTeacherAfterEnd: true,
    },
    faceRule: {
      enabled: needsPhoto,
      provider: 'placeholder',
    },
  }
}

function mapReviewResult(raw: BackendReviewResult, id: number, payload: ReviewTeacherExceptionPayload): TeacherException {
  return {
    id,
    studentName: '学生',
    taskTitle: '打卡任务',
    groupName: '相关分组',
    submittedAt: '',
    reason: raw.reviewed ? '已完成审核' : '审核结果待确认',
    status: normalizeExceptionStatus(raw.record_status === 'normal' ? 'approved' : raw.record_status),
    comment: payload.comment ?? '',
  }
}

export function getTeacherDashboard() {
  return requestData<BackendTeacherDashboard>({
    url: '/teacher/dashboard',
    method: 'GET',
  }).then((data) => ({
    todayTasks: data.task_count ?? 0,
    exceptions: data.exception_count ?? 0,
    pendingReviews: data.pending_review_count ?? data.exception_count ?? 0,
    quickCreateCount: data.quick_create_count ?? 0,
  }))
}

export function getTeacherGroups() {
  return requestItems<BackendTeacherGroup>({
    url: '/teacher/groups',
    method: 'GET',
  }).then((items) => items.map(mapTeacherGroup))
}

export function getTeacherTasks(status?: TeacherTaskStatus) {
  const search = status ? `?status=${encodeURIComponent(status)}` : ''

  return requestItems<BackendTeacherTask>({
    url: `/teacher/tasks${search}`,
    method: 'GET',
  }).then((items) => items.map(mapTeacherTask))
}

export function createTeacherTask(payload: CreateTeacherTaskPayload) {
  return requestData<BackendTeacherTask>({
    url: '/teacher/tasks',
    method: 'POST',
    data: {
      title: payload.title,
      type_id: taskTypeId(payload.taskType),
      group_ids: payload.groupIds,
      starts_at: payload.startsAt,
      ends_at: payload.endsAt,
      rules_snapshot: buildRulesSnapshot(payload),
    },
  }).then(mapTeacherTask)
}

export function getTeacherTaskDetail(id: number) {
  return requestData<BackendTeacherTaskDetail>({
    url: `/teacher/tasks/${id}`,
    method: 'GET',
  }).then(mapTaskDetail)
}

export function publishTeacherTask(id: number) {
  return requestData<{ published?: boolean; status?: string }>({
    url: `/teacher/tasks/${id}/publish`,
    method: 'POST',
  }).then(() => getTeacherTaskDetail(id))
}

export function endTeacherTask(id: number) {
  return requestData<{ ended?: boolean; status?: string }>({
    url: `/teacher/tasks/${id}/end`,
    method: 'POST',
  }).then(() => getTeacherTaskDetail(id))
}

export function getTeacherExceptions() {
  return requestItems<BackendTeacherException>({
    url: '/teacher/exceptions',
    method: 'GET',
  }).then((items) => items.map(mapTeacherException))
}

export function reviewTeacherException(id: number, payload: ReviewTeacherExceptionPayload) {
  return requestData<BackendReviewResult>({
    url: `/teacher/exceptions/${id}/review`,
    method: 'POST',
    data: {
      decision: payload.decision ?? payload.action,
      comment: payload.comment ?? '',
    },
  }).then((data) => mapReviewResult(data, id, payload))
}
