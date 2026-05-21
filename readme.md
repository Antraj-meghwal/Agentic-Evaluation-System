
# Agentic Evaluation System (GradeOps)

## Human-in-the-Loop AI Grading Platform

Agentic Evaluation System is an AI-powered Human-in-the-Loop (HITL) grading platform designed to automate and streamline the evaluation of handwritten examinations using Vision-Language Models (VLMs), OCR pipelines, and Agentic LLM workflows.

The platform enables instructors to upload bulk scanned exam papers and structured JSON rubrics, allowing the system to automatically extract handwritten responses, interpret complex answers, award partial credit, and generate transparent grading justifications.

To ensure fairness and reliability, AI-generated evaluations are reviewed through a high-speed Teaching Assistant dashboard where grades can be approved, modified, or overridden.

## Quick start (for reviewers)

**Full instructions:** [docs/SETUP.md](docs/SETUP.md)  
**Project goals checklist:** [docs/PROJECT_GOALS.md](docs/PROJECT_GOALS.md)  
**Before pushing to GitHub:** [docs/SECURITY.md](docs/SECURITY.md) and `./scripts/check-secrets.sh`

Run **one command per line** (zsh treats `#` as a comment only at the start of a line):

```bash
./scripts/setup_database.sh
./scripts/check-secrets.sh
cp frontend-react/.env.example frontend-react/.env.local
cd backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
./scripts/run_dev.sh
```

Frontend (second terminal):

```bash
cd frontend-react && npm install && npm run dev
```

## Multi-model pipeline (Hugging Face)

See `docs/PIPELINE_ROADMAP.md` for the step-by-step build. **Step 1 (EXTRACT)** is implemented:

- PDF → page/question crops
- Qwen-VL OCR via Hugging Face Inference API
- Context assembly (transcript + image + rubric JSON)

```bash
POST /grading/extract/{upload_id}      # Step 1 — OCR + context
POST /grading/run/{upload_id}          # Full Tribunal + DB persist
GET  /grading/results/{upload_id}      # Per-question scores
GET  /api/review/review-queue          # TA review queue
```

Set `HF_TOKEN` in `backend/.env`, or `PIPELINE_DRY_RUN=true` for local dev without API calls.

**Full pipeline (Steps 1–4)**

```bash
POST /grading/extract/{upload_id}      # Step 1 — OCR + context
POST /grading/run-async/{upload_id}    # Steps 2–3 — Tribunal + verify (Celery)
GET  /grading/results/{upload_id}      # Per-question scores
GET  /api/review/review-queue          # TA review queue
GET  /api/export/csv/{upload_id}       # Gradebook export
```

