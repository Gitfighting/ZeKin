# ZeKin · 知勤打卡系统 72 小时 MVP

ZeKin 是一个面向高校学生日常管理的知勤打卡 MVP。系统围绕一个最小业务闭环展开：

```text
学生提交打卡 -> 教师审核打卡 -> 学生查看结果 -> 管理端查看用户、记录和统计
```

本仓库已经包含 FastAPI 后端、Vue 管理端、学生微信小程序、教师微信小程序、MySQL 初始化脚本、Docker Compose 配置，以及 Bruno API 测试集合。

## 项目内容

### 后端 API

`backend/` 使用 FastAPI + SQLAlchemy 实现核心接口，默认不配置环境变量时会使用内存 SQLite，便于本地快速启动和测试。连接 MySQL/Redis 时可使用 `.env.example` 或 Docker Compose 中的配置。

当前接口覆盖：

- 账号注册、登录、获取当前用户
- 学生提交打卡、查看个人打卡历史
- 教师查看班级打卡、通过/驳回审核
- 管理员查看用户列表、打卡记录
- 教师/管理员查看统计概览

### 管理端 Web

`admin-web/` 是 Vue 3 + Vite 管理端，用于登录管理员账号、查看统计卡片、打卡记录和用户列表。

### 微信小程序

`student-miniprogram/` 是学生端小程序骨架，包含登录、首页、提交打卡、历史记录和个人页。

`teacher-miniprogram/` 是教师端小程序骨架，包含登录、审核列表、审核详情、班级概览和个人页。

### 数据库脚本

`db/init.sql` 是 MySQL 初始化文件，包含 `users`、`checkins`、`reviews` 三张表，以及演示账号和演示打卡数据。

演示账号密码均为：

```text
Passw0rd!
```

账号：

```text
admin_demo
student_demo
teacher_demo
```

### 测试资产

`backend/tests/` 是 pytest 后端自动化测试。

`test/bruno/ZeKin-MVP/` 是 Bruno API 测试集合，用于从接口层跑通注册、登录、学生打卡、教师审核、统计和管理员查询。

## 目录结构

```text
backend/                 FastAPI 后端和 pytest 测试
admin-web/               Vue 3 管理端
student-miniprogram/     学生端微信小程序
teacher-miniprogram/     教师端微信小程序
test/bruno/ZeKin-MVP/    Bruno API 测试集合
db/init.sql              MySQL 初始化脚本
docs/                    需求、UI、WBS、实施计划文档
diagrams/                PlantUML 图源文件
prototypes/              原型 SVG
docker-compose.yml       MySQL、Redis、后端、管理端编排
```

## 本地运行

### 1. 启动后端 API

在 Windows 上建议使用 `py`，因为部分机器的 `python` 会指向 Microsoft Store 占位符。

```powershell
cd C:\Users\Orion\Desktop\ZeKin\backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload --port 8000
```

健康检查：

```text
http://127.0.0.1:8000/health
```

返回 `{"status":"ok"}` 表示后端已启动。

### 2. 启动管理端 Web

另开一个 PowerShell：

```powershell
cd C:\Users\Orion\Desktop\ZeKin\admin-web
npm install
npm run dev
```

浏览器打开：

```text
http://localhost:5173
```

### 3. 运行后端 pytest

```powershell
cd C:\Users\Orion\Desktop\ZeKin\backend
py -m pytest tests/test_mvp_api.py -q
```

## 使用 Bruno 跑通接口测试

Bruno 测试集合位于：

```text
C:\Users\Orion\Desktop\ZeKin\test\bruno\ZeKin-MVP
```

集合的 `Local` 环境默认使用：

```text
baseUrl = http://127.0.0.1:8000
```

因此运行 Bruno 前必须先启动后端 API。

### 1. 安装 Bruno CLI

如果本机还没有 `bru` 命令：

```powershell
npm install -g @usebruno/cli
```

检查是否安装成功：

```powershell
bru --version
```

### 2. 启动后端

```powershell
cd C:\Users\Orion\Desktop\ZeKin\backend
py -m uvicorn app.main:app --reload --port 8000
```

### 3. 执行 Bruno 集合

另开一个 PowerShell：

```powershell
cd C:\Users\Orion\Desktop\ZeKin\test\bruno\ZeKin-MVP
bru run --env Local
```

Bruno 会按请求编号依次执行：

```text
00 注册管理员
01 注册学生
02 注册教师
03 学生登录，保存 student_token
04 教师登录，保存 teacher_token
05 管理员登录，保存 admin_token
06 学生提交打卡，保存 checkin_id
07 学生查看自己的打卡记录
08 教师查看打卡列表
09 教师审核打卡
10 查看统计概览
11 管理员查看用户列表
12 管理员查看打卡列表
```

测试通过时，每个请求会返回 2xx 状态码，并且集合中的断言会通过。登录请求会把 token 写入 Bruno 环境变量，提交打卡请求会把 `checkin_id` 写入环境变量，后续教师审核会复用它。

### 4. 常见问题

如果出现连接失败，先确认后端是否正在运行：

```text
http://127.0.0.1:8000/health
```

如果出现用户已存在，说明之前已经跑过注册接口。可以继续跑后续接口，或者重启后端内存 SQLite 数据库后重新执行集合。

如果你改成 MySQL 运行，想重置数据，可以导入初始化脚本：

```powershell
mysql -uroot -p < C:\Users\Orion\Desktop\ZeKin\db\init.sql
```

## Docker Compose

也可以用 Docker 同时启动 MySQL、Redis、后端和管理端：

```powershell
cd C:\Users\Orion\Desktop\ZeKin
docker compose up --build
```

服务端口：

- 后端 API：`http://localhost:8000`
- 管理端 Web：`http://localhost:5173`
- MySQL：`localhost:3306`
- Redis：`localhost:6379`

## MVP 范围

本版只追求能完成核心业务闭环：

1. 学生完成查寝、上课、实习三类打卡。
2. 教师查看班级打卡并完成审核。
3. 学生查看审核结果。
4. 管理端查看用户、打卡记录和统计概览。
5. 系统保存可追溯记录，方便后续扩展。

AI 审核、人脸识别、复杂推送、补签、积分体系和日志查询接口不进入 72 小时 MVP 核心范围，作为后续 V1.1 或更高版本扩展。

## 文档和建模资产

- [72 小时 MVP 需求精简与里程碑](docs/72h-mvp-ice-miniapp-plan.md)
- [技术栈与日志规范](docs/tech-stack-and-logging-spec.md)
- [UI 页面设计规范](docs/ui-page-design-spec.md)
- [需求分析报告](docs/requirements-analysis-report.md)
- [用例规约文档](docs/use-case-specifications.md)
- [72 小时极限开发计划](docs/72h-extreme-programming-plan.md)
- [原型设计说明](docs/prototype-design.md)
- `diagrams/`：PlantUML 用例图、活动图、顺序图、时序图、分析类图
- `prototypes/`：学生端、教师端、管理端原型 SVG
