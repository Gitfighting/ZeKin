import { request } from '@/services/request'
import type { ApiResponse } from '@/services/types'

export type StatusTone = 'normal' | 'in-progress' | 'pending' | 'exception' | 'ended'
export type ResultState = 'normal' | 'exception' | 'pending_review'

export interface QuickEntry {
  label: string
  path: string
  badge?: string
}

export interface DynamicField {
  key: string
  label: string
  type: 'text' | 'textarea' | 'number' | 'code'
  placeholder: string
  required?: boolean
  maxLength?: number
}

export interface StudentTask {
  id: string
  title: string
  type: string
  status: StatusTone
  deadline: string
  actionText: string
  description: string
  timeWindow: string
  locationName: string
  locationHint: string
  requirements: string[]
  faceRule: {
    enabled: boolean
    tip: string
  }
  dynamicFields: DynamicField[]
}

export interface StudentDashboard {
  greeting: string
  pendingCount: number
  upcomingDeadline: string
  exceptionCount: number
  alerts: string[]
  quickEntries: QuickEntry[]
  focusTasks: StudentTask[]
}

export interface StudentTaskQuery {
  status?: string
}

export interface CheckinPayload {
  taskId: string
  longitude: number
  latitude: number
  verificationCode?: string
  formData: Record<string, string>
  photoUrls?: string[]
}

export interface CheckinResult {
  id: string
  taskId: string
  state: ResultState
  title: string
  subtitle: string
  tips: string[]
  submittedAt: string
  locationLabel: string
}

export interface StudentRecord {
  id: string
  taskTitle: string
  type: string
  status: ResultState
  submittedAt: string
  reviewComment?: string
  locationLabel: string
}

export interface AppealPayload {
  recordId: string
  reason: string
  images: string[]
}

export interface MessageItem {
  id: string
  type: 'reminder' | 'teacher_feedback' | 'appeal_result'
  title: string
  content: string
  time: string
  read: boolean
}

export interface StudentProfile {
  realName: string
  studentNo: string
  className: string
  phone: string
  counselor: string
  activationState: 'activated' | 'pending'
  privacyEntryText: string
}

export interface GrowthSummary {
  checkedInDays: number
  normalCount: number
  appealSuccessRate: string
  streakDays: number
}

const demoTasks: StudentTask[] = [
  {
    id: 'task-1',
    title: '晨读思政签到',
    type: '课堂打卡',
    status: 'in-progress',
    deadline: '今天 08:20 前',
    actionText: '立即打卡',
    description: '完成晨读后提交课程码与现场定位。',
    timeWindow: '07:30 - 08:20',
    locationName: '一教 A201',
    locationHint: '需在教学楼 200 米范围内完成定位',
    requirements: ['上传当前位置', '填写签到码', '补充课堂备注'],
    faceRule: {
      enabled: false,
      tip: '本次任务无需人脸核验',
    },
    dynamicFields: [
      {
        key: 'classNote',
        label: '课堂备注',
        type: 'textarea',
        placeholder: '补充本次思政学习情况',
        maxLength: 100,
      },
    ],
  },
  {
    id: 'task-2',
    title: '晚归宿舍打卡',
    type: '宿舍打卡',
    status: 'pending',
    deadline: '今天 22:30 前',
    actionText: '查看规则',
    description: '返宿后提交定位与宿舍状态说明。',
    timeWindow: '21:30 - 22:30',
    locationName: '8 栋学生公寓',
    locationHint: '宿舍楼 150 米范围内可提交',
    requirements: ['上传当前位置', '补充宿舍情况说明'],
    faceRule: {
      enabled: false,
      tip: '本次任务无需人脸核验',
    },
    dynamicFields: [
      {
        key: 'dormRemark',
        label: '宿舍情况',
        type: 'textarea',
        placeholder: '例如：已返宿，正在整理内务',
        maxLength: 100,
      },
    ],
  },
  {
    id: 'task-3',
    title: '校外实践日报',
    type: '实习打卡',
    status: 'exception',
    deadline: '昨天 18:00 前',
    actionText: '去申诉',
    description: '昨日定位偏离实习点，需要补充说明。',
    timeWindow: '17:00 - 18:00',
    locationName: '高新区科创园',
    locationHint: '偏离登记地点将转入异常复核',
    requirements: ['上传当前位置', '补充实践内容'],
    faceRule: {
      enabled: false,
      tip: '本次任务无需人脸核验',
    },
    dynamicFields: [
      {
        key: 'practiceSummary',
        label: '实践内容',
        type: 'textarea',
        placeholder: '填写今日工作或实践内容',
        maxLength: 120,
      },
    ],
  },
]

