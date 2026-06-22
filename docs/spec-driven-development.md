# ZeKin 规格驱动开发指南

> 2026 Agent 开发最佳实践：Spec → Contract → Code → Test

---

## 1. 什么是规格驱动开发（SDD）

在 AI Agent 辅助编程时代，**规格文档是 Prompt 的权威上下文**，代码是规格的派生物。

```
specs/features/*.md  ──→  验收标准（Gherkin）
specs/openapi.yaml   ──→  API 契约（前后端并行）
specs/database/      ──→  数据模型
         │
         ▼
   backend/ + frontend/
         │
         ▼
   tests/ + CI 契约校验
```

**原则**：未写入 Spec/OpenAPI 的功能，不实现；变更先改 Spec，再改代码。

---

## 2. 目录职责

| 路径 | Owner | 说明 |
|------|-------|------|
| `specs/openapi.yaml` | 赵耀 | API 单一事实来源 |
| `specs/features/` | 王韩韵 | Feature Spec + Gherkin |
| `specs/database/schema.sql` | 赵耀 | DDL 基线 |
| `docs/requirements-analysis-report.md` | 王韩韵 | 需求总览 |

---

## 3. Agent 开发工作流（Cursor）

### Step 1 · 领取 Story

从 Sprint Backlog 取 `US-00X`，打开对应 `specs/features/FEAT-XXX.md`。

### Step 2 · Prompt 模板

```
你是 ZeKin 项目开发助手。
技术栈：FastAPI + SQLAlchemy + Vue3 + MySQL。
请阅读：
- specs/features/FEAT-002-checkin.md
- specs/openapi.yaml 中 Checkins 相关 paths
- specs/database/schema.sql 中 checkins 表

任务：实现 POST /api/v1/checkins，不要添加 Spec 未声明的字段。
完成后编写 pytest 覆盖 Scenario「提交查寝打卡成功」。
```

### Step 3 · 契约校验

```bash
# 后端启动后
curl http://localhost:8000/openapi.json | diff - specs/openapi.yaml  # 人工对账

# 或使用 schemathesis（可选）
schemathesis run specs/openapi.yaml --base-url=http://localhost:8000/api/v1
```

### Step 4 · PR Checklist

- [ ] Feature Spec 状态 → Done
- [ ] OpenAPI 已同步
- [ ] 测试用例 ID 已覆盖
- [ ] 至少 1 人 Review

---

## 4. OpenAPI 变更流程

1. 赵耀提 PR 修改 `specs/openapi.yaml`
2. @胡钊炫 @华心仪 Review 前端影响
3. 合并后前端运行 `npm run generate:api`（从 OpenAPI 生成 TS 类型）
4. 各 feature 分支 rebase `develop`

---

## 5. 与敏捷 Sprint 对齐

| Sprint | Spec 活动 |
|--------|-----------|
| S0 | 冻结 Must Spec + OpenAPI v1.0 |
| S1 | Must Spec → 实现 → Review |
| S2 | Should Spec 增量 + OpenAPI v1.1 |
| S3 | 回归 RTM，Spec 状态全 Done |

---

## 6. 反模式（禁止）

- ❌ 先写代码后补文档
- ❌ Agent 自由发挥新增 API 字段
- ❌ 前后端口头约定接口
- ❌ 跳过 Gherkin 验收标准

---

## 7. 工具推荐

| 工具 | 用途 |
|------|------|
| Cursor / Claude Code | Agent 编码 |
| Bruno / Postman | 导入 openapi.yaml 调试 |
| openapi-typescript | 生成前端类型 |
| pytest + httpx | 后端 API 测试 |
| Playwright | 前端 E2E（S3） |
