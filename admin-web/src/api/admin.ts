import { http } from './http'
import type { LoginResponse } from './types'

export interface DashboardStats {
  studentCount: number
  taskCount: number
  completionRate: number
  exceptionCount: number
  pendingAppealCount: number
}

export interface AnalyticsTrendRow {
  date: string
  label: string
  expected: number
  checked: number
  completionRate: number
}

export interface AnalyticsCollegeRateRow {
  name: string
  expected: number
  checked: number
  completionRate: number
}

export interface AnalyticsExceptionTypeRow {
  label: string
  value: number
  percent: number
}

export interface AnalyticsClassRankingRow {
  rank: number
  className: string
  exceptionCount: number
  exceptionStudentCount: number
  exceptionRate: number
}

export interface AnalyticsOverview {
  taskCount: number
  coveredClassCount: number
  coveredStudentCount: number
  checkinCount: number
  exceptionCount: number
  appealCount: number
}

export interface AnalyticsStats {
  summary: {
    expectedStudents: number
    checkedStudents: number
    completionRate: number
    exceptionCount: number
    pendingAppealCount: number
    taskCount: number
    coveredClassCount: number
    checkinCount: number
  }
  trend: AnalyticsTrendRow[]
  collegeRates: AnalyticsCollegeRateRow[]
  exceptionTypes: AnalyticsExceptionTypeRow[]
  classExceptionRanking: AnalyticsClassRankingRow[]
  overview: AnalyticsOverview
}

export type ScenarioKey = 'all' | 'classroom' | 'dorm' | 'internship' | 'custom'
export type AnalyticsRangeKey = 'today' | 'week' | 'month' | 'semester'

export interface ScenarioAnalyticsFilters {
  college: string
  major: string
  className: string
  grade: string
}

export interface ScenarioAnalyticsFilterOptions {
  colleges: string[]
  majors: string[]
  classes: string[]
  grades: string[]
}

export interface ScenarioAnalyticsSummary {
  expectedCount: number
  checkedCount: number
  completionRate: number
  exceptionCount: number
  exceptionRate: number
  pendingAppealCount: number
  taskCount: number
  coveredStudentCount: number
  faceRegistrationRate: number
  locationPassRate: number
  facePassRate: number
}

export interface ScenarioRateRow {
  name: string
  expected: number
  checked: number
  completionRate: number
}

export interface ScenarioVerificationRow {
  label: string
  method: string
  passed: number
  failed: number
  passRate: number
}

export interface ScenarioTimeDistributionRow {
  label: string
  count: number
}

export interface ScenarioRiskStudentRow {
  studentNo: string
  name: string
  major: string
  className: string
  missingCount: number
  exceptionCount: number
  riskLevel: 'high' | 'medium' | 'low'
  riskScore: number
}

export interface ScenarioFaceRegistrationRow {
  name: string
  total: number
  registered: number
  rate: number
}

