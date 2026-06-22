# FEAT-003 · 教师审核

| Feature ID | FEAT-003 |
|------------|----------|
| 需求 ID | FR-M04, FR-M05 |
| 优先级 | Must |
| Sprint | S1 |
| 后端 Owner | 赵耀 |
| 前端 Owner | 胡钊炫 |
| 状态 | Approved |

## 1. 背景与目标

教师按班级/日期查看学生打卡，手动通过或驳回；学生可在历史中看到审核结果。

## 2. 用户故事

- 作为教师，我想按班级和日期筛选打卡列表，以便批量审核。
- 作为教师，我想查看打卡详情（内容、照片、定位、AI 结果）并填写评语。
- 作为学生，我想看到 teacher_status 更新为 approved/rejected。

## 3. 验收标准

```gherkin
Scenario: 教师查看班级打卡列表
  Given 教师 role=teacher 且 class_name=软件2201
  When  GET /api/v1/teacher/checkins?class_name=软件2201&date=2026-07-15
  Then  返回该班当日所有学生打卡（含未打卡占位）

Scenario: 无权限班级返回 403
  When  请求非所管班级
  Then  code=403

Scenario: 审核通过
  Given 打卡 id=42 且 teacher_status=pending
  When  POST /api/v1/teacher/reviews 含 checkin_id=42, action=approved, comment
  Then  teacher_status=approved
  And   reviews 表新增记录

Scenario: 重复审核被拒绝
  Given 已 approved
  When  再次审核
  Then  code=409
```

## 4. UI 行为

- `/teacher/review`：班级 Select、DatePicker、Table（姓名、类型、AI 状态、教师状态、操作）
- 详情 Drawer：全文、图片预览、地图点、通过/驳回按钮、评语输入

## 5. 数据影响

- 表：`reviews`，更新 `checkins.teacher_status`

## 6. 测试用例

- TC-REV-01 ~ TC-REV-07
