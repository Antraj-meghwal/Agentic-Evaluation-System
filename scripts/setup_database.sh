#!/usr/bin/env bash
# Reset and initialize GradeOps PostgreSQL (dev only).
# Canonical: user=gradeops  password=gradeops  database=gradeops
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"
ENV_FILE="$BACKEND/.env"
EXAMPLE="$BACKEND/.env.example"

DB_USER="${POSTGRES_USER:-gradeops}"
DB_PASS="${POSTGRES_PASSWORD:-gradeops}"
DB_NAME="${POSTGRES_DB:-gradeops}"
DB_HOST="${POSTGRES_HOST:-localhost}"

write_env() {
  local port="$1"
  if [[ ! -f "$ENV_FILE" ]]; then
    cp "$EXAMPLE" "$ENV_FILE"
    echo "Created $ENV_FILE"
  fi
  local canonical="DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${port}/${DB_NAME}"
  if grep -q '^DATABASE_URL=' "$ENV_FILE"; then
    sed -i.bak "s|^DATABASE_URL=.*|${canonical}|" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
  else
    echo "$canonical" >> "$ENV_FILE"
  fi
  # Ensure POSTGRES_PORT in .env matches (db_url.py reads this if set)
  if grep -q '^POSTGRES_PORT=' "$ENV_FILE"; then
    sed -i.bak "s|^POSTGRES_PORT=.*|POSTGRES_PORT=${port}|" "$ENV_FILE" && rm -f "$ENV_FILE.bak"
  else
    echo "POSTGRES_PORT=${port}" >> "$ENV_FILE"
  fi
  export DATABASE_URL="postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${port}/${DB_NAME}"
  export POSTGRES_PORT="$port"
  echo "DATABASE_URL → postgresql://${DB_USER}:***@${DB_HOST}:${port}/${DB_NAME}"
}

COMPOSE_ENV="$ROOT/.env.compose"
COMPOSE_EXAMPLE="$ROOT/.env.compose.example"
if [[ ! -f "$COMPOSE_ENV" ]] && [[ -f "$COMPOSE_EXAMPLE" ]]; then
  cp "$COMPOSE_EXAMPLE" "$COMPOSE_ENV"
  echo "Created .env.compose from .env.compose.example"
fi

echo "== GradeOps database setup =="

USE_DOCKER=false
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  USE_DOCKER=true
fi

if [[ "$USE_DOCKER" == true ]]; then
  DB_PORT=5433
  echo "Using Docker Postgres on host port ${DB_PORT} (avoids Homebrew Postgres on 5432)."
  write_env "$DB_PORT"

  cd "$ROOT"
  if [[ ! -f "$COMPOSE_ENV" ]]; then
    echo "ERROR: Missing .env.compose — run: cp .env.compose.example .env.compose"
    exit 1
  fi
  docker compose down -v 2>/dev/null || true
  docker compose up -d postgres redis
  echo "Waiting for Postgres..."
  for i in $(seq 1 40); do
    if docker compose exec -T postgres pg_isready -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
      echo "Postgres ready."
      break
    fi
    sleep 1
    [[ "$i" -eq 40 ]] && { echo "ERROR: Postgres timeout"; exit 1; }
  done
else
  DB_PORT=5432
  if command -v docker >/dev/null 2>&1; then
    echo "Docker installed but daemon not running — using local Postgres on port ${DB_PORT}."
    echo "  (Start Docker Desktop, then re-run this script for port 5433.)"
  else
    echo "Using local Homebrew Postgres on port ${DB_PORT}."
  fi
  write_env "$DB_PORT"

  if ! command -v psql >/dev/null 2>&1; then
    echo "ERROR: Install Docker Desktop or: brew install postgresql@16"
    exit 1
  fi
  psql -v ON_ERROR_STOP=1 postgres <<SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();
DROP DATABASE IF EXISTS ${DB_NAME};
DROP ROLE IF EXISTS ${DB_USER};
CREATE ROLE ${DB_USER} WITH LOGIN PASSWORD '${DB_PASS}' CREATEDB;
CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
ALTER DATABASE ${DB_NAME} OWNER TO ${DB_USER};
GRANT ALL ON SCHEMA public TO ${DB_USER};
SQL
  echo "Local database recreated."
fi

echo ""
if [[ ! -d "$BACKEND/.venv" ]]; then
  python3 -m venv "$BACKEND/.venv"
fi
# shellcheck disable=SC1091
source "$BACKEND/.venv/bin/activate"
pip install -q psycopg2-binary alembic python-dotenv sqlalchemy

cd "$BACKEND"
python -c "
from core.db_url import get_database_url
import psycopg2
url = get_database_url()
conn = psycopg2.connect(url)
print('Connection OK:', url.replace('${DB_PASS}', '***'))
conn.close()
"

python -m alembic upgrade head
echo ""
echo "Success. Start API:"
echo "  cd backend && source .venv/bin/activate && uvicorn main:app --reload"
