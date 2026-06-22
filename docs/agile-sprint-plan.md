# ZeKin 敏捷 Sprint 计划

| 项目周期 | 2026-07-01 ~ 2026-08-16（47 天） |
|----------|----------------------------------|
| 模式 | Scrum · 2 周 Sprint × 2 + S0/S3/S4 |

---

## Sprint 0 · 需求与设计（D1–D7 · 7.1–7.7）

**目标**：规格冻结，四环境 Local 就绪，团队对齐技术栈 **FastAPI + Vue + MySQL**。

| 任务 ID | 任务 | 负责人 | 交付物 |
|---------|------|--------|--------|
| S0-01 | 需求评审与 MVP 范围签字 | 王韩韵 | `docs/requirements-analysis-report.md` |
| S0-02 | OpenAPI 3.1 契约 v0.1 | 赵耀 | `specs/openapi.yaml` |
| S0-03 | MySQL DDL + ER 图 | 赵耀 | `specs/database/schema.sql` |
| S0-04 | Feature Spec（Must 模块） | 王韩韵 | `specs/features/*.md` |
| S0-05 | 后端脚手架 FastAPI | 赵耀 | `backend/` 可启动 |
| S0-06 | admin-web 脚手架 | 胡钊炫 | `frontend/admin/` |
| S0-07 | student-web 脚手架 | 华心仪 | `frontend/student/` |
| S0-08 | docker-compose Local | 赵耀 | `deploy/docker-compose.local.yml` |
| S0-09 | Git 分支策略 + README | 全员 | `develop` 分支 |

**Sprint 0 Review 标准**：Local `docker-compose up` 后 API `/health` 200，前端两 app 可访问。

---

## Sprint 1 · 核心 Must（D8–D21 · 7.8–7.21）

**目标**：认证 + 打卡 + 教师审核 E2E 跑通；**首次 Dev 环境部署**。

### Backlog

| Story | 点数 | 负责人 | 模块 |
|-------|------|--------|------|
| US-001 用户注册登录 JWT | 5 | 赵耀 + 双端 | Auth |
| US-002 提交三种打卡 | 8 | 赵耀 + 华心仪 | Checkin |
| US-003 今日状态与历史 | 5 | 赵耀 + 华心仪 | Checkin |
| US-004 教师审核列表/详情 | 8 | 赵耀 + 胡钊炫 | Review |
| US-005 照片上传与存储 | 3 | 赵耀 | Upload |
| US-006 GPS 记录 | 2 | 赵耀 + 华心仪 | Checkin |
| US-007 Dev 环境 CI 部署 | 5 | 赵耀 | DevOps |

**合计**：~36 点（四人团队可承载）

### 里程碑

- **W1 结束**：Auth API + 双端登录页
- **W2 结束**：打卡 E2E + 教师审核 E2E
- **S1 末**：Dev 服务器演示 Must 功能

---

## Sprint 2 · Should 增强（D22–D35 · 7.22–8.4）

**目标**：AI 审核、统计导出、补签、管理后台；**UAT 环境部署**。

| Story | 点数 | 负责人 |
|-------|------|--------|
| US-008 AI 异步内容审核 | 8 | 赵耀 |
| US-009 班级统计与 Excel 导出 | 5 | 赵耀 + 胡钊炫 |
| US-010 补签申请与审批 | 8 | 赵耀 + 华心仪 + 胡钊炫 |
| US-011 管理员 CRUD（用户/地点/课程） | 8 | 赵耀 + 胡钊炫 |
| US-012 定位白名单校验（可开关） | 3 | 赵耀 |
| US-013 站内消息通知 | 5 | 赵耀 + 华心仪 |
| US-014 UAT 环境部署 | 3 | 赵耀 |

**Could（余量）**：打卡日历、积分字段、每日语录

---

## Sprint 3 · 测试与优化（D36–D42 · 8.5–8.11）

**目标**：UAT 验收通过，零 P0/P1 缺陷。

| 任务 | 负责人 |
|------|--------|
| 功能回归（RTM 全量） | 王韩韵 |
| 接口压测 1000 并发打卡 | 赵耀 |
| 安全扫描（JWT、SQL 注入、XSS） | 赵耀 |
| 移动端兼容性 | 华心仪 |
| 管理端 UX 优化 | 胡钊炫 |
| Bug 修复 | 按模块 Owner |
| 用户手册 / 部署手册 | 王韩韵 + 赵耀 |

---

## Sprint 4 · 生产上线（D43–D47 · 8.12–8.16）

**目标**：**Prod 环境**上线，验收签字。

| 日 | 活动 | 负责人 |
|----|------|--------|
| D43 | Prod 环境搭建、DB 迁移、密钥配置 | 赵耀 |
| D44 | Prod 冒烟测试 + 回滚演练 | 赵耀 + 王韩韵 |
| D45 | 用户培训（学生/教师/管理员） | 王韩韵 |
| D46 | 甲方 UAT 签字复测 | 王韩韵 |
| D47 | 验收报告、源码交付、项目复盘 | 全员 |

---

## 燃尽图跟踪

使用 GitHub Projects / 飞书多维表格，按 Story 点数每日更新 Remaining Points。

---

## 敏捷仪式日历（示例 · Sprint 1）

| 日期 | 事件 |
|------|------|
| 7.8 Mon | Sprint 1 Planning |
| 7.8–7.21 | Daily Standup 10:00 |
| 7.15 Tue | Backlog Refinement（S2 预排） |
| 7.21 Fri | Sprint 1 Review + Retro |

---

## 变更管理

需求变更须填写 `docs/change-request-template.md`，王韩韵评估影响 → 团队投票 → 更新 OpenAPI & RTM。