export const demoStudentTasks = demoTasks

export const demoStudentDashboard: StudentDashboard = {
  greeting: '张同学，下午好',
  pendingCount: 2,
  upcomingDeadline: '晨读思政签到 08:20 截止',
  exceptionCount: 1,
  alerts: ['昨日校外实践日报定位异常，待补充申诉说明'],
  quickEntries: [
    { label: '今日任务', path: '/pages/student/tasks', badge: '2' },
    { label: '打卡记录', path: '/pages/student/records' },
    { label: '异常申诉', path: '/pages/student/appeal' },
    { label: '个人中心', path: '/pages/student/profile' },
  ],
  focusTasks: demoTasks.slice(0, 2),
}

export const demoStudentRecords: StudentRecord[] = [
  {
    id: 'record-1',
    taskTitle: '晨读思政签到',
    type: '课堂打卡',
    status: 'normal',
    submittedAt: '2026-06-24 08:05',
    reviewComment: '签到正常',
    locationLabel: '一教 A201',
  },
  {
    id: 'record-2',
    taskTitle: '晚归宿舍打卡',
    type: '宿舍打卡',
    status: 'pending_review',
    submittedAt: '2026-06-23 22:11',
    reviewComment: '等待辅导员复核',
    locationLabel: '8 栋学生公寓',
  },
  {
    id: 'record-3',
    taskTitle: '校外实践日报',
    type: '实习打卡',
    status: 'exception',
    submittedAt: '2026-06-23 17:58',
    reviewComment: '定位偏离实习点 480 米',
    locationLabel: '高新区科创园',
  },
]

export const demoStudentMessages: MessageItem[] = [
  {
    id: 'message-1',
    type: 'reminder',
    title: '晨读任务即将截止',
    content: '请在 08:20 前完成晨读思政签到并提交课堂码。',
    time: '今天 07:56',
    read: false,
  },
  {
    id: 'message-2',
    type: 'teacher_feedback',
    title: '辅导员反馈',
    content: '昨晚宿舍打卡材料已收到，请保持定位权限开启。',
    time: '昨天 22:40',
    read: true,
  },
  {
    id: 'message-3',
    type: 'appeal_result',
    title: '申诉结果通知',
    content: '校外实践日报申诉已进入复核队列，预计 24 小时内反馈。',
    time: '昨天 19:20',
    read: true,
  },
]

export const demoStudentProfile: StudentProfile = {
  realName: '张思源',
  studentNo: '2024010823',
  className: '软件 2401',
  phone: '138****1024',
  counselor: '王老师',
  activationState: 'activated',
  privacyEntryText: '查看定位与照片使用说明',
}

export const demoGrowthSummary: GrowthSummary = {
  checkedInDays: 28,
  normalCount: 24,
  appealSuccessRate: '92%',
  streakDays: 13,
}

export const demoCheckinResults: Record<ResultState, CheckinResult> = {
  normal: {
    id: 'result-1',
    taskId: 'task-1',
    state: 'normal',
    title: '打卡成功',
    subtitle: '定位与课堂码校验完成，已同步辅导员台账。',
    tips: ['保持定位权限开启，后续复核更顺畅', '如有补充说明，可在记录中追加申诉材料'],
    submittedAt: '2026-06-24 08:02',
    locationLabel: '一教 A201',
  },
  exception: {
    id: 'result-2',
    taskId: 'task-3',
    state: 'exception',
    title: '已记录为异常',
    subtitle: '当前位置偏离签到点，请补充申诉说明。',
    tips: ['进入记录页可发起异常申诉', '申诉时可补充图片与文字材料'],
    submittedAt: '2026-06-24 18:02',
    locationLabel: '高新区科创园外 480 米',
  },
  pending_review: {
    id: 'result-3',
    taskId: 'task-2',
    state: 'pending_review',
    title: '提交完成，等待复核',
    subtitle: '材料已提交，辅导员会在消息页反馈结果。',
    tips: ['定位、备注和图片都可在记录页再次查看', '消息页会同步推送复核结论'],
    submittedAt: '2026-06-24 22:02',
    locationLabel: '8 栋学生公寓',
  },
}

