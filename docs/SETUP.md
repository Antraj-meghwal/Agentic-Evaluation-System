# GradeOps — setup for reviewers (mentor / TA)

This guide is for someone who **clones the repo and runs it locally**. No passwords or API keys are stored in Git — you create your own `.env` files.

## Prerequisites

| Tool | Version (tested) |
|------|------------------|
| Python | 3.11+ |
| Node.js | 18+ |
| Docker Desktop | optional but recommended (Postgres + Redis) |
| poppler | for PDF → image (`brew install poppler` on macOS) |

## 1. Clone and configure secrets (local only)

```bash
git clone https://github.com/Antraj-meghwal/Agentic-Evaluation-System.git
cd Agentic-Evaluation-System
```

**Never commit these files:** `backend/.env`, `frontend-react/.env`, anything under `backend/uploads/` except `.gitkeep`.

```bash
./scripts/setup_database.sh   # creates backend/.env with correct port + runs migrations
cp frontend-react/.env.example frontend-react/.env.local
```

Edit `backend/.env` after setup if needed:

- `SECRET_KEY` — `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `PIPELINE_DRY_RUN=true` — recommended for first run (no Hugging Face billing)
- `HF_TOKEN` — only for live OCR/grading

**Never commit:** `backend/.env`, `.env.compose`, `frontend-react/.env.local`. See [docs/SECURITY.md](SECURITY.md).

## 2. Database (one command — recommended)

```bash
./scripts/setup_database.sh
```

| Mode | Port | When |
|------|------|------|
| **Docker** (Docker Desktop running) | **5433** | Avoids conflict with Homebrew Postgres |
| **Local Homebrew** | **5432** | When Docker is not running |

Same credentials everywhere: user **`gradeops`**, password **`gradeops`**, database **`gradeops`**.

```bash
cp .env.compose.example .env.compose   # only if using Docker
```

## 3. Backend (venv + all requirements)

From the **repo root**:

```bash
./scripts/setup_venv.sh
```

This creates `backend/.venv` and installs everything in `backend/requirements.txt` (FastAPI, Postgres, Celery, PyTorch, LangGraph, ChromaDB, etc.).

Activate manually if needed:

```bash
cd backend
source .venv/bin/activate   # Windows: .venv\Scripts\activate
# If you skipped setup_database.sh:
python -m alembic upgrade head
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Or from repo root: `./scripts/run_dev.sh` (activates venv automatically).

Optional — async tribunal (Celery) in a **second terminal**:

```bash
cd backend && source .venv/bin/activate
celery -A tasks.celery_app worker --loglevel=info
```

API docs: http://127.0.0.1:8000/docs

## 4. Frontend

```bash
cd frontend-react
npm install
npm run dev
```

Open http://localhost:5173

## 5. Demo users (optional)

```bash
cd backend && python scripts/seed_demo_users.py
```

| Email | Password | Role |
|-------|----------|------|
| instructor@gradeops.edu | demo1234 | instructor |
| ta@gradeops.edu | demo1234 | ta |

## 6. Smoke test

1. Register at `/register` or use demo accounts above.
2. Log in — you should receive a JWT.
3. Upload a sample PDF + rubric from `examples/sample_rubric.json`.
4. Run **Extract** then **Run Tribunal (now)** on the upload details page (sync; no Celery required).
5. Optional: use **Run in background** if Celery worker is running.
6. Log in as TA → **Review** queue → approve with **A**, override with **O** (focus field, press O again to submit).
7. With `PIPELINE_DRY_RUN=true`, grades are mock but the full UI flow works.

See [PROJECT_GOALS.md](PROJECT_GOALS.md) for brief ↔ implementation mapping.

## Environment reference

| Variable | Required | Purpose |
|----------|----------|---------|
| `DATABASE_URL` | yes | PostgreSQL connection string |
| `SECRET_KEY` | yes | JWT signing (must differ per machine) |
| `HF_TOKEN` | no* | Hugging Face Inference API |
| `PIPELINE_DRY_RUN` | no | `true` = mock OCR/grades without API |
| `REDIS_URL` | for async | Celery broker |

\* Required only when `PIPELINE_DRY_RUN=false`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `DATABASE_URL is not set` | Create `backend/.env` from `.env.example` |
| Alembic connection refused | Start `docker compose up -d` |
| CORS / network errors in UI | Check `frontend-react/.env` → `VITE_API_URL` matches backend |
| Celery tasks never run | Start Redis + Celery worker |
| PDF crop fails | Install poppler (`pdftoppm` on PATH) |

## Security before you push to GitHub

Run from repo root:

```bash
./scripts/check-secrets.sh
```

See [docs/SECURITY.md](SECURITY.md) for what must stay out of the repo and how to scrub leaked history.
