# GradeOps Tribunal — Step-by-step build plan

Architecture reference: `gradeops_tribunal_architecture.svg`

## Step 1 — EXTRACT (done)

- [x] `services/pipeline/` package with HF config + client
- [x] PDF → page crops → question crops (`vision_router`)
- [x] Qwen-VL OCR via Hugging Face (`extract/ocr.py`)
- [x] Context assembler: transcript + image + rubric
- [x] API: `POST /grading/extract/{upload_id}`

**Try it**

```bash
cd backend
cp .env.example .env   # add HF_TOKEN or PIPELINE_DRY_RUN=true
pip install -r requirements.txt
uvicorn main:app --reload
# Upload a PDF, then:
curl -X POST http://127.0.0.1:8000/grading/extract/1 -H "Authorization: Bearer <token>"
```

## Step 2 — TRIBUNAL (next)

- LangGraph workflow: Grader + Critic + RAG agents
- HF models: Qwen-VL (grader), Llama-3 (critic), embeddings for RAG
- Coordinator + consensus loop

## Step 3 — VERIFY

- Plagiarism: CLIP + sentence-transformers on HF
- Persist grades to PostgreSQL

## Step 4 — DELIVER

- Wire TA dashboard to pipeline results
- Keyboard shortcuts for approve / override
