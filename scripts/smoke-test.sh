#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://127.0.0.1:5173}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

command -v python >/dev/null 2>&1 || { echo "[FAIL] python is not available"; exit 1; }
command -v curl >/dev/null 2>&1 || { echo "[FAIL] curl is not available"; exit 1; }

pass() { echo "[PASS] $1"; }
fail() { echo "[FAIL] $1"; exit 1; }

python - "$ROOT" "$BACKEND_URL" "$FRONTEND_URL" <<'PY'
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

root = Path(sys.argv[1])
backend_url = sys.argv[2].rstrip("/")
frontend_url = sys.argv[3].rstrip("/")

def request(method, url, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read()
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return json.loads(body.decode("utf-8"))
        return body.decode("utf-8")

def fail(message):
    print(f"[FAIL] {message}")
    raise SystemExit(1)

health = request("GET", f"{backend_url}/health")
if health.get("status") != "ok":
    fail("Backend health returned unexpected status")
print("[PASS] Backend health")

novel = (root / "examples" / "novel-sample-1.txt").read_text(encoding="utf-8")
parsed = request("POST", f"{backend_url}/api/chapters/parse", {"content": novel})
if not parsed.get("valid") or parsed.get("chapter_count", 0) < 3:
    fail("Chapter parse did not return at least 3 valid chapters")
print("[PASS] Chapter parse")

generated = request("POST", f"{backend_url}/api/script/generate", {
    "title": "Smoke Test Novel",
    "genre": "都市",
    "chapters": parsed["chapters"],
})
if not generated.get("yaml"):
    fail("Script generate returned empty YAML")
print("[PASS] Script generate")

validation = request("POST", f"{backend_url}/api/script/validate", {"yaml": generated["yaml"]})
if not validation.get("valid"):
    fail("YAML validate failed: " + "; ".join(validation.get("errors", [])))
print("[PASS] YAML validate")

project = request("POST", f"{backend_url}/api/projects", {
    "title": "Smoke Test Project",
    "genre": "都市",
    "source_content": novel,
    "chapters": parsed["chapters"],
    "yaml": generated["yaml"],
    "validation": validation,
    "generation_mode": "mock",
})
if not project.get("id"):
    fail("Project create did not return an id")
print("[PASS] Project create")

version = request("POST", f"{backend_url}/api/projects/{project['id']}/versions", {
    "version_name": "Smoke Snapshot",
    "yaml": generated["yaml"],
    "validation": validation,
    "note": "Created by smoke test",
})
if not version.get("id"):
    fail("Version create did not return an id")
print("[PASS] Version create")

for fmt in ("yaml", "json", "markdown"):
    content = request("GET", f"{backend_url}/api/projects/{project['id']}/export/{fmt}")
    if not content:
        fail(f"Export {fmt} failed")
    print(f"[PASS] Export {fmt}")

request("GET", frontend_url)
print("[PASS] Frontend reachable")
print("[PASS] Smoke test completed")
PY
