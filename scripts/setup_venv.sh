#!/usr/bin/env bash
# Create backend/.venv and install all Python dependencies from requirements.txt
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
VENV="$BACKEND/.venv"
REQ="$BACKEND/requirements.txt"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Install Python 3.11+."
  exit 1
fi

echo "== GradeOps Python venv =="

if [[ ! -d "$VENV" ]]; then
  echo "Creating $VENV"
  python3 -m venv "$VENV"
else
  echo "Using existing $VENV"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

python -m pip install --upgrade pip wheel
# torch requires setuptools<82
pip install "setuptools>=70,<82"
echo "Installing dependencies from requirements.txt (this may take several minutes)..."
pip install -r "$REQ"

echo ""
echo "Verifying key imports..."
python -c "
import fastapi, uvicorn, sqlalchemy, psycopg2, celery, redis
import pdf2image, fitz, chromadb, langgraph
import torch, transformers, sentence_transformers
print('All core packages OK')
"

echo ""
echo "venv ready. Activate with:"
echo "  cd backend && source .venv/bin/activate"
echo ""
echo "Then run database setup (if needed):"
echo "  ./scripts/setup_database.sh"
echo ""
echo "Start API:"
echo "  ./scripts/run_dev.sh"
