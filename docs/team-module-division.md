# ZeKin 团队模块划分与协作规范

| 版本 | V1.0 · 2026-06-22 |
|------|-------------------|
| 团队 | 王韩韵 · 赵耀 · 胡钊炫 · 华心仪 |

---

## 1. 总体原则

- **契约先行**：所有跨模块交互以 `specs/openapi.yaml` 为准
- **边界清晰**：每人拥有明确目录 Owner 权，跨模块改动需 PR Review
- **并行开发**：后端 Mock 接口 → 前端并行 → 联调窗口（每周三、五下午）
- **Agent 辅助**：各成员在 Cursor 中引用 `specs/features/<模块>.md` 作为 Prompt 上下文

---

## 2. 成员职责矩阵（RACI）

| 工作项 | 王韩韵 | 赵耀 | 胡钊炫 | 华心仪 |
|--------|:------:|:----:|:------:|:------:|
| 需求分析与验收 | **R/A** | C | C | C |
| OpenAPI 契约 | A | **R** | C | C |
| 数据库设计 | A | **R** | I | I |
| 后端 API 实现 | I | **R/A** | I | I |
| 学生端 UI | C | I | I | **R/A** |
| 教师/管理端 UI | C | I | **R/A** | I |
| AI 审核对接 | A | **R** | — | — |
| 单元/接口测试 | **R** | R | R | R |
| CI/CD 与部署 | A | **R** | C | C |
| UAT 组织 | **R/A** | C | C | C |

> R=负责执行 A=最终审批 C=协商 I=知会

---

## 3. 代码仓库模块划分

```
ZeKin/
├── specs/                    # 王韩韵维护 Feature Spec；赵耀维护 OpenAPI/DDL
├── backend/                  # 赵耀 Owner
│   ├── app/
│   │   ├── api/v1/           # 路由层（按 domain 分包）
│   │   │   ├── auth.py
│   │   │   ├── checkins.py
│   │   │   ├── teacher.py
│   │   │   ├── stats.py
│   │   │   └── admin.py
│   │   ├── core/             # 配置、安全、依赖
│   │   ├── models/           # SQLAlchemy 模型
│   │   ├── schemas/          # Pydantic DTO
│   │   ├── services/         # 业务逻辑
│   │   └── workers/          # AI 异步任务
│   └── tests/
├── frontend/
│   ├── student/              # 华心仪 Owner
│   │   └── src/views/        # home, checkin, profile, auth
│   └── admin/                # 胡钊炫 Owner
│       └── src/views/        # dashboard, review, stats, admin/*
├── docs/                     # 王韩韵 Owner
├── deploy/                   # 赵耀 Owner（四环境 compose + nginx）
└── .github/workflows/        # 赵耀 Owner
```

---

## 4. 后端 Domain 模块（赵耀）

| Domain | 目录 | 核心 API | Sprint |
|--------|------|----------|--------|
| **M1 Auth** | `services/auth_service.py` | register, login, me | S1 |
| **M2 Checkin** | `services/checkin_service.py` | CRUD checkins, today | S1 |
| **M3 Review** | `services/review_service.py` | teacher checkins, reviews | S1 |
| **M4 Stats** | `services/stats_service.py` | overview, export | S2 |
| **M5 Admin** | `services/admin_service.py` | users, locations, courses | S2 |
| **M6 AI** | `workers/ai_review.py` | 异步内容审核 | S2 |
| **M7 Makeup** | `services/makeup_service.py` | 补签申请/审批 | S2 |

**M1–M3 为关键路径**，S1 结束必须联调通过。

---

## 5. 前端模块划分

### 5.1 学生端（华心仪 · `frontend/student/`）

| 页面/组件 | 路由 | 依赖 API | Sprint |
|-----------|------|----------|--------|
| 登录/注册 | `/login` `/register` | auth | S1 W1 |
| 首页 | `/home` | checkins/today, checkins list | S1 W2 |
| 打卡页 | `/checkin` | POST checkins, 上传 | S1 W2 |
| 个人中心 | `/profile` | auth/me, 补签 | S2 |
| 打卡日历 | `/calendar` | checkins (Could) | S3 |

