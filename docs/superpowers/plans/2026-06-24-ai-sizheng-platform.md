# AI Sizheng Platform Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first-phase AI 思政辅助三端平台: 管理员配置治理、教师发布任务与处理异常、学生激活登录与定位打卡、后端规则校验与基础监管统计。

**Architecture:** Use a modular monolith FastAPI backend with PostgreSQL persistence, Vue3 + Element Plus for the admin web app, and one uni-app project for student and teacher mini-program flows. The first milestone creates a stable scaffold and shared API contract, then five agents work in bounded lanes: scaffold, backend, admin web, student mini-app, and teacher mini-app.

**Tech Stack:** FastAPI, uv, SQLAlchemy, Alembic, PostgreSQL, pytest, Bruno, Vue3, Vite, TypeScript, Element Plus, Pinia, uni-app Vue3/Vite, SCSS tokens.

---

## Source Specs

- `docs/superpowers/specs/2026-06-24-ai-sizheng-platform/01-architecture.md`
- `docs/superpowers/specs/2026-06-24-ai-sizheng-platform/02-data-model.md`
- `docs/superpowers/specs/2026-06-24-ai-sizheng-platform/03-rule-engine-integrations.md`
- `docs/superpowers/specs/2026-06-24-ai-sizheng-platform/04-client-scope.md`
- `docs/superpowers/specs/2026-06-24-ai-sizheng-platform/05-api-and-structure.md`
- `docs/superpowers/specs/2026-06-24-ai-sizheng-platform/06-testing-and-milestones.md`
- `docs/superpowers/specs/2026-06-24-ai-sizheng-platform/07-frontend-style-guide.md`

## Agent Ownership

| Agent | Lane | Owns | Must Not Edit |
| --- | --- | --- | --- |
| Agent 1 | Scaffold and integration contract | root config, Docker, repo scripts, backend/admin/mini initial skeletons, shared docs contracts | business module internals after scaffold handoff |
| Agent 2 | Backend | `backend/`, `test/bruno/`, API contract updates after implementation | `admin-web/src/views`, `mini-app/src/pages` |
| Agent 3 | Admin frontend | `admin-web/` except generated API contract notes | backend business logic, mini-app pages |
| Agent 4 | Student mini-app | `mini-app/src/pages/student`, student services, shared mobile components by additive props only | teacher pages, backend |
| Agent 5 | Teacher mini-app | `mini-app/src/pages/teacher`, teacher services, shared mobile components by additive props only | student pages, backend |

Parallelization rule: Agent 1 finishes Task 1 and Task 2 first. After that, Agents 2-5 can run in parallel. Agent 2 owns the final API truth; Agents 3-5 use mock adapters until `/api/auth/me`, dashboard, task, record, exception, and message endpoints are available.

## Shared Contract

All agents use these enums and payload fields unless a spec update changes them.

```ts
export type UserType = 'admin' | 'teacher' | 'student'
export type TaskStatus = 'draft' | 'not_started' | 'in_progress' | 'ended'
export type RecordStatus = 'normal' | 'late' | 'exception' | 'pending_review' | 'rejected'
export type ExceptionType =
  | 'missing'
  | 'late'
  | 'location_error'
  | 'dynamic_code_error'
  | 'face_failed'
  | 'safety_risk'
  | 'log_missing'
  | 'appeal_pending'

export interface RuleSnapshot {
  timeRule: {
    mode: 'single' | 'range'
    startTime: string
    endTime: string
    allowLate: boolean
    allowMakeup: boolean
    makeupNeedReview: boolean
  }
  locationRule: {
    mode: 'fixed_area' | 'none'
    placeName: string
    longitude: number
    latitude: number
    radius: number
    allowExceptionSubmit: boolean
  }
  verificationRule: {
    methods: Array<'location' | 'dynamic_code' | 'face'>
  }
  submitRule: {
    fields: Array<{
      key: string
      label: string
      type: 'text' | 'textarea' | 'image' | 'log' | 'safety_status'
      required: boolean
    }>
  }
  reviewRule: {
    mode: 'auto' | 'exception_only' | 'manual_all'
  }
  reminderRule: {
    beforeStartMinutes: number
    beforeEndMinutes: number
    notifyTeacherAfterEnd: boolean
  }
  faceRule: {
    enabled: boolean
    provider: 'placeholder'
  }
}
```

Core endpoint payloads:

```json
{
  "POST /api/auth/login": {
    "request": { "account": "string", "password": "string", "user_type": "admin|teacher|student" },
    "response": { "access_token": "string", "token_type": "bearer", "user": { "id": 1, "user_type": "student", "display_name": "张三" } }
  },
  "POST /api/auth/student/activate": {
    "request": { "name": "string", "student_no": "string", "phone": "string", "code": "string", "password": "string" },
    "response": { "activated": true, "access_token": "string" }
  },
  "POST /api/teacher/tasks": {
    "request": { "title": "晚间查寝", "type_id": 1, "group_ids": [1], "starts_at": "2026-06-24T21:30:00+08:00", "ends_at": "2026-06-24T22:30:00+08:00", "rules_snapshot": "RuleSnapshot" },
    "response": { "id": 1, "status": "draft", "rules_snapshot": "RuleSnapshot" }
  },
  "POST /api/student/tasks/{id}/checkin": {
    "request": { "longitude": 120.000001, "latitude": 30.000001, "dynamic_code": "123456", "submit_payload": { "remark": "已在宿舍" } },
    "response": { "record_id": 1, "status": "normal", "exception_types": [], "need_review": false }
  },
  "POST /api/student/records/{id}/appeal": {
    "request": { "reason": "定位偏移，实际在宿舍楼内", "attachment_ids": [1] },
    "response": { "appeal_id": 1, "status": "appeal_pending" }
  },
  "POST /api/teacher/exceptions/{id}/review": {
    "request": { "decision": "approve|reject|need_more", "comment": "说明文字" },
    "response": { "reviewed": true, "record_status": "normal|rejected|pending_review" }
  }
}
```

## File Structure

```text
backend/
  pyproject.toml
  alembic.ini
  alembic/
  app/
    main.py
    core/
      config.py
      database.py
      security.py
      errors.py
      logging.py
    modules/
      auth/
      identity/
      groups/
      checkin_types/
      rule_templates/
      tasks/
      records/
      exceptions/
      messages/
      statistics/
      integrations/
    shared/
      enums.py
      pagination.py
      response.py
      validators.py
  tests/
    unit/
    integration/
admin-web/
  src/
    api/
    components/
    layouts/
    router/
    stores/
    styles/
    views/
mini-app/
  src/
    components/
    pages/
      auth/
      student/
      teacher/
    services/
    stores/
    styles/
test/
  bruno/
docs/
  contracts/
```

