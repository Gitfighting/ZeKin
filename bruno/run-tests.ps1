$ErrorActionPreference = "Stop"
$BaseUrl = if ($env:BASE_URL) { $env:BASE_URL } else { "http://127.0.0.1:8000" }
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "==> 检查后端健康..."
try {
  $health = Invoke-RestMethod "$BaseUrl/health"
  if ($health.status -ne "ok") { throw "health not ok" }
} catch {
  Write-Host "后端未启动，请先运行: cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
  exit 1
}

Write-Host "==> 安装 Bruno CLI..."
Push-Location "$Root\bruno"
npm install --silent

Write-Host "==> 运行 zeKin-e2e 全链路测试..."
Push-Location "$Root\bruno\zeKin-e2e"
npx bru run --env local
$code = $LASTEXITCODE
Pop-Location

if ($code -ne 0) { exit $code }
Write-Host "==> 全部通过"
