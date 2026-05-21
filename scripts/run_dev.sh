#!/usr/bin/env bash
# Start backend after DB is ready. Run from repo root.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
source .venv/bin/activate
python -m alembic upgrade head
exec uvicorn main:app --reload --host 127.0.0.1 --port 8000
