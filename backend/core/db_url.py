"""
Single source of truth for PostgreSQL — reads only from environment / backend/.env.
No passwords or hosts are hardcoded in Python.
"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")


def get_database_url() -> str:
    explicit = (os.getenv("DATABASE_URL") or "").strip()
    if explicit:
        return explicit

    user = (os.getenv("POSTGRES_USER") or "").strip()
    password = (os.getenv("POSTGRES_PASSWORD") or "").strip()
    host = (os.getenv("POSTGRES_HOST") or "localhost").strip()
    port = (os.getenv("POSTGRES_PORT") or "").strip()
    name = (os.getenv("POSTGRES_DB") or "").strip()

    missing = [
        k
        for k, v in [
            ("POSTGRES_USER", user),
            ("POSTGRES_PASSWORD", password),
            ("POSTGRES_PORT", port),
            ("POSTGRES_DB", name),
        ]
        if not v
    ]
    if missing:
        raise RuntimeError(
            f"Set DATABASE_URL or all of {', '.join(missing)} in {BACKEND_DIR / '.env'}. "
            f"Copy from {BACKEND_DIR / '.env.example'} and run ./scripts/setup_database.sh"
        )

    safe_password = quote_plus(password)
    return f"postgresql://{user}:{safe_password}@{host}:{port}/{name}"
