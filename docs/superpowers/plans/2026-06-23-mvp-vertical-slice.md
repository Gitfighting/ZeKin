# ZeKin MVP Vertical Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable 72-hour MVP vertical slice for ZeKin with FastAPI APIs, Bruno interface tests, Vue admin shell, and WeChat mini program page skeletons.

**Architecture:** The backend exposes the 8 MVP APIs from the requirements document and uses SQLAlchemy models that run against SQLite in tests and MySQL in deployment through `DATABASE_URL`. Redis is integrated behind a tiny cache client so local tests can run without Redis while deployment keeps the required Redis service. The frontends are thin clients that match the UI design spec and consume the same API contract.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, PyJWT, bcrypt/passlib, pytest, httpx/TestClient, MySQL 8.0, Redis, Vue 3 + Vite, Element Plus, WeChat Mini Program, Bruno CLI.

---

## File Structure

- `backend/app/main.py`: FastAPI application factory, routers, middleware, startup table creation.
- `backend/app/core/config.py`: environment-based settings.
- `backend/app/core/database.py`: SQLAlchemy engine/session setup.
- `backend/app/core/security.py`: password hashing, JWT creation, current-user dependency helpers.
- `backend/app/core/logging.py`: structured logging setup based on the provided logging documents.
- `backend/app/middleware/request_logger.py`: request logging middleware with `request_id`.
- `backend/app/models.py`: `User`, `Checkin`, `Review` SQLAlchemy models.
- `backend/app/schemas.py`: Pydantic request/response models.
- `backend/app/routers/auth.py`: register, login, me endpoints.
- `backend/app/routers/checkins.py`: student submit and history endpoints.
- `backend/app/routers/teacher.py`: teacher list and review endpoints.
- `backend/app/routers/stats.py`: overview stats endpoint.
- `backend/tests/test_mvp_api.py`: end-to-end API tests with SQLite.
- `backend/requirements.txt`: backend runtime and test dependencies.
- `backend/.env.example`: local MySQL/Redis/JWT configuration sample.
- `test/bruno/ZeKin-MVP`: Bruno collection with auth, checkin, teacher review, stats requests.
- `admin-web`: Vue 3 admin shell matching the Octo Code design direction.
- `student-miniprogram`: WeChat mini program pages for student login, home, submit, history.
- `teacher-miniprogram`: WeChat mini program pages for teacher login, review list, review detail, overview.
- `docker-compose.yml`: MySQL, Redis, backend, admin web service wiring for local/server parity.

## Task 1: Backend Tests First

**Files:**
- Create: `backend/tests/test_mvp_api.py`
- Create: `backend/requirements.txt`

- [ ] **Step 1: Write failing API tests**

Create `backend/tests/test_mvp_api.py` with tests that register a student and teacher, log in, submit a checkin, review it, and fetch stats.

- [ ] **Step 2: Run tests to verify RED**

Run: `cd backend; python -m pytest tests/test_mvp_api.py -q`

Expected: fail because `app.main` does not exist yet.

## Task 2: Backend Minimal Implementation

**Files:**
- Create: backend application files listed in File Structure.

- [ ] **Step 1: Implement FastAPI app and models**

Create SQLAlchemy models for `users`, `checkins`, and `reviews`, matching the requirements document.

- [ ] **Step 2: Implement security**

Add bcrypt password hashing and JWT authentication. Use `role` to protect student, teacher, and admin-only endpoints.

- [ ] **Step 3: Implement 8 MVP APIs**

Implement:

```text
POST /api/auth/register
POST /api/auth/login
GET /api/auth/me
POST /api/checkins
GET /api/checkins/my
GET /api/teacher/checkins
POST /api/teacher/reviews
GET /api/stats/overview
```

- [ ] **Step 4: Run tests to verify GREEN**

Run: `cd backend; python -m pytest tests/test_mvp_api.py -q`

Expected: all tests pass.

## Task 3: Bruno API Tests

**Files:**
- Create: `test/bruno/ZeKin-MVP/collection.bru`
- Create: `test/bruno/ZeKin-MVP/environments/local.bru`
- Create: request files under `test/bruno/ZeKin-MVP/Auth`, `Checkins`, `Teacher`, and `Stats`.

- [ ] **Step 1: Create Git-friendly Bruno collection**

Use Bruno `.bru` files so requests and assertions can be reviewed in Git.

- [ ] **Step 2: Add run instructions**

Document:

```powershell
cd test\bruno\ZeKin-MVP
bru run --env Local
```

Bruno official docs confirm `bru run` runs a collection and `--env`/`--env-file` can select environment variables.

## Task 4: Admin Web Skeleton

**Files:**
- Create: `admin-web/package.json`
- Create: `admin-web/index.html`
- Create: `admin-web/src/main.js`
- Create: `admin-web/src/App.vue`
- Create: `admin-web/src/styles.css`

- [ ] **Step 1: Build Octo Code admin shell**

Create dark sidebar layout with dashboard, checkins, users, and logs sections.

- [ ] **Step 2: Add static MVP data states**

Show cards and tables that match the UI design spec so API integration can be added independently.

## Task 5: Mini Program Skeletons

**Files:**
- Create: `student-miniprogram/**`
- Create: `teacher-miniprogram/**`

- [ ] **Step 1: Build student pages**

Create login, home, submit, history, and profile pages using MicroPost-style cards and chips.

- [ ] **Step 2: Build teacher pages**

Create login, review list, review detail, overview, and profile pages using compact card lists.

## Task 6: Docker and Documentation

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Modify: `README.md`

- [ ] **Step 1: Add local services**

Define MySQL, Redis, backend, and admin web services.

- [ ] **Step 2: Add run commands**

Document backend tests, admin web dev server, and Bruno CLI commands.

## Self-Review

- Spec coverage: covers the 8 MVP APIs, MySQL/Redis backend, Vue admin web, WeChat student/teacher mini programs, logging requirement, and Bruno API testing.
- Placeholder scan: no implementation step relies on `TBD` or undefined future work.
- Scope check: this is a vertical slice, not a complete production system. AI审核、人脸识别、补签、复杂用户管理 remain out of MVP scope according to the requirements.