interface BackendList<T> {
  items: T[]
  total?: number
}

interface BackendStudentTask {
  id: number | string
  title?: string
  status?: string
  starts_at?: string
  ends_at?: string
  type_id?: number
  description?: string
  rules_snapshot?: Record<string, unknown>
}

interface BackendCheckinResult {
  record_id?: number | string
  id?: number | string
  task_id?: number | string
  status?: string
  exception_types?: string[]
  need_review?: boolean
  submitted_at?: string
  location_label?: string
}

interface BackendStudentRecord {
  id: number | string
  task_id?: number | string
  task_title?: string
  type?: string
  status?: string
  submitted_at?: string
  need_review?: boolean
  review_comment?: string
  location_label?: string
}

interface BackendMessage {
  id: number | string
  title?: string
  content?: string
  read_status?: boolean
  read?: boolean
  created_at?: string
}

interface BackendStudentProfile {
  student_no?: string
  name?: string
  class_name?: string
  phone?: string
  counselor?: string
}

interface BackendGrowthSummary {
  normal_count?: number
  total_records?: number
  appeal_success_rate?: string
  streak_days?: number
}

interface BackendDashboard {
  task_count?: number
  record_count?: number
  exception_count?: number
  pending_count?: number
  upcoming_deadline?: string
  focus_tasks?: BackendStudentTask[]
}

function unwrapData<T>(response: ApiResponse<T> | T): T {
  if (typeof response === 'object' && response !== null && 'data' in response) {
    return (response as ApiResponse<T>).data
  }
  return response as T
}

