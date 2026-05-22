# GradeOps — Video Demo Recording Guide

This guide provides step-by-step instructions and terminal commands to run a complete, end-to-end product demonstration of the **GradeOps Agentic Evaluation System**.

---

## 1. Environment Preparation & Cleanup

Before starting the recording, ensure that local PostgreSQL and Redis servers are running, the database is fresh, and demo users are seeded.

```bash
# 1. Start database and cache services (PostgreSQL & Redis)
# If PostgreSQL is not running:
/Users/deepak/bin/pg_ctl -D /Users/deepak/pgdata start

# 2. Reset database and run migrations
./scripts/setup_database.sh

# 3. Seed demo accounts
backend/.venv/bin/python backend/scripts/seed_demo_users.py

# 4. Download a few layout sample pages for the demo
backend/.venv/bin/python scripts/download_doclaynet_samples.py --count 3
```

---

## 2. Start Application Servers

Open two terminal windows/tabs to start the backend API and frontend dev server:

### Terminal 1: Backend FastAPI Server
```bash
cd backend
source .venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
*API docs will be available at:* http://127.0.0.1:8000/docs

### Terminal 2: Frontend React (Vite) Server
```bash
cd frontend-react
npm run dev
```
*Frontend UI will be available at:* http://localhost:5173

---

## 3. Demo Walkthrough Script (The Video Flow)

Use the following narrative script for the screen recording:

### Phase A: Instructor Portal & Upload (0:00 - 1:00)
1. Navigate to http://localhost:5173 in your browser.
2. Log in as the Instructor:
   - **Email:** `instructor@gradeops.edu`
   - **Password:** `demo1234`
3. Click on the **"New Upload"** button.
4. Upload test files:
   - Click the file picker and select PNG or PDF files from `examples/doclaynet_samples/`.
   - Select the rubric JSON file: `examples/doclaynet_rubric.json`.
5. Click **"Upload & Continue"**. This redirects you to the Upload Details page.

### Phase B: Extraction & Tribunal Pipeline (1:00 - 2:00)
1. Explain the **OCR/Vision** step:
   - Click **"Extract (OCR)"**. This processes the document pages, extracting messy textual and mathematical layout regions (simulating Qwen-VL with Nougat fallback).
2. Explain the **Agentic LLM Pipeline**:
   - Click **"Run Tribunal (now)"**. This triggers the LangGraph state machine:
     - **Grader Node:** Evaluates the rubric criteria and awards partial credit.
     - **Critic Node:** Audits the grader's decisions for inconsistencies.
     - **Resolution Node:** Integrates the critique and makes the final determination.
3. Observe the pipeline status changing to **Graded** and notice any plagiarism flags (visual or cross-paper similarity).
4. **Log Out** of the instructor account.

### Phase C: TA Review Dashboard & Keyboard Shortcuts (2:00 - 3:15)
1. Log in as the Teaching Assistant (TA):
   - **Email:** `ta@gradeops.edu`
   - **Password:** `demo1234`
2. Navigate to the **"Review"** dashboard queue.
3. Show the side-by-side interface:
   - **Left side:** The cropped region of the student answer sheet.
   - **Right side:** The AI-awarded score, grading criteria breakdown, and textual justifications.
4. Demo the **Keyboard Shortcuts** (designed for high-throughput grading):
   - Press **`J`** and **`K`** to navigate between student answers.
   - Press **`A`** to approve the current grade instantly.
   - Press **`O`** to focus the override score field. Modify the score/feedback, then press **`O`** again to submit the override.
5. Highlight the **Plagiarism Alerts** flag showing identical or highly similar logic structures across different papers.

---

## 4. Recording Commands & Tools

### Option A: Native macOS Screen Recording (Recommended)
The built-in macOS screen recorder is hardware-optimized and captures crisp GUI interfaces:
- Press `Cmd + Shift + 5`.
- Select **"Record Selected Portion"** and adjust the frame to capture the browser window.
- Click **"Record"** to start, and click the Stop icon in the top macOS menu bar to save.

### Option B: Command Line Recording via FFmpeg
If you prefer recording via terminal, verify `ffmpeg` is installed (`brew install ffmpeg`) and run:

```bash
# Capture full screen (1920x1080) at 30 fps
ffmpeg -f avfoundation -i "1:0" -r 30 -s 1920x1080 out.mp4
```
*Note: Adjust `"1:0"` input index to select your specific display or audio source (use `ffmpeg -f avfoundation -list_devices true -i ""` to list them).*
