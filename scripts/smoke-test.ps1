param(
    [string]$BackendUrl = "http://127.0.0.1:8000",
    [string]$FrontendUrl = "http://127.0.0.1:5173"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$passCount = 0

function Pass($Message) {
    $script:passCount += 1
    Write-Host "[PASS] $Message"
}

function Fail($Message) {
    Write-Host "[FAIL] $Message"
    exit 1
}

function Invoke-JsonPost($Url, $Body) {
    $json = $Body | ConvertTo-Json -Depth 30
    Invoke-RestMethod -Method Post -Uri $Url -ContentType "application/json; charset=utf-8" -Body $json
}

try {
    $health = Invoke-RestMethod -Method Get -Uri "$BackendUrl/health"
    if ($health.status -ne "ok") { Fail "Backend health returned unexpected status" }
    Pass "Backend health"

    $novel = Get-Content -Raw -Encoding UTF8 (Join-Path $Root "examples/novel-sample-1.txt")
    $parse = Invoke-JsonPost "$BackendUrl/api/chapters/parse" @{ content = $novel }
    if (-not $parse.valid -or $parse.chapter_count -lt 3) { Fail "Chapter parse did not return at least 3 valid chapters" }
    Pass "Chapter parse"

    $generate = Invoke-JsonPost "$BackendUrl/api/script/generate" @{
        title = "Smoke Test Novel"
        genre = "都市"
        chapters = $parse.chapters
    }
    if ([string]::IsNullOrWhiteSpace($generate.yaml)) { Fail "Script generate returned empty YAML" }
    Pass "Script generate"

    $validate = Invoke-JsonPost "$BackendUrl/api/script/validate" @{ yaml = $generate.yaml }
    if (-not $validate.valid) { Fail ("YAML validate failed: " + ($validate.errors -join "; ")) }
    Pass "YAML validate"

    $project = Invoke-JsonPost "$BackendUrl/api/projects" @{
        title = "Smoke Test Project"
        genre = "都市"
        source_content = $novel
        chapters = $parse.chapters
        yaml = $generate.yaml
        validation = $validate
        generation_mode = "mock"
    }
    if (-not $project.id) { Fail "Project create did not return an id" }
    Pass "Project create"

    $version = Invoke-JsonPost "$BackendUrl/api/projects/$($project.id)/versions" @{
        version_name = "Smoke Snapshot"
        yaml = $generate.yaml
        validation = $validate
        note = "Created by smoke test"
    }
    if (-not $version.id) { Fail "Version create did not return an id" }
    Pass "Version create"

    foreach ($format in @("yaml", "json", "markdown")) {
        $response = Invoke-WebRequest -Method Get -Uri "$BackendUrl/api/projects/$($project.id)/export/$format"
        if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 300 -or [string]::IsNullOrWhiteSpace($response.Content)) {
            Fail "Export $format failed"
        }
        Pass "Export $format"
    }

    $frontend = Invoke-WebRequest -Method Get -Uri $FrontendUrl
    if ($frontend.StatusCode -lt 200 -or $frontend.StatusCode -ge 300) { Fail "Frontend is not reachable" }
    Pass "Frontend reachable"

    Write-Host "[PASS] Smoke test completed ($passCount checks)"
}
catch {
    Fail $_.Exception.Message
}
