# Feature Spec 模板

> 规格驱动开发（Spec-Driven Development）— 先写规格，再写代码。  
> Owner：王韩韵 · 技术契约：赵耀（OpenAPI）

---

## 元信息

| 字段 | 值 |
|------|-----|
| Feature ID | FEAT-XXX |
| 需求 ID | FR-Mxx / FR-Sxx |
| 优先级 | Must / Should / Could |
| Sprint | S1 / S2 |
| 后端 Owner | 赵耀 |
| 前端 Owner | 华心仪 / 胡钊炫 |
| 状态 | Draft / Review / Approved / Done |

---

## 1. 背景与目标

（为什么做？成功标准是什么？）

---

## 2. 用户故事

```
作为 [角色]，
我想要 [能力]，
以便 [价值]。
```

---

## 3. 验收标准（Given-When-Then）

```gherkin
Scenario: 场景名称
  Given 前置条件
  When  用户操作
  Then  期望结果
  And   附加断言
```

---

## 4. API 契约引用

| 方法 | 路径 | OpenAPI ref |
|------|------|-------------|
| POST | /api/v1/... | `#/paths/...` |

请求/响应示例（JSON）。

---

## 5. UI 行为

- 页面路由：
- 交互说明：
- 空态/错误态：

---

## 6. 数据影响

- 涉及表：
- Migration：是/否

---

## 7. 测试用例 ID

- TC-XXX-01
- TC-XXX-02

---

## 8. 非目标（Out of Scope）

---

## 9. Agent 开发提示（Cursor / Claude）

```
请严格依据 specs/features/FEAT-XXX.md 与 specs/openapi.yaml 实现。
不要新增未在 OpenAPI 中声明的字段。
后端使用 FastAPI + SQLAlchemy；前端使用 Vue 3。
```

---

## 变更记录

| 日期 | 作者 | 变更 |
|------|------|------|
