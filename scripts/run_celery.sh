#!/usr/bin/env bash
# Celery worker for async tribunal grading (requires Redis).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
source .venv/bin/activate
exec celery -A tasks.celery_app worker --loglevel=info
