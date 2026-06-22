# 知勤打卡系统 72 小时 MVP 模块划分与 WBS 任务分解报告

版本：V1.0  
日期：2026-06-22  
角色定位：产品经理 / 项目经理 / 需求负责人  
技术约束：Python + FastAPI + Vue + MySQL  
协作方式：Git + GitHub Pull Request + 规格驱动开发  
团队成员：王韩韵、赵耀、胡钊炫、华心仪

## 1. 报告目标

本报告将《实训-知勤打卡系统-需求分析》转化为可执行的工程开发计划，重点回答四个问题：

1. 72 小时 MVP 到底拆成哪些模块。
2. 四位成员分别负责什么，哪些文件和目录归谁所有。
3. 每个任务的输入、输出、依赖、验收标准是什么。
4. 如何用 Git 保证并行开发互不干扰。

本报告的设计原则是“业务闭环优先、模块边界清晰、接口契约先行、每日集成可演示”。72 小时内不追求平台完整性，优先保证“学生打卡 → 教师审核 → 学生查看结果 → 统计概览”的最小可用闭环。

## 2. 2026 技术最佳实践约束

### 2.1 后端：FastAPI 模块化

FastAPI 官方建议大型应用使用 `APIRouter` 拆分多文件路由；`APIRouter` 可被视作一个小型 FastAPI 应用，支持独立的参数、响应、依赖和标签配置。因此后端按业务域拆分 router，而不是把所有接口写在 `main.py` 中。

后端约束：

- `backend/app/main.py` 只负责应用创建、中间件、路由挂载和健康检查。
- `backend/app/api/v1/*.py` 按业务模块拆分接口。
- `backend/app/schemas/` 存放 Pydantic 请求和响应模型。
- `backend/app/services/` 存放业务规则，不在 router 中写复杂业务逻辑。
- `backend/app/repositories/` 存放数据库访问逻辑，避免服务层直接拼 SQL。
- 鉴权、当前用户、数据库会话使用 FastAPI Dependency Injection。

### 2.2 前端：Vue 组件化与独立端拆分

Vue 官方将组件定义为可独立思考、可复用的 UI 单元，并推荐使用 Vite 创建单页应用。为了让学生端和教师/管理端互不影响，本项目采用双前端应用：

- `frontend/student/`：学生移动端 H5。
- `frontend/admin/`：教师与管理员 Web 工作台。

前端约束：

- 页面级组件放在 `views/`。
- 复用组件放在 `components/`。
- API 调用封装在 `api/`。
- 登录态和用户信息放在 `stores/`。
- 地理定位、表单校验等复用逻辑放在 `composables/`。
- 前端不得绕过接口契约新增字段，接口字段以 `docs/api-contract.md` 为准。

### 2.3 数据库：MySQL 事务与外键一致性

MySQL 官方文档说明 InnoDB 支持事务隔离，外键用于跨表引用并保持相关数据一致。MVP 阶段数据库必须简洁，但不能牺牲关键一致性。

数据库约束：

- 使用 MySQL 8.x + InnoDB。
- 核心表使用主键、唯一约束、外键和必要索引。
- `users`、`classes`、`checkins`、`reviews`、`courses`、`location_rules` 为 72 小时 MVP 基础表。
- 同一学生同一日期同一类型打卡通过唯一约束或服务层校验保证。
- 所有核心记录保留 `created_at`、`updated_at` 或业务时间字段。

### 2.4 Git：保护主分支与 Pull Request 评审

GitHub 官方支持分支保护规则，可限制删除、强推，并要求状态检查或 PR 审批；Required Reviews 可要求合并前获得审批。项目必须避免多人直接向 `main` 推送导致覆盖。

Git 约束：

- `main`：只保存可演示、可验收版本。
- `develop`：72 小时集成分支。
- 个人功能分支：每个人只在自己的模块目录内开发。
- 所有跨模块变更必须先提交 issue 或在群内说明。
- `main` 建议开启保护：禁止 force push、至少 1 个 review、要求 CI 通过。

