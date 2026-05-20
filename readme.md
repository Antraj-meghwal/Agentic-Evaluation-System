
# Agentic Evaluation System

## Human-in-the-Loop AI Grading Platform

Agentic Evaluation System is an AI-powered Human-in-the-Loop (HITL) grading platform designed to automate and streamline the evaluation of handwritten examinations using Vision-Language Models (VLMs), OCR pipelines, and Agentic LLM workflows.

The platform enables instructors to upload bulk scanned exam papers and structured JSON rubrics, allowing the system to automatically extract handwritten responses, interpret complex answers, award partial credit, and generate transparent grading justifications.

To ensure fairness and reliability, AI-generated evaluations are reviewed through a high-speed Teaching Assistant dashboard where grades can be approved, modified, or overridden.

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

