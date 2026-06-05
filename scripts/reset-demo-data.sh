#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rm -f "$ROOT/backend/data/novel2script.db" "$ROOT/backend/data/novel2script.db-shm" "$ROOT/backend/data/novel2script.db-wal"
echo "[PASS] Demo data reset. The backend will recreate SQLite tables on next start."