## 3. 总体模块架构

### 3.1 模块视图

```text
知勤打卡系统
├── 学生端 H5（华心仪）
│   ├── 登录
│   ├── 今日状态
│   ├── 提交打卡
│   └── 打卡历史
├── 教师/管理端 Web（胡钊炫）
│   ├── 教师登录
│   ├── 审核列表
│   ├── 打卡详情
│   ├── 审核通过/驳回
│   └── 统计概览
├── 后端 API 与业务服务（赵耀）
│   ├── 认证授权
│   ├── 打卡服务
│   ├── 审核服务
│   ├── 统计服务
│   └── 数据库迁移与初始化
└── 产品规格与验收（王韩韵）
    ├── 需求冻结
    ├── 接口契约
    ├── 验收脚本
    ├── 缺陷优先级
    └── 四环境验收
```

### 3.2 独立开发目录边界

| 成员 | Owner 目录 | 可独立开发内容 | 禁止直接修改 |
|---|---|---|---|
| 王韩韵 | `docs/`、`acceptance/` | 需求、验收、测试脚本、演示数据说明 | `backend/`、`frontend/` 业务代码 |
| 赵耀 | `backend/`、`database/`、`deploy/` | FastAPI、MySQL、部署、接口实现 | `frontend/student/`、`frontend/admin/` 页面 |
| 胡钊炫 | `frontend/admin/` | 教师/管理端页面、组件、状态管理 | `backend/` 数据库和业务规则 |
| 华心仪 | `frontend/student/` | 学生端页面、组件、定位交互 | `backend/` 数据库和业务规则 |

跨模块修改规则：

- 前端需要新增接口字段：先由王韩韵更新需求说明，再由赵耀更新接口契约。
- 后端改变响应结构：必须同步通知胡钊炫和华心仪，并更新 `docs/api-contract.md`。
- 数据库字段改变：必须由赵耀统一修改迁移和初始化数据。
- 页面文案、验收逻辑改变：必须由王韩韵确认。

## 4. 模块拆分说明

### 4.1 M1 认证与角色模块

业务目标：让学生、教师、管理员以合法身份进入系统，并进入对应工作台。

后端范围：

- 登录接口。
- 当前用户接口。
- Token 签发与校验。
- 角色权限依赖。

前端范围：

- 学生端登录页。
- 教师/管理端登录页。
- 登录态保存与退出。
- 未登录拦截。

独立性说明：

- 后端先提供 mock 账号和固定 Token 结构。
- 学生端和管理端只依赖 `/auth/login`、`/auth/me`，不互相依赖。

### 4.2 M2 学生打卡模块

业务目标：学生完成查寝、上课、实习三类打卡，系统保存可审核、可追溯记录。

后端范围：

- 今日状态接口。
- 提交打卡接口。
- 我的历史接口。
- 重复打卡校验。
- 定位异常标记。

学生端范围：

- 今日状态卡片。
- 打卡类型切换。
- 内容输入。
- 定位采集。
- 提交结果提示。
- 历史记录列表。

独立性说明：

- 学生端可先用 mock 数据开发页面。
- 后端按接口契约完成后替换 API 地址。
- 不依赖教师端页面完成。

### 4.3 M3 教师审核模块

业务目标：教师查看所管班级打卡记录，完成通过或驳回。

后端范围：

- 教师打卡列表接口。
- 打卡详情接口。
- 审核提交接口。
- 班级权限校验。

教师端范围：

- 筛选栏：班级、日期、类型、状态。
- 审核列表。
- 详情面板。
- 通过/驳回操作。
- 驳回原因填写。

独立性说明：

- 教师端依赖教师审核接口，不依赖学生端页面。
- 后端可通过演示数据构造待审核记录，让教师端独立联调。

### 4.4 M4 统计概览模块