export interface ScenarioAnalyticsStats {
  scenario: ScenarioKey
  scenarioLabel: string
  range: AnalyticsRangeKey
  filters: ScenarioAnalyticsFilters
  filterOptions: ScenarioAnalyticsFilterOptions
  summary: ScenarioAnalyticsSummary
  trend: AnalyticsTrendRow[]
  majorRates: ScenarioRateRow[]
  classRates: ScenarioRateRow[]
  exceptionTypes: AnalyticsExceptionTypeRow[]
  verificationBreakdown: ScenarioVerificationRow[]
  checkinTimeDistribution: ScenarioTimeDistributionRow[]
  classExceptionRanking: AnalyticsClassRankingRow[]
  riskStudents: ScenarioRiskStudentRow[]
  faceRegistrationByMajor: ScenarioFaceRegistrationRow[]
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

export interface StudentFaceStatus {
  studentProfileId: number
  registered: boolean
  encodingCount: number
  model: string | null
  dimension: number | null
  source: string | null
  updatedAt: string | null
}

export interface StudentFaceRegisterResult {
  studentProfileId: number
  encodingCount: number
  dimension: number
  model: string
}

export interface StudentFaceClearResult {
  studentProfileId: number
  cleared: number
  registered: boolean
}

export interface StudentFaceBatchItem {
  filename: string
  studentNo: string
  studentProfileId?: number
  studentName?: string
  success: boolean
  message: string
  encodingCount?: number
  dimension?: number
}

export interface StudentFaceBatchResult {
  total: number
  successCount: number
  failedCount: number
  items: StudentFaceBatchItem[]
}

const FACE_UPLOAD_TIMEOUT_MS = 120_000
const FACE_BATCH_UPLOAD_TIMEOUT_MS = 600_000

export interface StudentRow extends Record<string, unknown> {
  id: number
  name: string
  studentNo: string
  className: string
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

export const getAnalytics = async (): Promise<AnalyticsStats> => {
  const response = await http.get('/admin/analytics')
  const data = unwrap<{
    summary: {
      expected_students: number
      checked_students: number
      completion_rate: number
      exception_count: number
      pending_appeal_count: number
      task_count: number
      covered_class_count: number
      checkin_count: number
    }
    trend: Array<{
      date: string
      label: string
      expected: number
      checked: number
      completion_rate: number
    }>
    college_rates: Array<{
      name: string
      expected: number
      checked: number
      completion_rate: number
    }>
    exception_types: AnalyticsExceptionTypeRow[]
    class_exception_ranking: Array<{
      rank: number
      class_name: string
      exception_count: number
      exception_student_count: number
      exception_rate: number
    }>
    overview: {
      task_count: number
      covered_class_count: number
      covered_student_count: number
      checkin_count: number
      exception_count: number
      appeal_count: number
    }
  }>(response)
  return {
    summary: {
      expectedStudents: data.summary.expected_students,
      checkedStudents: data.summary.checked_students,
      completionRate: data.summary.completion_rate,
      exceptionCount: data.summary.exception_count,
      pendingAppealCount: data.summary.pending_appeal_count,
      taskCount: data.summary.task_count,
      coveredClassCount: data.summary.covered_class_count,
      checkinCount: data.summary.checkin_count,
    },
    trend: data.trend.map((item) => ({
      date: item.date,
      label: item.label,
      expected: item.expected,
      checked: item.checked,
      completionRate: item.completion_rate,
    })),
    collegeRates: data.college_rates.map((item) => ({
      name: item.name,
      expected: item.expected,
      checked: item.checked,
      completionRate: item.completion_rate,
    })),
    exceptionTypes: data.exception_types,
    classExceptionRanking: data.class_exception_ranking.map((item) => ({
      rank: item.rank,
      className: item.class_name,
      exceptionCount: item.exception_count,
      exceptionStudentCount: item.exception_student_count,
      exceptionRate: item.exception_rate,
    })),
    overview: {
      taskCount: data.overview.task_count,
      coveredClassCount: data.overview.covered_class_count,
      coveredStudentCount: data.overview.covered_student_count,
      checkinCount: data.overview.checkin_count,
      exceptionCount: data.overview.exception_count,
      appealCount: data.overview.appeal_count,
    },
  }
}

export interface ScenarioAnalyticsQuery {
  scenario?: ScenarioKey
  range?: AnalyticsRangeKey
  college?: string
  major?: string
  className?: string
  grade?: string
}

export const getScenarioAnalytics = async (
  query: ScenarioAnalyticsQuery = {},
): Promise<ScenarioAnalyticsStats> => {
  const response = await http.get('/admin/analytics/scenario', {
    params: {
      scenario: query.scenario ?? 'all',
      range: query.range ?? 'week',
      college: query.college || undefined,
      major: query.major || undefined,
      class_name: query.className || undefined,
      grade: query.grade || undefined,
    },
  })
  const data = unwrap<{
    scenario: ScenarioKey
    scenario_label: string
    range: AnalyticsRangeKey
    filters: {
      college: string
      major: string
      class_name: string
      grade: string
    }
    filter_options: {
      colleges: string[]
      majors: string[]
      classes: string[]
      grades: string[]
    }
    summary: {
      expected_count: number
      checked_count: number
      completion_rate: number
      exception_count: number
      exception_rate: number
      pending_appeal_count: number
      task_count: number
      covered_student_count: number
      face_registration_rate: number
      location_pass_rate: number
      face_pass_rate: number
    }
    trend: Array<{
      date: string
      label: string
      expected: number
      checked: number
      completion_rate: number
    }>
    major_rates: Array<{
      name: string
      expected: number
      checked: number
      completion_rate: number
    }>
    class_rates: Array<{
      name: string
      expected: number
      checked: number
      completion_rate: number
    }>
    exception_types: AnalyticsExceptionTypeRow[]
    verification_breakdown: Array<{
      label: string
      method: string
      passed: number
      failed: number
      pass_rate: number
    }>
    checkin_time_distribution: Array<{ label: string; count: number }>
    class_exception_ranking: Array<{
      rank: number
      class_name: string
      exception_count: number
      exception_student_count: number
      exception_rate: number
    }>
    risk_students: Array<{
      student_no: string
      name: string
      major: string
      class_name: string
      missing_count: number
      exception_count: number
      risk_level: 'high' | 'medium' | 'low'
      risk_score: number
    }>
    face_registration_by_major: Array<{
      name: string
      total: number
      registered: number
      rate: number
    }>
  }>(response)

  return {
    scenario: data.scenario,
    scenarioLabel: data.scenario_label,
    range: data.range,
    filters: {
      college: data.filters.college,
      major: data.filters.major,
      className: data.filters.class_name,
      grade: data.filters.grade,
    },
    filterOptions: {
      colleges: data.filter_options.colleges,
      majors: data.filter_options.majors,
      classes: data.filter_options.classes,
      grades: data.filter_options.grades,
    },
    summary: {
      expectedCount: data.summary.expected_count,
      checkedCount: data.summary.checked_count,
      completionRate: data.summary.completion_rate,
      exceptionCount: data.summary.exception_count,
      exceptionRate: data.summary.exception_rate,
      pendingAppealCount: data.summary.pending_appeal_count,
      taskCount: data.summary.task_count,
      coveredStudentCount: data.summary.covered_student_count,
      faceRegistrationRate: data.summary.face_registration_rate,
      locationPassRate: data.summary.location_pass_rate,
      facePassRate: data.summary.face_pass_rate,
    },
    trend: data.trend.map((item) => ({
      date: item.date,
      label: item.label,
      expected: item.expected,
      checked: item.checked,
      completionRate: item.completion_rate,
    })),
    majorRates: data.major_rates.map((item) => ({
      name: item.name,
      expected: item.expected,
      checked: item.checked,
      completionRate: item.completion_rate,
    })),
    classRates: data.class_rates.map((item) => ({
      name: item.name,
      expected: item.expected,
      checked: item.checked,
      completionRate: item.completion_rate,
    })),
    exceptionTypes: data.exception_types,
    verificationBreakdown: data.verification_breakdown.map((item) => ({
      label: item.label,
      method: item.method,
      passed: item.passed,
      failed: item.failed,
      passRate: item.pass_rate,
    })),
    checkinTimeDistribution: data.checkin_time_distribution,
    classExceptionRanking: data.class_exception_ranking.map((item) => ({
      rank: item.rank,
      className: item.class_name,
      exceptionCount: item.exception_count,
      exceptionStudentCount: item.exception_student_count,
      exceptionRate: item.exception_rate,
    })),
    riskStudents: data.risk_students.map((item) => ({
      studentNo: item.student_no,
      name: item.name,
      major: item.major,
      className: item.class_name,
      missingCount: item.missing_count,
      exceptionCount: item.exception_count,
      riskLevel: item.risk_level,
      riskScore: item.risk_score,
    })),
    faceRegistrationByMajor: data.face_registration_by_major.map((item) => ({
      name: item.name,
      total: item.total,
      registered: item.registered,
      rate: item.rate,
    })),
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
      faceRegistered: Boolean(item.face_registered),
    })),
  }
}

