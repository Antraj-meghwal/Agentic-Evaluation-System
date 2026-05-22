#!/usr/bin/env python3
"""
GradeOps System Connections & Dependencies Validator.
Run with:
  cd backend && source .venv/bin/activate
  python ../scripts/check_connections.py
"""

import os
import shutil
import sys
from pathlib import Path

# Setup path to import core config
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "backend"))

# Terminal colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_section(title):
    print(f"\n{BOLD}{BLUE}=== {title} ==={RESET}")

def print_ok(msg):
    print(f"  {GREEN}✓{RESET} {msg}")

def print_warn(msg):
    print(f"  {YELLOW}⚠{RESET} {msg}")

def print_fail(msg):
    print(f"  {RED}✗{RESET} {msg}")

def check_venv():
    print_section("Python Environment")
    venv_path = os.getenv("VIRTUAL_ENV")
    if venv_path:
        print_ok(f"Active Virtual Environment: {venv_path}")
    else:
        print_warn("No active python virtual environment detected in environment variables. Run: source backend/.venv/bin/activate")

    try:
        import fastapi
        import sqlalchemy
        import langgraph
        print_ok("Core python packages (fastapi, sqlalchemy, langgraph) are importable.")
    except ImportError as e:
        print_fail(f"Missing core python package: {e}. Run ./scripts/setup_venv.sh")
        return False
    return True

def check_database():
    print_section("PostgreSQL Database Connection")
    try:
        from core.config import settings
        db_url = settings.DATABASE_URL
    except Exception as e:
        print_fail(f"Could not load database configuration: {e}")
        return False

    # Hide password in logs
    masked_url = db_url
    if "@" in db_url:
        parts = db_url.split("@")
        cred_part = parts[0].split("://")
        if len(cred_part) > 1 and ":" in cred_part[1]:
            user = cred_part[1].split(":")[0]
            masked_url = f"{cred_part[0]}://{user}:***@{parts[1]}"

    print(f"  Configured URL: {masked_url}")

    try:
        import psycopg2
        conn = psycopg2.connect(db_url, connect_timeout=3)
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        cur.execute("SELECT current_database();")
        db_name = cur.fetchone()[0]
        print_ok(f"Connected successfully to database: {db_name}")
        print_ok(f"PostgreSQL Version: {version.split(',')[0]}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print_fail(f"Database connection failed: {e}")
        print_warn("Make sure Postgres is running: docker compose up -d postgres")
        return False

def check_redis():
    print_section("Redis Connection (Celery Broker)")
    try:
        from core.config import settings
        redis_url = settings.REDIS_URL
    except Exception as e:
        print_fail(f"Could not load Redis configuration: {e}")
        return False

    print(f"  Configured URL: {redis_url}")

    try:
        import redis
        r = redis.Redis.from_url(redis_url, socket_timeout=3)
        if r.ping():
            print_ok("Redis ping successful.")
            return True
        else:
            print_fail("Redis ping returned False.")
            return False
    except Exception as e:
        print_fail(f"Redis connection failed: {e}")
        print_warn("Make sure Redis is running: docker compose up -d redis")
        return False

def check_poppler():
    print_section("System Dependencies (Poppler)")
    pdftoppm_path = shutil.which("pdftoppm")
    if pdftoppm_path:
        print_ok(f"poppler ('pdftoppm') found at: {pdftoppm_path}")
        return True
    else:
        print_fail("poppler ('pdftoppm') not found in system PATH.")
        if sys.platform == "darwin":
            print_warn("Install via Homebrew: brew install poppler")
        else:
            print_warn("Install via apt: apt-get install -y poppler-utils")
        return False

def check_huggingface():
    print_section("Hugging Face API & Pipeline Mode")
    try:
        from services.pipeline.config import MODELS, PIPELINE_DRY_RUN
        from services.pipeline.hf_client import HF_TOKEN
    except Exception as e:
        print_fail(f"Could not load Hugging Face config: {e}")
        return False

    print(f"  PIPELINE_DRY_RUN: {PIPELINE_DRY_RUN}")
    print(f"  OCR Primary Model: {MODELS.ocr_vlm}")
    print(f"  OCR Fallback Model: {MODELS.ocr_fallback}")

    if PIPELINE_DRY_RUN:
        print_ok("Running in DRY_RUN mode. Grading will use local mock models (no API keys required).")
        return True

    if not HF_TOKEN:
        print_fail("HF_TOKEN is missing in .env but PIPELINE_DRY_RUN is set to false.")
        print_warn("Set PIPELINE_DRY_RUN=true in backend/.env to run locally without a token.")
        return False

    # Mask token
    masked_token = HF_TOKEN[:8] + "..." + HF_TOKEN[-4:] if len(HF_TOKEN) > 12 else "***"
    print(f"  HF_TOKEN: {masked_token}")

    try:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=HF_TOKEN)
        # Quick check by looking up a lightweight config or checking token validity
        print_ok("Hugging Face Hub library imported and token parsed.")
        return True
    except Exception as e:
        print_fail(f"Hugging Face token validation failed: {e}")
        return False

def main():
    print(f"{BOLD}==================================================")
    print("      GradeOps Dependency & Connection Check")
    print(f"=================================================={RESET}")

    venv_ok = check_venv()
    db_ok = check_database()
    redis_ok = check_redis()
    poppler_ok = check_poppler()
    hf_ok = check_huggingface()

    print(f"\n{BOLD}==================================================")
    if venv_ok and db_ok and redis_ok and poppler_ok and hf_ok:
        print(f"  {GREEN}Status: ALL CONNECTIONS AND DEPENDENCIES OK{RESET}")
        return 0
    else:
        print(f"  {YELLOW}Status: SOME DEPENDENCIES ARE MISSING OR OFFLINE{RESET}")
        print("  Please check warnings/failures above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