业务目标：让教师和管理员快速掌握今日完成率、待审核和异常情况。

后端范围：

- 今日统计接口。
- 教师班级范围统计。
- 管理员全局统计。

管理端范围：

- 指标卡片。
- 趋势图占位或轻量图。
- 异常待处理列表入口。

独立性说明：

- 统计模块只读，不阻塞打卡和审核闭环。
- 可用初始化数据提前联调。

### 4.5 M5 数据库与演示数据模块

业务目标：用最少表结构支撑 72 小时验收演示。

表范围：

- `users`
- `classes`
- `courses`
- `checkins`
- `reviews`
- `location_rules`

独立性说明：

- 赵耀负责 DDL 和 seed 数据。
- 前端只通过 API 使用数据，不直接连接数据库。

### 4.6 M6 验收与项目管理模块

业务目标：保证 72 小时内有明确验收脚本、缺陷分级和四环境检查。

范围：

- 需求跟踪矩阵。
- 验收脚本。
- 演示账号。
- 缺陷模板。
- 四环境检查清单。

独立性说明：

- 王韩韵可独立完成文档与验收材料。
- 不阻塞其他成员编码，但会约束最终验收。

## 5. WBS 任务分解

### 5.1 WBS 总览

| WBS 编号 | 工作包 | 负责人 | 产出物 | 依赖 |
|---|---|---|---|---|
| 1.0 | 项目规格与验收管理 | 王韩韵 | 需求冻结、验收脚本、缺陷模板 | 无 |
| 2.0 | 后端 API 与数据库 | 赵耀 | FastAPI 服务、MySQL 表、接口 | 1.1 接口契约 |
| 3.0 | 学生端 H5 | 华心仪 | 登录、今日状态、打卡、历史 | 1.1 接口契约 |
| 4.0 | 教师/管理端 Web | 胡钊炫 | 审核、详情、统计 | 1.1 接口契约 |
| 5.0 | 联调与四环境验收 | 全员 | 可演示系统、验收记录 | 2.0、3.0、4.0 |

### 5.2 WBS 详细任务

#### 1.0 项目规格与验收管理（王韩韵）

| WBS | 任务 | 输入 | 输出 | 验收标准 | 时间 |
|---|---|---|---|---|---|
| 1.1 | 冻结 72 小时 MVP 范围 | 需求分析报告 | MVP 范围清单 | Must/Should/Could 明确 | H0-H2 |
| 1.2 | 编写接口契约草案 | 用例规约、顺序图 | `docs/api-contract.md` | 前后端字段一致 | H0-H4 |
| 1.3 | 编写验收脚本 | 用例规约 | `acceptance/uat-script.md` | 覆盖登录、打卡、审核、统计 | H2-H6 |
| 1.4 | 建立缺陷分级规则 | 验收目标 | `acceptance/bug-template.md` | P0/P1/P2 定义清晰 | H4-H6 |
| 1.5 | 每 12 小时组织集成检查 | 各成员进度 | 集成记录 | 阻塞问题有负责人 | H12/H24/H36/H48/H60 |
| 1.6 | 组织最终验收 | 可运行系统 | 验收报告 | 四环境结果明确 | H66-H72 |

#### 2.0 后端 API 与数据库（赵耀）