export const getStudentFaceStatus = async (studentId: number): Promise<StudentFaceStatus> => {
  const response = await http.get(`/admin/students/${studentId}/face`)
  const data = unwrap<{
    student_profile_id: number
    registered: boolean
    encoding_count: number
    model?: string | null
    dimension?: number | null
    source?: string | null
    updated_at?: string | null
  }>(response)
  return {
    studentProfileId: data.student_profile_id,
    registered: data.registered,
    encodingCount: data.encoding_count,
    model: data.model ?? null,
    dimension: data.dimension ?? null,
    source: data.source ?? null,
    updatedAt: data.updated_at ?? null,
  }
}

export const registerStudentFace = async (
  studentId: number,
  file: File,
): Promise<StudentFaceRegisterResult> => {
  const form = new FormData()
  form.append('photo', file)
  console.info('[AI思政管理端] 请求录入人脸', {
    studentId,
    fileName: file.name,
    fileSize: file.size,
    fileType: file.type,
  })
  const response = await http.post(`/admin/students/${studentId}/face`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: FACE_UPLOAD_TIMEOUT_MS,
  })
  const data = unwrap<{
    student_profile_id: number
    encoding_count: number
    dimension: number
    model: string
  }>(response)
  const result: StudentFaceRegisterResult = {
    studentProfileId: data.student_profile_id,
    encodingCount: data.encoding_count,
    dimension: data.dimension,
    model: data.model,
  }
  console.info('[AI思政管理端] 人脸录入接口返回', { studentId, result })
  return result
}

