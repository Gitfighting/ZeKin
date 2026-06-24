import { request } from './request'
import type { ApiResponse, TaskStatus } from './types'

export type TeacherTaskStatus = TaskStatus | 'pending_review'
export type TeacherExceptionStatus = 'pending' | 'approved' | 'rejected' | 'need_more'
export type TeacherTaskTemplate = '晨检模板' | '课堂考勤模板' | '晚点名模板' | '外出签到模板'
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
  action: 'approve' | 'reject' | 'need_more'
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

async function unwrap<T>(promise: Promise<ApiResponse<T>>): Promise<T> {
  const response = await promise
  return response.data
}

export function getTeacherDashboard() {
  return unwrap(
    request<ApiResponse<TeacherDashboard>>({
      url: '/teacher/dashboard',
      method: 'GET',
    }),
  )
}

export function getTeacherGroups() {
  return unwrap(
    request<ApiResponse<TeacherGroup[]>>({
      url: '/teacher/groups',
      method: 'GET',
    }),
  )
}

export function getTeacherTasks(status?: TeacherTaskStatus) {
  const search = status ? `?status=${encodeURIComponent(status)}` : ''

  return unwrap(
    request<ApiResponse<TeacherTask[]>>({
      url: `/teacher/tasks${search}`,
      method: 'GET',
    }),
  )
}

export function createTeacherTask(payload: CreateTeacherTaskPayload) {
  return unwrap(
    request<ApiResponse<TeacherTask>>({
      url: '/teacher/tasks',
      method: 'POST',
      data: payload,
    }),
  )
}

export function getTeacherTaskDetail(id: number) {
  return unwrap(
    request<ApiResponse<TeacherTaskDetail>>({
      url: `/teacher/tasks/${id}`,
      method: 'GET',
    }),
  )
}

export function publishTeacherTask(id: number) {
  return unwrap(
    request<ApiResponse<TeacherTaskDetail>>({
      url: `/teacher/tasks/${id}/publish`,
      method: 'POST',
    }),
  )
}

export function endTeacherTask(id: number) {
  return unwrap(
    request<ApiResponse<TeacherTaskDetail>>({
      url: `/teacher/tasks/${id}/end`,
      method: 'POST',
    }),
  )
}

export function getTeacherExceptions() {
  return unwrap(
    request<ApiResponse<TeacherException[]>>({
      url: '/teacher/exceptions',
      method: 'GET',
    }),
  )
}

export function reviewTeacherException(id: number, payload: ReviewTeacherExceptionPayload) {
  return unwrap(
    request<ApiResponse<TeacherException>>({
      url: `/teacher/exceptions/${id}/review`,
      method: 'POST',
      data: payload,
    }),
  )
}
