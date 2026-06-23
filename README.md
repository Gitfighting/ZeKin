# ZeKin · 知勤打卡系统 72 小时 MVP

ZeKin 是面向高校学生日常管理的知勤打卡 MVP。项目采用 Python + FastAPI + MySQL + Redis + Vue 管理端 + 微信小程序技术栈，目标是在 72 小时内打通：

```text
学生打卡 -> 教师审核 -> 学生查看结果 -> 管理端查看统计
```

## 当前交付

- [72 小时 MVP 需求精简与里程碑](docs/72h-mvp-ice-miniapp-plan.md)
- [技术栈与日志规范](docs/tech-stack-and-logging-spec.md)
- [UI 页面设计规范](docs/ui-page-design-spec.md)
- [需求分析报告](docs/requirements-analysis-report.md)
- [用例规约文档](docs/use-case-specifications.md)
- [72 小时极限开发计划](docs/72h-extreme-programming-plan.md)
- [原型设计说明](docs/prototype-design.md)
- [UML/PlantUML 图源文件](diagrams/)
- [原型样图 SVG](prototypes/)

## 工程目录

```text
backend/              FastAPI 后端，包含 8 个 MVP API 和 pytest 测试
admin-web/            Vue 3 管理端 Web 骨架
student-miniprogram/  学生端微信小程序骨架
teacher-miniprogram/  教师端微信小程序骨架
bruno/ZeKin-MVP/      Bruno API 测试集合
docs/                 产品、需求、UI、WBS、实施计划文档
```

## 72 小时 MVP 范围

本版以“能完成业务闭环”为唯一目标：

1. 学生完成三类打卡：查寝、上课、实习。
2. 辅导员/教师查看班级打卡并完成审核。
3. 管理员/教师查看统计概览。
4. 系统保存可追溯记录，支撑后续扩展 AI 审核、人脸识别、补签和通知。

AI 审核、人脸识别、复杂推送、积分体系不进入 72 小时核心实现，作为扩展点预留。

## 本地运行

### 后端 API

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

默认不配置环境变量时，后端会使用内存 SQLite，方便本地快速启动。连接 MySQL/Redis 时复制 `.env.example` 为 `.env` 并修改：

```text
DATABASE_URL=mysql+pymysql://zekin:zekin@127.0.0.1:3306/zekin
REDIS_URL=redis://127.0.0.1:6379/0
JWT_SECRET=please-change-this-secret
```

### 后端测试

```powershell
cd backend
python -m pytest tests/test_mvp_api.py -q
```

### Bruno 接口测试

Bruno 官方 CLI 支持在集合目录执行 `bru run`，也支持通过 `--env` 或 `--env-file` 选择环境变量。

```powershell
cd bruno\ZeKin-MVP
bru run --env Local
```

如果没有安装 Bruno CLI：

```powershell
npm install -g @usebruno/cli
```

### 管理端 Web

```powershell
cd admin-web
npm install
npm run dev
```

打开 `http://localhost:5173` 查看管理端骨架页面。

### Docker Compose

```powershell
docker compose up --build
```

服务端口：

- 后端 API：`http://localhost:8000`
- 管理端 Web：`http://localhost:5173`
- MySQL：`localhost:3306`
- Redis：`localhost:6379`

## 建模资产

- 用例图：`diagrams/00_system_usecase.puml`
- 活动图：`diagrams/01_submit_checkin_activity.puml`、`diagrams/02_teacher_review_activity.puml`、`diagrams/03_statistics_activity.puml`
- 顺序图：`diagrams/04_submit_checkin_sequence.puml`、`diagrams/05_teacher_review_sequence.puml`
- 时序图：`diagrams/06_checkin_timing.puml`
- 分析类图：`diagrams/07_analysis_class_diagram.puml`

PlantUML 文件可在 VS Code PlantUML 插件、IntelliJ PlantUML 插件或 PlantUML Server 中渲染。
