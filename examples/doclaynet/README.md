# DocLayNet samples for GRADEOPS testing

[DocLayNet](https://huggingface.co/datasets/docling-project/DocLayNet) is an IBM document layout dataset (80k+ pages, 11 layout classes). GRADEOPS uses it to test **upload → OCR → tribunal grading → review** on real document pages—not handwritten exams.

## 1. Download samples (one-time)

From repo root, with backend venv:

```bash
cd backend && source .venv/bin/activate
pip install pyarrow huggingface_hub Pillow
cd ..
python scripts/download_doclaynet_samples.py --count 5
```

This downloads **one parquet shard** (~250MB), not the full dataset, and exports 5 PNG/PDF pages to `examples/doclaynet_samples/`.

Optional: set `HF_TOKEN` in the environment for faster Hugging Face downloads.

## 2. Run GRADEOPS on the samples

1. Start stack: `./scripts/run_dev.sh` and `cd frontend-react && npm run dev`
2. Login: `instructor@gradeops.edu` / `demo1234`
3. **New Upload** → select all files in `examples/doclaynet_samples/*.png` (or PDFs)
4. Rubric: `examples/doclaynet_rubric.json`
5. **Upload & Continue**
6. **Extract (OCR)** → **Run Tribunal (now)** (avoid background unless Celery is running)
7. Login as TA → **Review** queue

## 3. What this tests

| GRADEOPS goal | DocLayNet test |
|---------------|----------------|
| Bulk upload | Multiple document pages |
| OCR / vision | Printed/scanned layout pages |
| Rubric + partial credit | 2 region-based questions (q1/q2) |
| Tribunal pipeline | Full LangGraph grading |
| Review UI | Side-by-side crop + feedback |

## 4. Layout classes (reference)

Caption, Footnote, Formula, List-item, Page-footer, Page-header, Picture, Section-header, Table, Text, Title — see `manifest.json` after download for bbox counts per page.