function unwrapItems<T>(response: ApiResponse<BackendList<T> | T[]> | BackendList<T> | T[]): T[] {
  const data = unwrapData(response)
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

function readNumber(value: unknown): number | undefined {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
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

function formatNow(): string {
  const now = new Date()
  const pad = (value: number) => String(value).padStart(2, '0')
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`
}

function normalizeTaskStatus(status?: string): StatusTone {
  switch (status) {
    case 'in_progress':
      return 'in-progress'
    case 'ended':
      return 'ended'
    case 'exception':
      return 'exception'
    case 'normal':
      return 'normal'
    case 'draft':
    case 'not_started':
    case 'pending_review':
    case 'appeal_pending':
    default:
      return 'pending'
  }
}

function normalizeRecordState(status?: string, needReview = false): ResultState {
  if (status === 'normal') {
    return 'normal'
  }
  if (needReview || status === 'pending_review' || status === 'appeal_pending') {
    return 'pending_review'
  }
  return 'exception'
}

function mapTaskType(typeId?: number): string {
  return typeId === 1 ? '晚间查寝' : '打卡任务'
}

function mapActionText(status: StatusTone): string {
  const actionMap: Record<StatusTone, string> = {
    normal: '查看详情',
    'in-progress': '立即打卡',
    pending: '查看规则',
    exception: '去申诉',
    ended: '查看记录',
  }
  return actionMap[status]
}

function mapDynamicField(value: unknown, index: number): DynamicField {
  const field = readObject(value)
  const label = readString(field.label, `补充信息 ${index + 1}`)
  const rawType = readString(field.type, 'text')
  const type = ['text', 'textarea', 'number', 'code'].includes(rawType)
    ? (rawType as DynamicField['type'])
    : 'text'
  const maxLength = readNumber(field.maxLength) ?? readNumber(field.max_length)

  return {
    key: readString(field.key, `field_${index}`),
    label,
    type,
    placeholder: readString(field.placeholder, `请输入${label}`),
    required: Boolean(field.required),
    ...(maxLength ? { maxLength } : {}),
  }
}

function mapStudentTask(raw: BackendStudentTask): StudentTask {
  const rules = readObject(raw.rules_snapshot)
  const locationRule = readObject(rules.locationRule)
  const submitRule = readObject(rules.submitRule)
  const faceRule = readObject(rules.faceRule)
  const dynamicFields = readArray(submitRule.fields).map(mapDynamicField)
  const status = normalizeTaskStatus(raw.status)
  const locationName = readString(locationRule.placeName, '指定地点')
  const radius = readNumber(locationRule.radius)
  const timeWindow = [formatTime(raw.starts_at), formatTime(raw.ends_at)].filter(Boolean).join(' - ')
  const requirements = [
    '上传当前位置',
    ...dynamicFields.map((field) => field.label),
    ...(faceRule.enabled ? ['完成人脸核验'] : []),
  ]

  return {
    id: String(raw.id),
    title: readString(raw.title, '打卡任务'),
    type: mapTaskType(raw.type_id),
    status,
    deadline: raw.ends_at ? `${formatDateTime(raw.ends_at)} 截止` : '按任务要求截止',
    actionText: mapActionText(status),
    description: readString(raw.description, `请在${timeWindow || '规定时间'}内完成${locationName}打卡。`),
    timeWindow: timeWindow || '按任务要求',
    locationName,
    locationHint: radius ? `需在${radius} 米范围内完成定位` : '',
    requirements,
    faceRule: {
      enabled: Boolean(faceRule.enabled),
      tip: Boolean(faceRule.enabled) ? '请按提示完成人脸核验' : '本次任务无需人脸核验',
    },
    dynamicFields,
  }
}

function mapCheckinResult(raw: BackendCheckinResult, payload: CheckinPayload): CheckinResult {
  const state = normalizeRecordState(raw.status, Boolean(raw.need_review))
  const titleMap: Record<ResultState, string> = {
    normal: '打卡成功',
    exception: '已记录为异常',
    pending_review: '提交完成，等待复核',
  }
  const subtitleMap: Record<ResultState, string> = {
    normal: '定位与补充信息已提交。',
    exception: '当前记录存在异常，请在记录页补充申诉说明。',
    pending_review: '材料已提交，辅导员会在消息页反馈结果。',
  }

  return {
    id: String(raw.record_id ?? raw.id ?? ''),
    taskId: String(raw.task_id ?? payload.taskId),
    state,
    title: titleMap[state],
    subtitle: subtitleMap[state],
    tips: raw.exception_types?.length
      ? raw.exception_types.map((item) => `异常类型：${item}`)
      : ['结果已同步到打卡记录'],
    submittedAt: formatDateTime(raw.submitted_at) || formatNow(),
    locationLabel: readString(raw.location_label, `${payload.latitude}, ${payload.longitude}`),
  }
}

function mapStudentRecord(raw: BackendStudentRecord): StudentRecord {
  return {
    id: String(raw.id),
    taskTitle: readString(raw.task_title, raw.task_id ? `任务 #${raw.task_id}` : '打卡任务'),
    type: readString(raw.type, '打卡记录'),
    status: normalizeRecordState(raw.status, Boolean(raw.need_review)),
    submittedAt: formatDateTime(raw.submitted_at),
    reviewComment: readString(raw.review_comment, raw.need_review ? '等待辅导员复核' : undefined),
    locationLabel: readString(raw.location_label, '已提交定位'),
  }
}

function mapMessageType(message: BackendMessage): MessageItem['type'] {
  const text = `${message.title ?? ''} ${message.content ?? ''}`
  if (text.includes('审核结果') || text.includes('申诉结果')) {
    return 'appeal_result'
  }
  if (text.includes('反馈')) {
    return 'teacher_feedback'
  }
  return 'reminder'
}

function mapMessage(raw: BackendMessage): MessageItem {
  return {
    id: String(raw.id),
    type: mapMessageType(raw),
    title: readString(raw.title, '系统消息'),
    content: readString(raw.content),
    time: formatDateTime(raw.created_at),
    read: Boolean(raw.read_status ?? raw.read),
  }
}

function mapProfile(raw: BackendStudentProfile): StudentProfile {
  return {
    realName: readString(raw.name, '同学'),
    studentNo: readString(raw.student_no),
    className: readString(raw.class_name),
    phone: readString(raw.phone),
    counselor: readString(raw.counselor),
    activationState: 'activated',
    privacyEntryText: '查看定位与照片使用说明',
  }
}

function mapGrowthSummary(raw: BackendGrowthSummary): GrowthSummary {
  const totalRecords = raw.total_records ?? 0
  const normalCount = raw.normal_count ?? 0

  return {
    checkedInDays: totalRecords,
    normalCount,
    appealSuccessRate: readString(raw.appeal_success_rate, '0%'),
    streakDays: raw.streak_days ?? 0,
  }
}

function numericAttachmentIds(images: string[]): number[] {
  return images
    .map((image) => Number(image))
    .filter((value) => Number.isInteger(value) && value > 0)
}

export async function getStudentDashboard(): Promise<StudentDashboard> {
  const response = await request<ApiResponse<BackendDashboard>>({
    url: '/student/dashboard',
    method: 'GET',
  })
  const data = unwrapData(response)
  const pendingCount = data.pending_count ?? data.task_count ?? 0
  const exceptionCount = data.exception_count ?? 0

  return {
    greeting: '同学，你好',
    pendingCount,
    upcomingDeadline: readString(data.upcoming_deadline, pendingCount ? `待完成 ${pendingCount} 项任务` : '暂无待办任务'),
    exceptionCount,
    alerts: exceptionCount ? [`你有 ${exceptionCount} 条异常记录待处理`] : [],
    quickEntries: [
      { label: '今日任务', path: '/pages/student/tasks', ...(pendingCount ? { badge: String(pendingCount) } : {}) },
      { label: '打卡记录', path: '/pages/student/records' },
      { label: '异常申诉', path: '/pages/student/appeal' },
      { label: '个人中心', path: '/pages/student/profile' },
    ],
    focusTasks: (data.focus_tasks ?? []).map(mapStudentTask),
  }
}

export async function getStudentTasks(_query?: StudentTaskQuery): Promise<StudentTask[]> {
  const response = await request<ApiResponse<BackendList<BackendStudentTask>>>({
    url: '/student/tasks',
    method: 'GET',
  })
  return unwrapItems(response).map(mapStudentTask)
}

export async function getStudentTaskDetail(taskId: string): Promise<StudentTask> {
  const response = await request<ApiResponse<BackendStudentTask>>({
    url: `/student/tasks/${taskId}`,
    method: 'GET',
  })
  return mapStudentTask(unwrapData(response))
}

export async function submitCheckin(payload: CheckinPayload): Promise<CheckinResult> {
  const submitPayload = {
    ...payload.formData,
    ...(payload.photoUrls?.length ? { photo_urls: payload.photoUrls } : {}),
  }
  const response = await request<ApiResponse<BackendCheckinResult>>({
    url: `/student/tasks/${payload.taskId}/checkin`,
    method: 'POST',
    data: {
      longitude: payload.longitude,
      latitude: payload.latitude,
      dynamic_code: payload.verificationCode ?? '',
      submit_payload: submitPayload,
    },
  })
  return mapCheckinResult(unwrapData(response), payload)
}

export async function getStudentRecords(_status?: ResultState | 'all'): Promise<StudentRecord[]> {
  const response = await request<ApiResponse<BackendList<BackendStudentRecord>>>({
    url: '/student/records',
    method: 'GET',
  })
  return unwrapItems(response).map(mapStudentRecord)
}

export async function submitAppeal(payload: AppealPayload): Promise<{ success: boolean }> {
  const response = await request<ApiResponse<{ appeal_id?: number | string; status?: string }>>({
    url: `/student/records/${payload.recordId}/appeal`,
    method: 'POST',
    data: {
      reason: payload.reason,
      attachment_ids: numericAttachmentIds(payload.images),
    },
  })
  const data = unwrapData(response)
  return {
    success: Boolean(data.appeal_id ?? data.status),
  }
}

export async function getStudentMessages(): Promise<MessageItem[]> {
  const response = await request<ApiResponse<BackendList<BackendMessage>>>({
    url: '/student/messages',
    method: 'GET',
  })
  return unwrapItems(response).map(mapMessage)
}

export async function getStudentProfile(): Promise<StudentProfile> {
  const response = await request<ApiResponse<BackendStudentProfile>>({
    url: '/student/profile',
    method: 'GET',
  })
  return mapProfile(unwrapData(response))
}

export async function getGrowthSummary(): Promise<GrowthSummary> {
  const response = await request<ApiResponse<BackendGrowthSummary>>({
    url: '/student/growth-summary',
    method: 'GET',
  })
  return mapGrowthSummary(unwrapData(response))
}
