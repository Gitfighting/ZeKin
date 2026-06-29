import { request } from './request'
import type { ApiResponse, TaskStatus } from './types'
import { formatBeijingDateTime, formatBeijingClock } from '@/utils/datetime'

export type TeacherTaskStatus = TaskStatus | 'pending_review'
export type TeacherExceptionStatus = 'pending' | 'approved' | 'rejected' | 'need_more'
export type TeacherTaskTemplate = string
export type TeacherTaskType = 'attendance' | 'photo' | 'location' | 'custom'
export type CheckinMethod = 'face' | 'location' | 'qr_code' | 'checkin_code' | 'attachment' | 'gesture'
export type ScheduleMode = 'one_time' | 'recurring'

export interface MethodConfig {
  face?: { tolerance?: number }
  location?: {
    mode?: 'fixed_area' | 'student_dorm' | 'student_internship'
    placeName?: string
    longitude?: number
    latitude?: number
    radius?: number
  }
  qr_code?: { expireSeconds?: number; refreshIntervalSeconds?: number }
  checkin_code?: { code?: string }
  attachment?: { required?: boolean; minTextLength?: number; label?: string }
  gesture?: { presetPattern?: string }
}

export interface TaskQrCode {
  taskId: number
  qrToken: string
  qrImage: string
  expiresAt: number
  expireSeconds: number
  refreshIntervalSeconds: number
}

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
  inviteCode?: string
  grade?: string
  major?: string
  createdAt?: string
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
  published: boolean
  scheduledPublishAt?: string
}

