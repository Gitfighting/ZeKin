# API v1 Contract

This markdown contract is the shared boundary for parallel frontend and backend lanes during the scaffold phase. Backend OpenAPI becomes authoritative after Task 5 implements the endpoint routes and DTO schemas.

## Shared Response Shape

```ts
export interface ApiResponse<T> {
  data: T
  message: string
}
```

## Enums

```ts
export type UserType = 'admin' | 'teacher' | 'student'
export type TaskStatus = 'draft' | 'not_started' | 'in_progress' | 'ended'
export type RecordStatus = 'normal' | 'late' | 'exception' | 'pending_review' | 'rejected'
export type ExceptionType =
  | 'missing'
  | 'late'
  | 'location_error'
  | 'dynamic_code_error'
  | 'face_failed'
  | 'safety_risk'
  | 'log_missing'
  | 'appeal_pending'
```

## RuleSnapshot

```ts
export interface RuleSnapshot {
  timeRule: {
    mode: 'single' | 'range'
    startTime: string
    endTime: string
    allowLate: boolean
    allowMakeup: boolean
    makeupNeedReview: boolean
  }
  locationRule: {
    mode: 'fixed_area' | 'none'
    placeName: string
    longitude: number
    latitude: number
    radius: number
    allowExceptionSubmit: boolean
  }
  verificationRule: {
    methods: Array<'location' | 'dynamic_code' | 'face'>
  }
  submitRule: {
    fields: Array<{
      key: string
      label: string
      type: 'text' | 'textarea' | 'image' | 'log' | 'safety_status'
      required: boolean
    }>
  }
  reviewRule: {
    mode: 'auto' | 'exception_only' | 'manual_all'
  }
  reminderRule: {
    beforeStartMinutes: number
    beforeEndMinutes: number
    notifyTeacherAfterEnd: boolean
  }
  faceRule: {
    enabled: boolean
    provider: 'placeholder'
  }
}
```

## Core Endpoint Payloads

### `POST /api/auth/login`

Request:

```json
{
  "account": "string",
  "password": "string",
  "user_type": "admin|teacher|student"
}
```

Response:

```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "user_type": "student",
    "display_name": "张三"
  }
}
```

### `POST /api/auth/student/activate`

Request:

```json
{
  "name": "string",
  "student_no": "string",
  "phone": "string",
  "code": "string",
  "password": "string"
}
```

Response:

```json
{
  "activated": true,
  "access_token": "string"
}
```

### `POST /api/teacher/tasks`

Request:

```json
{
  "title": "晚间查寝",
  "type_id": 1,
  "group_ids": [1],
  "starts_at": "2026-06-24T21:30:00+08:00",
  "ends_at": "2026-06-24T22:30:00+08:00",
  "rules_snapshot": "RuleSnapshot"
}
```

Response:

```json
{
  "id": 1,
  "status": "draft",
  "rules_snapshot": "RuleSnapshot"
}
```

### `POST /api/student/tasks/{id}/checkin`

Request:

```json
{
  "longitude": 120.000001,
  "latitude": 30.000001,
  "dynamic_code": "123456",
  "submit_payload": {
    "remark": "已在宿舍"
  }
}
```

Response:

```json
{
  "record_id": 1,
  "status": "normal",
  "exception_types": [],
  "need_review": false
}
```

### `POST /api/student/records/{id}/appeal`

Request:

```json
{
  "reason": "定位偏移，实际在宿舍楼内",
  "attachment_ids": [1]
}
```

Response:

```json
{
  "appeal_id": 1,
  "status": "appeal_pending"
}
```

### `POST /api/teacher/exceptions/{id}/review`

Request:

```json
{
  "decision": "approve|reject|need_more",
  "comment": "说明文字"
}
```

Response:

```json
{
  "reviewed": true,
  "record_status": "normal|rejected|pending_review"
}
```
