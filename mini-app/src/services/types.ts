export type UserType = 'admin' | 'teacher' | 'student'
export type TaskStatus = 'draft' | 'not_started' | 'in_progress' | 'ended'
export type RecordStatus = 'normal' | 'late' | 'exception' | 'pending_review' | 'rejected'

export interface ApiResponse<T> {
  data: T
  message: string
}

export interface LoginResponse {
  access_token: string
  token_type: 'bearer'
  user: {
    id: number
    user_type: UserType
    display_name: string
  }
}