| WBS | 任务 | 输入 | 输出 | 验收标准 | 时间 |
|---|---|---|---|---|---|
| 2.1 | 初始化 FastAPI 项目 | 技术栈约束 | `backend/app/main.py` | `/health` 可访问 | H6-H8 |
| 2.2 | 建立项目分层目录 | 架构约束 | `api/`、`schemas/`、`services/`、`repositories/` | 目录清晰可导入 | H6-H8 |
| 2.3 | 设计 MySQL 最小 DDL | 分析类图 | `database/schema.sql` | 6 张基础表可创建 | H8-H10 |
| 2.4 | 初始化演示数据 | 验收脚本 | `database/seed.sql` | 至少 1 管理员、1 教师、3 学生 | H10-H12 |
| 2.5 | 实现认证接口 | M1 | `/auth/login`、`/auth/me` | 三类角色可登录 | H12-H18 |
| 2.6 | 实现学生打卡接口 | M2 | `/checkins/today`、`POST /checkins`、`GET /checkins` | 支持三类打卡和重复校验 | H18-H30 |
| 2.7 | 实现教师审核接口 | M3 | `/teacher/checkins`、`POST /teacher/reviews` | 支持筛选、通过、驳回 | H30-H42 |
| 2.8 | 实现统计接口 | M4 | `/stats/overview` | 返回打卡率、待审核、异常数 | H42-H50 |
| 2.9 | 权限和异常处理 | 所有接口 | 统一错误响应 | 未登录 401、越权 403 | H48-H56 |
| 2.10 | 部署与环境变量 | 四环境要求 | `.env.example`、启动说明 | 本地和服务器可启动 | H56-H66 |

#### 3.0 学生端 H5（华心仪）

| WBS | 任务 | 输入 | 输出 | 验收标准 | 时间 |
|---|---|---|---|---|---|
| 3.1 | 初始化 Vue 学生端 | 原型样图 | `frontend/student/` | Vite 可启动 | H6-H8 |
| 3.2 | 登录页 | M1 接口 | `LoginView.vue` | 学生账号可登录 | H8-H14 |
| 3.3 | 路由与登录态 | M1 接口 | router、store | 未登录自动回登录页 | H12-H18 |
| 3.4 | 今日状态页面 | M2 接口或 mock | `HomeView.vue` | 三类状态清晰展示 | H18-H26 |
| 3.5 | 打卡表单 | 原型、M2 接口 | `CheckinView.vue` | 可选类型、填内容、定位 | H24-H34 |
| 3.6 | 定位 composable | 浏览器定位 API | `useGeolocation.ts/js` | 定位失败有降级提示 | H26-H34 |
| 3.7 | 历史记录页面 | M2 接口 | `HistoryView.vue` | 显示审核状态和评语 | H34-H42 |
| 3.8 | 学生端联调 | 后端接口 | 可演示学生端 | 登录、打卡、历史闭环通过 | H42-H58 |
| 3.9 | 移动端适配 | 核心页面 | CSS 修正 | 手机宽度不溢出 | H58-H66 |

#### 4.0 教师/管理端 Web（胡钊炫）

| WBS | 任务 | 输入 | 输出 | 验收标准 | 时间 |
|---|---|---|---|---|---|
| 4.1 | 初始化 Vue 管理端 | 原型样图 | `frontend/admin/` | Vite 可启动 | H6-H8 |
| 4.2 | 教师/管理员登录页 | M1 接口 | `LoginView.vue` | 教师、管理员可登录 | H8-H14 |
| 4.3 | 管理端布局 | 原型样图 | Layout、导航、路由 | 审核和统计入口清晰 | H12-H18 |
| 4.4 | 审核筛选栏 | M3 接口 | 班级、日期、类型、状态筛选 | 筛选条件可提交 | H18-H26 |
| 4.5 | 审核列表 | M3 接口或 mock | `ReviewList.vue` | 待审核记录展示完整 | H24-H34 |
| 4.6 | 打卡详情面板 | M3 接口 | `ReviewDetail.vue` | 内容、定位、状态可见 | H30-H38 |
| 4.7 | 通过/驳回操作 | M3 接口 | 审核按钮和原因输入 | 驳回必须填原因 | H36-H46 |
| 4.8 | 统计概览页面 | M4 接口 | `DashboardView.vue` | 指标卡片正确展示 | H42-H54 |
| 4.9 | 管理端联调 | 后端接口 | 可演示管理端 | 审核和统计闭环通过 | H54-H66 |

#### 5.0 联调、质量与四环境验收（全员）

