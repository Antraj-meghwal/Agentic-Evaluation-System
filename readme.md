# GradeOps — Agentic Evaluation System

> **Human-in-the-Loop AI Grading Platform** for handwritten examinations using Vision-Language Models, OCR pipelines, and Agentic LLM workflows.

---

## Overview

GradeOps automates the evaluation of scanned exam papers end-to-end:

1. **Bulk Upload** — Instructors upload PDFs/images + structured JSON rubrics.
2. **OCR / Vision** — Qwen-VL (with Nougat fallback) extracts handwritten answers.
3. **Agentic Tribunal** — A LangGraph state machine runs Grader → Critic → Resolution nodes, awarding partial credit with per-criterion justifications.
4. **Plagiarism Detection** — Text similarity (within-exam + cross-paper) and CLIP visual similarity flag suspicious pairs.
5. **TA Review Dashboard** — Side-by-side crop + AI grade with keyboard shortcuts (`A` approve, `O` override, `J/K` navigate) for high-throughput review.
6. **Export** — CSV gradebook export for institutional systems.

## Architecture

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite + TailwindCSS 4 |
| Backend API | FastAPI (Python) |
| Database | PostgreSQL 16 + Alembic migrations |
| Async Jobs | Celery + Redis |
| AI Pipeline | Hugging Face Inference API, LangGraph, ChromaDB (RAG) |
| Auth | JWT with role-based access control (Instructor / TA) |
| Storage | Local filesystem or S3 (`STORAGE_BACKEND` env var) |

## Project Structure

```
GRADEOPS/
├── backend/                  # FastAPI application
│   ├── api/routes/           # Review, export, dashboard API routes
│   ├── core/                 # Config, security, constants
│   ├── db/                   # SQLAlchemy session, base model
│   ├── models/               # ORM models (User, Batch, Submission, GradingResult, etc.)
│   ├── pipeline/tribunal/    # LangGraph graph (grader → critic → resolution)
│   ├── routes/               # Upload, user, grading routes
│   ├── schemas/              # Pydantic request/response schemas
│   ├── services/             # Business logic (OCR, tribunal, plagiarism, RAG, export)
│   ├── scripts/              # Seed demo users
│   ├── tasks/                # Celery async tasks
│   └── requirements.txt      # Python dependencies
├── frontend-react/           # Vite + React SPA
│   └── src/
│       ├── components/       # Navbar, Sidebar, StatCard, StatusBadge, etc.
│       ├── context/          # AuthContext (JWT decode, role management)
│       ├── pages/            # Login, Register, Dashboard, Upload, Review, etc.
│       ├── routes/           # ProtectedRoute (RBAC guard)
│       └── services/         # Axios API client with interceptors
├── docs/                     # Setup, security, pipeline roadmap, demo guide
├── examples/                 # Sample rubric + DocLayNet test data
├── scripts/                  # Setup, run, check scripts
├── docker/                   # Postgres init SQL
└── docker-compose.yml        # Postgres + Redis for local dev
```

## Quick Start

> **Full instructions:** [docs/SETUP.md](docs/SETUP.md)

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Node.js | 18+ |
| PostgreSQL | 16+ (local or Docker) |
| poppler | `brew install poppler` on macOS |

### 1. Clone & Configure

```bash
git clone https://github.com/Antraj-meghwal/Agentic-Evaluation-System.git
cd Agentic-Evaluation-System
cp backend/.env.example backend/.env        # Edit SECRET_KEY, HF_TOKEN
cp frontend-react/.env.example frontend-react/.env.local
```

### 2. Setup Backend

```bash
./scripts/setup_venv.sh          # Creates backend/.venv + installs all requirements
./scripts/setup_database.sh      # Postgres + Alembic migrations
```

### 3. Start Servers

**Terminal 1 — Backend:**
```bash
./scripts/run_dev.sh
# API docs at http://127.0.0.1:8000/docs
```

**Terminal 2 — Frontend:**
```bash
cd frontend-react && npm install && npm run dev
# UI at http://localhost:5173
```

### 4. Demo Accounts

```bash
cd backend && python scripts/seed_demo_users.py
```

| Email | Password | Role |
|-------|----------|------|
| instructor@gradeops.edu | demo1234 | Instructor |
| ta@gradeops.edu | demo1234 | TA |

## API Endpoints

```
POST /upload/bulk                    # Bulk PDF/image upload + rubric
POST /grading/extract/{upload_id}    # Step 1 — OCR + context assembly
POST /grading/run/{upload_id}        # Full Tribunal pipeline (sync)
POST /grading/run-async/{upload_id}  # Tribunal pipeline (Celery async)
GET  /grading/results/{upload_id}    # Per-question scores + feedback
GET  /api/review/review-queue        # TA review queue
POST /api/review/approve/{id}        # Approve a grading result
POST /api/review/override/{id}       # Override score + feedback
GET  /api/export/csv/{upload_id}     # Gradebook CSV export
GET  /api/dashboard/stats            # Dashboard statistics
```

## Pipeline Modes

| Mode | Config | Description |
|------|--------|-------------|
| **Dry Run** | `PIPELINE_DRY_RUN=true` | Mock OCR/grading — full UI flow without API calls |
| **Live** | `PIPELINE_DRY_RUN=false` + `HF_TOKEN` | Real Qwen-VL OCR + LLM tribunal grading |

## Utility Scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup_venv.sh` | Create Python venv + install dependencies |
| `scripts/setup_database.sh` | Initialize PostgreSQL + run migrations |
| `scripts/run_dev.sh` | Start FastAPI with auto-reload |
| `scripts/run_celery.sh` | Start Celery worker for async tribunal |
| `scripts/check-secrets.sh` | Scan tracked files for leaked credentials |
| `scripts/check_connections.py` | Verify PostgreSQL, Redis, poppler, HF API |
| `scripts/download_doclaynet_samples.py` | Download DocLayNet test pages |

## Security

- **No secrets in Git.** All credentials live in gitignored `.env` files.
- Run `./scripts/check-secrets.sh` before every push.
- See [docs/SECURITY.md](docs/SECURITY.md) for full policy.

## Demo Recording

See [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) for step-by-step demo video instructions.

## Goals Checklist

See [docs/PROJECT_GOALS.md](docs/PROJECT_GOALS.md) for the feature-by-feature implementation status.
