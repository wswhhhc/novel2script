#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_HOST="${BACKEND_HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-127.0.0.1}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

command -v python >/dev/null 2>&1 || { echo "[FAIL] python is not available"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "[FAIL] node is not available"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "[FAIL] npm is not available"; exit 1; }

check_port() {
  local port="$1"
  local label="$2"
  if command -v lsof >/dev/null 2>&1 && lsof -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "[FAIL] $label port $port is already in use"
    exit 1
  fi
}

check_port "$BACKEND_PORT" "Backend"
check_port "$FRONTEND_PORT" "Frontend"

cd "$ROOT"

if [ ! -d "frontend/node_modules" ]; then
  echo "[INFO] Installing frontend dependencies..."
  (cd frontend && npm install)
fi

cleanup() {
  kill "${BACKEND_PID:-0}" "${FRONTEND_PID:-0}" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

echo "[INFO] Starting backend at http://$BACKEND_HOST:$BACKEND_PORT"
python -m uvicorn app.main:app --reload --app-dir backend --host "$BACKEND_HOST" --port "$BACKEND_PORT" &
BACKEND_PID=$!

echo "[INFO] Starting frontend at http://$FRONTEND_HOST:$FRONTEND_PORT"
(cd frontend && VITE_API_BASE_URL="http://$BACKEND_HOST:$BACKEND_PORT" npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT") &
FRONTEND_PID=$!

echo "Novel2Script is starting."
echo "Backend:  http://$BACKEND_HOST:$BACKEND_PORT"
echo "Frontend: http://$FRONTEND_HOST:$FRONTEND_PORT"
echo "Mock mode is enabled unless ENABLE_AI_GENERATION=true is set."
wait
