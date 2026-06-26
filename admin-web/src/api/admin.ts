import { http } from './http'
import type { LoginResponse } from './types'

export interface DashboardStats {
  studentCount: number
  taskCount: number
  completionRate: number
  exceptionCount: number
  pendingAppealCount: number
}

export interface OrgNode {
  id: number
  label: string
  type: string
  children?: OrgNode[]
}

export interface StudentImportPayload {
  fileName: string
  overwrite: boolean
}

export interface ListResponse<T> {
  items: T[]
  total: number
}

export interface StudentRow extends Record<string, unknown> {
  id: number
  name: string
  studentNo: string
  className: string
  status: '已启用' | '待激活'
  counselor: string
  faceRegistered: boolean
}

export interface TeacherRow extends Record<string, unknown> {
  id: number
  account: string
  name: string
  teacherNo: string
  department: string
  phone: string
  groups: string[]
}

export interface GroupRow extends Record<string, unknown> {
  id: number
  name: string
  groupType: string
  studentCount: number
  teacherCount: number
}

export interface CheckinTypeRow extends Record<string, unknown> {
  id: number
  name: string
  description: string
}

export interface RuleTemplateRow extends Record<string, unknown> {
  id: number
  name: string
  typeId: number
  ruleCount: number
  rulesSnapshot: Record<string, unknown>
}

export interface TaskRow extends Record<string, unknown> {
  id: number
  title: string
  teacher: string
  type: string
  status: string
  date: string
  completionRate: string
  groupNames: string[]
}

export interface ExceptionRow extends Record<string, unknown> {
  id: number
  student: string
  taskTitle: string
  exceptionType: string
  status: string
  reviewStatus: string
}

function unwrap<T>(response: { data: { data: T } | T }): T {
  const payload = response.data
  if (typeof payload === 'object' && payload !== null && 'data' in payload) {
    return (payload as { data: T }).data
  }
  return payload as T
}

const statusLabel: Record<string, string> = {
  draft: '草稿',
  not_started: '未开始',
  in_progress: '进行中',
  ended: '已结束',
  normal: '正常',
  exception: '异常',
  pending_review: '待复核',
  approved: '已通过',
  rejected: '已驳回',
  need_more: '需补充',
  appeal_pending: '申诉中',
}

export const loginAdmin = async (account: string, password: string) => {
  const response = await http.post<{ data: LoginResponse }>('/auth/login', {
    account,
    password,
    user_type: 'admin',
  })
  return unwrap<LoginResponse>(response)
}

export const getDashboard = async () => {
  const response = await http.get('/admin/dashboard')
  const data = unwrap<{
    student_count?: number
    task_count: number
    completion_rate?: number
    exception_count: number
    pending_appeal_count?: number
  }>(response)
  return {
    studentCount: data.student_count ?? 0,
    taskCount: data.task_count,
    completionRate: data.completion_rate ?? 0,
    exceptionCount: data.exception_count,
    pendingAppealCount: data.pending_appeal_count ?? 0,
  }
}

export const getOrgTree = async () => {
  const response = await http.get('/admin/org/tree')
  const groups = unwrap<Array<{ id: number; name: string; type: string }>>(response)
  return groups.map((group) => ({
    id: group.id,
    label: group.name,
    type: group.type,
  }))
}

export const importStudents = async (payload: StudentImportPayload) => {
  const response = await http.post('/admin/students/import', payload)
  return unwrap(response)
}

export const getStudents = async (params?: Record<string, unknown>) => {
  const response = await http.get('/admin/students', { params })
  const data = unwrap<ListResponse<{
    id: number
    name: string
    student_no: string
    class_name: string
    activated: boolean
    face_registered?: boolean
  }>>(response)
  return {
    total: data.total,
    items: data.items.map<StudentRow>((item) => ({
      id: item.id,
      name: item.name,
      studentNo: item.student_no,
      className: item.class_name,
      status: item.activated ? '已启用' : '待激活',
      counselor: '按班级关联教师',
      faceRegistered: Boolean(item.face_registered),
    })),
  }
}

export const registerStudentFace = async (studentId: number, file: File) => {
  const form = new FormData()
  form.append('photo', file)
  const response = await http.post(`/admin/students/${studentId}/face`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return unwrap(response)
}

export const getTeachers = async (params?: Record<string, unknown>) => {
  const response = await http.get('/admin/teachers', { params })
  const data = unwrap<ListResponse<{
    id: number
    account?: string
    teacher_no: string
    name: string
    phone?: string
    department?: string
    groups?: string[]
  }>>(response)
  return {
    total: data.total,
    items: data.items.map<TeacherRow>((item) => ({
      id: item.id,
      account: item.account ?? item.teacher_no,
      name: item.name,
      teacherNo: item.teacher_no,
      department: item.department ?? '',
      phone: item.phone ?? '',
      groups: item.groups ?? [],
    })),
  }
}

export const getGroups = async (params?: Record<string, unknown>) => {
  const response = await http.get('/admin/groups', { params })
  const data = unwrap<ListResponse<{
    id: number
    name: string
    group_type: string
    student_count?: number
    teacher_count?: number
  }>>(response)
  return {
    total: data.total,
    items: data.items.map<GroupRow>((item) => ({
      id: item.id,
      name: item.name,
      groupType: item.group_type,
      studentCount: item.student_count ?? 0,
      teacherCount: item.teacher_count ?? 0,
    })),
  }
}

export const getCheckinTypes = async () => {
  const response = await http.get('/admin/checkin-types')
  const data = unwrap<ListResponse<{
    id: number
    name: string
    description?: string
  }>>(response)
  return {
    total: data.total,
    items: data.items.map<CheckinTypeRow>((item) => ({
      id: item.id,
      name: item.name,
      description: item.description ?? '',
    })),
  }
}

export const getRuleTemplates = async () => {
  const response = await http.get('/admin/rule-templates')
  const data = unwrap<ListResponse<{
    id: number
    name: string
    type_id: number
    rules_snapshot?: Record<string, unknown>
  }>>(response)
  return {
    total: data.total,
    items: data.items.map<RuleTemplateRow>((item) => {
      const rulesSnapshot = item.rules_snapshot ?? {}
      return {
        id: item.id,
        name: item.name,
        typeId: item.type_id,
        ruleCount: Object.keys(rulesSnapshot).length,
        rulesSnapshot,
      }
    }),
  }
}

export const getTasks = async (params?: Record<string, unknown>) => {
  const response = await http.get('/admin/tasks', { params })
  const data = unwrap<ListResponse<{
    id: number
    title: string
    status: string
    starts_at: string
    teacher_name?: string
    group_names?: string[]
    completion_rate?: number
  }>>(response)
  return {
    total: data.total,
    items: data.items.map<TaskRow>((item) => ({
      id: item.id,
      title: item.title,
      teacher: item.teacher_name ?? '未绑定',
      type: item.title,
      status: statusLabel[item.status] ?? item.status,
      date: item.starts_at ? item.starts_at.slice(0, 10) : '',
      completionRate: `${item.completion_rate ?? 0}%`,
      groupNames: item.group_names ?? [],
    })),
  }
}

export const getExceptions = async (params?: Record<string, unknown>) => {
  const response = await http.get('/admin/exceptions', { params })
  const data = unwrap<ListResponse<{
    id: number
    student_name?: string
    task_title?: string
    status: string
    exception_types: string[]
  }>>(response)
  return {
    total: data.total,
    items: data.items.map<ExceptionRow>((item) => ({
      id: item.id,
      student: item.student_name ?? '未知学生',
      taskTitle: item.task_title ?? `任务 ${item.id}`,
      exceptionType: item.exception_types.join(' / ') || '异常',
      status: statusLabel[item.status] ?? item.status,
      reviewStatus: item.status === 'pending_review' ? '申诉待处理' : (statusLabel[item.status] ?? item.status),
    })),
  }
}
