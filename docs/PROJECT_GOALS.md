# GRADEOPS — project brief vs implementation

| Goal | Status | Implementation |
|------|--------|----------------|
| Web portal: bulk PDF upload + JSON rubric | **Done** | `POST /upload/bulk`, rubric validated with `GradingRubric`, upload UI + details |
| RBAC: Instructor vs TA | **Done** | JWT roles; `require_role`; separate dashboards; review API for TA+ |
| OCR (Qwen-VL + Nougat fallback) | **Done** | `services/pipeline/extract/ocr.py` via Hugging Face |
| Cloud storage for scans | **Done** | `STORAGE_BACKEND=s3` or local default |
| Agentic pipeline: partial credit | **Done** | LangGraph tribunal + `criteria_breakdown` |
| Structured justifications | **Done** | `feedback` + per-criterion `reasoning` |
| Plagiarism detection | **Done** | Within-exam + cross-paper (same rubric batch) + CLIP visual |
| RAG consistency | **Done** | `retrieve_similar_answers` wired into tribunal context |
| Review dashboard: side-by-side + shortcuts | **Done** | `ReviewPage.jsx` — A approve, O override (submit when focused), J/K navigate |
| LangGraph orchestration | **Done** | `pipeline/tribunal/graph.py` |
| PostgreSQL | **Done** | Docker Compose + Alembic |
| React + FastAPI | **Done** | `frontend-react` + `backend` |

## Demo accounts (after seed)

```bash
cd backend && python scripts/seed_demo_users.py
```

| Email | Password | Role |
|-------|----------|------|
| instructor@gradeops.edu | demo1234 | instructor |
| ta@gradeops.edu | demo1234 | ta |

## Real model testing

```bash
# backend/.env
PIPELINE_DRY_RUN=false
HF_TOKEN=your_huggingface_token
```

Requires **poppler** (`brew install poppler` on macOS) and optional Celery worker for async tribunal.
