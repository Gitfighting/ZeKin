# FEAT-001 · 用户认证（注册 / 登录 / JWT）

| Feature ID | FEAT-001 |
|------------|----------|
| 需求 ID | FR-M01 |
| 优先级 | Must |
| Sprint | S1 |
| 后端 Owner | 赵耀 |
| 前端 Owner | 华心仪 + 胡钊炫 |
| 状态 | Approved |

## 1. 背景与目标

系统需识别用户身份并基于 RBAC 控制 API 访问。MVP 采用手机号 + 密码注册，JWT Bearer 认证。

## 2. 用户故事

- 作为新用户，我想注册账号并选择角色（student/teacher），以便使用系统。
- 作为用户，我想登录获取 token，以便访问受保护接口。
- 作为登录用户，我想查看个人信息，以便确认账号状态。

## 3. 验收标准

```gherkin
Scenario: 学生注册成功
  Given 手机号 13800138000 未被注册
  When  POST /api/v1/auth/register 含 phone, password, real_name, role=student, class_name
  Then  返回 code=200 且 data.user.id 存在
  And   密码不以明文存储

Scenario: 重复手机号注册失败
  Given 手机号已存在
  When  再次注册
  Then  返回 code=409

Scenario: 登录成功返回 JWT
  Given 用户已注册
  When  POST /api/v1/auth/login 含 phone, password
  Then  返回 access_token 与 token_type=bearer
  And   token 含 sub=user_id 与 role

Scenario: 错误密码登录失败
  When  password 错误
  Then  返回 code=401

Scenario: 获取当前用户
  Given 有效 JWT
  When  GET /api/v1/auth/me
  Then  返回用户信息不含 password_hash
```

## 4. API 契约

见 `specs/openapi.yaml` → `Auth` tag

## 5. UI 行为

- 学生端 `/login` `/register`：手机号、密码、姓名、班级（学生必填）
- 管理端 `/login`：同上，teacher/admin 无班级字段
- 登录成功：Pinia 存 token，路由跳转首页
- 401 响应：清 token，跳转登录

## 6. 数据影响

- 表：`users`
- Migration：初始 migration

## 7. 测试用例

- TC-AUTH-01 ~ TC-AUTH-05

## 8. 非目标

- 短信验证码登录（V2）
- OAuth 第三方登录（V2）