| WBS | 任务 | 负责人 | 输出 | 验收标准 | 时间 |
|---|---|---|---|---|---|
| 5.1 | 第一次集成 | 全员 | develop 可启动 | 登录接口和两个前端启动 | H12 |
| 5.2 | 第二次集成 | 全员 | 学生打卡闭环 | 学生可提交打卡 | H24 |
| 5.3 | 第三次集成 | 全员 | 教师审核闭环 | 教师可审核记录 | H36 |
| 5.4 | 第四次集成 | 全员 | 统计联调 | 统计指标可展示 | H48 |
| 5.5 | 回归测试 | 王韩韵主导，全员配合 | 缺陷清单 | P0 缺陷为 0 | H60-H66 |
| 5.6 | 本地开发环境验收 | 全员 | 本地验收记录 | 每人机器可启动 | H60-H66 |
| 5.7 | 服务器部署环境验收 | 赵耀 | 服务器访问地址 | 外部浏览器可访问 | H62-H68 |
| 5.8 | 用户验收环境演示 | 王韩韵 | UAT 记录 | 10 步验收脚本通过 | H66-H70 |
| 5.9 | 生产环境测试冒烟 | 赵耀、王韩韵 | 冒烟报告 | 关键流程无阻塞 | H70-H72 |

## 6. 接口契约与并行开发边界

### 6.1 最小接口清单

| 模块 | 方法 | 路径 | 调用方 | 负责人 |
|---|---|---|---|---|
| Auth | POST | `/api/v1/auth/login` | 学生端、管理端 | 赵耀 |
| Auth | GET | `/api/v1/auth/me` | 学生端、管理端 | 赵耀 |
| Checkin | GET | `/api/v1/checkins/today` | 学生端 | 赵耀 |
| Checkin | POST | `/api/v1/checkins` | 学生端 | 赵耀 |
| Checkin | GET | `/api/v1/checkins` | 学生端 | 赵耀 |
| Teacher | GET | `/api/v1/teacher/checkins` | 管理端 | 赵耀 |
| Teacher | POST | `/api/v1/teacher/reviews` | 管理端 | 赵耀 |
| Stats | GET | `/api/v1/stats/overview` | 管理端 | 赵耀 |

### 6.2 状态枚举约束

| 字段 | 可选值 | 说明 |
|---|---|---|
| `role` | `student`、`teacher`、`admin` | 用户角色 |
| `checkin_type` | `dorm`、`class`、`internship` | 查寝、上课、实习 |
| `teacher_status` | `pending`、`approved`、`rejected` | 教师审核状态 |
| `location_status` | `normal`、`abnormal`、`unknown` | 定位状态 |

前后端并行开发时，字段名和枚举值不得自行翻译。页面展示可翻译为中文，接口传输必须使用英文枚举。

## 7. Git 版本管理方案

### 7.1 分支设计

| 分支 | 用途 | 合并方向 |
|---|---|---|
| `main` | 稳定演示版本 | 只接收 `develop` 的稳定合并 |
| `develop` | 72 小时集成版本 | 接收各 feature 分支 |
| `docs/wbs-plan` | WBS 与验收文档 | 合并到 `develop` 或 `main` |
| `feat/backend-mvp` | 后端 API、数据库、部署 | 合并到 `develop` |
| `feat/student-h5` | 学生端 H5 | 合并到 `develop` |
| `feat/admin-review` | 教师/管理端 Web | 合并到 `develop` |

### 7.2 提交规范

```text
feat(auth): implement login api
feat(checkin): add submit checkin service
feat(student): build today status view
feat(admin): build teacher review list
docs(wbs): update 72h task plan
fix(review): require reject comment
chore(deploy): add env example
```

### 7.3 PR 合并规则

- 每个 PR 必须说明影响范围、测试结果和关联 WBS 编号。
- 跨模块 PR 必须 @ 对应 Owner。
- `develop` 每 12 小时集成一次。
- `main` 只在演示前合并稳定版本。
- 禁止 force push 到 `main`。
- 禁止把本地 `.env`、日志、数据库 dump 提交到仓库。

