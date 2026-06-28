# 人脸识别联调脚本（PowerShell）
# 依赖：后端已启动，且已安装 face_recognition 或 opencv-python

$BaseUrl = if ($env:ZEKIN_BASE_URL) { $env:ZEKIN_BASE_URL } else { "http://127.0.0.1:8000" }
$PhotoPath = if ($env:FACE_PHOTO_PATH) { $env:FACE_PHOTO_PATH } else { "../Img/Student/首页.png" }

Write-Host "==> 1. 管理员登录"
$adminLogin = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/auth/login" -ContentType "application/json" -Body '{"account":"admin","password":"123456","user_type":"admin"}'
$adminToken = $adminLogin.data.access_token
Write-Host "admin_token 获取成功"

Write-Host "==> 2. 查询演示学生档案"
$students = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/admin/students" -Headers @{ Authorization = "Bearer $adminToken" }
$student = $students.data.items | Where-Object { $_.student_no -eq "20260001" } | Select-Object -First 1
if (-not $student) { throw "未找到学号 20260001 的演示学生" }
$studentProfileId = $student.id
Write-Host "student_profile_id=$studentProfileId name=$($student.name)"

Write-Host "==> 3. 管理员录入人脸"
if (-not (Test-Path $PhotoPath)) { throw "照片不存在: $PhotoPath" }
$photoItem = Get-Item $PhotoPath
$form = @{
  photo = $photoItem
}
$register = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/admin/students/$studentProfileId/face" -Headers @{ Authorization = "Bearer $adminToken" } -Form $form
Write-Host "录入结果:" ($register.data | ConvertTo-Json -Compress)

Write-Host "==> 4. 查询人脸状态"
$status = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/admin/students/$studentProfileId/face" -Headers @{ Authorization = "Bearer $adminToken" }
Write-Host "状态:" ($status.data | ConvertTo-Json -Compress)

Write-Host "==> 5. 学生登录"
$studentLogin = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/auth/login" -ContentType "application/json" -Body '{"account":"20260001","password":"123456","user_type":"student"}'
$studentToken = $studentLogin.data.access_token
Write-Host "student_token 获取成功"

Write-Host "==> 6. 获取学生任务列表"
$tasks = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/student/tasks" -Headers @{ Authorization = "Bearer $studentToken" }
$faceTask = $tasks.data.items | Where-Object { $_.methods -contains "face" -or $_.title -match "查寝|人脸|宿舍" } | Select-Object -First 1
if (-not $faceTask) {
  Write-Host "未找到启用人脸的任务，请先在教师端创建并发布含 face 规则的任务"
  exit 0
}
Write-Host "task_id=$($faceTask.id) title=$($faceTask.title)"

Write-Host "==> 7. 提交带人脸照片的打卡"
$bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $PhotoPath))
$base64 = [Convert]::ToBase64String($bytes)
$payload = @{
  longitude = 120.000001
  latitude = 30.000001
  occurrence_date = (Get-Date -Format "yyyy-MM-dd")
  dynamic_code = ""
  face_image = "data:image/jpeg;base64,$base64"
  submit_payload = @{ remark = "PowerShell 人脸联调" }
} | ConvertTo-Json -Depth 5
try {
  $checkin = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/student/tasks/$($faceTask.id)/checkin" -Headers @{ Authorization = "Bearer $studentToken" } -ContentType "application/json" -Body $payload
  Write-Host "打卡成功:" ($checkin.data | ConvertTo-Json -Compress)
} catch {
  Write-Host "打卡失败:" $_.Exception.Message
  if ($_.ErrorDetails.Message) { Write-Host $_.ErrorDetails.Message }
  exit 1
}

Write-Host "==> 完成。请同时查看 backend 控制台日志（zeKin.face_recognition / zeKin.checkin）"
