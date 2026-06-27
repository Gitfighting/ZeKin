#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> 检查后端健康..."
curl -sf "${BASE_URL:-http://127.0.0.1:8000}/health" | grep -q '"ok"' || {
  echo "后端未启动，请先运行: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
  exit 1
}

echo "==> 安装 Bruno CLI..."
cd "$ROOT/bruno"
npm install --silent

echo "==> 运行 zeKin-e2e 全链路测试..."
cd "$ROOT/bruno/zeKin-e2e"
npx bru run --env local

echo "==> 全部通过"