## 8. 72 小时里程碑

| 时间点 | 里程碑 | 负责人 | 判断标准 |
|---|---|---|---|
| H6 | 需求和接口冻结 | 王韩韵 | 所有人确认 Must 范围 |
| H12 | 项目骨架可启动 | 赵耀、胡钊炫、华心仪 | 后端和两个前端均可启动 |
| H24 | 学生打卡最小闭环 | 赵耀、华心仪 | 学生可登录并提交打卡 |
| H36 | 教师审核最小闭环 | 赵耀、胡钊炫 | 教师可审核一条记录 |
| H48 | 统计概览可用 | 赵耀、胡钊炫 | 指标卡片返回真实数据 |
| H60 | 全流程联调完成 | 全员 | 验收脚本主路径通过 |
| H72 | 四环境验收 | 王韩韵主导 | 本地、服务器、UAT、生产测试完成记录 |

## 9. 验收脚本

最终演示按以下顺序执行：

1. 学生账号登录。
2. 学生查看今日三类打卡状态。
3. 学生提交查寝打卡。
4. 学生重复提交查寝打卡，系统提示不可重复。
5. 教师账号登录。
6. 教师筛选今日查寝待审核记录。
7. 教师打开学生打卡详情。
8. 教师审核通过。
9. 学生刷新历史记录，看到审核通过。
10. 管理员或教师进入统计页，看到打卡率、待审核数、异常数。

通过标准：

- 10 步主流程全部可执行。
- P0 缺陷为 0。
- P1 缺陷不影响主流程演示。
- 所有演示账号和演示数据可复现。

## 10. 风险与降级策略

| 风险 | 影响 | 降级策略 | 决策人 |
|---|---|---|---|
| 登录鉴权耗时过长 | 阻塞前后端联调 | 使用简单 Token 或固定演示账号 | 赵耀 |
| 定位 API 浏览器权限失败 | 学生端打卡受阻 | 允许手动 mock 经纬度并标记 `unknown` | 华心仪 |
| 教师审核页面联调延迟 | 管理闭环受阻 | 使用 mock 列表先完成页面，后切真实接口 | 胡钊炫 |
| 统计接口复杂 | 演示受阻 | 只返回今日核心指标，不做趋势计算 | 赵耀 |
| 服务器部署失败 | 环境验收受阻 | 先用本地局域网演示，同时记录部署缺陷 | 王韩韵、赵耀 |

## 11. Definition of Done

单个任务完成必须满足：

- 代码或文档已提交到对应分支。
- 任务关联 WBS 编号。
- 不修改非 Owner 目录，或跨模块修改已获得 Owner 确认。
- 可在本地启动或可被文档验证。
- 涉及接口的任务已同步接口契约。
- 涉及页面的任务已通过基本交互检查。
- 涉及数据库的任务已提供迁移或建表脚本。

MVP 完成必须满足：

- 学生打卡闭环通过。
- 教师审核闭环通过。
- 统计概览可见。
- 四环境验收记录完成。
- GitHub `main` 分支保存最终可演示版本。

## 12. 参考资料

- FastAPI 官方文档：Bigger Applications - Multiple Files，https://fastapi.tiangolo.com/tutorial/bigger-applications/
- FastAPI 官方文档：Dependencies，https://fastapi.tiangolo.com/tutorial/dependencies/
- Vue 官方文档：Components Basics，https://vuejs.org/guide/essentials/component-basics
- Vue 官方文档：Quick Start，https://vuejs.org/guide/quick-start
- MySQL 官方文档：Foreign Key Constraints，https://dev.mysql.com/doc/refman/8.4/en/create-table-foreign-keys.html
- MySQL 官方文档：Transaction Isolation Levels，https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html
- GitHub Docs：About protected branches，https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub Docs：About pull request reviews，https://docs.github.com/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews
