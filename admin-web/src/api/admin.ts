import { http } from './http'

export interface DashboardStats {
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

export const getDashboard = async () => {
  const { data } = await http.get<DashboardStats>('/admin/dashboard')
  return data
}

export const getOrgTree = async () => {
  const { data } = await http.get<OrgNode[]>('/admin/organizations/tree')
  return data
}

export const importStudents = async (payload: StudentImportPayload) => {
  const { data } = await http.post('/admin/students/import', payload)
  return data
}

export const getStudents = async (params?: Record<string, unknown>) => {
  const { data } = await http.get('/admin/students', { params })
  return data
}

export const getTeachers = async (params?: Record<string, unknown>) => {
  const { data } = await http.get('/admin/teachers', { params })
  return data
}

export const getGroups = async (params?: Record<string, unknown>) => {
  const { data } = await http.get('/admin/groups', { params })
  return data
}

export const getCheckinTypes = async () => {
  const { data } = await http.get('/admin/checkin-types')
  return data
}

export const getRuleTemplates = async () => {
  const { data } = await http.get('/admin/rule-templates')
  return data
}

export const getTasks = async (params?: Record<string, unknown>) => {
  const { data } = await http.get('/admin/tasks', { params })
  return data
}

export const getExceptions = async (params?: Record<string, unknown>) => {
  const { data } = await http.get('/admin/exceptions', { params })
  return data
}
