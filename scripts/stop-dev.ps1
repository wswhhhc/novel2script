# Novel2Script - 停止开发服务
# Windows PowerShell 脚本

Write-Host "正在停止 Novel2Script 开发服务..." -ForegroundColor Cyan

# 停止后端服务（通过 8000 端口查找）
$backendPids = netstat -ano | Select-String ":8000.*LISTENING" | ForEach-Object {
    if ($_ -match "\s+(\d+)$") {
        $matches[1]
    }
} | Select-Object -Unique

if ($backendPids) {
    foreach ($pid in $backendPids) {
        Write-Host "停止后端服务 (PID: $pid)..." -ForegroundColor Yellow
        taskkill /F /PID $pid 2>$null
    }
    Write-Host "✓ 后端服务已停止" -ForegroundColor Green
} else {
    Write-Host "○ 后端服务未运行" -ForegroundColor Gray
}

# 停止前端服务（通过 5173 端口查找）
$frontendPids = netstat -ano | Select-String ":5173.*LISTENING" | ForEach-Object {
    if ($_ -match "\s+(\d+)$") {
        $matches[1]
    }
} | Select-Object -Unique

if ($frontendPids) {
    foreach ($pid in $frontendPids) {
        Write-Host "停止前端服务 (PID: $pid)..." -ForegroundColor Yellow
        taskkill /F /PID $pid 2>$null
    }
    Write-Host "✓ 前端服务已停止" -ForegroundColor Green
} else {
    Write-Host "○ 前端服务未运行" -ForegroundColor Gray
}

Write-Host "`n所有服务已停止" -ForegroundColor Cyan
