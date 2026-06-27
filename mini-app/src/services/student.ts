import { request } from '@/services/request'
import type { ApiResponse } from '@/services/types'

export type StatusTone = 'normal' | 'in-progress' | 'pending' | 'exception' | 'ended'
export type ResultState = 'normal' | 'exception' | 'pending_review'

export interface QuickEntry {
  label: string
  path: string
  badge?: string
}

export interface StudentJoinedGroup {
  id: number
  name: string
  inviteCode?: string
  studentCount: number
  recentTaskCount?: number
  teacherId?: number
  teacherName?: string
  studentProfileId?: number
  alreadyMember?: boolean
}

export interface DynamicField {
  key: string
  label: string
  type: 'text' | 'textarea' | 'number' | 'code'
  placeholder: string
  required?: boolean
  maxLength?: number
}

export type CheckinMethod = 'face' | 'location' | 'qr_code' | 'checkin_code' | 'attachment' | 'gesture'

export interface AttachmentRule {
  required: boolean
  minTextLength: number
  maxFileCount: number
  label: string
}

export interface GestureRule {
  presetPattern: string
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
  targetLat?: number
  targetLng?: number
  targetRadius?: number
  requirements: string[]
  faceRule: {
    enabled: boolean
    tip: string
  }
  dynamicFields: DynamicField[]
  scheduleMode: 'one_time' | 'recurring'
  methods: CheckinMethod[]
  attachmentRule: AttachmentRule
  gestureRule: GestureRule
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
  longitude?: number
  latitude?: number
  checkinCode?: string
  verificationCode?: string
  formData: Record<string, string>
  faceImage?: string
  photoUrls?: string[]
  qrPayload?: string
  attachment?: { text?: string; files?: string[] }
  gesture?: { pattern_id?: string; points?: number[][] }
  occurrenceDate?: string
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

export type AttendanceStatusKey = 'present' | 'late' | 'early_leave' | 'absent' | 'leave'

export const ATTENDANCE_LABELS: Record<AttendanceStatusKey, string> = {
  present: '签到',
  late: '迟到',
  early_leave: '早退',
  absent: '未签到',
  leave: '请假',
}

export interface StudentRecord {
  id: string
  taskTitle: string
  type: string
  status: ResultState
  attendanceStatus: AttendanceStatusKey
  occurrenceDate: string
  submittedAt: string
  reviewComment?: string
  locationLabel: string
}

export type RecordFilterKey = 'all' | AttendanceStatusKey

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
  attendance_status?: string
  attendanceStatus?: string
  submitted_at?: string
  occurrence_date?: string
  manual_status?: string | null
  need_review?: boolean
  review_comment?: string
  location_label?: string
}

interface BackendMessage {
  id: number | string
  title?: string
  content?: string
  read_status?: string | boolean
  read?: boolean
  created_at?: string
}

