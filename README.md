# AI Sizheng Platform

Monorepo scaffold for the AI Sizheng Platform. The first gate establishes shared local infrastructure, backend health checks, and frontend application shells so backend, admin, teacher, and student lanes can proceed independently.

## Workspace Layout

- `backend/` - FastAPI backend service.
- `admin-web/` - Vue 3 + Vite admin web application.
- `mini-app/` - uni-app Vue student/teacher mini-app shell.
- `docs/contracts/` - shared API contracts until backend OpenAPI becomes authoritative.

## Prerequisites

- Docker and Docker Compose
- Python with `uv`
- Node.js and npm
- `just`

## Local Services

Start Postgres and Redis:

```powershell
docker compose up -d
```

## Common Commands

```powershell
just backend-dev
just backend-test
just admin-dev
just admin-test
just mini-dev
just mini-test
```

Copy `.env.example` to `.env` for local backend runtime values. Do not commit `.env`.
