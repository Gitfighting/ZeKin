# 知勤打卡系统 72 小时 MVP API 契约草案

版本：V0.1  
负责人：赵耀  
协作约束：前后端并行开发时，以本文档字段为准；任何字段变更必须先更新本文档。

## 1. 通用约定

接口前缀：`/api/v1`

通用响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

通用错误：

```json
{
  "code": 40001,
  "message": "今日该类型已打卡",
  "data": null
}
```

认证方式：

```text
Authorization: Bearer <token>
```

## 2. 枚举

| 字段 | 值 |
|---|---|
| `role` | `student`、`teacher`、`admin` |
| `checkin_type` | `dorm`、`class`、`internship` |
| `teacher_status` | `pending`、`approved`、`rejected` |
| `location_status` | `normal`、`abnormal`、`unknown` |

## 3. Auth

### POST `/auth/login`

请求：

```json
{
  "account": "student001",
  "password": "123456"
}
```

响应：

```json
{
  "token": "demo-token",
  "user": {
    "id": 1,
    "real_name": "李明",
    "role": "student",
    "class_name": "软件2401"
  }
}
```

### GET `/auth/me`

响应：

```json
{
  "id": 1,
  "real_name": "李明",
  "role": "student",
  "class_name": "软件2401"
}
```

## 4. Checkin

### GET `/checkins/today`

响应：

```json
{
  "date": "2026-06-22",
  "items": [
    {
      "checkin_type": "dorm",
      "teacher_status": "pending",
      "submitted_at": "2026-06-22 22:14:00"
    },
    {
      "checkin_type": "class",
      "teacher_status": null,
      "submitted_at": null
    },
    {
      "checkin_type": "internship",
      "teacher_status": null,
      "submitted_at": null
    }
  ]
}
```

### POST `/checkins`

请求：

```json
{
  "checkin_type": "dorm",
  "content": "今日完成思政学习并已在宿舍。",
  "latitude": 30.5728,
  "longitude": 104.0668,
  "photo_url": ""
}
```

响应：

```json
{
  "id": 101,
  "checkin_type": "dorm",
  "teacher_status": "pending",
  "location_status": "normal",
  "submitted_at": "2026-06-22 22:14:00"
}
```

### GET `/checkins`

查询参数：

```text
page=1&page_size=10
```

响应：

```json
{
  "total": 1,
  "items": [
    {
      "id": 101,
      "checkin_type": "dorm",
      "content": "今日完成思政学习并已在宿舍。",
      "teacher_status": "approved",
      "review_comment": "情况属实",
      "submitted_at": "2026-06-22 22:14:00"
    }
  ]
}
```

## 5. Teacher

### GET `/teacher/checkins`

查询参数：

```text
class_name=软件2401&date=2026-06-22&checkin_type=dorm&teacher_status=pending
```

响应：

```json
{
  "total": 1,
  "items": [
    {
      "id": 101,
      "student_name": "李明",
      "class_name": "软件2401",
      "checkin_type": "dorm",
      "content": "今日完成思政学习并已在宿舍。",
      "teacher_status": "pending",
      "location_status": "normal",
      "submitted_at": "2026-06-22 22:14:00"
    }
  ]
}
```

### POST `/teacher/reviews`

请求：

```json
{
  "checkin_id": 101,
  "action": "approved",
  "comment": "情况属实"
}
```

响应：

```json
{
  "checkin_id": 101,
  "teacher_status": "approved",
  "review_comment": "情况属实",
  "reviewed_at": "2026-06-22 22:30:00"
}
```

## 6. Stats

### GET `/stats/overview`

查询参数：

```text
date=2026-06-22&class_name=软件2401
```

响应：

```json
{
  "date": "2026-06-22",
  "scope": "软件2401",
  "expected_count": 128,
  "submitted_count": 109,
  "submit_rate": 0.85,
  "pending_review_count": 19,
  "abnormal_count": 4
}
```
