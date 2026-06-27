# Bruno API 自动化测试

使用 [Bruno CLI](https://docs.usebruno.com/bru-cli/overview) 一键跑通 ZeKin 全链路 API 测试。

## 前置条件

1. 后端已启动（默认 `http://127.0.0.1:8000`）：

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. 数据库已种子化（首次启动会自动执行，账号见下）。

## 测试账号

| 角色 | 账号 | 密码 |
|------|------|------|
| 管理员 | admin | 123456 |
| 教师 | 20261001 | 123456 |
| 学生 | 20260001 | 123456 |

## 一键运行（推荐）

```bash
cd bruno
npm install
npm test
```

等价命令：

```bash
cd bruno
npx bru run --cwd zeKin-e2e --env local
```

## 测试集合说明

### `zeKin-e2e/` — 全链路 E2E（推荐）

按顺序覆盖：

| 目录 | 内容 |
|------|------|
| `00-health` | 健康检查 |
| `01-auth` | 管理员 / 教师 / 学生登录 + `/me` |
| `02-admin` | 看板、学生、班级、任务监管、统计 |
| `03-teacher` | 看板、建任务、发布、手动考勤、二维码 |
| `04-student` | 看板、任务、位置签到、二维码签到、记录、消息 |
| `05-daily-report` | 实习日报提交 / 列表 / 教师点评 |

- 每个请求均含 `tests {}` 断言
- `collection.bru` 自动注入 `today` / `starts_at` / `ends_at`，无需手改日期
- 变量在请求间链式传递（token → task_id → record_id 等）

### `checkin-flow/` — 打卡专项流程

查寝 / 课程 / 实习三类任务创建 + 学生打卡 + 日报，已同步修复学号与动态日期。

```bash
npm run test:checkin-flow
```

## 修改环境

编辑 `zeKin-e2e/environments/local.bru`：

```
vars {
  base_url: http://192.168.x.x:8000   # 真机联调时改局域网 IP
}
```

## AI / CI 自动化示例

```bash
# 确保后端健康
curl -sf http://127.0.0.1:8000/health

# 跑全量 Bruno 测试（非零退出码表示失败）
cd bruno/zeKin-e2e && npx bru run --env local
```

PowerShell：

```powershell
cd bruno
npm install
npm test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```
