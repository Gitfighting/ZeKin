# 05 后端 API 与前端目录结构

## 后端目录

```text
backend/
  pyproject.toml
  uv.lock
  alembic/
  app/
    main.py
    core/
      config.py
      database.py
      security.py
      errors.py
      logging.py
    modules/
      auth/
      identity/
      groups/
      checkin_types/
      rule_templates/
      tasks/
      records/
      exceptions/
      messages/
      statistics/
      integrations/
    shared/
      pagination.py
      response.py
      enums.py
      validators.py
```

每个业务模块内部按以下结构组织：

```text
modules/tasks/
  models.py
  schemas.py
  repository.py
  service.py
  router.py
```

`models.py` 定义 SQLAlchemy 模型；`schemas.py` 定义 Pydantic 请求和响应；`repository.py` 负责数据访问；`service.py` 负责业务逻辑；`router.py` 暴露 FastAPI 路由。

## API 分组

### 认证

- `POST /api/auth/login`
- `POST /api/auth/student/activate`
- `POST /api/auth/send-code`
- `POST /api/auth/bind-wechat`
- `GET /api/auth/me`

### 管理员

- `GET /api/admin/dashboard`
- `GET /api/admin/org/tree`
- `POST /api/admin/students/import`
- `GET /api/admin/students`
- `GET /api/admin/teachers`
- `GET /api/admin/groups`
- `GET /api/admin/checkin-types`
- `GET /api/admin/rule-templates`
- `GET /api/admin/tasks`
- `GET /api/admin/exceptions`

### 教师

- `GET /api/teacher/dashboard`
- `GET /api/teacher/groups`
- `GET /api/teacher/tasks`
- `POST /api/teacher/tasks`
- `GET /api/teacher/tasks/{id}`
- `POST /api/teacher/tasks/{id}/publish`
- `POST /api/teacher/tasks/{id}/end`
- `GET /api/teacher/exceptions`
- `POST /api/teacher/exceptions/{id}/review`

### 学生

- `GET /api/student/dashboard`
- `GET /api/student/tasks`
- `GET /api/student/tasks/{id}`
- `POST /api/student/tasks/{id}/checkin`
- `GET /api/student/records`
- `POST /api/student/records/{id}/appeal`
- `GET /api/student/messages`
- `GET /api/student/profile`
- `GET /api/student/growth-summary`

## 管理端目录

```text
admin-web/
  src/
    api/
    router/
    stores/
    layouts/
    views/
      login/
      dashboard/
      organization/
      students/
      teachers/
      groups/
      checkin-types/
      rule-templates/
      task-monitor/
      exceptions/
    components/
      DataTable/
      RuleEditor/
      OrgTree/
```

重点复用组件：

- `OrgTree`：组织树和范围选择。
- `DataTable`：筛选、分页、批量操作。
- `RuleEditor`：规则模板编辑器。

## uni-app 目录

```text
mini-app/
  src/
    pages/
      auth/
        login.vue
        activate.vue
      student/
        home.vue
        tasks.vue
        task-detail.vue
        checkin-submit.vue
        result.vue
        messages.vue
        profile.vue
        records.vue
        appeal.vue
      teacher/
        home.vue
        tasks.vue
        task-create.vue
        task-detail.vue
        exceptions.vue
        groups.vue
        group-detail.vue
        profile.vue
    services/
      request.ts
      auth.ts
      student.ts
      teacher.ts
      location.ts
    stores/
      user.ts
      app.ts
    components/
      TaskCard.vue
      StatusTag.vue
      RuleSummary.vue
      DynamicForm.vue
      LocationPicker.vue
```

学生端和教师端放在同一个 uni-app 项目中，通过登录后的 `user_type` 和角色路由跳转。这样可以复用登录、请求、消息、定位、动态表单组件。

## 关键复用组件

- `DynamicForm`：根据任务规则渲染文字、图片、日志、安全状态等提交项。
- `RuleSummary`：教师确认发布、学生任务详情都可复用。
- `LocationPicker`：封装 `uni.getLocation` 和定位授权提示。
- `StatusTag`：统一展示正常、迟到、异常、待审核、已驳回等状态。
