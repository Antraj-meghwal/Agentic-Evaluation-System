# GradeOps Tribunal — Step-by-step build plan

Architecture reference: `gradeops_tribunal_architecture.svg`

## Step 1 — EXTRACT (done)

- [x] `services/pipeline/` package with HF config + client
- [x] PDF → page crops → question crops (`vision_router`)
- [x] Qwen-VL OCR via Hugging Face (`extract/ocr.py`) with Nougat fallback
- [x] Context assembler: transcript + image + rubric
- [x] API: `POST /grading/extract/{upload_id}`

## Step 2 — TRIBUNAL (done)

- [x] Grader + Critic agents via shared HF client (`services/tribunal_agents.py`)
- [x] Coordinator + escalation (`pipeline/tribunal/`, `pipeline/verify/`)
- [x] Bridge: `services/tribunal_runner.py` — EXTRACT → Tribunal → PostgreSQL
- [x] API: `POST /grading/run/{upload_id}` (+ `/rubric` variant)
- [x] API: `GET /grading/results/{upload_id}`

## Step 3 — VERIFY (partial)

- [x] Plagiarism: transcript similarity within upload (`services/plagiarism_service.py`)
- [x] Persist grades to PostgreSQL (`grading_results`, `question_crops`)
- [ ] CLIP visual plagiarism (not implemented)
- [ ] Celery async batch queue wired from upload UI

## Step 4 — DELIVER (done)

- [x] TA dashboard → `/api/review/stats` + review queue preview
- [x] Review page: crop image + AI grade side-by-side
- [x] Keyboard shortcuts: **A** approve, **O** override, **J/K** next/prev
- [x] Upload details: rubric JSON upload + Extract + Tribunal buttons
- [ ] Gradebook CSV/LMS export

**Try full pipeline**

```bash
cd backend
cp .env.example .env   # HF_TOKEN or PIPELINE_DRY_RUN=true
pip install -r requirements.txt
uvicorn main:app --reload
# Upload PDF → open upload details → Run Tribunal → /review for flagged items
```