interface BackendMessagesResponse {
  items?: BackendMessage[]
  total?: number
  unread_count?: number
  unreadCount?: number
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

const METHOD_LABELS: Record<CheckinMethod, string> = {
  face: '完成人脸核验',
  location: '上传当前位置',
  qr_code: '扫描签到二维码',
  checkin_code: '输入签到码',
  attachment: '上传日志/附件',
  gesture: '绘制签到手势',
}

function resolveMethods(rules: Record<string, unknown>): CheckinMethod[] {
  const vr = readObject(rules.verificationRule)
  const known: CheckinMethod[] = ['face', 'location', 'qr_code', 'checkin_code', 'attachment', 'gesture']
  const declared = readArray(vr.methods)
    .map((item) => String(item))
    .filter((item): item is CheckinMethod => known.includes(item as CheckinMethod))

  if (declared.length > 0) {
    const order = readArray(vr.order).map((item) => String(item))
    const ordered = order.filter((item): item is CheckinMethod => declared.includes(item as CheckinMethod))
    declared.forEach((item) => {
      if (!ordered.includes(item)) {
        ordered.push(item)
      }
    })
    // 兼容旧 faceRule.enabled
    if (readObject(rules.faceRule).enabled && !ordered.includes('face')) {
      ordered.push('face')
    }
    return ordered
  }

  // 旧结构推断
  const legacy: CheckinMethod[] = []
  if (readObject(rules.locationRule).mode !== 'none' && Object.keys(readObject(rules.locationRule)).length > 0) {
    legacy.push('location')
  }
  if (readObject(rules.faceRule).enabled) {
    legacy.push('face')
  }
  return legacy
}

function mapStudentTask(raw: BackendStudentTask): StudentTask {
  const rules = readObject(raw.rules_snapshot)
  const vr = readObject(rules.verificationRule)
  // 位置配置：新结构优先 verificationRule.location，回退 locationRule
  const locationRule = Object.keys(readObject(vr.location)).length
    ? readObject(vr.location)
    : readObject(rules.locationRule)
  const submitRule = readObject(rules.submitRule)
  const faceRule = Object.keys(readObject(vr.face)).length
    ? readObject(vr.face)
    : readObject(rules.faceRule)
  const attachmentConfig = readObject(vr.attachment)
  const gestureConfig = readObject(vr.gesture)
  const dynamicFields = readArray(submitRule.fields).map(mapDynamicField)
  const methods = resolveMethods(rules)
  const status = normalizeTaskStatus(raw.status)
  const locationName = readString(locationRule.placeName, '指定地点')
  const radius = readNumber(locationRule.radius)
  const timeWindow = [formatTime(raw.starts_at), formatTime(raw.ends_at)].filter(Boolean).join(' - ')
  const requirements = [
    ...(methods.length ? methods.map((method) => METHOD_LABELS[method]) : ['上传当前位置']),
    ...dynamicFields.map((field) => field.label),
  ]
  const faceEnabled = methods.includes('face') || Boolean(faceRule.enabled)
  const scheduleMode = readString(
    (raw as Record<string, unknown>).schedule_mode as string,
    'one_time',
  ) === 'recurring' ? 'recurring' : 'one_time'

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
    targetLat: readNumber(locationRule.latitude),
    targetLng: readNumber(locationRule.longitude),
    targetRadius: radius,
    requirements,
    faceRule: {
      enabled: faceEnabled,
      tip: faceEnabled ? '请按提示完成人脸核验' : '本次任务无需人脸核验',
    },
    dynamicFields,
    scheduleMode,
    methods,
    attachmentRule: {
      required: Boolean(attachmentConfig.required),
      minTextLength: readNumber(attachmentConfig.minTextLength) ?? 0,
      maxFileCount: readNumber(attachmentConfig.maxFileCount) ?? 3,
      label: readString(attachmentConfig.label, '日志/附件'),
    },
    gestureRule: {
      presetPattern: readString(gestureConfig.presetPattern, ''),
    },
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
    locationLabel: readString(
      raw.location_label,
      payload.latitude !== undefined && payload.longitude !== undefined
        ? `${payload.latitude}, ${payload.longitude}`
        : '已提交',
    ),
  }
}

function isAttendanceStatus(value: string): value is AttendanceStatusKey {
  return value in ATTENDANCE_LABELS
}

function mapAttendanceStatus(raw: BackendStudentRecord): StudentRecord['attendanceStatus'] {
  const fromApi = raw.attendanceStatus ?? raw.attendance_status
  if (fromApi && isAttendanceStatus(fromApi)) {
    return fromApi
  }

  if (raw.manual_status && isAttendanceStatus(raw.manual_status)) {
    return raw.manual_status
  }

  if (raw.status === 'late') {
    return 'late'
  }
  if (raw.status === 'normal') {
    return 'present'
  }
  if (raw.status === 'exception' || raw.status === 'rejected') {
    return 'absent'
  }
  return 'absent'
}

