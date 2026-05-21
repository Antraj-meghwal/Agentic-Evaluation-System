# GRADEOPS — project brief vs implementation

| Goal | Status | Implementation |
|------|--------|----------------|
| Web portal: bulk PDF upload + JSON rubric | Done | `POST /upload/bulk`, rubric on upload page |
| RBAC: Instructor vs TA | Done | JWT roles; route guards; review API restricted to TA/instructor |
| OCR (Qwen-VL + Nougat fallback) | Done | `services/pipeline/extract/ocr.py` via Hugging Face |
| Cloud storage for scans | Done (optional) | `STORAGE_BACKEND=s3` or local default |
| Agentic pipeline: partial credit | Done | `criteria_breakdown` in grader + review UI |
| Structured justifications | Done | `feedback` + per-criterion `reasoning` |
| Plagiarism detection | Done | Transcript + CLIP similarity in `plagiarism_service.py` |
| Review dashboard: side-by-side + shortcuts | Done | `ReviewPage.jsx` — A/O/J/K |
| LangGraph orchestration | Done | `pipeline/tribunal/graph.py` |
| PostgreSQL | Done | Docker Compose + Alembic |
| React + FastAPI | Done | `frontend-react` + `backend` |

## Demo accounts (after seed)

```bash
cd backend && python scripts/seed_demo_users.py
```

| Email | Password | Role |
|-------|----------|------|
| instructor@gradeops.edu | demo1234 | instructor |
| ta@gradeops.edu | demo1234 | ta |