export const batchRegisterStudentFaces = async (
  files: File[],
): Promise<StudentFaceBatchResult> => {
  const form = new FormData()
  files.forEach((file) => {
    form.append('photos', file)
  })
  console.info('[AI思政管理端] 请求批量录入人脸', {
    count: files.length,
    fileNames: files.map((file) => file.name),
  })
  const response = await http.post('/admin/students/faces/batch', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: FACE_BATCH_UPLOAD_TIMEOUT_MS,
  })
  const data = unwrap<{
    total: number
    success_count: number
    failed_count: number
    items: Array<{
      filename: string
      student_no: string
      student_profile_id?: number
      student_name?: string
      success: boolean
      message: string
      encoding_count?: number
      dimension?: number
    }>
  }>(response)
  const result: StudentFaceBatchResult = {
    total: data.total,
    successCount: data.success_count,
    failedCount: data.failed_count,
    items: data.items.map((item) => ({
      filename: item.filename,
      studentNo: item.student_no,
      studentProfileId: item.student_profile_id,
      studentName: item.student_name,
      success: item.success,
      message: item.message,
      encodingCount: item.encoding_count,
      dimension: item.dimension,
    })),
  }
  console.info('[AI思政管理端] 批量人脸录入接口返回', result)
  return result
}

export const clearStudentFace = async (studentId: number): Promise<StudentFaceClearResult> => {
  console.info('[AI思政管理端] 请求清除人脸', { studentId })
  const response = await http.delete(`/admin/students/${studentId}/face`)
  const data = unwrap<{
    student_profile_id: number
    cleared: number
    registered: boolean
  }>(response)
  const result: StudentFaceClearResult = {
    studentProfileId: data.student_profile_id,
    cleared: data.cleared,
    registered: data.registered,
  }
  console.info('[AI思政管理端] 清除人脸接口返回', { studentId, result })
  return result
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
