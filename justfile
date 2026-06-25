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
