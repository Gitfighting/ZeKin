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

function unwrap<T>(response: ApiResponse<T> | T): T {
  if (typeof response === 'object' && response !== null && 'data' in response) {
    return (response as ApiResponse<T>).data
  }
  return response as T
}

function withQuery(path: string, params?: Record<string, string | undefined>) {
  const query = new URLSearchParams()
  Object.entries(params ?? {}).forEach(([key, value]) => {
    if (value) {
      query.append(key, value)
    }
  })

  const serialized = query.toString()
  return serialized ? `${path}?${serialized}` : path
}

export async function getStudentDashboard(): Promise<StudentDashboard> {
  const response = await request<ApiResponse<StudentDashboard>>({
    url: '/student/dashboard',
    method: 'GET',
  })
  return unwrap(response)
}

export async function getStudentTasks(query?: StudentTaskQuery): Promise<StudentTask[]> {
  const response = await request<ApiResponse<StudentTask[]>>({
    url: withQuery('/student/tasks', { status: query?.status }),
    method: 'GET',
  })
  return unwrap(response)
}

export async function getStudentTaskDetail(taskId: string): Promise<StudentTask> {
  const response = await request<ApiResponse<StudentTask>>({
    url: `/student/tasks/${taskId}`,
    method: 'GET',
  })
  return unwrap(response)
}

export async function submitCheckin(payload: CheckinPayload): Promise<CheckinResult> {
  const response = await request<ApiResponse<CheckinResult>>({
    url: '/student/checkins',
    method: 'POST',
    data: payload,
  })
  return unwrap(response)
}

export async function getStudentRecords(status?: ResultState | 'all'): Promise<StudentRecord[]> {
  const response = await request<ApiResponse<StudentRecord[]>>({
    url: withQuery('/student/records', { status: status && status !== 'all' ? status : undefined }),
    method: 'GET',
  })
  return unwrap(response)
}

export async function submitAppeal(payload: AppealPayload): Promise<{ success: boolean }> {
  const response = await request<ApiResponse<{ success: boolean }>>({
    url: '/student/appeals',
    method: 'POST',
    data: payload,
  })
  return unwrap(response)
}

export async function getStudentMessages(): Promise<MessageItem[]> {
  const response = await request<ApiResponse<MessageItem[]>>({
    url: '/student/messages',
    method: 'GET',
  })
  return unwrap(response)
}

export async function getStudentProfile(): Promise<StudentProfile> {
  const response = await request<ApiResponse<StudentProfile>>({
    url: '/student/profile',
    method: 'GET',
  })
  return unwrap(response)
}

export async function getGrowthSummary(): Promise<GrowthSummary> {
  const response = await request<ApiResponse<GrowthSummary>>({
    url: '/student/growth-summary',
    method: 'GET',
  })
  return unwrap(response)
}