function mapStudentRecord(raw: BackendStudentRecord): StudentRecord {
  return {
    id: String(raw.id),
    taskTitle: readString(raw.task_title, raw.task_id ? `任务 #${raw.task_id}` : '打卡任务'),
    type: readString(raw.type, '打卡记录'),
    status: normalizeRecordState(raw.status, Boolean(raw.need_review)),
    attendanceStatus: mapAttendanceStatus(raw),
    occurrenceDate: readString(raw.occurrence_date, raw.submitted_at?.slice(0, 10) ?? ''),
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

function isMessageRead(raw: BackendMessage): boolean {
  if (typeof raw.read_status === 'string') {
    return raw.read_status === 'read'
  }
  return Boolean(raw.read_status ?? raw.read)
}

function mapMessage(raw: BackendMessage): MessageItem {
  return {
    id: String(raw.id),
    type: mapMessageType(raw),
    title: readString(raw.title, '系统消息'),
    content: readString(raw.content),
    time: formatDateTime(raw.created_at),
    read: isMessageRead(raw),
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
      { label: '加入班级', path: '/pages/student/join-class' },
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
  const checkinCode = payload.checkinCode ?? payload.verificationCode
  const response = await request<ApiResponse<BackendCheckinResult>>({
    url: `/student/tasks/${payload.taskId}/checkin`,
    method: 'POST',
    data: {
      ...(payload.longitude !== undefined ? { longitude: payload.longitude } : {}),
      ...(payload.latitude !== undefined ? { latitude: payload.latitude } : {}),
      ...(checkinCode ? { checkin_code: checkinCode, dynamic_code: checkinCode } : {}),
      ...(payload.faceImage ? { face_image: payload.faceImage } : {}),
      ...(payload.qrPayload ? { qr_payload: payload.qrPayload } : {}),
      ...(payload.attachment ? { attachment: payload.attachment } : {}),
      ...(payload.gesture ? { gesture: payload.gesture } : {}),
      ...(payload.occurrenceDate ? { occurrence_date: payload.occurrenceDate } : {}),
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

export async function getStudentMessages(): Promise<{ messages: MessageItem[]; unreadCount: number }> {
  const response = await request<ApiResponse<BackendMessagesResponse>>({
    url: '/student/messages',
    method: 'GET',
  })
  const data = unwrapData(response)
  const messages = unwrapItems(response).map(mapMessage)
  const unreadCount =
    data.unreadCount ??
    data.unread_count ??
    messages.filter((item) => !item.read).length
  return { messages, unreadCount }
}

export async function getStudentMessageDetail(messageId: string): Promise<MessageItem> {
  const response = await request<ApiResponse<BackendMessage>>({
    url: `/student/messages/${messageId}`,
    method: 'GET',
  })
  return mapMessage(unwrapData(response))
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

// ─── 日报接口 ─────────────────────────────────────────────────────────

export interface DailyReportPayload {
  task_id?: number
  report_date: string  // YYYY-MM-DD
  content: string
  work_hours?: number
  mood?: 'good' | 'normal' | 'bad'
  photo_urls?: string[]
}

export interface DailyReportItem {
  id: string
  report_date: string
  content: string
  work_hours: number | null
  mood: string | null
  status: string
  teacher_comment: string | null
  created_at: string
}

interface BackendDailyReport {
  id: number | string
  report_date?: string
  content?: string
  work_hours?: number | null
  mood?: string | null
  status?: string
  teacher_comment?: string | null
  created_at?: string | null
}

function mapDailyReport(raw: BackendDailyReport): DailyReportItem {
  return {
    id: String(raw.id),
    report_date: readString(raw.report_date),
    content: readString(raw.content),
    work_hours: typeof raw.work_hours === 'number' ? raw.work_hours : null,
    mood: raw.mood ?? null,
    status: readString(raw.status, 'submitted'),
    teacher_comment: raw.teacher_comment ?? null,
    created_at: formatDateTime(raw.created_at),
  }
}

export async function submitDailyReport(payload: DailyReportPayload): Promise<DailyReportItem> {
  const response = await request<ApiResponse<BackendDailyReport>>({
    url: '/student/daily-reports',
    method: 'POST',
    data: payload,
  })
  return mapDailyReport(unwrapData(response))
}

export async function getDailyReports(): Promise<DailyReportItem[]> {
  const response = await request<ApiResponse<BackendList<BackendDailyReport>>>({
    url: '/student/daily-reports',
    method: 'GET',
  })
  return unwrapItems(response).map(mapDailyReport)
}

interface BackendJoinGroupResponse {
  group?: {
    id: number
    name?: string
    invite_code?: string
    inviteCode?: string
    student_count?: number
    studentCount?: number
  }
  already_member?: boolean
  alreadyMember?: boolean
}

interface BackendStudentGroup {
  id: number
  name?: string
  student_count?: number
  studentCount?: number
  recent_task_count?: number
  recentTaskCount?: number
  teacher_id?: number
  teacherId?: number
  teacher_name?: string
  teacherName?: string
  student_profile_id?: number
  studentProfileId?: number
}

function mapStudentGroup(raw: BackendStudentGroup): StudentJoinedGroup {
  return {
    id: raw.id,
    name: readString(raw.name, '班级'),
    studentCount: raw.studentCount ?? raw.student_count ?? 0,
    recentTaskCount: raw.recentTaskCount ?? raw.recent_task_count ?? 0,
    teacherId: raw.teacherId ?? raw.teacher_id,
    teacherName: readString(raw.teacherName ?? raw.teacher_name, ''),
    studentProfileId: raw.studentProfileId ?? raw.student_profile_id,
  }
}

export async function getStudentJoinedGroups(): Promise<StudentJoinedGroup[]> {
  const response = await request<ApiResponse<BackendList<BackendStudentGroup>>>({
    url: '/student/groups',
    method: 'GET',
  })
  return unwrapItems(response).map(mapStudentGroup)
}

export async function joinClassByInviteCode(inviteCode: string): Promise<StudentJoinedGroup> {
  const response = await request<ApiResponse<BackendJoinGroupResponse>>({
    url: '/student/groups/join',
    method: 'POST',
    data: { invite_code: inviteCode.trim().toUpperCase() },
  })
  const data = unwrapData(response)
  const group = data.group ?? { id: 0 }
  return {
    id: group.id,
    name: readString(group.name, '班级'),
    inviteCode: group.inviteCode ?? group.invite_code,
    studentCount: group.studentCount ?? group.student_count ?? 0,
    alreadyMember: Boolean(data.alreadyMember ?? data.already_member),
  }
}
