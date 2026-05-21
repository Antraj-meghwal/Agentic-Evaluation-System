"""
Single source of truth for PostgreSQL connection settings.

Used by: database.py, db/session.py, alembic/env.py, core/config.py
Matches docker-compose.yml and backend/.env.example exactly.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Always load backend/.env (not cwd-dependent)
BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

# Canonical dev credentials — same as docker-compose.yml
DB_USER = os.getenv("POSTGRES_USER", "gradeops")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "gradeops")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
# Default 5433 matches docker-compose host port; use 5432 only for local Homebrew Postgres
DB_PORT = os.getenv("POSTGRES_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB", "gradeops")

DEFAULT_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def get_database_url() -> str:
    url = (os.getenv("DATABASE_URL") or DEFAULT_DATABASE_URL).strip()
    if not url:
        raise RuntimeError(
            f"DATABASE_URL is empty. Copy {BACKEND_DIR / '.env.example'} to "
            f"{BACKEND_DIR / '.env'} or set DATABASE_URL."
        )
    return url
