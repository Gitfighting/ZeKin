# 知勤打卡系统技术栈与日志规范

版本：V1.0  
日期：2026-06-23  
适用范围：72 小时 MVP 与后续 V1.1 开发  
参考文件：`23-logging.md`、`23-logging-format.md`

## 1. 最新技术栈确认

项目采用以下技术栈：

| 层级 | 技术 | 说明 |
|---|---|---|
| 学生端 | 微信小程序 | 学生提交查寝、上课、实习打卡，查看历史和审核结果 |
| 教师端 | 微信小程序 | 教师查看班级打卡列表，完成通过/拒绝审核 |
| 管理端 | Vue 3 + Vite + Element Plus | 管理员在 Web 端查看统计、系统状态和基础配置 |
| 后端 API | Python 3.11 + FastAPI | 提供认证、打卡、审核、统计接口 |
| 主数据库 | MySQL 8.0 | 持久化保存用户、打卡记录、审核记录 |
| 缓存/会话 | Redis | 保存登录态、验证码、限流计数、热点统计缓存 |
| 部署 | Docker Compose | 本地、服务器、UAT、生产测试环境统一启动 |
| 协作 | Git + GitHub Pull Request | 分支开发、评审合并、版本追踪 |

## 2. 端侧架构调整

原方案中学生端和教师端均可能使用 Vue H5。现在调整为：

- 学生端：微信小程序。
- 教师端：微信小程序。
- 管理端：Web 管理后台。

调整原因：

- 学生和教师日常使用手机频率高，微信小程序入口更轻，不需要安装 App。
- 管理员更适合在电脑端查看统计和配置，因此管理端保留 Web。
- 后端 API 统一，三个端只负责展示和交互，不直接操作数据库。

## 3. Redis 在 MVP 中的用途

Redis 不替代 MySQL。MySQL 负责“长期保存”，Redis 负责“临时高速存取”。

MVP 阶段 Redis 用途：

| 用途 | Key 示例 | 过期时间 | 说明 |
|---|---|---|---|
| 登录 Token 黑名单 | `auth:blacklist:<token_id>` | Token 剩余时间 | 用户退出或封禁后使 Token 失效 |
| 手机验证码 | `sms:code:<phone>` | 5 分钟 | 注册/登录验证码，MVP 可 mock |
| 接口限流 | `rate:<user_id>:<api>` | 60 秒 | 防止短时间重复提交 |
| 今日统计缓存 | `stats:overview:<date>:<class>` | 1-5 分钟 | 减少频繁聚合查询 |
| 重复打卡锁 | `lock:checkin:<user_id>:<type>:<date>` | 10 秒 | 防止重复点击导致并发提交 |

72 小时内如果 Redis 集成风险较高，可以先保留配置和封装，核心流程仍以 MySQL 为准；但工程结构必须预留 Redis 客户端。

## 4. FastAPI 日志规范

参考文件是 Rust/Axum/tracing 写法，本项目需要改造成 Python/FastAPI 版本。核心思想保留：

- 结构化日志。
- 控制台 + 文件双输出。
- 日志包含时间、级别、模块、文件名、行号、请求方法、路径、状态码、耗时。
- 不记录密码、Token、验证码等敏感信息。
- 开发环境 DEBUG，生产环境 INFO。

### 4.1 标准日志格式

```text
[时间戳] [Emoji级别] [级别] [模块名] [文件名:行号] 日志内容
```

示例：

```text
2026-06-23 09:30:12.188 🟢 INFO  app.middleware.request_logger (request_logger.py:42) POST /api/checkins 200 37ms
2026-06-23 09:30:12.221 🔴 ERROR app.services.checkin_service (checkin_service.py:88) 创建打卡失败 user_id=12 error=DuplicateCheckin
```

### 4.2 日志级别

| 级别 | Emoji | 使用场景 |
|---|---|---|
| ERROR | 🔴 | 功能失败，例如数据库连接失败、写入失败 |
| WARN | 🟠 | 有风险但系统还能继续运行，例如 Redis 不可用降级 |
| INFO | 🟢 | 关键业务事件，例如服务启动、用户登录、打卡提交、审核完成 |
| DEBUG | 🟡 | 开发调试信息，例如请求参数摘要、SQL 耗时 |
| TRACE | ⚫ | 极细调用链，MVP 不建议默认开启 |

### 4.3 请求日志字段

每个 HTTP 请求必须记录：

| 字段 | 示例 | 说明 |
|---|---|---|
| request_id | `req_abc123` | 每个请求唯一 ID，方便追踪 |
| method | `POST` | HTTP 方法 |
| path | `/api/checkins` | 请求路径 |
| query | `page=1` | 查询参数，敏感字段脱敏 |
| status | `200` | 响应状态码 |
| latency_ms | `37` | 请求耗时 |
| user_id | `12` | 已登录用户 ID，没有则为空 |
| client | `student-miniapp` | student-miniapp / teacher-miniapp / admin-web |

### 4.4 Python 实现建议

建议使用：

- 标准库 `logging`
- `logging.handlers.TimedRotatingFileHandler`
- FastAPI middleware
- `contextvars` 保存 request_id

推荐目录：

```text
backend/app/core/logging.py
backend/app/middleware/request_logger.py
backend/logs/
```

### 4.5 日志轮转

日志文件：

```text
logs/zekin.log
logs/zekin.log.2026-06-23
logs/zekin.log.2026-06-24
```

规则：

- 按天轮转。
- 本地和服务器默认保留 30 天。
- 生产测试环境禁止输出明文密码、Token、验证码、身份证号。

## 5. 72 小时 MVP 影响

技术栈变更后，72 小时任务需要调整：

| 原任务 | 新任务 |
|---|---|
| Vue 学生端 | 微信小程序学生端 |
| Vue 教师端 | 微信小程序教师端 |
| Vue 管理端 | Vue 管理端保留 |
| MySQL | MySQL + Redis |
| 普通日志 | 结构化日志 + 请求日志 + 文件轮转 |

仍然不变：

- 只做 5 个 MVP 功能。
- 只保留 3 张 MySQL 核心表。
- AI 审核、人脸识别、补签、提醒进入 V1.1。
- 72 小时主流程仍是：学生打卡 → 教师审核 → 学生看结果 → 管理端看统计。

## 6. 参考资料

- FastAPI Bigger Applications：https://fastapi.tiangolo.com/tutorial/bigger-applications/
- FastAPI APIRouter：https://fastapi.tiangolo.com/reference/apirouter/
- Redis Python Client：https://redis.io/docs/latest/integrate/redis-py/
- redis-py asyncio examples：https://redis.readthedocs.io/en/stable/examples/asyncio_examples.html
- Vue Quick Start：https://vuejs.org/guide/quick-start
- WeChat Mini Program Introduction：https://www.tencentcloud.com/document/product/1219/60341
