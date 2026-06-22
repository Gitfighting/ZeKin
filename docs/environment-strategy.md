# ZeKin 四环境部署与验收策略

| 版本 | V1.0 · 2026-06-22 |
|------|-------------------|

---

## 1. 环境总览

```
Developer Laptop          Dev Server              UAT Server           Prod Server
     (Local)                 (集成)                  (验收)               (生产)
        │                      │                      │                    │
        ▼                      ▼                      ▼                    ▼
 docker-compose.local    docker-compose.dev    docker-compose.uat   docker-compose.prod
 branch: feat/*          branch: develop       tag: v1.0.0-rc1      tag: v1.0.0
 auto on save            push develop          manual promote       manual + approval
```

| # | 环境 | 代号 | 用途 | 数据 | 访问者 |
|---|------|------|------|------|--------|
| 1 | **本地开发** | `local` | 个人编码、单元测试、Mock 联调 | 本地 MySQL 种子数据 | 开发四人 |
| 2 | **开发服务器** | `dev` | 持续集成、模块联调、内部演示 | 可重置的测试数据 | 开发 + 导师 |
| 3 | **用户验收** | `uat` | 甲方试用、培训、验收测试 | 脱敏真实结构数据 | 甲方 + 王韩韵 |
| 4 | **生产** | `prod` | 正式上线服务 | 真实生产数据 | 全校师生 |

---

## 2. 环境配置矩阵

| 配置项 | Local | Dev | UAT | Prod |
|--------|-------|-----|-----|------|
| `APP_ENV` | local | dev | uat | prod |
| `DEBUG` | true | true | false | false |
| `DATABASE_URL` | localhost:3306 | dev-db内网 | uat-db内网 | prod-db主从 |
| `JWT_SECRET` | dev-secret | dev-secret | uat-secret | **强随机 KMS** |
| `AI_API_KEY` | mock / sandbox | sandbox | sandbox | production |
| `CORS_ORIGINS` | localhost:* | dev.domain | uat.domain | prod.domain |
| `HTTPS` | 否 | 建议 | **必须** | **必须** |
| `LOG_LEVEL` | DEBUG | INFO | INFO | WARNING |

配置文件：

- `backend/.env.example` — 模板
- `backend/.env.local` — 本地（gitignore）
- 服务器 `/etc/zekin/.env.{dev,uat,prod}` — 运维托管

---

## 3. Local 环境（环境 1）

### 3.1 前置条件

- Docker Desktop
- Python 3.11+
- Node.js 20+
- Git

### 3.2 启动

```bash
# 根目录
docker compose -f deploy/docker-compose.local.yml up -d

# 后端
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 管理端
cd frontend/admin && npm install && npm run dev

# 学生端
cd frontend/student && npm install && npm run dev
```

### 3.3 验收标准

- [ ] `GET http://localhost:8000/health` → 200
- [ ] `GET http://localhost:8000/docs` Swagger 可访问
- [ ] MySQL 3306 可连接，表结构已迁移
- [ ] admin `:5173`、student `:5174` 可打开登录页

---

## 4. Dev 环境（环境 2 · 部署到服务器）

### 4.1 触发

- Push / Merge 到 `develop` → GitHub Actions 自动构建部署

### 4.2 架构

```
Internet → Nginx (443) → frontend static
                      → /api → FastAPI (8000)
                      → MySQL 8.0 (Docker volume)
```

### 4.3 部署步骤（赵耀）

```bash
ssh dev-server
cd /opt/zekin && git pull origin develop
docker compose -f deploy/docker-compose.dev.yml pull
docker compose -f deploy/docker-compose.dev.yml up -d --build
docker compose exec backend alembic upgrade head
curl -f https://dev.zekin.example.com/health
```

### 4.4 验收标准（S1 末）

- [ ] Must 功能 E2E 可在 Dev 演示
- [ ] CI pipeline 绿
- [ ] 部署文档可由另一成员独立复现

---

## 5. UAT 环境（环境 3 · 用户验收）

### 5.1 晋升流程

```
develop (测试通过) → 打 tag v1.0.0-rc1 → 部署 UAT → 王韩韵组织验收
```

### 5.2 与 Dev 差异

- 关闭 DEBUG，启用 HTTPS
- 使用脱敏数据集（`deploy/seed/uat_seed.sql`）
- 甲方账号预置
- 变更需 Change Request，不直接 hotfix

### 5.3 UAT 验收清单（王韩韵）

| 类别 | 检查项 |
|------|--------|
| 功能 | RTM 全部 Must + 90% Should |
| 性能 | 50 并发打卡无错误 |
| 安全 | 越权测试（学生访问 teacher API → 403） |
| 兼容 | Chrome + 手机浏览器 |
| 文档 | 用户手册可操作 |

### 5.4 签字

验收通过后，甲方签署 `docs/uat-signoff.md`，方可晋升 Prod。

---

## 6. Prod 环境（环境 4 · 生产）

### 6.1 发布流程

1. UAT 签字完成
2. 从 `main` 打 tag `v1.0.0`
3. 赵耀执行 `deploy/scripts/release-prod.sh`
4. 王韩韵 Prod 冒烟（15min）
5. 监控 24h

### 6.2 生产加固

| 项 | 措施 |
|----|------|
| 数据库 | 每日全量备份，保留 30 天 |
| 密钥 | 环境变量 / Vault，禁止入库 |
| 回滚 | 保留上一版 Docker image，`release-prod.sh rollback` |
| 监控 | `/health` + 磁盘 + MySQL 连接数 |

### 6.3 Prod 验收标准

- [ ] 全量 Must/Should 功能正常
- [ ] HTTPS 证书有效
- [ ] 备份任务 cron 已启用
- [ ] 培训完成，运维手册交付

---

## 7. Git 与环境映射

| Git 操作 | 目标环境 |
|----------|----------|
| `feat/*` 本地开发 | Local |
| merge → `develop` | Dev（自动） |
| tag `v*-rc*` | UAT（手动 promote） |
| tag `v*` on `main` | Prod（审批后） |

**禁止**：直接向 `main` push；Prod 禁止 `DEBUG=true`。

---

## 8. 规格驱动与环境一致性

- OpenAPI `servers` 段声明四套 base URL
- 契约测试在 CI 中对 Local/Dev 跑；UAT 做冒烟
- 数据库 migration 版本四环境一致（Alembic revision）

---

## 9. 故障分级与响应

| 级别 | 定义 | 响应 | 环境 |
|------|------|------|------|
| P0 | 服务不可用 / 数据丢失 | 15min | Prod |
| P1 | 核心功能不可用 | 2h | Prod/UAT |
| P2 | 非核心缺陷 | 下一 Sprint | 全部 |
| P3 | 优化建议 | Backlog | 全部 |

Prod P0/P1：赵耀 on-call + 王韩韵通知甲方。