## Task 1: Agent 1 - Scaffold Workspace

**Files:**
- Create: `README.md`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `docker-compose.yml`
- Create: `justfile`
- Create: `docs/contracts/api-v1.md`
- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`
- Create: `backend/app/shared/response.py`
- Create: `admin-web/package.json`
- Create: `admin-web/src/main.ts`
- Create: `admin-web/src/styles/theme.scss`
- Create: `mini-app/package.json`
- Create: `mini-app/src/styles/tokens.scss`

- [ ] **Step 1: Record the current worktree state**

Run:

```powershell
git status --short
rg --files
```

Expected: write the dirty/untracked file summary into the agent handoff note before editing. If unrelated deleted files or untracked documents already exist, preserve them exactly as-is; do not restore, remove, stage, or overwrite them during scaffold work.

- [ ] **Step 2: Create the working branch**

Run:

```powershell
git switch -c codex/ai-sizheng-platform
```

Expected: branch switches to `codex/ai-sizheng-platform`.

- [ ] **Step 3: Create root runtime files**

Add `.env.example`:

```dotenv
APP_NAME=AI_SIZHENG_PLATFORM
APP_ENV=local
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ai_sizheng
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=change-me-in-local-env
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=720
BACKEND_CORS_ORIGINS=http://localhost:5173,http://localhost:5174
FILE_STORAGE_ROOT=./storage
WECHAT_PROVIDER_MODE=log
FACE_PROVIDER_MODE=disabled
```

Add `docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:16
    container_name: ai-sizheng-postgres
    environment:
      POSTGRES_DB: ai_sizheng
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - ai_sizheng_pg:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d ai_sizheng"]
      interval: 5s
      timeout: 5s
      retries: 10

  redis:
    image: redis:7
    container_name: ai-sizheng-redis
    ports:
      - "6379:6379"

volumes:
  ai_sizheng_pg:
```

Add `justfile`:

```makefile
backend-dev:
    cd backend && uv run fastapi dev app/main.py --host 0.0.0.0 --port 8000

backend-test:
    cd backend && uv run pytest -q

backend-migrate:
    cd backend && uv run alembic upgrade head

admin-dev:
    cd admin-web && npm run dev -- --host 0.0.0.0 --port 5173

admin-test:
    cd admin-web && npm run test:unit -- --run

mini-dev:
    cd mini-app && npm run dev:mp-weixin

mini-test:
    cd mini-app && npm run test:unit -- --run
```

- [ ] **Step 4: Scaffold backend project**

Run:

```powershell
New-Item -ItemType Directory -Force backend/app/core,backend/app/shared,backend/app/modules,backend/tests/unit,backend/tests/integration | Out-Null
cd backend
uv init --package
uv add "fastapi[standard]" sqlalchemy alembic psycopg[binary] pydantic-settings python-jose[cryptography] passlib[bcrypt] python-multipart redis
uv add --dev pytest pytest-asyncio httpx ruff
cd ..
```

Expected: `backend/pyproject.toml` exists and contains runtime plus test dependencies.

- [ ] **Step 5: Add backend health app**

Create `backend/app/main.py`:

```python
from fastapi import FastAPI

