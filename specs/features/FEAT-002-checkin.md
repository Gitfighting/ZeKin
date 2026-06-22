# FEAT-002 · 学生打卡（三种场景）

| Feature ID | FEAT-002 |
|------------|----------|
| 需求 ID | FR-M02, FR-M03 |
| 优先级 | Must |
| Sprint | S1 |
| 后端 Owner | 赵耀 |
| 前端 Owner | 华心仪 |
| 状态 | Approved |

## 1. 背景与目标

支持查寝(dorm)、上课(class)、实习(internship) 三种打卡；记录文字心得、可选照片、GPS；同日同类型不可重复。

## 2. 用户故事

- 作为学生，我想选择打卡类型并提交心得，以便完成每日任务。
- 作为学生，我想在首页看到今日三种打卡状态，以便知道还需做什么。
- 作为学生，我想查看历史打卡及 AI/教师审核状态。

## 3. 验收标准

```gherkin
Scenario: 提交查寝打卡成功
  Given 学生已登录且今日未查寝打卡
  And   当前时间在查寝时段内（可配置，默认 22:00-23:00）
  When  POST /api/v1/checkins 含 checkin_type=dorm, content(20-500字), latitude, longitude
  Then  返回 id 与 ai_status=pending
  And   checkins 表新增记录

Scenario: 重复打卡被拒绝
  Given 今日已提交 dorm 打卡
  When  再次提交 dorm
  Then  返回 code=400 消息含"已打卡"

Scenario: 获取今日状态
  When  GET /api/v1/checkins/today
  Then  返回 dorm/class/internship 各自 status: done|pending|not_required

Scenario: 分页历史列表
  When  GET /api/v1/checkins?page=1&page_size=10
  Then  仅返回当前学生记录，按 created_at 降序
```

## 4. 业务规则

| 类型 | 时段规则 | 内容要求 |
|------|----------|----------|
| dorm | 22:00–23:00 | 20–500 字 |
| class | 对应课程 start_time 前 10min | 20–500 字 |
| internship | 工作日 | 20–500 字 |

照片：可选，≤2MB，jpg/png；存储路径 `/uploads/{user_id}/{date}_{uuid}.jpg`

GPS：获取失败允许提交，字段 `location_valid=false`

## 5. UI 行为

- `/checkin`：Tab 切换三种类型；字数计数；定位按钮；拍照；提交 loading
- `/home`：三卡片状态；最近 5 条历史

## 6. 数据影响

- 表：`checkins`
- 索引：`idx_user_date (user_id, created_at)`

## 7. 测试用例

- TC-CK-01 ~ TC-CK-10

## 8. 非目标

- 人脸识别（Could）
- 强制 GPS 白名单（Should，S2）