export interface TeacherTaskStudent {
  id: number
  name: string
  status:
    | 'submitted'
    | 'missing'
    | 'pending_review'
    | 'approved'
    | 'rejected'
    | 'present'
    | 'late'
    | 'early_leave'
    | 'absent'
    | 'leave'
  manualStatus?: AttendanceStatus | null
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

export interface TeacherRiskStudent {
  id: number
  name: string
  groupName: string
  missCount: number
}

export interface TeacherTaskDetail {
  task: TeacherTask & {
    description?: string
    published: boolean
    checkinCode?: string
    methods?: CheckinMethod[]
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
  checkinScene?: 'class' | 'dorm' | 'internship' | 'custom'
  methods?: CheckinMethod[]
  methodConfig?: MethodConfig
  scheduleMode?: ScheduleMode
  advancedRules?: {
    allowLateMinutes?: number
    needPhoto?: boolean
    allowAppeal?: boolean
    autoEnd?: boolean
  }
  scheduledPublishAt?: string
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
  invite_code?: string
  inviteCode?: string
  student_count?: number
  studentCount?: number
  recent_task_count?: number
  recentTaskCount?: number
  course_name?: string
  courseName?: string
  grade?: string
  major?: string
  created_at?: string
  createdAt?: string
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
  is_published?: boolean
  scheduled_publish_at?: string
  scheduledPublishAt?: string
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
  manual_status?: string | null
  manualStatus?: string | null
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
  return formatBeijingDateTime(value)
}

function formatTime(value?: string | null): string {
  return formatBeijingClock(value)
}

function normalizeTaskStatus(status?: string): TeacherTaskStatus {
  switch (status) {
    case 'draft':
    case 'not_started':
    case 'in_progress':
    case 'ended':
    case 'pending_review':
      return status
    case 'published':
    case 'active':
      return 'in_progress'
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
    inviteCode: raw.inviteCode ?? raw.invite_code,
    grade: readString(raw.grade),
    major: readString(raw.major),
    createdAt: raw.createdAt ?? raw.created_at
      ? formatDateTime(raw.createdAt ?? raw.created_at)
      : undefined,
  }
}

function mapTeacherTask(raw: BackendTeacherTask): TeacherTask {
  const rules = readObject(raw.rules_snapshot)
  const groupIds = raw.group_ids ?? []
  const groupName = raw.groupName ?? raw.group_name ?? raw.group_names?.join(' / ')
  const published = Boolean(
    raw.published ?? raw.is_published ?? (raw.status !== 'draft' && !raw.scheduledPublishAt),
  )
  const scheduledPublishAt = raw.scheduledPublishAt ?? raw.scheduled_publish_at

  return {
    id: raw.id,
    title: readString(raw.title, '打卡任务'),
    status: published && normalizeTaskStatus(raw.status) === 'not_started'
      ? 'in_progress'
      : normalizeTaskStatus(raw.status),
    groupName: groupName ?? (groupIds.length ? `分组 ${groupIds.join('、')}` : '未指定分组'),
    templateName: readString(raw.templateName) ? (raw.templateName as TeacherTaskTemplate) : templateFromRules(rules),
    taskType: taskTypeFromBackend(raw, rules),
    startsAt: formatDateTime(raw.startsAt ?? raw.starts_at),
    endsAt: formatDateTime(raw.endsAt ?? raw.ends_at),
    completionRate: raw.completionRate ?? raw.completion_rate ?? 0,
    pendingReviewCount: raw.pendingReviewCount ?? raw.pending_review_count ?? 0,
    exceptionCount: raw.exceptionCount ?? raw.exception_count ?? 0,
    published,
    scheduledPublishAt: scheduledPublishAt ? formatDateTime(scheduledPublishAt) : undefined,
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
    case 'present':
    case 'late':
    case 'early_leave':
    case 'absent':
    case 'leave':
      return status
    default:
      return 'missing'
  }
}

function mapTeacherTaskStudent(raw: BackendTeacherTaskStudent): TeacherTaskStudent {
  const manual = raw.manualStatus ?? raw.manual_status ?? null
  return {
    id: raw.id,
    name: readString(raw.name, `学生 ${raw.id}`),
    status: normalizeStudentStatus(raw.status),
    manualStatus: (manual as TeacherTaskStudent['manualStatus']) ?? null,
    submittedAt: formatDateTime(raw.submittedAt ?? raw.submitted_at),
  }
}

function mapTaskDetail(raw: BackendTeacherTaskDetail): TeacherTaskDetail {
  const rawTask = raw.task ?? raw
  const rules = readObject(rawTask.rules_snapshot)
  const vr = readObject(rules.verificationRule)
  const checkinCfg = readObject(vr.checkin_code)
  const knownMethods: CheckinMethod[] = ['face', 'location', 'qr_code', 'checkin_code', 'attachment', 'gesture']
  const methods = readArray(vr.methods)
    .map((item) => String(item))
    .filter((item): item is CheckinMethod => knownMethods.includes(item as CheckinMethod))
  const task = mapTeacherTask(rawTask)
  return {
    task: {
      ...task,
      description: readString(rawTask.description, readString(rules.description)),
      published: Boolean(rawTask.published ?? rawTask.status !== 'draft'),
      checkinCode: readString(checkinCfg.code) || undefined,
      methods: methods.length ? methods : undefined,
    },
    students: (raw.students ?? []).map(mapTeacherTaskStudent),
    exceptions: (raw.exceptions ?? []).map(mapTeacherException),
  }
}

export function generateCheckinCode(length = 6): string {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let code = ''
  for (let i = 0; i < length; i += 1) {
    code += chars[Math.floor(Math.random() * chars.length)]
  }
  return code
}

function buildVerificationRule(methods: CheckinMethod[], cfg: MethodConfig) {
  const verificationRule: Record<string, unknown> = {
    methods,
    order: methods,
  }
  if (methods.includes('face')) {
    verificationRule.face = {
      tolerance: cfg.face?.tolerance ?? 0.6,
      detectionModel: 'hog',
    }
  }
  if (methods.includes('location')) {
    const locationMode = cfg.location?.mode
    const isStudentDorm = locationMode === 'student_dorm'
    const isStudentInternship = locationMode === 'student_internship'
    verificationRule.location = isStudentDorm || isStudentInternship
      ? {
          mode: locationMode,
          radius: cfg.location?.radius ?? (isStudentInternship ? 500 : 200),
        }
      : {
          mode: 'fixed_area',
          placeName: cfg.location?.placeName ?? '指定签到地点',
          longitude: cfg.location?.longitude ?? 0,
          latitude: cfg.location?.latitude ?? 0,
          radius: cfg.location?.radius ?? 300,
        }
  }
  if (methods.includes('qr_code')) {
    verificationRule.qr_code = {
      refreshIntervalSeconds: cfg.qr_code?.refreshIntervalSeconds ?? 60,
      expireSeconds: cfg.qr_code?.expireSeconds ?? 120,
      allowReuse: false,
    }
  }
  if (methods.includes('checkin_code')) {
    const rawCode = cfg.checkin_code?.code?.trim()
    verificationRule.checkin_code = {
      code: (rawCode || generateCheckinCode(6)).toUpperCase(),
      caseSensitive: false,
    }
  }
  if (methods.includes('attachment')) {
    verificationRule.attachment = {
      required: cfg.attachment?.required ?? true,
      acceptTypes: ['text', 'image'],
      minTextLength: cfg.attachment?.minTextLength ?? 10,
      maxFileCount: 3,
      maxFileSizeMb: 10,
      label: cfg.attachment?.label ?? '今日工作日志',
    }
  }
  if (methods.includes('gesture')) {
    verificationRule.gesture = {
      mode: 'preset',
      presetPattern: cfg.gesture?.presetPattern ?? '12369',
      tolerance: 0.15,
      challengeEnabled: false,
    }
  }
  return verificationRule
}

function buildRulesSnapshot(payload: CreateTeacherTaskPayload) {
  const rules = payload.advancedRules ?? {}
  const needsPhoto = Boolean(rules.needPhoto)
  const cfg = payload.methodConfig ?? {}
  const methods: CheckinMethod[] = payload.methods?.length
    ? payload.methods
    : (needsPhoto ? ['location', 'face'] : ['location'])
  const locationCfg = cfg.location ?? {}
  const isPerStudentLocationScene =
    (payload.checkinScene === 'dorm' || payload.checkinScene === 'internship')
    && methods.includes('location')
  const perStudentMode = payload.checkinScene === 'internship' ? 'student_internship' : 'student_dorm'
  const locationMode = !methods.includes('location')
    ? 'none'
    : isPerStudentLocationScene
      ? perStudentMode
      : 'fixed_area'
  const defaultRadius = payload.checkinScene === 'internship' ? 500 : 200

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
      mode: locationMode,
      placeName: isPerStudentLocationScene
        ? (payload.checkinScene === 'internship' ? '实习单位' : '学生寝室')
        : (locationCfg.placeName ?? '指定签到地点'),
      longitude: isPerStudentLocationScene ? undefined : (locationCfg.longitude ?? 0),
      latitude: isPerStudentLocationScene ? undefined : (locationCfg.latitude ?? 0),
      radius: locationCfg.radius ?? (isPerStudentLocationScene ? defaultRadius : 300),
      allowExceptionSubmit: true,
    },
    verificationRule: buildVerificationRule(
      methods,
      isPerStudentLocationScene
        ? {
            ...cfg,
            location: {
              ...locationCfg,
              mode: perStudentMode,
            },
          }
        : cfg,
    ),
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
      enabled: methods.includes('face'),
      provider: 'face_recognition',
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

export function createTeacherGroup(name: string) {
  return requestData<BackendTeacherGroup>({
    url: '/teacher/groups',
    method: 'POST',
    data: { name },
  }).then(mapTeacherGroup)
}

interface BackendTeacherGroupDetail {
  group?: BackendTeacherGroup
  stats?: {
    attendance_rate?: number
    attendanceRate?: number
    exception_rate?: number
    exceptionRate?: number
    pending_review_count?: number
    pendingReviewCount?: number
  }
  students?: BackendTeacherTaskStudent[]
  tasks?: BackendTeacherTask[]
}

export function getTeacherGroupDetail(groupId: number): Promise<TeacherGroupDetail> {
  return requestData<BackendTeacherGroupDetail>({
    url: `/teacher/groups/${groupId}`,
    method: 'GET',
  }).then((data) => ({
    group: mapTeacherGroup(data.group ?? { id: groupId }),
    stats: {
      attendanceRate: readNumber(data.stats?.attendanceRate ?? data.stats?.attendance_rate),
      exceptionRate: readNumber(data.stats?.exceptionRate ?? data.stats?.exception_rate),
      pendingReviewCount: readNumber(
        data.stats?.pendingReviewCount ?? data.stats?.pending_review_count,
      ),
    },
    students: (data.students ?? []).map((student) => ({
      id: student.id,
      name: readString(student.name, `学生 ${student.id}`),
      status: (readString(student.status, 'joined') as TeacherTaskStudent['status']),
    })),
    tasks: (data.tasks ?? []).map(mapTeacherTask),
  }))
}

export function getTeacherTasks(status?: TeacherTaskStatus) {
  const search = status ? `?status=${encodeURIComponent(status)}` : ''

  return requestItems<BackendTeacherTask>({
    url: `/teacher/tasks${search}`,
    method: 'GET',
  }).then((items) => items.map(mapTeacherTask))
}

export function createTeacherTask(payload: CreateTeacherTaskPayload) {
  const scheduleMode: ScheduleMode = payload.scheduleMode ?? 'one_time'
  return requestData<BackendTeacherTask>({
    url: '/teacher/tasks',
    method: 'POST',
    data: {
      title: payload.title,
      description: payload.description ?? '',
      template_name: payload.templateName,
      type_id: taskTypeId(payload.taskType),
      group_ids: payload.groupIds,
      starts_at: payload.startsAt,
      ends_at: payload.endsAt,
      schedule_mode: scheduleMode,
      ...(scheduleMode === 'recurring' ? { recurrence_rule: 'FREQ=DAILY' } : {}),
      ...(payload.scheduledPublishAt
        ? { scheduled_publish_at: payload.scheduledPublishAt }
        : {}),
      rules_snapshot: buildRulesSnapshot(payload),
    },
  }).then(mapTeacherTask)
}

interface BackendTaskQrCode {
  task_id?: number
  qr_token?: string
  qr_image?: string
  expires_at?: number
  expire_seconds?: number
  refresh_interval_seconds?: number
}

function mapTaskQrCode(raw: BackendTaskQrCode, taskId: number): TaskQrCode {
  return {
    taskId: raw.task_id ?? taskId,
    qrToken: readString(raw.qr_token),
    qrImage: readString(raw.qr_image),
    expiresAt: readNumber(raw.expires_at),
    expireSeconds: readNumber(raw.expire_seconds, 120),
    refreshIntervalSeconds: readNumber(raw.refresh_interval_seconds, 60),
  }
}

export function getTaskQrCode(id: number) {
  return requestData<BackendTaskQrCode>({
    url: `/teacher/tasks/${id}/qr-code`,
    method: 'GET',
  }).then((data) => mapTaskQrCode(data, id))
}

export function refreshTaskQrCode(id: number) {
  return requestData<BackendTaskQrCode>({
    url: `/teacher/tasks/${id}/qr-code/refresh`,
    method: 'POST',
  }).then((data) => mapTaskQrCode(data, id))
}

export type AttendanceStatus = 'present' | 'late' | 'early_leave' | 'absent' | 'leave'

export function setStudentAttendance(
  taskId: number,
  studentId: number,
  status: AttendanceStatus,
  remark?: string,
) {
  return requestData<{ task_id: number; student_id: number; manual_status: string; status: string }>({
    url: `/teacher/tasks/${taskId}/students/${studentId}/attendance`,
    method: 'POST',
    data: { status, remark: remark ?? '' },
  })
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

export async function getTeacherRiskStudents(): Promise<TeacherRiskStudent[]> {
  const counter = new Map<number, TeacherRiskStudent>()

  function addMiss(id: number, name: string, groupName: string, count = 1) {
    const existing = counter.get(id) ?? { id, name, groupName, missCount: 0 }
    existing.missCount += count
    existing.name = name
    existing.groupName = groupName
    counter.set(id, existing)
  }

  const tasks = await getTeacherTasks()
  const trackedTasks = tasks.filter((task) =>
    ['in_progress', 'ended', 'pending_review'].includes(task.status),
  )

  await Promise.all(
    trackedTasks.slice(0, 20).map(async (task) => {
      try {
        const detail = await getTeacherTaskDetail(task.id)
        for (const student of detail.students) {
          if (student.status === 'missing' || student.status === 'absent') {
            addMiss(student.id, student.name, task.groupName, 1)
          }
        }
      } catch {
        // 单个任务失败不影响整体统计
      }
    }),
  )

  return [...counter.values()]
    .filter((item) => item.missCount > 0)
    .sort((a, b) => b.missCount - a.missCount)
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
