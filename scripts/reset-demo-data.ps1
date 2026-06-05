$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$DataDir = Join-Path $Root "backend/data"
$Files = @(
    Join-Path $DataDir "novel2script.db",
    Join-Path $DataDir "novel2script.db-shm",
    Join-Path $DataDir "novel2script.db-wal"
)

foreach ($file in $Files) {
    if (Test-Path $file) {
        Remove-Item -LiteralPath $file -Force
        Write-Host "[PASS] Removed $file"
    }
}

Write-Host "[PASS] Demo data reset. The backend will recreate SQLite tables on next start."
