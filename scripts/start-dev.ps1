param(
    [string]$BackendHost = "127.0.0.1",
    [int]$BackendPort = 8000,
    [string]$FrontendHost = "127.0.0.1",
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$BackendUrl = "http://$BackendHost`:$BackendPort"
$FrontendUrl = "http://$FrontendHost`:$FrontendPort"

function Assert-Command($Name, $InstallHint) {
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name is not available. $InstallHint"
    }
}

function Assert-PortFree($Port, $Label) {
    $used = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($used) {
        throw "$Label port $Port is already in use. Stop that process or pass another port."
    }
}

Assert-Command python "Install Python 3.10+ and add it to PATH."
Assert-Command node "Install Node.js 18+ and add it to PATH."
Assert-Command npm "Install npm with Node.js."
Assert-PortFree $BackendPort "Backend"
Assert-PortFree $FrontendPort "Frontend"

Push-Location $Root
try {
    if (-not (Test-Path "frontend/node_modules")) {
        Write-Host "[INFO] Installing frontend dependencies..."
        Push-Location "frontend"
        npm install
        Pop-Location
    }

    Write-Host "[INFO] Starting backend at $BackendUrl"
    $backendJob = Start-Job -Name "novel2script-backend" -ScriptBlock {
        param($RootPath, $Port)
        Set-Location $RootPath
        python -m uvicorn app.main:app --reload --app-dir backend --host 127.0.0.1 --port $Port
    } -ArgumentList $Root, $BackendPort

    Write-Host "[INFO] Starting frontend at $FrontendUrl"
    $frontendJob = Start-Job -Name "novel2script-frontend" -ScriptBlock {
        param($RootPath, $HostName, $Port, $ApiUrl)
        Set-Location (Join-Path $RootPath "frontend")
        $env:VITE_API_BASE_URL = $ApiUrl
        npm run dev -- --host $HostName --port $Port
    } -ArgumentList $Root, $FrontendHost, $FrontendPort, $BackendUrl

    Write-Host ""
    Write-Host "Novel2Script is starting."
    Write-Host "Backend:  $BackendUrl"
    Write-Host "Frontend: $FrontendUrl"
    Write-Host "Mock mode is enabled unless ENABLE_AI_GENERATION=true is set."
    Write-Host "Press Ctrl+C to stop both services."

    while ($true) {
        Receive-Job $backendJob, $frontendJob
        Start-Sleep -Seconds 2
    }
}
finally {
    Get-Job -Name "novel2script-backend","novel2script-frontend" -ErrorAction SilentlyContinue | Stop-Job
    Get-Job -Name "novel2script-backend","novel2script-frontend" -ErrorAction SilentlyContinue | Remove-Job
    $ports = @($BackendPort, $FrontendPort)
    $listeners = Get-NetTCPConnection -LocalPort $ports -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($processId in $listeners) {
        $proc = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($proc) {
            Stop-Process -Id $processId -Force
        }
    }
    Pop-Location
}