**技术要点**：Vue 3 + Vite + Pinia + Vue Router；Geolocation API；`<input capture>` 拍照。

### 5.2 管理端（胡钊炫 · `frontend/admin/`）

| 页面/组件 | 路由 | 依赖 API | Sprint |
|-----------|------|----------|--------|
| 登录 | `/login` | auth | S1 W1 |
| 审核面板 | `/teacher/review` | teacher/checkins, reviews | S1 W2 |
| 数据看板 | `/teacher/dashboard` | stats/overview | S2 |
| 报表导出 | `/teacher/stats` | stats/export | S2 |
| 用户管理 | `/admin/users` | admin/users | S2 |
| 地点/课程 | `/admin/locations` `/admin/courses` | admin CRUD | S2 |

**技术要点**：Vue 3 + Element Plus + ECharts；Table 虚拟滚动；Excel 下载 blob。

---

## 6. 产品/QA 模块（王韩韵）

| 交付物 | 路径 | 节奏 |
|--------|------|------|
| Feature Spec | `specs/features/*.md` | Sprint 开始前 2 天 |
| 测试用例 | `docs/test-cases/` | 与 Spec 同步 |
| Sprint Review 纪要 | `docs/sprints/sprint-N.md` | 每 Sprint 末 |
| 验收清单 | `docs/acceptance-checklist.md` | UAT 前 |

---

## 7. Git 协作规范

### 7.1 分支模型

```
main          ← 生产（仅 PR + 标签）
develop       ← 集成分支
feat/backend-auth-xxx    赵耀
feat/admin-review-xxx    胡钊炫
feat/student-checkin-xxx 华心仪
docs/sprint1-specs       王韩韵
```

### 7.2 Commit 规范（Conventional Commits）

```
feat(checkin): add dorm checkin API
fix(auth): correct JWT expiry
docs(spec): update UC001 acceptance criteria
```

### 7.3 PR 规则

- 至少 1 人 Review（跨模块需双方 Owner）
- CI 通过：lint + unit test
- 关联 Issue / 需求 ID（如 `FR-M02`）

### 7.4 并行冲突预防

| 场景 | 规则 |
|------|------|
| 改 OpenAPI | 赵耀提 PR，@all Review，合并后各端 rebase |
| 改 DDL | 仅赵耀；附 migration 脚本 |
| 共享类型 | 从 OpenAPI 生成 TS 类型（`openapi-typescript`） |

---

## 8. 沟通机制

| 仪式 | 频率 | 参与 | 时长 |
|------|------|------|------|
| Daily Standup | 每工作日 | 全员 | 15min |
| Backlog Refinement | 每周二 | 王韩韵 + 全员 | 30min |
| Sprint Planning | 每 2 周周一 | 全员 | 1h |
| Sprint Review | 每 2 周周五 | 全员 + 甲方 | 1h |
| Retrospective | Review 后 | 全员 | 30min |

---

## 9. Sprint 与模块交付对照

| Sprint | 赵耀 | 胡钊炫 | 华心仪 | 王韩韵 |
|--------|------|--------|--------|--------|
| S0 | OpenAPI + DDL + 项目脚手架 | admin 脚手架 | student 脚手架 | 需求报告 + Feature Spec |
| S1 | M1–M3 API + 部署 Dev | 登录 + 审核页 | 登录 + 打卡 + 首页 | 测试用例 + S1 验收 |
| S2 | M4–M7 + UAT 部署 | 统计 + 管理后台 | 补签 + 个人中心 | UAT 计划 |
| S3 | Bugfix + 性能 | UI  polish | 移动端适配 | 全量测试 + 验收报告 |
| S4 | Prod 部署 | — | — | 培训 + 签字 |

---

## 10. Definition of Done（DoD）

- [ ] Feature Spec 与 OpenAPI 已更新
- [ ] 代码已合并 `develop` 并通过 CI
- [ ] 单元测试覆盖核心路径
- [ ] 已在 Local 联调；Dev 环境可演示
- [ ] 王韩韵测试用例通过或缺陷已登记