app = FastAPI(title="AI Sizheng Platform API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

Create `backend/tests/unit/test_health.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

Run:

```powershell
cd backend
uv run pytest tests/unit/test_health.py -q
cd ..
```

Expected: `1 passed`.

- [ ] **Step 6: Scaffold admin web**

Run:

```powershell
npm create vite@latest admin-web -- --template vue-ts
cd admin-web
npm install
npm install element-plus @element-plus/icons-vue pinia vue-router axios
npm install -D vitest @vue/test-utils jsdom sass
cd ..
```

Add `admin-web/src/styles/theme.scss`:

```scss
:root {
  --sz-primary: #1677ff;
  --sz-primary-light: #eaf4ff;
  --sz-primary-deep: #0066e6;
  --sz-success: #20c55a;
  --sz-warning: #ff9f1a;
  --sz-danger: #f04438;
  --sz-text: #101828;
  --sz-muted: #667085;
  --sz-border: #d8e8ff;
  --sz-page-bg: #f6faff;
  --sz-card: #ffffff;
}

body {
  margin: 0;
  color: var(--sz-text);
  background: var(--sz-page-bg);
  font-family: Inter, "Microsoft YaHei", system-ui, sans-serif;
}
```

- [ ] **Step 7: Scaffold mini-app**

Run:

```powershell
npx degit dcloudio/uni-preset-vue#vite-ts mini-app
cd mini-app
npm install
npm install pinia
npm install -D vitest @vue/test-utils jsdom sass
cd ..
```

Add `mini-app/src/styles/tokens.scss`:

```scss
$primary: #1677ff;
$primary-light: #eaf4ff;
$primary-deep: #0066e6;
$sky-blue: #2ea8ff;
$success: #20c55a;
$warning: #ff9f1a;
$danger: #f04438;
$text-primary: #101828;
$text-secondary: #667085;
$text-muted: #98a2b3;
$border-light: #d8e8ff;
$page-bg: #f3f8ff;
$card-bg: #ffffff;
$mobile-gradient: linear-gradient(180deg, #0f8bff 0%, #38b6ff 48%, #f3f8ff 100%);
```

- [ ] **Step 8: Commit scaffold**

Run:

```powershell
git add README.md .gitignore .env.example docker-compose.yml justfile docs/contracts backend admin-web mini-app
git commit -m "Enable parallel platform implementation lanes" -m "The project needs one stable scaffold before backend and three frontends can proceed independently, so this commit establishes runtime commands, local infrastructure, and initial app shells." -m "Constraint: Five-agent implementation needs clear file ownership before parallel execution`nConfidence: high`nScope-risk: moderate`nTested: backend health unit test`nNot-tested: admin and mini dev servers before feature pages exist"
```

Expected: one commit on `codex/ai-sizheng-platform`.

## Task 2: Agent 1 - Shared API Contract and Mock Boundary

**Files:**
- Create: `docs/contracts/api-v1.md`
- Create: `admin-web/src/api/types.ts`
- Create: `admin-web/src/api/http.ts`
- Create: `mini-app/src/services/types.ts`
- Create: `mini-app/src/services/request.ts`

- [ ] **Step 1: Write the contract document**

`docs/contracts/api-v1.md` must contain the endpoint payloads from the Shared Contract section, the enum values, and the rule snapshot structure. Add a note that backend OpenAPI becomes authoritative after Task 5.

- [ ] **Step 2: Add admin API types**

Create `admin-web/src/api/types.ts`:

```ts
export type UserType = 'admin' | 'teacher' | 'student'
export type TaskStatus = 'draft' | 'not_started' | 'in_progress' | 'ended'
export type RecordStatus = 'normal' | 'late' | 'exception' | 'pending_review' | 'rejected'

export interface ApiResponse<T> {
  data: T
  message: string
}

export interface LoginResponse {
  access_token: string
  token_type: 'bearer'
  user: {
    id: number
    user_type: UserType
    display_name: string
  }
}
```

- [ ] **Step 3: Add mini-app API types**

Create `mini-app/src/services/types.ts` with the same `UserType`, `TaskStatus`, `RecordStatus`, `ApiResponse<T>`, and `LoginResponse` declarations. Keep this file framework-neutral so both student and teacher pages can import it.

- [ ] **Step 4: Add request wrappers**

Admin `admin-web/src/api/http.ts`:

```ts
import axios from 'axios'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api',
  timeout: 10000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

Mini `mini-app/src/services/request.ts`:

```ts
const API_BASE_URL = 'http://localhost:8000/api'

export function request<T>(options: UniApp.RequestOptions): Promise<T> {
  const token = uni.getStorageSync('access_token')

  return new Promise((resolve, reject) => {
    uni.request({
      ...options,
      url: `${API_BASE_URL}${options.url}`,
      header: {
        ...(options.header ?? {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success: (response) => {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(response.data as T)
          return
        }
        reject(response)
      },
      fail: reject,
    })
  })
}
```

- [ ] **Step 5: Commit shared contract**

Run:

```powershell
git add docs/contracts/api-v1.md admin-web/src/api mini-app/src/services
git commit -m "Stabilize the cross-agent API contract" -m "Frontend lanes need a typed boundary before the backend is fully implemented, so this commit records the shared DTOs and request wrappers used by all clients." -m "Constraint: Backend OpenAPI replaces the markdown contract after endpoint implementation`nConfidence: high`nScope-risk: narrow`nTested: TypeScript files compile during later app test runs`nNot-tested: live API calls before backend routes exist"
```

## Task 3: Agent 2 - Backend Core, Database, and Evaluators

**Files:**
- Create: `backend/app/shared/enums.py`
- Create: `backend/app/shared/response.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`
- Create: `backend/app/modules/records/evaluators.py`
- Create: `backend/tests/unit/test_rule_evaluators.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write failing evaluator tests**

Create `backend/tests/unit/test_rule_evaluators.py`:

```python
from datetime import datetime
from zoneinfo import ZoneInfo

from app.modules.records.evaluators import LocationRuleEvaluator, TimeRuleEvaluator


def test_time_rule_passes_inside_window() -> None:
    evaluator = TimeRuleEvaluator()
    result = evaluator.evaluate(
        now=datetime(2026, 6, 24, 21, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
        rule={"startTime": "21:30", "endTime": "22:30", "allowLate": False},
    )

    assert result.passed is True
    assert result.exception_types == []


def test_time_rule_marks_late_outside_window() -> None:
    evaluator = TimeRuleEvaluator()
    result = evaluator.evaluate(
        now=datetime(2026, 6, 24, 22, 45, tzinfo=ZoneInfo("Asia/Shanghai")),
        rule={"startTime": "21:30", "endTime": "22:30", "allowLate": False},
    )

    assert result.passed is False
    assert result.status == "exception"
    assert result.exception_types == ["late"]


def test_location_rule_passes_within_radius() -> None:
    evaluator = LocationRuleEvaluator()
    result = evaluator.evaluate(
        submitted_longitude=120.000001,
        submitted_latitude=30.000001,
        rule={
            "mode": "fixed_area",
            "longitude": 120.000001,
            "latitude": 30.000001,
            "radius": 300,
        },
    )

    assert result.passed is True
    assert result.exception_types == []


def test_location_rule_fails_outside_radius() -> None:
    evaluator = LocationRuleEvaluator()
    result = evaluator.evaluate(
        submitted_longitude=120.01,
        submitted_latitude=30.01,
        rule={
            "mode": "fixed_area",
            "longitude": 120.000001,
            "latitude": 30.000001,
            "radius": 100,
        },
    )

    assert result.passed is False
    assert result.status == "exception"
    assert result.exception_types == ["location_error"]
```

Run:

```powershell
cd backend
uv run pytest tests/unit/test_rule_evaluators.py -q
cd ..
```

Expected: fail with `ModuleNotFoundError` or missing evaluator classes.

- [ ] **Step 2: Implement evaluator result and strategies**

Create `backend/app/modules/records/evaluators.py`:

```python
from dataclasses import dataclass
from datetime import datetime, time
from math import asin, cos, radians, sin, sqrt


@dataclass(frozen=True)
class EvaluationResult:
    passed: bool
    status: str
    exception_types: list[str]
    messages: list[str]
    need_review: bool


class TimeRuleEvaluator:
    def evaluate(self, now: datetime, rule: dict) -> EvaluationResult:
        start_time = time.fromisoformat(rule["startTime"])
        end_time = time.fromisoformat(rule["endTime"])
        current = now.timetz().replace(tzinfo=None)
        inside_window = start_time <= current <= end_time
        if inside_window:
            return EvaluationResult(True, "normal", [], [], False)
        return EvaluationResult(False, "exception", ["late"], ["当前时间不在打卡窗口内"], True)


class LocationRuleEvaluator:
    def evaluate(
        self,
        submitted_longitude: float,
        submitted_latitude: float,
        rule: dict,
    ) -> EvaluationResult:
        if rule.get("mode") == "none":
            return EvaluationResult(True, "normal", [], [], False)

        distance = self._distance_meters(
            submitted_longitude,
            submitted_latitude,
            float(rule["longitude"]),
            float(rule["latitude"]),
        )
        if distance <= float(rule["radius"]):
            return EvaluationResult(True, "normal", [], [], False)
        return EvaluationResult(False, "exception", ["location_error"], ["当前位置不在有效范围内"], True)

    @staticmethod
    def _distance_meters(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        earth_radius = 6_371_000
        dlon = radians(lon2 - lon1)
        dlat = radians(lat2 - lat1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        return 2 * earth_radius * asin(sqrt(a))
```

Run:

```powershell
cd backend
uv run pytest tests/unit/test_rule_evaluators.py -q
cd ..
```

Expected: `4 passed`.

- [ ] **Step 3: Add config and database session**

Create `backend/app/core/config.py`:

```python
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Sizheng Platform"
    app_env: str = "local"
    database_url: str
    redis_url: str | None = None
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 720
    backend_cors_origins: str = "http://localhost:5173"
    file_storage_root: str = "./storage"
    wechat_provider_mode: str = "log"
    face_provider_mode: str = "disabled"

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Create `backend/app/core/database.py`:

```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


engine = create_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: Commit backend core**

Run:

```powershell
git add backend/app backend/tests
git commit -m "Ground check-in validation in explicit rule evaluators" -m "The product depends on rule snapshots rather than hard-coded attendance scenarios, so the first backend slice proves time and location validation with focused tests." -m "Constraint: First phase avoids external rule engines and PostGIS`nRejected: Add a dedicated rules engine | unnecessary for the first closed-loop demo`nConfidence: high`nScope-risk: narrow`nTested: backend evaluator unit tests`nNot-tested: database-backed task submission route"
```

## Task 4: Agent 2 - Backend Models, Auth, and Main APIs

**Files:**
- Create: `backend/app/modules/*/models.py`
- Create: `backend/app/modules/*/schemas.py`
- Create: `backend/app/modules/*/repository.py`
- Create: `backend/app/modules/*/service.py`
- Create: `backend/app/modules/*/router.py`
- Create: `backend/alembic/versions/0001_initial_schema.py`
- Create: `backend/tests/integration/test_checkin_flow.py`
- Create: `test/bruno/AI-Sizheng-Platform/**`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Write the integration test for the demo flow**

Create `backend/tests/integration/test_checkin_flow.py` with this scenario:

```python
def test_admin_teacher_student_checkin_flow(client):
    admin_login = client.post("/api/auth/login", json={
        "account": "admin",
        "password": "123456",
        "user_type": "admin",
    })
    assert admin_login.status_code == 200

    import_students = client.post("/api/admin/students/import", json={
        "students": [{
            "student_no": "20260001",
            "name": "张三",
            "phone": "13800000001",
            "college": "软件学院",
            "major": "软件工程",
            "grade": "2026",
            "class_name": "软件2601",
            "dormitory": "3号楼301",
        }]
    })
    assert import_students.status_code == 200

    activation = client.post("/api/auth/student/activate", json={
        "name": "张三",
        "student_no": "20260001",
        "phone": "13800000001",
        "code": "000000",
        "password": "123456",
    })
    assert activation.status_code == 200

    teacher_login = client.post("/api/auth/login", json={
        "account": "teacher",
        "password": "123456",
        "user_type": "teacher",
    })
    assert teacher_login.status_code == 200

    task = client.post("/api/teacher/tasks", json={
        "title": "晚间查寝",
        "type_id": 1,
        "group_ids": [1],
        "starts_at": "2026-06-24T21:30:00+08:00",
        "ends_at": "2026-06-24T22:30:00+08:00",
        "rules_snapshot": {
            "timeRule": {"mode": "single", "startTime": "21:30", "endTime": "22:30", "allowLate": False, "allowMakeup": True, "makeupNeedReview": True},
            "locationRule": {"mode": "fixed_area", "placeName": "3号宿舍楼", "longitude": 120.000001, "latitude": 30.000001, "radius": 300, "allowExceptionSubmit": True},
            "verificationRule": {"methods": ["location"]},
            "submitRule": {"fields": [{"key": "remark", "label": "情况说明", "type": "textarea", "required": False}]},
            "reviewRule": {"mode": "exception_only"},
            "reminderRule": {"beforeStartMinutes": 10, "beforeEndMinutes": 5, "notifyTeacherAfterEnd": True},
            "faceRule": {"enabled": False, "provider": "placeholder"}
        },
    })
    assert task.status_code == 200
    task_id = task.json()["id"]

    checkin = client.post(f"/api/student/tasks/{task_id}/checkin", json={
        "longitude": 120.000001,
        "latitude": 30.000001,
        "dynamic_code": "",
        "submit_payload": {"remark": "已在宿舍"},
    })
    assert checkin.status_code == 200
    assert checkin.json()["status"] == "normal"
```

Run:

```powershell
cd backend
uv run pytest tests/integration/test_checkin_flow.py -q
cd ..
```

Expected: fail because routers and seed users do not exist.

- [ ] **Step 2: Implement SQLAlchemy models**

Create models matching the spec tables:

```text
users: id, account, phone, password_hash, user_type, status, last_login_at, wechat_openid, created_at
student_profiles: id, user_id, student_no, name, college, major, grade, class_name, dormitory, internship_company, current_status, activated
teacher_profiles: id, user_id, teacher_no, name, department, teacher_role, phone
admin_profiles: id, user_id, department, admin_type, scope_jsonb
organizations: id, parent_id, name, org_type, sort_order
groups: id, organization_id, name, group_type, description
group_members: id, group_id, student_id
group_teachers: id, group_id, teacher_id
checkin_types: id, name, code, enabled
rule_templates: id, name, template_type, checkin_type_id, organization_id, creator_id, status, usage_count, rules_jsonb
checkin_tasks: id, title, description, type_id, teacher_id, status, starts_at, ends_at, is_recurring, should_notify, rules_snapshot_jsonb
checkin_task_groups: id, task_id, group_id
checkin_task_students: id, task_id, student_id, include_mode
checkin_records: id, task_id, student_id, submitted_at, status, longitude, latitude, location_result_jsonb, dynamic_code_result_jsonb, face_result_jsonb, submit_payload_jsonb, system_result_jsonb
checkin_record_attachments: id, record_id, file_url, file_type, original_name
checkin_exceptions: id, record_id, exception_type, status, description
appeals: id, record_id, student_id, reason, status
review_logs: id, reviewer_id, target_type, target_id, decision, comment
messages: id, recipient_user_id, title, content, message_type, read_at, provider_result_jsonb
audit_logs: id, actor_user_id, action, target_type, target_id, detail_jsonb
```

- [ ] **Step 3: Implement route groups**

Add routers for these endpoints:

```text
POST /api/auth/login
POST /api/auth/student/activate
POST /api/auth/send-code
POST /api/auth/bind-wechat
GET /api/auth/me
GET /api/admin/dashboard
GET /api/admin/org/tree
POST /api/admin/students/import
GET /api/admin/students
GET /api/admin/teachers
GET /api/admin/groups
GET /api/admin/checkin-types
GET /api/admin/rule-templates
GET /api/admin/tasks
GET /api/admin/exceptions
GET /api/teacher/dashboard
GET /api/teacher/groups
GET /api/teacher/tasks
POST /api/teacher/tasks
GET /api/teacher/tasks/{id}
POST /api/teacher/tasks/{id}/publish
POST /api/teacher/tasks/{id}/end
GET /api/teacher/exceptions
POST /api/teacher/exceptions/{id}/review
GET /api/student/dashboard
GET /api/student/tasks
GET /api/student/tasks/{id}
POST /api/student/tasks/{id}/checkin
GET /api/student/records
POST /api/student/records/{id}/appeal
GET /api/student/messages
GET /api/student/profile
GET /api/student/growth-summary
```

- [ ] **Step 4: Preserve task rule snapshots**

Write a unit or integration assertion that updates a `rule_templates.rules_jsonb` value after task creation and confirms the existing `checkin_tasks.rules_snapshot_jsonb` is unchanged.

Run:

```powershell
cd backend
uv run pytest tests/integration/test_checkin_flow.py -q
uv run pytest -q
cd ..
```

Expected: all backend tests pass.

- [ ] **Step 5: Add Bruno collection**

Create `test/bruno/AI-Sizheng-Platform` with folders `Auth`, `Admin`, `Teacher`, `Student`, `Checkin`, `Exceptions`, and `Statistics`. The collection order must match:

```text
1. 管理员登录
2. 导入学生、教师、班级
3. 学生首次激活
4. 教师登录
5. 创建并发布任务
6. 学生查询任务
7. 学生提交打卡
8. 教师查看异常
9. 学生提交申诉
10. 教师审核申诉
11. 管理员查看监管统计
```

- [ ] **Step 6: Commit backend APIs**

Run:

```powershell
git add backend test/bruno docs/contracts/api-v1.md
git commit -m "Close the backend attendance loop" -m "The first phase needs a demonstrable admin-teacher-student workflow, so this commit wires models, routes, rule snapshots, and Bruno requests around the core check-in path." -m "Constraint: PostgreSQL JSONB stores flexible rules for first-phase configurability`nRejected: Microservice split | too much deployment and transaction overhead for the demo phase`nConfidence: medium`nScope-risk: broad`nTested: backend unit and integration tests`nNot-tested: real WeChat subscription delivery and real face recognition"
```

## Task 5: Agent 3 - Admin Web Shell and Visual Baseline

**Files:**
- Create: `admin-web/src/router/index.ts`
- Create: `admin-web/src/stores/auth.ts`
- Create: `admin-web/src/layouts/AdminLayout.vue`
- Create: `admin-web/src/views/login/LoginView.vue`
- Create: `admin-web/src/views/dashboard/DashboardView.vue`
- Create: `admin-web/src/components/DataTable/DataTable.vue`
- Create: `admin-web/src/components/OrgTree/OrgTree.vue`
- Create: `admin-web/src/components/RuleEditor/RuleEditor.vue`
- Create: `admin-web/src/views/login/LoginView.spec.ts`
- Modify: `admin-web/src/main.ts`

- [ ] **Step 1: Write failing login render test**

Create `admin-web/src/views/login/LoginView.spec.ts`:

```ts
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import LoginView from './LoginView.vue'

describe('LoginView', () => {
  it('renders admin login fields', () => {
    const wrapper = mount(LoginView)

    expect(wrapper.text()).toContain('AI思政辅助平台')
    expect(wrapper.text()).toContain('账号')
    expect(wrapper.text()).toContain('密码')
    expect(wrapper.text()).toContain('登录')
  })
})
```

Run:

```powershell
cd admin-web
npm run test:unit -- --run src/views/login/LoginView.spec.ts
cd ..
```

Expected: fail because `LoginView.vue` does not exist.

- [ ] **Step 2: Build admin app shell**

Implement:

```text
AdminLayout: left menu, top user bar, main content area
Menu items: 工作台, 组织管理, 学生管理, 教师管理, 班级与分组, 打卡类型, 规则模板, 任务监管, 异常与申诉
LoginView: blue campus background hint, white login panel, Element Plus form
DashboardView: task count, today completion rate, exception count, pending appeal count
```

Use these route names:

```ts
export const adminRoutes = [
  { path: '/login', name: 'login', component: () => import('../views/login/LoginView.vue') },
  { path: '/', component: () => import('../layouts/AdminLayout.vue'), children: [
    { path: '', name: 'dashboard', component: () => import('../views/dashboard/DashboardView.vue') },
    { path: 'organization', name: 'organization', component: () => import('../views/organization/OrganizationView.vue') },
    { path: 'students', name: 'students', component: () => import('../views/students/StudentsView.vue') },
    { path: 'teachers', name: 'teachers', component: () => import('../views/teachers/TeachersView.vue') },
    { path: 'groups', name: 'groups', component: () => import('../views/groups/GroupsView.vue') },
    { path: 'checkin-types', name: 'checkinTypes', component: () => import('../views/checkin-types/CheckinTypesView.vue') },
    { path: 'rule-templates', name: 'ruleTemplates', component: () => import('../views/rule-templates/RuleTemplatesView.vue') },
    { path: 'task-monitor', name: 'taskMonitor', component: () => import('../views/task-monitor/TaskMonitorView.vue') },
    { path: 'exceptions', name: 'exceptions', component: () => import('../views/exceptions/ExceptionsView.vue') },
  ] },
]
```

- [ ] **Step 3: Run admin shell tests**

Run:

```powershell
cd admin-web
npm run test:unit -- --run
npm run build
cd ..
```

Expected: Vitest passes and Vite build succeeds.

- [ ] **Step 4: Commit admin shell**

Run:

```powershell
git add admin-web/src
git commit -m "Give administrators a stable operating shell" -m "The admin lane needs a shared layout and visual baseline before data-heavy pages are filled in, so this commit establishes navigation, login, dashboard, and reusable management components." -m "Constraint: Admin web should stay efficient and not copy the mobile illustration-heavy layout`nConfidence: high`nScope-risk: moderate`nTested: admin unit tests and production build`nNot-tested: live API authorization redirects"
```

## Task 6: Agent 3 - Admin Management Pages

**Files:**
- Create: `admin-web/src/api/admin.ts`
- Create: `admin-web/src/views/organization/OrganizationView.vue`
- Create: `admin-web/src/views/students/StudentsView.vue`
- Create: `admin-web/src/views/teachers/TeachersView.vue`
- Create: `admin-web/src/views/groups/GroupsView.vue`
- Create: `admin-web/src/views/checkin-types/CheckinTypesView.vue`
- Create: `admin-web/src/views/rule-templates/RuleTemplatesView.vue`
- Create: `admin-web/src/views/task-monitor/TaskMonitorView.vue`
- Create: `admin-web/src/views/exceptions/ExceptionsView.vue`

- [ ] **Step 1: Add API client methods**

Create methods for:

```ts
getDashboard()
getOrgTree()
importStudents(payload)
getStudents(params)
getTeachers(params)
getGroups(params)
getCheckinTypes()
getRuleTemplates()
getTasks(params)
getExceptions(params)
```

- [ ] **Step 2: Build pages by workflow**

Implement each page with these controls:

```text
组织管理: OrgTree, create/edit organization form
学生管理: import dialog, search by name/student_no/class, activation status tag, edit profile drawer
教师管理: create teacher dialog, associate groups drawer
班级与分组: group type tabs, member table, teacher table
打卡类型: enabled switch, name/code table
规则模板: RuleEditor with time/location/verification/submit/review/reminder/face sections
任务监管: filter by teacher/type/status/date, completion rate column
异常与申诉: filter by exception type/status, review status column
```

- [ ] **Step 3: Verify admin feature pages**

Run:

```powershell
cd admin-web
npm run test:unit -- --run
npm run build
cd ..
```

Expected: unit tests pass and no TypeScript or Vite build errors remain.

- [ ] **Step 4: Commit admin pages**

Run:

```powershell
git add admin-web/src
git commit -m "Expose first-phase governance pages" -m "Administrators need to configure people, groups, types, templates, and oversight data before teachers and students can complete the check-in loop." -m "Constraint: First phase excludes export approvals and deep audit screens`nConfidence: medium`nScope-risk: moderate`nTested: admin unit tests and production build`nNot-tested: large Excel import files"
```

## Task 7: Agent 4 - Student Mini-App Shell, Auth, and Shared Mobile Components

**Files:**
- Create: `mini-app/src/pages/auth/login.vue`
- Create: `mini-app/src/pages/auth/activate.vue`
- Create: `mini-app/src/pages/student/home.vue`
- Create: `mini-app/src/pages/student/tasks.vue`
- Create: `mini-app/src/stores/user.ts`
- Create: `mini-app/src/services/auth.ts`
- Create: `mini-app/src/services/student.ts`
- Create: `mini-app/src/components/TaskCard.vue`
- Create: `mini-app/src/components/StatusTag.vue`
- Create: `mini-app/src/components/RuleSummary.vue`
- Create: `mini-app/src/components/DynamicForm.vue`
- Create: `mini-app/src/components/LocationPicker.vue`
- Modify: `mini-app/src/pages.json`

- [ ] **Step 1: Write failing auth component test**

Create `mini-app/src/pages/auth/login.spec.ts`:

```ts
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import LoginPage from './login.vue'

describe('student login page', () => {
  it('renders login and activation entry points', () => {
    const wrapper = mount(LoginPage)

    expect(wrapper.text()).toContain('智慧考勤')
    expect(wrapper.text()).toContain('学号/手机号')
    expect(wrapper.text()).toContain('密码')
    expect(wrapper.text()).toContain('首次激活')
  })
})
```

Run:

```powershell
cd mini-app
npm run test:unit -- --run src/pages/auth/login.spec.ts
cd ..
```

Expected: fail because login page is not implemented.

- [ ] **Step 2: Implement mobile visual baseline**

Use `tokens.scss` and the spec visual language:

```text
login/activate: blue campus top area, white rounded card, tab switch, rounded inputs, blue primary button
student home: greeting, 今日待打卡, 即将截止, 异常提醒, quick entries
bottom nav: 首页, 打卡任务, 消息, 我的
StatusTag: green normal, blue in-progress, orange pending, red exception, gray ended
TaskCard: title, type, status, deadline, primary action
```

- [ ] **Step 3: Add auth and student services**

Create service methods:

```ts
login(payload: { account: string; password: string; user_type: 'student' | 'teacher' | 'admin' })
activateStudent(payload: { name: string; student_no: string; phone: string; code: string; password: string })
getStudentDashboard()
getStudentTasks(status?: string)
getStudentTaskDetail(id: number)
submitCheckin(id: number, payload)
getStudentRecords()
submitAppeal(recordId: number, payload)
getStudentMessages()
getStudentProfile()
getGrowthSummary()
```

- [ ] **Step 4: Verify student shell**

Run:

```powershell
cd mini-app
npm run test:unit -- --run
npm run build:mp-weixin
cd ..
```

Expected: unit tests pass and mini-program build emits `dist/build/mp-weixin`.

- [ ] **Step 5: Commit student shell**

Run:

```powershell
git add mini-app/src
git commit -m "Give students the activation and task shell" -m "The student lane needs login, activation, dashboard, task cards, and shared mobile components before the actual check-in flow can be completed." -m "Constraint: Student registration is activation of imported profiles, not open public signup`nConfidence: high`nScope-risk: moderate`nTested: mini-app unit tests and mp-weixin build`nNot-tested: real device location permission prompts"
```

## Task 8: Agent 4 - Student Check-In, Result, Messages, and Profile

**Files:**
- Create: `mini-app/src/pages/student/task-detail.vue`
- Create: `mini-app/src/pages/student/checkin-submit.vue`
- Create: `mini-app/src/pages/student/result.vue`
- Create: `mini-app/src/pages/student/messages.vue`
- Create: `mini-app/src/pages/student/profile.vue`
- Create: `mini-app/src/pages/student/records.vue`
- Create: `mini-app/src/pages/student/appeal.vue`
- Create: `mini-app/src/services/location.ts`
- Modify: `mini-app/src/pages.json`

- [ ] **Step 1: Add location service**

Create `mini-app/src/services/location.ts`:

```ts
export interface LocationResult {
  longitude: number
  latitude: number
}

export function getCurrentLocation(): Promise<LocationResult> {
  return new Promise((resolve, reject) => {
    uni.getLocation({
      type: 'gcj02',
      success: (res) => resolve({ longitude: res.longitude, latitude: res.latitude }),
      fail: reject,
    })
  })
}
```

- [ ] **Step 2: Build check-in pages**

Implement:

```text
task-detail: RuleSummary, time window, place, submit requirements, status action
checkin-submit: LocationPicker, dynamic code input, DynamicForm fields, face entry hidden when faceRule.enabled is false
result: normal, exception, pending_review states with next action
records: personal record list with status filters
appeal: reason textarea, image attachment picker, submit button
messages: reminder, teacher feedback, appeal result list
profile: personal info, growth overview, activation state, privacy entry
```

- [ ] **Step 3: Verify student flow**

Run:

```powershell
cd mini-app
npm run test:unit -- --run
npm run build:mp-weixin
cd ..
```

Expected: unit tests pass and mini-program build succeeds.

- [ ] **Step 4: Commit student flow**

Run:

```powershell
git add mini-app/src/pages/student mini-app/src/services mini-app/src/pages.json
git commit -m "Complete the student check-in path" -m "Students need to inspect rules, submit real location data, see outcomes, appeal exceptions, and review messages for the closed-loop demo." -m "Constraint: Face recognition entry is rule-controlled and disabled by default`nConfidence: medium`nScope-risk: moderate`nTested: mini-app unit tests and mp-weixin build`nNot-tested: physical WeChat device submission against campus coordinates"
```

## Task 9: Agent 5 - Teacher Mini-App Shell and Task Creation

**Files:**
- Create: `mini-app/src/pages/teacher/home.vue`
- Create: `mini-app/src/pages/teacher/tasks.vue`
- Create: `mini-app/src/pages/teacher/task-create.vue`
- Create: `mini-app/src/services/teacher.ts`
- Modify: `mini-app/src/pages.json`

- [ ] **Step 1: Write failing task creation test**

Create `mini-app/src/pages/teacher/task-create.spec.ts`:

```ts
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import TaskCreate from './task-create.vue'

describe('teacher task creation', () => {
  it('shows the required creation steps', () => {
    const wrapper = mount(TaskCreate)

    expect(wrapper.text()).toContain('基础信息')
    expect(wrapper.text()).toContain('选择分组')
    expect(wrapper.text()).toContain('选择模板')
    expect(wrapper.text()).toContain('确认发布')
  })
})
```

Run:

```powershell
cd mini-app
npm run test:unit -- --run src/pages/teacher/task-create.spec.ts
cd ..
```

Expected: fail because teacher task page is not implemented.

- [ ] **Step 2: Add teacher service methods**

Create methods:

```ts
getTeacherDashboard()
getTeacherGroups()
getTeacherTasks(status?: string)
createTeacherTask(payload)
getTeacherTaskDetail(id: number)
publishTeacherTask(id: number)
endTeacherTask(id: number)
getTeacherExceptions()
reviewTeacherException(id: number, payload)
```

- [ ] **Step 3: Build teacher shell**

Implement:

```text
home: 今日任务, 异常, 待审核, 快捷创建
tasks: status tabs 进行中/未开始/已结束/待审核, TaskCard list
task-create: basic info, group selector, type/template selector, folded advanced rules, RuleSummary confirmation
bottom nav: 首页, 任务, 班级, 我的
```

- [ ] **Step 4: Verify teacher shell**

Run:

```powershell
cd mini-app
npm run test:unit -- --run
npm run build:mp-weixin
cd ..
```

Expected: unit tests pass and mini-program build succeeds.

- [ ] **Step 5: Commit teacher task creation**

Run:

```powershell
git add mini-app/src/pages/teacher mini-app/src/services/teacher.ts mini-app/src/pages.json
git commit -m "Enable teachers to create attendance tasks" -m "Teachers need a template-first creation flow so the first phase can publish tasks without exposing every rule knob up front." -m "Constraint: Advanced rules stay folded to keep the mini-app workflow efficient`nConfidence: medium`nScope-risk: moderate`nTested: mini-app unit tests and mp-weixin build`nNot-tested: creating recurring tasks"
```

## Task 10: Agent 5 - Teacher Task Detail, Exceptions, Groups, and Profile

**Files:**
- Create: `mini-app/src/pages/teacher/task-detail.vue`
- Create: `mini-app/src/pages/teacher/exceptions.vue`
- Create: `mini-app/src/pages/teacher/groups.vue`
- Create: `mini-app/src/pages/teacher/group-detail.vue`
- Create: `mini-app/src/pages/teacher/profile.vue`
- Modify: `mini-app/src/pages.json`

- [ ] **Step 1: Build teacher task detail and exception flow**

Implement:

```text
task-detail: completion rate, student list, exception list, publish/end actions
exceptions: pending/reviewed tabs, approve/reject/need_more actions, comment input
groups: managed group list, student count, recent task count
group-detail: student list, class tasks, basic statistics
profile: teacher info, managed classes, message settings entry
```

- [ ] **Step 2: Verify teacher flow**

Run:

```powershell
cd mini-app
npm run test:unit -- --run
npm run build:mp-weixin
cd ..
```

Expected: unit tests pass and mini-program build succeeds.

- [ ] **Step 3: Commit teacher management flow**

Run:

```powershell
git add mini-app/src/pages/teacher mini-app/src/pages.json
git commit -m "Close the teacher review workflow" -m "The teacher lane needs task monitoring, group context, and exception review to complete the student appeal loop." -m "Constraint: First phase focuses on class-level statistics, not long-term AI risk scoring`nConfidence: medium`nScope-risk: moderate`nTested: mini-app unit tests and mp-weixin build`nNot-tested: push notification settings against real WeChat templates"
```

## Task 11: Cross-Agent Integration

**Files:**
- Modify: `admin-web/.env.example`
- Modify: `mini-app/src/services/request.ts`
- Modify: `backend/app/main.py`
- Modify: `docs/contracts/api-v1.md`
- Modify: `README.md`

- [ ] **Step 1: Start infrastructure**

Run:

```powershell
docker compose up -d postgres redis
docker compose ps
```

Expected: `postgres` is healthy and `redis` is running.

- [ ] **Step 2: Run database migration**

Run:

```powershell
just backend-migrate
```

Expected: Alembic applies `0001_initial_schema`.

- [ ] **Step 3: Run backend**

Run:

```powershell
just backend-dev
```

Expected: FastAPI starts on `http://localhost:8000` and `/health` returns `{"status":"ok"}`.

- [ ] **Step 4: Run admin web**

Run in a second terminal:

```powershell
just admin-dev
```

Expected: admin web opens on `http://localhost:5173`.

- [ ] **Step 5: Run mini-app build**

Run:

```powershell
just mini-test
cd mini-app
npm run build:mp-weixin
cd ..
```

Expected: unit tests pass and `dist/build/mp-weixin` is generated.

- [ ] **Step 6: Execute the manual acceptance flow**

Use browser/dev tools or Bruno to complete:

```text
1. Admin logs in.
2. Admin imports one student and one teacher.
3. Student activates account.
4. Teacher logs in.
5. Teacher creates and publishes 晚间查寝 task.
6. Student sees task.
7. Student submits check-in with valid location.
8. Backend returns normal record.
9. Student submits an out-of-range check-in for another task.
10. Backend creates location_error exception.
11. Student submits appeal.
12. Teacher approves or rejects appeal.
13. Admin dashboard shows task count, completion rate, exception count, and pending appeals.
```

- [ ] **Step 7: Commit integration fixes**

Run:

```powershell
git add backend admin-web mini-app docs/contracts README.md
git commit -m "Integrate the first-phase attendance demo" -m "The independent lanes now need one verified end-to-end path, so this commit aligns API URLs, CORS, contracts, and documentation around the demo workflow." -m "Constraint: Bruno and pytest prove different parts of the workflow`nConfidence: medium`nScope-risk: broad`nTested: backend tests, admin build, mini build, manual demo flow`nNot-tested: production deployment and real WeChat subscriptions"
```

## Task 12: Final Verification and Handoff

**Files:**
- Modify: `README.md`
- Modify: `docs/contracts/api-v1.md`
- Create: `docs/superpowers/reports/2026-06-24-ai-sizheng-platform-verification.md`

- [ ] **Step 1: Run backend verification**

Run:

```powershell
cd backend
uv run ruff check .
uv run pytest -q
cd ..
```

Expected: ruff exits 0 and pytest exits 0.

- [ ] **Step 2: Run admin verification**

Run:

```powershell
cd admin-web
npm run test:unit -- --run
npm run build
cd ..
```

Expected: tests and production build pass.

- [ ] **Step 3: Run mini-app verification**

Run:

```powershell
cd mini-app
npm run test:unit -- --run
npm run build:mp-weixin
cd ..
```

Expected: tests pass and mini-program build succeeds.

- [ ] **Step 4: Write verification report**

Create `docs/superpowers/reports/2026-06-24-ai-sizheng-platform-verification.md` with:

```markdown
# AI Sizheng Platform Verification Report

## Automated Verification

- Backend lint: command and result
- Backend tests: command and result
- Admin tests: command and result
- Admin build: command and result
- Mini-app tests: command and result
- Mini-app build: command and result

## Manual Demo Flow

- Admin import: pass/fail and evidence
- Student activation: pass/fail and evidence
- Teacher task publish: pass/fail and evidence
- Student normal check-in: pass/fail and evidence
- Student exception and appeal: pass/fail and evidence
- Teacher review: pass/fail and evidence
- Admin statistics: pass/fail and evidence

## Known Gaps

- Real WeChat subscription templates are not configured in first-phase local verification.
- Real face recognition provider is intentionally disabled by rule configuration.
- Production deployment is outside this first-phase implementation plan.
```

- [ ] **Step 5: Commit verification report**

Run:

```powershell
git add README.md docs/contracts/api-v1.md docs/superpowers/reports/2026-06-24-ai-sizheng-platform-verification.md
git commit -m "Record first-phase verification evidence" -m "A multi-agent build needs a durable handoff that separates verified behavior from known first-phase gaps." -m "Confidence: high`nScope-risk: narrow`nTested: recorded in verification report`nNot-tested: items listed under known gaps"
```

## Milestone Mapping

| Spec Milestone | Covered By |
| --- | --- |
| 1 工程骨架与基础设施 | Task 1, Task 2 |
| 2 账号、组织、用户、分组 | Task 4, Task 6, Task 7 |
| 3 打卡类型与规则模板 | Task 4, Task 6, Task 9 |
| 4 教师发布任务 | Task 4, Task 9, Task 10 |
| 5 学生真实定位打卡 | Task 3, Task 4, Task 8 |
| 6 异常、申诉、消息 | Task 4, Task 8, Task 10 |
| 7 监管与基础统计 | Task 4, Task 6, Task 8, Task 10, Task 11 |

## Self-Review

Spec coverage:

- Architecture and module boundaries: covered by Agent 1 scaffold and Agent 2 backend modules.
- Database and core data model: covered by Task 4 model list and migration requirement.
- Rule evaluator and integrations: covered by Task 3 evaluator tests and Task 4 route integration.
- Three client scopes: covered by Tasks 5-10.
- API and directory structure: covered by Shared Contract, File Structure, Tasks 1-2, and Task 4.
- Testing, Bruno, and milestones: covered by Tasks 4, 11, 12 and Milestone Mapping.
- Frontend visual guide: covered by Tasks 5, 7, 8, 9, and 10.

Placeholder scan:

- The plan avoids open-ended implementation markers. Each task has concrete files, commands, status expectations, and commit instructions.
- Real face recognition and real WeChat subscription delivery are explicitly first-phase gaps, not unfinished implementation items.

Type consistency:

- User, task, record, exception, and rule snapshot names match across shared TypeScript contract, backend route expectations, and frontend service names.

## Reference Notes

- Vite scaffold command follows the official Vite guide: `npm create vite@latest`.
- uni-app Vue3/Vite scaffold command follows the official DCloud CLI guide: `npx degit dcloudio/uni-preset-vue#vite-ts`.
- FastAPI with uv follows Astral's uv FastAPI integration guidance.
- Alembic migration flow follows Alembic's official tutorial.

Reference URLs:

- Vite: https://vite.dev/guide
- uni-app CLI: https://uniapp.dcloud.net.cn/quickstart-cli.html
- uv with FastAPI: https://docs.astral.sh/uv/guides/integration/fastapi
- Alembic tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
